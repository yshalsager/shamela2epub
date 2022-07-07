from re import Match
from typing import Dict, Optional

from bs4 import BeautifulSoup
from constants import BOOK_URL, SHAMELA_DOMAIN
from httpx import get

from shamela2epub.patterns import BOOK_URL_PATTERN


def is_valid_url(url: str) -> bool:
    return bool(BOOK_URL_PATTERN.search(url))


def get_book_first_page_url(url: str) -> str:
    match: Optional[Match[str]] = BOOK_URL_PATTERN.search(url)
    assert match is not None
    info: Dict[str, str] = match.groupdict()
    return f"https://{SHAMELA_DOMAIN}/{BOOK_URL}/{info['bookID']}/1"


def get_html(url: str) -> BeautifulSoup:
    return BeautifulSoup(get(url).content, "html.parser")
