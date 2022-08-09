import re

from shamela2epub.misc.constants import SHAMELA_DOMAIN

BOOK_URL_PATTERN = re.compile(
    r"(?:https?://)?{}/book/(?P<bookID>\d+)/?(?P<page>\d+)?#?(?P<paragraph>p\d+)?".format(
        SHAMELA_DOMAIN
    )
)

CSS_STYLE_COLOR_PATTERN = re.compile(r'style="(color:#[\w\d]{6})"')

HAMESH_CONTINUATION_PATTERN = re.compile(r"(?<=>)(?P<continuation>=.+?)(?=<br>|</p>)")

HAMESH_PATTERN = re.compile(
    r"(?P<number>\([\u0660-\u0669]+\))(?P<content>.+?)(?:</?br/?>(?=\([\u0660-\u0669]+\))|</p>)"
)

ARABIC_NUMBER_BETWEEN_BRACKETS_PATTERN = re.compile(r"(?P<number>\([\u0660-\u0669]+\))")

# POSSIBLE_HAMESH_NUMBER_HTML_PATTERN = re.compile(
#     r"(<span style=\"color:#008000\">(?P<other>.+?)?(?P<number>\([\u0660-\u0669]+\))</span>)"
# )

ARABIC_NUMBER_BETWEEN_CURLY_BRACES_PATTERN = re.compile(
    r"{.+?(\([\u0660-\u0669]+\)).+?}"
)
