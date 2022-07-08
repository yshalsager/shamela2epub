from typing import Dict, List

from ebooklib.epub import EpubBook, EpubHtml, EpubNav, EpubNcx, Link, write_epub

from shamela2epub.misc.constants import SHAMELA_DOMAIN
from shamela2epub.models.book_html_page import BookHTMLPage


class EPUBBook:
    def __init__(self, pages_count: str) -> None:
        self.pages_count = int(pages_count)
        self._zfill_length = len(pages_count) + 1
        self.book: EpubBook = EpubBook()
        self.pages: List[EpubHtml] = []
        self.sections: List[EpubHtml] = []

    def create_first_page(self, book_html_page: BookHTMLPage) -> None:
        self.book.set_language("ar")
        self.book.set_direction("rtl")
        self.book.set_title(book_html_page.title)
        self.book.add_author(book_html_page.author)
        self.book.add_metadata("DC", "publisher", f"https://{SHAMELA_DOMAIN}")
        new_page = self.add_page(
            book_html_page, file_name="info.xhtml", title="بطاقة الكتاب"
        )
        self.sections.append(new_page)

    def add_chapter(
        self, chapters_in_page: Dict, new_page: EpubHtml, default_page_filename: str
    ) -> None:
        # TODO: Handle nested chapters properly.
        if len(chapters_in_page) == 1:
            self.sections.append(new_page)
        else:
            self.sections += [
                Link(
                    default_page_filename,
                    i,
                    default_page_filename.replace(".xhtml", ""),
                )
                for i in chapters_in_page
            ]

    def add_page(
        self, book_html_page: BookHTMLPage, file_name: str = "", title: str = ""
    ) -> EpubHtml:
        chapters_in_page = book_html_page.chapters_by_page.get(book_html_page.page_url)
        if chapters_in_page:
            title = chapters_in_page[0]
        default_page_filename = (
            f"page_{book_html_page.current_page.zfill(self._zfill_length)}.xhtml"
        )
        new_page = EpubHtml(
            title=title,
            file_name=file_name or default_page_filename,
            lang="ar",
            direction="rtl",
            content=f"<html><body>{book_html_page.content}</body></html>",
        )
        self.book.add_item(new_page)
        self.pages.append(new_page)
        if chapters_in_page:
            self.add_chapter(chapters_in_page, new_page, default_page_filename)
        return new_page

    def save_book(self, book_name: str) -> None:
        self.book.toc = self.sections
        self.book.spine = ["nav", *self.pages]
        self.book.add_item(EpubNcx())
        self.book.add_item(EpubNav(direction="rtl"))
        write_epub(book_name, self.book)
