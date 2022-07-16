# shamela2epub

> A CLI and GUI tool to download a book on https://shamela.ws into an EPUB book.

![logo](shamela2epub/assets/books-duotone.svg)

[![PyPI version](https://badge.fury.io/py/shamela2epub.svg)](https://pypi.org/project/shamela2epub/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/shamela2epub?period=total\&units=international_system\&left_color=grey\&right_color=blue\&left_text=Total%20Downloads%20\(PyPI\))](https://pepy.tech/project/shamela2epub)

[![GitHub release](https://img.shields.io/github/release/yshalsager/shamela2epub.svg)](https://github.com/yshalsager/shamela2epub/releases/)
[![GitHub Downloads](https://img.shields.io/github/downloads/yshalsager/shamela2epub/total.svg)](https://github.com/yshalsager/shamela2epub/releases/latest)

[![made-with-python](https://img.shields.io/badge/Made%20with-Python%203-3776AB?style=flat\&labelColor=3776AB\&logo=python\&logoColor=white\&link=https://www.python.org/)](https://www.python.org/)
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

[![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?style=flat\&labelColor=00457C\&logo=PayPal\&logoColor=white\&link=https://www.paypal.me/yshalsager)](https://www.paypal.me/yshalsager)
[![LiberaPay](https://img.shields.io/badge/Liberapay-Support-F6C915?style=flat\&labelColor=F6C915\&logo=Liberapay\&logoColor=white\&link=https://liberapay.com/yshalsager)](https://liberapay.com/yshalsager)

**Disclaimer:**

*   This software is freeware and open source and is only intended for personal or educational use.

## Installation

### From PyPI

```bash
pip install shamela2epub
```

### From the cloned repository

```bash
# Using poetry
poetry install

# or using pip 18+
pip install .
```

## Usage

### Command-line Tool (CLI)

```bash
python3 -m shamela2epub download URL
# python3 -m shamela2epub download "https://shamela.ws/book/823"

python3 -m shamela2epub download --help
Usage: python -m shamela2epub download [OPTIONS] URL

  Download Shamela book form URL to ePub

Options:
  -o, --output TEXT  ePub output book custom name
  --help             Show this message and exit.
```

### Graphical User Interface (GUI)

![gui](gui.png)

*   If you installed the package from PyPI, you can use the following command:

```bash
shamela2epubgui
```

*   If you downloaded the latest gui exe file from releases you can open it normally and use it.
*   Otherwise, use normal python command:

```bash
python3 -m shamela2epub gui
```

## Features

*   CLI and GUI!
*   Creates an [EPUB3](https://www.w3.org/publishing/epub3/epub-spec.html) RTL standard book.
*   Automatically adds a page for book information.
*   Automatically generated table of contents with support for nested chapters.
*   Automatically adds book part and page number to each page's footer.
*   Sanitizes the book HTML from unnecessary elements and classes.
*   Converts inline CSS color styles to CSS classes.

## Known Issues

*   Books that have a last nested section with level deeper (e.g. 3) than its next section (e.g. 2) and both have the same
    page number (e.g. `page_017.xhtml`) cannot be converted to KFX unless that last nested section is removed.

## TODO

### Next

*   You tell me :)

### Maybe

*   Fix TOC conversion problem when last nested section with level deeper than its next has the same page number by
    removing it from the TOC

## Acknowledgments

*   GUI icons are made by the amazing [Phosphor Icons](https://phosphoricons.com/) (books - duotone - `#AB8B64`).
