from typing import Any

from shamela2epub.models.book_base_html_page import BookBaseHTMLPage


class BookInfoHTMLPage(BookBaseHTMLPage):
    SEARCH_SELECTOR = f"{BookBaseHTMLPage.BOOK_PAGE_CONTENT_SELECTOR} div.text-left"
    INDEX_SELECTOR = f"{BookBaseHTMLPage.BOOK_PAGE_CONTENT_SELECTOR} div.betaka-index"
    BOOK_AUTHOR_SELECTOR = "h1 + div a"
    BOOK_TITLE_SELECTOR = "h1 a"

    def __init__(self, url: str):
        self.url = url
        super().__init__(url)
        self._sanitize_html()
        self.title = self._html.select_one(self.BOOK_TITLE_SELECTOR).text.strip()
        self.author = self._html.select_one(self.BOOK_AUTHOR_SELECTOR).text.strip()

    def _sanitize_html(self) -> None:
        self._html.select_one(self.INDEX_SELECTOR).decompose()
        self._html.select_one(self.SEARCH_SELECTOR).decompose()
        del self.content["class"]
