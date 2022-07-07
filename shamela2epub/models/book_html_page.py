from typing import Any, Optional

from bs4 import BeautifulSoup, Tag
from httpx import get

from shamela2epub.misc.patterns import BOOK_URL_PATTERN


class BookHTMLPage:
    BOOK_TITLE_SELECTOR = "h1 a"
    BOOK_AUTHOR_SELECTOR = "h1 + div a"
    BOOK_PAGE_CONTENT_SELECTOR = "div.nass"
    BOOK_TOC_SELECTOR = "div.s-nav-head + ul"
    COPY_BTN_SELECTOR = "a.btn_tag"
    PAGE_NUMBER_SELECTOR = "input#fld_goto_bottom"
    NEXT_PAGE_SELECTOR = f"{PAGE_NUMBER_SELECTOR} + a"
    LAST_PAGE_SELECTOR = f"{PAGE_NUMBER_SELECTOR} + a + a"
    CHAPTER_TITLE_SELECTOR = "div.size-12 span.text-black"

    def __init__(self, url: str):
        self._html: BeautifulSoup = BeautifulSoup(get(url).content, "html.parser")
        self._remove_copy_btn_from_html()

    def _remove_copy_btn_from_html(self) -> None:
        copy_buttons = self._html.select(self.COPY_BTN_SELECTOR)
        for btn in copy_buttons:
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

    @property
    def toc(self) -> Tag:
        return self._html.select_one(self.BOOK_TOC_SELECTOR)

    @property
    def chapter_title(self) -> Any:
        chapter_hierarchy = self._html.select(self.CHAPTER_TITLE_SELECTOR)
        return chapter_hierarchy[-1].text or chapter_hierarchy[0].text
