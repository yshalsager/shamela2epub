"""shamela2epub main."""
from pathlib import Path

from gevent import Greenlet, joinall, spawn
from gevent.lock import BoundedSemaphore
from gevent.monkey import patch_all
from tqdm import tqdm

from shamela2epub import OUT_DIR
from shamela2epub.misc.utils import (
    get_book_first_page_url,
    get_book_info_page_url,
    is_valid_url,
)
from shamela2epub.models.book_html_page import BookHTMLPage
from shamela2epub.models.book_info_html_page import BookInfoHTMLPage
from shamela2epub.models.epub_book import EPUBBook

patch_all(thread=False)


class BookDownloader:
    book_info_page: BookInfoHTMLPage

    def __init__(self, url: str, connections: int) -> None:
        """Book Downloader constructor."""
        self.url = url
        self.valid = is_valid_url(self.url)
        self.epub_book = EPUBBook()
        self._sem = BoundedSemaphore(connections)
        self._progress_bar: tqdm | None = None

    def create_info_page(self) -> None:
        # Info Page
        self.book_info_page = BookInfoHTMLPage(get_book_info_page_url(self.url))
        self.epub_book.init()
        self.epub_book.create_info_page(self.book_info_page)

    def create_first_page(self) -> None:
        book_html_page = BookHTMLPage(get_book_first_page_url(self.url))
        self.epub_book.set_page_count(book_html_page.last_page)
        self.epub_book.set_parts_map(book_html_page.parts_map)
        self.epub_book.set_toc(book_html_page.toc)
        self.epub_book.add_page(book_html_page)
        if self._progress_bar is not None:
            self._progress_bar.total = self.epub_book.pages_count
            self._progress_bar.update(1)

    def download_page(self, page_number: int) -> BookHTMLPage:
        with self._sem:
            book_html_page = BookHTMLPage(f"{self.url}/{page_number}")
            if self._progress_bar is not None:
                self._progress_bar.update(1)
        return book_html_page

    def download(self) -> None:
        self._progress_bar = tqdm(
            desc="Downloading", colour="white", unit=" page", dynamic_ncols=True
        )
        self.create_first_page()
        jobs = [
            spawn(self.download_page, page_number)
            for page_number in range(2, self.epub_book.pages_count + 1)
        ]
        job: Greenlet
        for job in joinall(jobs):
            self.epub_book.add_page(job.value)

    def save_book(self, output: str) -> Path:
        # Generate TOC
        self.epub_book.generate_toc()
        # Save to disk
        book_name = f"{self.book_info_page.title} - {self.book_info_page.author}.epub"
        if output:
            output_book = (
                output if output.endswith(".epub") else f"{output}/{book_name}"
            )
        else:
            output_book = f"{OUT_DIR}/{book_name}"
        self.epub_book.save_book(output_book)
        if self._progress_bar is not None:
            self._progress_bar.close()
        return Path(output_book)
