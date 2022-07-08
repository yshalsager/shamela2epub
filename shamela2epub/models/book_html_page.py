from typing import Any, Dict, List, Optional, Union

from bs4 import BeautifulSoup, Tag
from bs4.element import PageElement
from httpx import get

from shamela2epub.misc.constants import BOOK_URL
from shamela2epub.misc.patterns import BOOK_URL_PATTERN


class BookHTMLPage:
    BOOK_TITLE_SELECTOR = "h1 a"
    BOOK_AUTHOR_SELECTOR = "h1 + div a"
    BOOK_PAGE_CONTENT_SELECTOR = "div.nass"
    BOOK_TOC_SELECTOR = "div.s-nav-head + ul"
    COPY_BTN_SELECTOR = "a.btn_tag"
    PAGE_NUMBER_SELECTOR = "input#fld_goto_bottom"
    PAGE_PART_SELECTOR = "#fld_part_top ~ div button"
    NEXT_PAGE_SELECTOR = f"{PAGE_NUMBER_SELECTOR} + a"
    LAST_PAGE_SELECTOR = f"{PAGE_NUMBER_SELECTOR} + a + a"
    CHAPTER_TITLE_SELECTOR = "div.size-12 span.text-black"
    CHAPTERS_SELECTOR = f"div.s-nav-head ~ ul a[href*='/{BOOK_URL}/']"

    def __init__(self, url: str):
        self._url = url
        self._html: BeautifulSoup = BeautifulSoup(get(url).content, "html.parser")
        self._remove_copy_btn_from_html()
        self.page_url = self._url.split("#")[0]
        self._chapters_by_page: Dict[str, str] = {}
        self._toc_chapters_levels: Dict[str, int] = {}

    def _remove_copy_btn_from_html(self) -> None:
        for btn in self._html.select(self.COPY_BTN_SELECTOR):
            btn.decompose()

    @property
    def title(self) -> Any:
        return self._html.select_one(self.BOOK_TITLE_SELECTOR).text.strip()

    @property
    def author(self) -> Any:
        return self._html.select_one(self.BOOK_AUTHOR_SELECTOR).text.strip()

    @property
    def current_page(self) -> Any:
        return self._html.select_one(self.PAGE_NUMBER_SELECTOR).get("value")

    @property
    def has_next_page(self) -> bool:
        return bool(self._html.select_one(self.NEXT_PAGE_SELECTOR))

    @staticmethod
    def _get_page_number(page_anchor: Tag) -> str:
        match = BOOK_URL_PATTERN.search(page_anchor.get("href"))
        assert match is not None
        return match.groupdict()["page"]

    @property
    def next_page(self) -> str:
        next_page_element = self._html.select_one(self.NEXT_PAGE_SELECTOR)
        if not next_page_element:
            return ""
        return self._get_page_number(next_page_element)

    @property
    def next_page_url(self) -> Any:
        next_page_element = self._html.select_one(self.NEXT_PAGE_SELECTOR)
        if not next_page_element:
            return ""
        return next_page_element.get("href")

    @property
    def last_page(self) -> str:
        last_page_element = self._html.select_one(self.LAST_PAGE_SELECTOR)
        if not last_page_element:
            return ""
        return self._get_page_number(last_page_element)

    @property
    def content(self) -> Tag:
        return self._html.select_one(self.BOOK_PAGE_CONTENT_SELECTOR)

    def parse_toc_levels(self, toc: Tag, current_level: int = 1) -> Dict[str, int]:
        toc_levels: Dict = {}
        item: Tag
        for item in toc.children:
            toc_levels.update(
                {item.select_one(self.CHAPTERS_SELECTOR).text: current_level}
            )
            ul_list = item.find("ul")
            if ul_list:
                toc_levels.update(self.parse_toc_levels(ul_list, current_level + 1))
        return toc_levels

    @property
    def toc_chapters_levels(self) -> Dict[str, int]:
        if self._toc_chapters_levels:
            return self._toc_chapters_levels
        self._toc_chapters_levels = self.parse_toc_levels(
            self._html.select_one(self.BOOK_TOC_SELECTOR)
        )
        return self._toc_chapters_levels

    @property
    def chapters_by_page(self) -> Any:
        if self._chapters_by_page:
            return self.chapters_by_page
        chapters_list = self._html.select(self.CHAPTERS_SELECTOR)
        chapters: Dict = {}
        for chapter in chapters_list:
            chapter_url = chapter.get("href")
            if chapters.get(chapter_url):
                chapters[chapter_url].append(chapter.text)
                chapters.update({chapter_url: chapters[chapter_url]})
            else:
                chapters.update({chapter_url: [chapter.text]})
        self._chapters_by_page = chapters
        return self._chapters_by_page

    @property
    def part(self) -> Any:
        part_element: Tag = self._html.select_one(self.PAGE_PART_SELECTOR)
        return part_element.text.strip() if part_element else ""
