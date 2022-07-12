"""
shamela2epub main
"""
from pathlib import Path
from typing import Iterator

from shamela2epub import OUT_DIR
from shamela2epub.misc.utils import (
    get_book_first_page_url,
    get_book_info_page_url,
    is_valid_url,
)
from shamela2epub.models.book_html_page import BookHTMLPage
from shamela2epub.models.book_info_html_page import BookInfoHTMLPage
from shamela2epub.models.epub_book import EPUBBook


class BookDownloader:
    book_info_page: BookInfoHTMLPage
    book_html_page: BookHTMLPage

    def __init__(self, url: str) -> None:
        self.url = url
        self.valid = is_valid_url(self.url)
        self.epub_book = EPUBBook()

    def create_info_page(self) -> None:
        # Info Page
        self.book_info_page = BookInfoHTMLPage(get_book_info_page_url(self.url))
        self.epub_book.init()
        self.epub_book.create_info_page(self.book_info_page)

    def create_first_page(self) -> str:
        # First Page
        first_page_url = get_book_first_page_url(self.url)
        self.book_html_page = BookHTMLPage(first_page_url)
        self.epub_book.set_page_count(self.book_html_page.last_page)
        self.epub_book.set_parts_map(self.book_html_page.parts_map)
        self.epub_book.add_page(self.book_html_page)
        return first_page_url

    def download(self) -> Iterator[str]:
        has_next = self.book_html_page.has_next_page
        next_page_url = self.book_html_page.next_page_url
        while has_next:
            yield next_page_url
            self.book_html_page = BookHTMLPage(next_page_url)
            self.epub_book.add_page(self.book_html_page)
            if not self.book_html_page.has_next_page:
                has_next = False
            next_page_url = self.book_html_page.next_page_url

    def save_book(self, output: str) -> Path:
        # Generate TOC
        self.epub_book.generate_toc(self.book_html_page.toc)
        # Save to disk
        book_name = f"{self.book_info_page.title} - {self.book_info_page.author}.epub"
        if output:
            output_book = (
                output if output.endswith(".epub") else f"{output}/{book_name}"
            )
        else:
            output_book = f"{OUT_DIR}/{book_name}"
        self.epub_book.save_book(output_book)
        return Path(output_book)
