from typing import Dict, List, Optional, Union

from ebooklib.epub import EpubBook, EpubHtml, EpubNav, EpubNcx, write_epub

from shamela2epub.misc.constants import SHAMELA_DOMAIN
from shamela2epub.models.book_html_page import BookHTMLPage


class EPUBBook:
    def __init__(self, pages_count: str, toc: List[Dict]) -> None:
        self.pages_count = int(pages_count)
        self._zfill_length = len(pages_count) + 1
        self.book: EpubBook = EpubBook()
        self.pages: List[EpubHtml] = []
        self.toc: List[Dict] = toc
        self.sections: List[EpubHtml] = []

    def get_chapter(self, url: str, toc: List[Dict] = []) -> Optional[Dict[str, str]]:
        if not toc:
            toc = self.toc
        for item in toc:
            if isinstance(item, list):
                chapter = self.get_chapter(url, toc=item)
                if chapter:
                    return chapter
            else:
                if int(url.split("/")[-1]) < int(item["url"].split("/")[-1]):
                    return {}
                if url == item["url"]:
                    return item
        return {}

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

    def add_page(
        self, book_html_page: BookHTMLPage, file_name: str = "", title: str = ""
    ) -> EpubHtml:
        chapter = self.get_chapter(book_html_page.page_url)
        if chapter:
            title = chapter["title"]
        new_page = EpubHtml(
            title=title,
            # title=book_html_page.chapter_title,
            file_name=file_name
            or f"page_{book_html_page.current_page.zfill(self._zfill_length)}.xhtml",
            lang="ar",
            direction="rtl",
            content=f"<html><body>{book_html_page.content}</body></html>",
        )
        self.book.add_item(new_page)
        self.pages.append(new_page)
        if chapter:
            self.sections.append(new_page)
        return new_page

    def save_book(self, book_name: str) -> None:
        self.book.toc = self.sections
        self.book.spine = ["nav", *self.pages]
        self.book.add_item(EpubNcx())
        self.book.add_item(EpubNav(direction="rtl"))
        write_epub(book_name, self.book)
