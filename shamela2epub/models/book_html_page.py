from typing import Any, Dict, List

from bs4 import Tag

from shamela2epub.misc.constants import BOOK_RESOURCE
from shamela2epub.misc.patterns import BOOK_URL_PATTERN
from shamela2epub.models.book_base_html_page import BookBaseHTMLPage


class BookHTMLPage(BookBaseHTMLPage):
    BOOK_TOC_SELECTOR = "div.s-nav-head + ul"
    COPY_BTN_SELECTOR = "a.btn_tag"
    PAGE_NUMBER_SELECTOR = "input#fld_goto_bottom"
    PAGE_PARTS_SELECTOR = "#fld_part_top ~ div"
    PAGE_PARTS_MENU_SELECTOR = f"{PAGE_PARTS_SELECTOR} ul[role='menu']"
    PAGE_PART_SELECTOR = f"{PAGE_PARTS_SELECTOR} button"
    NEXT_PAGE_SELECTOR = f"{PAGE_NUMBER_SELECTOR} + a"
    LAST_PAGE_SELECTOR = f"{PAGE_NUMBER_SELECTOR} + a + a"
    CHAPTERS_SELECTOR = f"div.s-nav-head ~ ul a[href*='/{BOOK_RESOURCE}/']"

    def __init__(self, url: str):
        """Book HTML page model constructor."""
        super().__init__(url)
        self._remove_copy_btn_from_html()
        self.page_url = self.url.split("#")[0]
        self._chapters_by_page: Dict[str, str] = {}
        self._toc_chapters_levels: Dict[str, int] = {}
        self.content = self.get_clean_page_content()

    def _remove_copy_btn_from_html(self) -> None:
        for btn in self._html.select(self.COPY_BTN_SELECTOR):
            btn.decompose()

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

    def parse_toc(self, toc: Tag) -> List:
        toc_list: List = []
        item: Tag
        for item in toc.children:
            link = item.select_one("a")
            ul_list = item.select_one("ul")
            if ul_list:
                toc_list.append([link.text, self.parse_toc(ul_list)])
            else:
                toc_list.append(link.text)
        return toc_list

    @property
    def toc(self) -> List[Any]:
        toc_ul: Tag = self._html.select_one(self.BOOK_TOC_SELECTOR)
        for item in toc_ul.select('a[href="javascript:;"]'):
            item.decompose()
        return self.parse_toc(toc_ul)

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

    @property
    def parts_map(self) -> Dict[str, int]:
        parts: Tag = self._html.select_one(self.PAGE_PARTS_MENU_SELECTOR)
        return (
            {part.text: index for index, part in enumerate(parts.select("li a")[1:])}
            if parts
            else {}
        )

    def get_clean_page_content(self) -> Tag:
        """Get cleaned-up page content."""
        content = self.content
        # Delete parent div class
        del content["class"]
        # Delete all elements classes
        for element in filter(
            lambda x: isinstance(x, Tag) and x.get("class", None),
            content.recursiveChildGenerator(),
        ):
            if element["class"] != "text-center":
                del element["class"]
        # Delete empty spans
        for element in content.select("span"):
            if not element.text:
                element.decompose()
        # Delete paragraph style
        for element in content.select('p[style="font-size: 15px"]'):
            del element["style"]
        return content
