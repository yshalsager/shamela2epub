from typing import Any, Dict, List

from bs4 import BeautifulSoup, Tag

from shamela2epub.misc.constants import BOOK_RESOURCE
from shamela2epub.misc.patterns import (
    ARABIC_NUMBER_BETWEEN_BRACKETS_PATTERN,
    ARABIC_NUMBER_BETWEEN_CURLY_BRACES_PATTERN,
    BOOK_URL_PATTERN,
    HAMESH_CONTINUATION_PATTERN,
    HAMESH_PATTERN,
)
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
    _previous_page_hamesh = ""

    def __init__(self, url: str):
        """Book HTML page model constructor."""
        super().__init__(url)
        self._remove_copy_btn_from_html()
        self.page_url = self.url.split("#")[0]
        self._chapters_by_page: Dict[str, str] = {}
        self._toc_chapters_levels: Dict[str, int] = {}
        self.content = self.get_clean_page_content()
        self.hamesh_items: Dict[str, Tag] = self.get_hamesh_items()
        self._update_hamesh()

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
            if not any([c for c in element["class"] if c in ["text-center", "hamesh"]]):
                del element["class"]
        # Delete empty spans
        for element in content.select("span"):
            if not element.text:
                element.decompose()
        # Delete paragraph style
        for element in content.select('p[style="font-size: 15px"]'):
            del element["style"]
        return content

    def get_hamesh_items(self) -> Dict[str, Tag]:
        hamesh_items: Dict[str, Tag] = {}
        hamesh = self.content.select_one(".hamesh")
        if not hamesh:
            return hamesh_items
        hamesh_counter = 0
        current_hamesh = ""
        hamesh_continuation = HAMESH_CONTINUATION_PATTERN.search(str(hamesh))
        if hamesh_continuation:
            type(self)._previous_page_hamesh = (
                hamesh_continuation.group("continuation")
                if not type(self)._previous_page_hamesh
                else f"{type(self)._previous_page_hamesh}\n{hamesh_continuation.group('continuation')}"
            )
        else:
            if not type(self)._previous_page_hamesh:
                type(self)._previous_page_hamesh = ""
        for match in HAMESH_PATTERN.finditer(str(hamesh)):
            hamesh_counter += 1
            current_hamesh = match.group("number").strip()
            hamesh_line = match.group("content").strip()
            #  <aside id="fn1" epub:type="footnote">
            #  <p><a href="#fnref1" title="footnote 1">[1]</a> Text in popup</p>
            #  </aside>
            new_footnote = Tag(
                builder=hamesh.builder,
                name="aside",
                attrs={"id": f"fn{hamesh_counter}", "epub:type": "footnote"},
            )
            new_footnote_p = Tag(builder=hamesh.builder, name="p")
            new_footnote_a = Tag(
                builder=hamesh.builder,
                name="a",
                attrs={
                    "href": f"#fnref{hamesh_counter}",
                    # "title": f"هامش {hamesh_counter}",
                    "class": "nu",
                },
            )
            new_footnote_a.string = current_hamesh
            new_footnote.append(new_footnote_p)
            if type(self)._previous_page_hamesh:
                new_footnote_p.append(
                    BeautifulSoup(
                        type(self)._previous_page_hamesh.replace("\n", "<br>"),
                        "html.parser",
                    )
                )
                new_footnote_p.append(Tag(name="br"))
                new_footnote_p.append(new_footnote_a)
                new_footnote_p.append(" ")
                new_footnote_p.append(BeautifulSoup(hamesh_line.strip(), "html.parser"))
                type(self)._previous_page_hamesh = ""
            else:
                new_footnote_p.append(new_footnote_a)
                new_footnote_p.append(" ")
                new_footnote_p.append(BeautifulSoup(hamesh_line.strip(), "html.parser"))
            hamesh_items.update({current_hamesh: new_footnote})
        return hamesh_items

    def _update_hamesh(self) -> None:
        footnote_count = 1
        hamesh = self.content.select_one(".hamesh")
        if not hamesh:
            return
        new_hamesh = Tag(builder=hamesh.builder, name="div", attrs={"class": "hamesh"})
        parent = self.content.select_one("div")
        p_elements = self.content.select("p:not(.hamesh)")
        for p in p_elements:
            matches = ARABIC_NUMBER_BETWEEN_BRACKETS_PATTERN.finditer(str(p))
            for match in matches:
                number = match.group("number")
                if not self.hamesh_items.get(number, ""):
                    continue
                aya_match = ARABIC_NUMBER_BETWEEN_CURLY_BRACES_PATTERN.search(str(p))
                if (
                    aya_match
                    and number in aya_match.group()
                    # number in inside aya
                    and match.start("number") > aya_match.start()
                ):
                    continue
                footnote_link: Tag = Tag(
                    builder=p.builder,
                    name="a",
                    attrs={
                        "href": f"#fn{footnote_count}",
                        "epub:type": "noteref",
                        "role": "doc-noteref",
                        "id": f"fnref{footnote_count}",
                        # "title": f"هامش {footnote_count}",
                        "class": "fn nu",
                    },
                )
                footnote_link.string = number
                # new_p_content = (
                #     str(p)[len("<p>") : match.start()]
                #     + str(footnote_link)
                #     + str(p)[match.start() + len(match.group()) : 0 - len("</p>")]
                # )
                # TODO: Find a better way to replace number with its a element,
                #  since replacing only the first occurrence might not be the best soluion
                new_p_content = str(p).replace(number, str(footnote_link), 1)
                new_p = Tag(builder=p.builder, name="p", parent=parent)
                new_p.append(BeautifulSoup(new_p_content, "html.parser"))
                p.replace_with(new_p)
                p = new_p
                footnote_count += 1
                new_hamesh.append(self.hamesh_items[number])
        hamesh.replace_with(new_hamesh)

    def __repr__(self) -> str:
        return f"<BookHTMLPage(url={self.url})>"
