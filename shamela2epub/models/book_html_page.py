from re import Match
from typing import Any, cast

from lxml.etree import Element, QName, XMLParser, tostring
from parsel import Selector, SelectorList

from shamela2epub.misc.constants import BOOK_RESOURCE
from shamela2epub.misc.patterns import (
    ARABIC_NUMBER_BETWEEN_BRACKETS_PATTERN,
    ARABIC_NUMBER_BETWEEN_CURLY_BRACES_PATTERN,
    BOOK_URL_PATTERN,
    HAMESH_CONTINUATION_PATTERN,
    HAMESH_PATTERN,
    HTML_STYLE_PATTERN,
    PARENT_DIV_CLASS_PATTERN,
)
from shamela2epub.models.book_base_html_page import BookBaseHTMLPage

xml_parser = XMLParser(resolve_entities=False)
epub_type = QName("http://www.idpf.org/2007/ops", "type")


class BookHTMLPage(BookBaseHTMLPage):
    BOOK_TOC_SELECTOR = "div.s-nav-head + ul > li"
    COPY_BTN_SELECTOR = "a.btn_tag"
    PAGE_NUMBER_SELECTOR = "input#fld_goto_bottom"
    PAGE_PARTS_SELECTOR = "#fld_part_top ~ div"
    PAGE_PARTS_MENU_SELECTOR = f"{PAGE_PARTS_SELECTOR} ul[role='menu']"
    PAGE_PART_SELECTOR = f"{PAGE_PARTS_SELECTOR} button::text"
    NEXT_PAGE_SELECTOR = f"{PAGE_NUMBER_SELECTOR} + a"
    LAST_PAGE_SELECTOR = f"{PAGE_NUMBER_SELECTOR} + a + a"
    CHAPTERS_SELECTOR = f"div.s-nav-head ~ ul a[href*='/{BOOK_RESOURCE}/']"
    _previous_page_hamesh: str = ""

    def __init__(self, url: str):
        """Book HTML page model constructor."""
        super().__init__(url)
        self._remove_copy_btn_from_html()
        self.page_url = self.url.split("#")[0]
        self._chapters_by_page: dict[str, str] = {}
        self._toc_chapters_levels: dict[str, int] = {}
        self.content: Selector | None = self.get_clean_page_content()
        self.hamesh_items: dict[str, Element] = self.get_hamesh_items()
        self._update_hamesh()

    def _remove_copy_btn_from_html(self) -> None:
        self._html.css(self.COPY_BTN_SELECTOR).drop()

    @property
    def current_page(self) -> Any:
        return self._html.css(f"{self.PAGE_NUMBER_SELECTOR}::attr(value)").get("")

    @property
    def has_next_page(self) -> bool:
        return bool(self._html.css(self.NEXT_PAGE_SELECTOR))

    @staticmethod
    def _get_page_number(page_anchor: SelectorList) -> str:
        match: Match | None = BOOK_URL_PATTERN.search(
            page_anchor.attrib.get("href", "")
        )
        assert match is not None
        page = match.group("page")
        assert isinstance(page, str)
        return page

    @property
    def next_page(self) -> str:
        next_page_element: SelectorList = self._html.css(self.NEXT_PAGE_SELECTOR)
        return self._get_page_number(next_page_element) if next_page_element else ""

    @property
    def next_page_url(self) -> str:
        next_page_element: SelectorList = self._html.css(self.NEXT_PAGE_SELECTOR)
        return (
            cast(str, next_page_element.attrib.get("href", ""))
            if next_page_element
            else ""
        )

    @property
    def last_page(self) -> str:
        last_page_element: SelectorList = self._html.css(self.LAST_PAGE_SELECTOR)
        return self._get_page_number(last_page_element) if last_page_element else ""

    def parse_toc(self, toc: SelectorList) -> list:
        toc_list: list = []
        item: Selector
        for item in toc:
            link: str = item.css("a::text").get("")
            ul_list: SelectorList = item.css("li ul")
            if ul_list:
                toc_list.append([link, self.parse_toc(ul_list.css("ul li"))])
            else:
                toc_list.append(link)
        return toc_list

    @property
    def toc(self) -> list[Any]:
        toc_ul: SelectorList = self._html.css(self.BOOK_TOC_SELECTOR)
        toc_ul.css('a[href="javascript:;"]').drop()
        return self.parse_toc(toc_ul)

    @property
    def chapters_by_page(self) -> dict[str, Any]:
        if self._chapters_by_page:
            return self.chapters_by_page
        chapters_list = self._html.css(self.CHAPTERS_SELECTOR)
        chapters: dict = {}
        for chapter in chapters_list:
            chapter_url = chapter.attrib.get("href", "")
            if chapters.get(chapter_url):
                chapters[chapter_url].append(chapter.css("::text").get("").strip())
                chapters.update({chapter_url: chapters[chapter_url]})
            else:
                chapters.update({chapter_url: [chapter.css("::text").get("").strip()]})
        self._chapters_by_page = chapters
        return self._chapters_by_page

    @property
    def part(self) -> str:
        return cast(str, self._html.css(self.PAGE_PART_SELECTOR).get("").strip())

    @property
    def parts_map(self) -> dict[str, int]:
        parts: SelectorList = self._html.css(self.PAGE_PARTS_MENU_SELECTOR)
        return (
            {
                part.get(""): index
                for index, part in enumerate(parts.css("li a::text")[1:])
            }
            if parts
            else {}
        )

    def get_clean_page_content(self) -> Selector | None:
        """Get cleaned-up page content."""
        if not self.content:
            return self.content
        # Delete parent div class
        self.content = Selector(
            text=PARENT_DIV_CLASS_PATTERN.sub("", self.content.get())
        )
        # Delete all elements classes
        # for element in filter(
        #     lambda x: isinstance(x, Tag) and x.get("class", None),
        #     content.recursiveChildGenerator(),
        # ):
        #     if not any([c for c in element["class"] if c in ["text-center", "hamesh"]]):
        #         del element["class"]
        # Delete empty spans
        for element in self.content.css("span"):
            if not element.css("::text").get():
                element.drop()
        # Delete paragraph style
        for _ in self.content.css('p[style="font-size: 15px"]'):
            _ = Selector(text=HTML_STYLE_PATTERN.sub("", self.content.get()))
        return self.content

    def get_hamesh_items(self) -> dict[str, Element]:
        hamesh_items: dict[str, Element] = {}
        if not self.content:
            return hamesh_items
        hamesh: SelectorList = self.content.css(".hamesh")
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
        elif not type(self)._previous_page_hamesh:
            type(self)._previous_page_hamesh = ""
        for match in HAMESH_PATTERN.finditer(hamesh.get("")):
            hamesh_counter += 1
            current_hamesh = match.group("number").strip()
            hamesh_line = match.group("content").strip()
            #  <aside id="fn1" epub:type="footnote">
            #  <p><a href="#fnref1" title="footnote 1">[1]</a> Text in popup</p>
            #  </aside>
            new_footnote_aside = Element(
                "aside",
                {"id": f"fn{hamesh_counter}", epub_type: "footnote"},
            )
            new_footnote_span = Element("span")
            new_footnote_a = Element(
                "a",
                {
                    "href": f"#fnref{hamesh_counter}",
                    # "title": f"هامش {hamesh_counter}",
                    "class": "nu",
                },
            )
            new_footnote_a.text = current_hamesh
            if type(self)._previous_page_hamesh:
                new_footnote_span.text = type(self)._previous_page_hamesh.replace(
                    "\n", "<br>"
                )
                new_footnote_span.append(Element("br"))
                new_footnote_span.text = " " + hamesh_line.strip()
                type(self)._previous_page_hamesh = ""
            else:
                new_footnote_span.text = " " + hamesh_line.strip()
            new_footnote_aside.append(new_footnote_a)
            new_footnote_aside.append(new_footnote_span)
            hamesh_items.update({current_hamesh: new_footnote_aside})
        return hamesh_items

    def _update_hamesh(self) -> None:
        footnote_count = 1
        if not self.content:
            return
        hamesh: SelectorList = self.content.css(".hamesh")
        if not hamesh:
            return
        new_hamesh: Element = Element("div", {"class": "hamesh"})
        parent: SelectorList = self.content.css("div")
        p_elements: SelectorList = self.content.css("p:not(.hamesh)")
        for p in p_elements:
            matches = ARABIC_NUMBER_BETWEEN_BRACKETS_PATTERN.finditer(p.get())
            for match in matches:
                number = match.group("number")
                if not self.hamesh_items.get(number, ""):
                    continue
                aya_match = ARABIC_NUMBER_BETWEEN_CURLY_BRACES_PATTERN.search(p.get())
                if (
                    aya_match
                    and number in aya_match.group()
                    # number in inside aya
                    and match.start("number") > aya_match.start()
                ):
                    continue
                footnote_link: Element = Element(
                    "a",
                    {
                        "href": f"#fn{footnote_count}",
                        epub_type: "noteref",
                        "role": "doc-noteref",
                        "id": f"fnref{footnote_count}",
                        # "title": f"هامش {footnote_count}",
                        "class": "fn nu",
                    },
                )
                footnote_link.text = number
                # new_p_content = (
                #     str(p)[len("<p>") : match.start()]
                #     + str(footnote_link)
                #     + str(p)[match.start() + len(match.group()) : 0 - len("</p>")]
                # )
                # TODO: Find a better way to replace number with its a element,
                #  since replacing only the first occurrence might not be the best solution
                new_p_el = p.get().replace(
                    number, self.element_as_text(footnote_link), 1
                )
                self.content = Selector(text=parent.get("").replace(p.get(), new_p_el))
                footnote_count += 1
                new_hamesh.append(self.hamesh_items[number])
        self.content = Selector(
            text=self.content.get().replace(
                hamesh.get(""), self.element_as_text(new_hamesh)
            )
        )

    @staticmethod
    def element_as_text(element: Element) -> str:
        element_text: str = tostring(element, encoding="utf-8").decode()
        assert isinstance(element_text, str)
        return element_text

    def __repr__(self) -> str:
        return f"<BookHTMLPage(url={self.url})>"
