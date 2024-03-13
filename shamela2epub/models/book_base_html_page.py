from parsel import Selector, SelectorList


class BookBaseHTMLPage:
    BOOK_PAGE_CONTENT_SELECTOR = ".nass"

    def __init__(self, html: str):
        """Base class for HTML pages."""
        self._html: Selector = Selector(text=html)
        self.content: SelectorList = self._html.css(self.BOOK_PAGE_CONTENT_SELECTOR)
