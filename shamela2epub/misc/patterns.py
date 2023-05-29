import re
from re import Pattern

from shamela2epub.misc.constants import SHAMELA_DOMAIN

BOOK_URL_PATTERN: Pattern = re.compile(
    r"(?:https?://)?{}/book/(?P<bookID>\d+)/?(?P<page>\d+)?#?(?P<paragraph>p\d+)?".format(
        SHAMELA_DOMAIN
    )
)

CSS_STYLE_COLOR_PATTERN: Pattern = re.compile(r'style="(color:#[\w\d]{6})"')

HAMESH_CONTINUATION_PATTERN: Pattern = re.compile(
    r"(?<=>)(?P<continuation>=.+?)(?=<br>|</p>)"
)

HAMESH_PATTERN: Pattern = re.compile(
    r"(?P<number>\([\u0660-\u0669]+\))(?P<content>.+?)(?:</?br/?>(?=\([\u0660-\u0669]+\))|</p>)"
)

ARABIC_NUMBER_BETWEEN_BRACKETS_PATTERN: Pattern = re.compile(
    r"(?P<number>\([\u0660-\u0669]+\))"
)

# POSSIBLE_HAMESH_NUMBER_HTML_PATTERN: Pattern = re.compile(
#     r"(<span style=\"color:#008000\">(?P<other>.+?)?(?P<number>\([\u0660-\u0669]+\))</span>)"
# )

ARABIC_NUMBER_BETWEEN_CURLY_BRACES_PATTERN: Pattern = re.compile(
    r"{.+?(\([\u0660-\u0669]+\)).+?}"
)


# HTML_CLASS_PATTERN = re.compile(r' class="(.*?)"')  # r' class="[\w\d -]+"'
HTML_STYLE_PATTERN = re.compile(r' style="(.*?)"')
PARENT_DIV_CLASS_PATTERN = re.compile(r' class="nass margin-top-10"')
