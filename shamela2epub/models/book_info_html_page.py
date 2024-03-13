from shamela2epub.misc.patterns import PARENT_DIV_CLASS_PATTERN
from shamela2epub.models.book_base_html_page import BookBaseHTMLPage


class BookInfoHTMLPage(BookBaseHTMLPage):
    SEARCH_SELECTOR = f"{BookBaseHTMLPage.BOOK_PAGE_CONTENT_SELECTOR} div.text-left"
    INDEX_SELECTOR = f"{BookBaseHTMLPage.BOOK_PAGE_CONTENT_SELECTOR} div.betaka-index"
    BOOK_AUTHOR_SELECTOR = "h1 + div a::text"
    BOOK_TITLE_SELECTOR = "h1 a::text"

    def __init__(self, url: str, html: str) -> None:
        """Book Info Page model constructor."""
        super().__init__(html)
        self.url = url
        self.text_content: str = ""
        self._sanitize_html()
        self.title = self._html.css(self.BOOK_TITLE_SELECTOR).get("").strip()
        self.author = self._html.css(self.BOOK_AUTHOR_SELECTOR).get("").strip()

    def _sanitize_html(self) -> None:
        self._html.css(self.INDEX_SELECTOR).drop()
        self._html.css(self.SEARCH_SELECTOR).drop()
        self.text_content = PARENT_DIV_CLASS_PATTERN.sub("", self.content.get(""))
