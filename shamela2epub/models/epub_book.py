import re
from typing import Dict, List, Optional

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
        """EPUB Book model."""
        self._pages_count: str = ""
        self._zfill_length = 0
        self._book: EpubBook = EpubBook()
        self._pages: List[EpubHtml] = []
        self._sections: List[Link] = []
        self._sections_map: Dict[str, Link] = {}
        self._parts_map: Dict[str, int] = {}
        self._default_css: EpubItem = EpubItem()
        self._color_styles_map: Dict[str, int] = {}
        self._last_color_id: int = 0
        self._pages_map: Dict[int, int] = {}

    def set_page_count(self, count: str) -> None:
        self._pages_count = count
        self._zfill_length = len(count) + 1

    def set_parts_map(self, parts_map: Dict[str, int]) -> None:
        self._parts_map = parts_map

    def init(self) -> None:
        self._book.set_language("ar")
        self._book.set_direction("rtl")
        self._book.add_metadata("DC", "publisher", f"https://{SHAMELA_DOMAIN}")
        self._book.add_metadata(
            None, "meta", "", {"name": "shamela2epub", "content": __version__}
        )
        self._default_css = EpubItem(
            uid="style_default",
            file_name="style/styles.css",
            media_type="text/css",
            content=get_stylesheet(),
        )
        self._book.add_item(self._default_css)

    def create_info_page(self, book_info_html_page: BookInfoHTMLPage) -> None:
        self._book.set_title(book_info_html_page.title)
        self._book.add_author(book_info_html_page.author)
        self._book.add_metadata("DC", "source", book_info_html_page.url)
        info_page = EpubHtml(
            title="بطاقة الكتاب",
            file_name="info.xhtml",
            lang="ar",
            content=f"<html><body>{book_info_html_page.content}</body></html>",
        )
        info_page.add_item(self._default_css)
        self._book.add_item(info_page)
        self._pages.append(info_page)

    def add_chapter(
        self, chapters_in_page: Dict, new_page: EpubHtml, page_filename: str
    ) -> None:
        for i in chapters_in_page:
            link = Link(
                page_filename,
                i,
                page_filename.replace(".xhtml", ""),
            )
            self._sections.append(link)
            self._sections_map.update({i: link})

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
                self._default_css.content += f"\n.{color_class} {{ {style}; }}\n\n"
            html_str = re.sub(f'style="{style}"', f'class="{color_class}"', html_str)
        return html_str

    def get_book_page_number(self, book_html_page: BookHTMLPage) -> str:
        """
        Get the correct page number, which will be in page file name
        """
        html_page_number: int = int(book_html_page.current_page)
        book_page_count: Optional[int] = self._pages_map.get(html_page_number)
        current_page = None
        if book_page_count:
            new_page_count = book_page_count + 1
            current_page = new_page_count
            self._pages_map[html_page_number] = new_page_count
            return f"{str(html_page_number).zfill(self._zfill_length)}_{current_page}"
        current_page = html_page_number
        self._pages_map[html_page_number] = 1
        return str(current_page).zfill(self._zfill_length)

    def add_page(
        self, book_html_page: BookHTMLPage, file_name: str = "", title: str = ""
    ) -> EpubHtml:
        chapters_in_page = book_html_page.chapters_by_page.get(book_html_page.page_url)
        if chapters_in_page:
            title = chapters_in_page[0]
        part = book_html_page.part
        page_filename = (
            f"page{'_' if part else ''}{self._parts_map[part] if self._parts_map else ''}_"
            f"{self.get_book_page_number(book_html_page)}.xhtml"
        )
        footer = ""
        if part:
            footer += f"الجزء: {book_html_page.part} - "
        footer += f"الصفحة: {book_html_page.current_page}"
        new_page = EpubHtml(
            title=title,
            file_name=file_name or page_filename,
            lang="ar",
            content=f"<html><body>{self.replace_color_styles_with_class(book_html_page.content)}"
            f'<div class="text-center">{footer}</div>'
            f"</body></html>",
        )
        new_page.add_item(self._default_css)
        self._book.add_item(new_page)
        self._pages.append(new_page)
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
                toc[index] = self._sections_map.get(element, None)

    def generate_toc(self, toc_list: List) -> None:
        self._update_toc_list(toc_list)
        toc_list.insert(0, Link("nav.xhtml", "فهرس الموضوعات", "nav"))
        toc_list.insert(0, Link("info.xhtml", "بطاقة الكتاب", "info"))
        self._book.toc = toc_list
        self._book.add_item(EpubNcx())
        nav = EpubNav()
        nav.add_item(self._default_css)
        self._book.add_item(nav)
        self._book.spine = [
            self._pages[0],
            "nav",
            *self._pages[1:],
        ]  # [info, nav, rest]

    def save_book(self, book_name: str) -> None:
        write_epub(book_name, self._book)
