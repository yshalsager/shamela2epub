from typing import Dict, List, Set

from ebooklib.epub import EpubBook, EpubHtml, EpubNav, EpubNcx, Link, write_epub

from shamela2epub.misc.constants import SHAMELA_DOMAIN
from shamela2epub.models.book_html_page import BookHTMLPage


class EPUBBook:
    def __init__(self, pages_count: str) -> None:
        self.pages_count = int(pages_count)
        self._zfill_length = len(pages_count) + 1
        self.book: EpubBook = EpubBook()
        self.pages: List[EpubHtml] = []
        self.sections: List[Link] = []

    def create_first_page(self, book_html_page: BookHTMLPage) -> None:
        self.book.set_language("ar")
        self.book.set_direction("rtl")
        self.book.set_title(book_html_page.title)
        self.book.add_author(book_html_page.author)
        self.book.add_metadata("DC", "publisher", f"https://{SHAMELA_DOMAIN}")
        new_page = self.add_page(
            book_html_page, file_name="info.xhtml", title="بطاقة الكتاب"
        )
        self.sections.insert(0, Link("info.xhtml", "بطاقة الكتاب", "info"))

    def add_chapter(
        self, chapters_in_page: Dict, new_page: EpubHtml, page_filename: str
    ) -> None:
        self.sections.extend(
            [
                Link(
                    page_filename,
                    i,
                    page_filename.replace(".xhtml", ""),
                )
                for i in chapters_in_page
            ]
        )

    def add_page(
        self, book_html_page: BookHTMLPage, file_name: str = "", title: str = ""
    ) -> EpubHtml:
        chapters_in_page = book_html_page.chapters_by_page.get(book_html_page.page_url)
        if chapters_in_page:
            title = chapters_in_page[0]
        part = book_html_page.part
        page_filename = (
            f"page{'_' if part else ''}{part}_"
            f"{book_html_page.current_page.zfill(self._zfill_length)}.xhtml"
        )
        footer = ""
        if part:
            footer += f"الجزء: {book_html_page.part} - "
        footer += f"الصفحة: {book_html_page.current_page}"
        new_page = EpubHtml(
            title=title,
            file_name=file_name or page_filename,
            lang="ar",
            direction="rtl",
            content=f"<html><body>{book_html_page.content}<hr>"
            f"<div style='text-align: center;'>{footer}</div>"
            f"</body></html>",
        )
        self.book.add_item(new_page)
        self.pages.append(new_page)
        if chapters_in_page:
            self.add_chapter(chapters_in_page, new_page, page_filename)
        return new_page

    def order_chapters(self, toc_chapters_levels: Dict[str, int]) -> None:
        chapters = []
        for idx, item in enumerate(self.sections[:2]):
            if idx == 0:
                chapters.append(self.sections.pop(idx))
            else:
                chapters.append(item)
        for previous_section, section in zip(self.sections, self.sections[1:]):
            previous_level = toc_chapters_levels.get(previous_section.title, 1)
            level = toc_chapters_levels.get(section.title, 1)
            if level > previous_level:
                if isinstance(chapters[-1], list):
                    nested = chapters[-1]
                    while isinstance(nested[-1], list):
                        nested = nested[-1]
                    last = nested.pop()
                    chapters.append([last, [section]])
                else:
                    if chapters[-1].title == previous_section.title:
                        chapters.pop()
                    chapters.append([previous_section, [section]])
            else:
                if level == previous_level and isinstance(chapters[-1], list):
                    nested = chapters[-1]
                    while isinstance(nested[-1], list):
                        nested = nested[-1]
                    nested.append(section)
                else:
                    chapters.append(section)
        self.sections = chapters

    def save_book(self, book_name: str) -> None:
        self.book.toc = self.sections
        self.book.spine = ["nav", *self.pages]
        self.book.add_item(EpubNcx())
        self.book.add_item(EpubNav(direction="rtl"))
        write_epub(book_name, self.book)
