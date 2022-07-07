import re

from shamela2epub.constants import SHAMELA_DOMAIN

BOOK_URL_PATTERN = re.compile(
    r"(?:https?://)?{}/book/(?P<bookID>\d+)/?(?P<page>\d+)?#?(?P<paragraph>p\d+)?".format(
        SHAMELA_DOMAIN
    )
)
