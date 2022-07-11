from typing import Dict

from bs4 import BeautifulSoup, Tag
from httpx import get


class BookBaseHTMLPage:
    BOOK_PAGE_CONTENT_SELECTOR = "div.nass"

    def __init__(self, url: str):
        self.url = url
        self._html: BeautifulSoup = BeautifulSoup(get(self.url).content, "html.parser")
        self.content = self._html.select_one(self.BOOK_PAGE_CONTENT_SELECTOR)
