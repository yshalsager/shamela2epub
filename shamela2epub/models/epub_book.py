from typing import List

from ebooklib.epub import EpubBook, EpubHtml, EpubNav, EpubNcx, write_epub

from shamela2epub.misc.constants import SHAMELA_DOMAIN
from shamela2epub.models.book_html_page import BookHTMLPage


class EPUBBook:
    def __init__(self, pages_count: str) -> None:
        self.pages_count = int(pages_count)
        self._zfill_length = len(pages_count) + 1
        self.book: EpubBook = EpubBook()
        self.book.set_language("ar")
        self.book.set_direction("rtl")
        self.pages: List[EpubHtml] = []

    def create_first_page(self, book_html_page: BookHTMLPage) -> None:
        self.book.set_title(book_html_page.title)
        self.book.add_author(book_html_page.author)
        self.book.add_metadata("DC", "publisher", f"https://{SHAMELA_DOMAIN}")
        self.add_page(book_html_page, file_name="info.xhtml")

    def add_page(self, book_html_page: BookHTMLPage, file_name: str = "") -> None:
        new_page = EpubHtml(
            # title=book_html_page.chapter_title,
            file_name=file_name
            or f"page_{book_html_page.current_page.zfill(self._zfill_length)}.xhtml",
            lang="ar",
            direction="rtl",
            content=f"<html><body>{book_html_page.content}</body></html>",
        )
        self.book.add_item(new_page)
        self.pages.append(new_page)

    def save_book(self, book_name: str) -> None:
        self.book.toc = self.pages
        self.book.spine = ["nav", *self.pages]
        # self.book.add_item(EpubNcx())
        # self.book.add_item(EpubNav())
        write_epub(book_name, self.book)
