import re

from shamela2epub.misc.constants import SHAMELA_DOMAIN

BOOK_URL_PATTERN = re.compile(
    r"(?:https?://)?{}/book/(?P<bookID>\d+)/?(?P<page>\d+)?#?(?P<paragraph>p\d+)?".format(
        SHAMELA_DOMAIN
    )
)

CSS_STYLE_COLOR_PATTERN = re.compile(r'style="(color:#[\w\d]{6})"')
