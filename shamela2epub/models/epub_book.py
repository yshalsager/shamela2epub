import re
from typing import Dict, List

from bs4 import Tag
from ebooklib.epub import (
    EpubBook,
    EpubHtml,
    EpubItem,
    EpubNav,
    EpubNcx,
    Link,
    write_epub,
)

from shamela2epub import __version__
from shamela2epub.misc.constants import SHAMELA_DOMAIN
from shamela2epub.misc.patterns import CSS_STYLE_COLOR_PATTERN
from shamela2epub.misc.utils import get_stylesheet
from shamela2epub.models.book_html_page import BookHTMLPage
from shamela2epub.models.book_info_html_page import BookInfoHTMLPage


class EPUBBook:
    def __init__(self) -> None:
        self.pages_count: str = ""
        self._zfill_length = 0
        self.book: EpubBook = EpubBook()
        self.pages: List[EpubHtml] = []
        self.sections: List[Link] = []
        self.sections_map: Dict[str, Link] = {}
        self.parts_map: Dict[str, int] = {}
        self.default_css: EpubItem = EpubItem()
        self._color_styles_map: Dict[str, int] = {}
        self._last_color_id: int = 0

    def set_page_count(self, count: str) -> None:
        self.pages_count = count
        self._zfill_length = len(count) + 1

    def set_parts_map(self, parts_map: Dict[str, int]) -> None:
        self.parts_map = parts_map

    def init(self) -> None:
        self.book.set_language("ar")
        self.book.set_direction("rtl")
        self.book.add_metadata("DC", "publisher", f"https://{SHAMELA_DOMAIN}")
        self.book.add_metadata(
            None, "meta", "", {"name": "shamela2epub", "content": __version__}
        )
        self.default_css = EpubItem(
            uid="style_default",
            file_name="style/styles.css",
            media_type="text/css",
            content=get_stylesheet(),
        )
        self.book.add_item(self.default_css)

    def create_info_page(self, book_info_html_page: BookInfoHTMLPage) -> None:
        self.book.set_title(book_info_html_page.title)
        self.book.add_author(book_info_html_page.author)
        self.book.add_metadata("DC", "source", book_info_html_page.url)
        info_page = EpubHtml(
            title="بطاقة الكتاب",
            file_name="info.xhtml",
            lang="ar",
            content=f"<html><body>{book_info_html_page.content}</body></html>",
        )
        info_page.add_item(self.default_css)
        self.book.add_item(info_page)
        self.pages.append(info_page)

    def add_chapter(
        self, chapters_in_page: Dict, new_page: EpubHtml, page_filename: str
    ) -> None:
        for i in chapters_in_page:
            link = Link(
                page_filename,
                i,
                page_filename.replace(".xhtml", ""),
            )
            self.sections.append(link)
            self.sections_map.update({i: link})

    def replace_color_styles_with_class(self, html: Tag) -> str:
        html_str = str(html)
        matches = CSS_STYLE_COLOR_PATTERN.findall(html_str)
        if not matches:
            return html_str
        for style in list(set(CSS_STYLE_COLOR_PATTERN.findall(html_str))):
            color_class = self._color_styles_map.get(style, "")
            if not color_class:
                color_class = f"color-{self._last_color_id + 1}"
                self._color_styles_map.update({style: color_class})
                self._last_color_id += 1
                self.default_css.content += f"\n.{color_class} {{ {style}; }}\n\n"
            html_str = re.sub(f'style="{style}"', f'class="{color_class}"', html_str)
        return html_str

    def add_page(
        self, book_html_page: BookHTMLPage, file_name: str = "", title: str = ""
    ) -> EpubHtml:
        chapters_in_page = book_html_page.chapters_by_page.get(book_html_page.page_url)
        if chapters_in_page:
            title = chapters_in_page[0]
        part = book_html_page.part
        page_filename = (
            f"page{'_' if part else ''}{self.parts_map[part] if self.parts_map else ''}_"
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
            content=f"<html><body>{self.replace_color_styles_with_class(book_html_page.content)}<hr>"
            f'<div class="text-center">{footer}</div>'
            f"</body></html>",
        )
        new_page.add_item(self.default_css)
        self.book.add_item(new_page)
        self.pages.append(new_page)
        if chapters_in_page:
            self.add_chapter(chapters_in_page, new_page, page_filename)
        return new_page

    def _update_toc_list(self, toc: List) -> None:
        # Bug: Books that have a last nested section with level deeper than its next with the same page number
        # cannot be converted to KFX unless that last nested section is removed.
        for index, element in enumerate(toc):
            if isinstance(element, list):
                self._update_toc_list(element)
            else:
                toc[index] = self.sections_map.get(element, None)

    def generate_toc(self, toc_list: List) -> None:
        self._update_toc_list(toc_list)
        toc_list.insert(0, Link("nav.xhtml", "فهرس الموضوعات", "nav"))
        toc_list.insert(0, Link("info.xhtml", "بطاقة الكتاب", "info"))
        self.book.toc = toc_list
        self.book.add_item(EpubNcx())
        nav = EpubNav()
        nav.add_item(self.default_css)
        self.book.add_item(nav)
        self.book.spine = [self.pages[0], "nav", *self.pages[1:]]  # [info, nav, rest]

    def save_book(self, book_name: str) -> None:
        write_epub(book_name, self.book)
