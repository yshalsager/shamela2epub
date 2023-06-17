import logging

from httpx import get
from parsel import Selector, SelectorList

logging.getLogger("httpx").setLevel(logging.WARNING)


class BookBaseHTMLPage:
    BOOK_PAGE_CONTENT_SELECTOR = ".nass"

    def __init__(self, url: str):
        """Base class for HTML pages."""
        self.url = url
        self._html: Selector = Selector(text=get(self.url).text)
        self.content: SelectorList = self._html.css(self.BOOK_PAGE_CONTENT_SELECTOR)
