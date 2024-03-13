"""shamela2epub main."""

from collections.abc import Callable
from pathlib import Path

from tqdm import tqdm

from shamela2epub import OUT_DIR
from shamela2epub.misc.http import TIME_OUT, get_session
from shamela2epub.misc.utils import get_book_first_page_url, get_book_info_page_url, is_valid_url
from shamela2epub.models.book_html_page import BookHTMLPage
from shamela2epub.models.book_info_html_page import BookInfoHTMLPage
from shamela2epub.models.epub_book import EPUBBook


class BookDownloader:
    book_info_page: BookInfoHTMLPage

    def __init__(self, url: str, connections: int) -> None:
        """Book Downloader constructor."""
        self.url = url
        self.valid = is_valid_url(self.url)
        self.epub_book = EPUBBook()
        self._session = get_session(connections)
        self._chunk_size = connections * 2
        self._progress_bar: tqdm | None = None

    def create_info_page(self) -> None:
        # Info Page
        url = get_book_info_page_url(self.url)
        self.book_info_page = BookInfoHTMLPage(url, self._session.get(url, timeout=TIME_OUT).text)
        self.epub_book.init()
        self.epub_book.create_info_page(self.book_info_page)

    def create_first_page(self) -> None:
        url = get_book_first_page_url(self.url)
        book_html_page = BookHTMLPage(url, self._session.get(url, timeout=TIME_OUT).text)
        self.epub_book.set_page_count(book_html_page.last_page)
        self.epub_book.set_parts_map(book_html_page.parts_map)
        self.epub_book.set_toc(book_html_page.toc)
        self.epub_book.add_page(book_html_page)
        if self._progress_bar is not None:
            self._progress_bar.total = self.epub_book.pages_count
            self._progress_bar.update(1)

    def _download(self, progress_callback: Callable[[str | int], None]) -> None:
        self.create_first_page()
        # This loop starts from the second page (since the first page is already downloaded)
        # and goes up to the total number of pages in the book. The step size is equal to the chunk size.
        for i in range(2, self.epub_book.pages_count + 1, self._chunk_size):
            responses = []
            # This inner loop iterates over each page number in the current chunk.
            # The range starts from the current page number `i` and goes up to
            # either the end of the current chunk or the total number of pages, whichever is smaller.
            for page_number in range(i, min(i + self._chunk_size, self.epub_book.pages_count + 1)):
                responses.append(self._session.get(f"{self.url}/{page_number}", timeout=TIME_OUT))
            for response in responses:
                self.epub_book.add_page(BookHTMLPage(response.url, response.text))
                progress_callback(response.url.split("/")[-1])

    def download(self) -> None:
        self._progress_bar = tqdm(
            desc="Downloading", colour="white", unit=" page", dynamic_ncols=True
        )
        self._download(lambda page_number: self._progress_bar.update(1))  # type: ignore[union-attr]

    def save_book(self, output: str) -> Path:
        # Generate TOC
        self.epub_book.generate_toc()
        # Save to disk
        book_name = f"{self.book_info_page.title} - {self.book_info_page.author}.epub"
        if output:
            output_book = output if output.endswith(".epub") else f"{output}/{book_name}"
        else:
            output_book = f"{OUT_DIR}/{book_name}"
        self.epub_book.save_book(output_book)
        if self._progress_bar is not None:
            self._progress_bar.close()
        return Path(output_book)
