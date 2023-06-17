from parsel import Selector, SelectorList

from shamela2epub.misc.http import get_url_text


class BookBaseHTMLPage:
    BOOK_PAGE_CONTENT_SELECTOR = ".nass"

    def __init__(self, url: str):
        """Base class for HTML pages."""
        self.url = url
        self._html: Selector = Selector(text=get_url_text(self.url))
        self.content: SelectorList = self._html.css(self.BOOK_PAGE_CONTENT_SELECTOR)
