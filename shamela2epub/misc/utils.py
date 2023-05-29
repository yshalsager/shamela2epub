from pathlib import Path
from platform import system
from re import Match
from subprocess import Popen

from shamela2epub import PKG_DIR
from shamela2epub.misc.constants import BOOK_RESOURCE, SHAMELA_DOMAIN
from shamela2epub.misc.patterns import BOOK_URL_PATTERN


def is_valid_url(url: str) -> bool:
    return bool(BOOK_URL_PATTERN.search(url))


def get_info_from_url(url: str) -> dict[str, str]:
    match: Match[str] | None = BOOK_URL_PATTERN.search(url)
    assert match is not None
    return match.groupdict()


def get_book_first_page_url(url: str) -> str:
    info: dict[str, str] = get_info_from_url(url)
    return f"https://{SHAMELA_DOMAIN}/{BOOK_RESOURCE}/{info['bookID']}/1"


def get_book_info_page_url(url: str) -> str:
    info: dict[str, str] = get_info_from_url(url)
    return f"https://{SHAMELA_DOMAIN}/{BOOK_RESOURCE}/{info['bookID']}/"


def get_stylesheet() -> str:
    return Path(PKG_DIR / "assets/styles.css").read_text()


def browse_file_directory(filepath: Path) -> None:
    """Browse a file parent directory in OS file explorer."""
    if system() == "Windows":
        from os import startfile  # type: ignore[attr-defined]

        startfile(filepath.parent)  # noqa: 606
    elif system() == "Darwin":
        Popen(["open", filepath.parent])  # noqa: S603, S607
    else:
        Popen(["xdg-open", filepath.parent])  # noqa: S603, S607
