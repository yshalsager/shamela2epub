# shamela2epub

![logo](shamela2epub/assets/books-duotone.svg)

[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

[![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?style=flat&labelColor=00457C&logo=PayPal&logoColor=white&link=https://www.paypal.me/yshalsager)](https://www.paypal.me/yshalsager)
[![LiberaPay](https://img.shields.io/badge/Liberapay-Support-F6C915?style=flat&labelColor=F6C915&logo=Liberapay&logoColor=white&link=https://liberapay.com/yshalsager)](https://liberapay.com/yshalsager)

A CLI and GUI tool to download a book on https://shamela.ws into an EPUB book.

## Installation

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

- If you installed the package from pypi, you can use the following command:

```bash
shamela2epubgui
```

- Otherwise, use normal python command:

```bash
python3 -m shamela2epub gui
```

## Features

- CLI and GUI!
- Creates an [EPUB3](https://www.w3.org/publishing/epub3/epub-spec.html) RTL standard book.
- Automatically adds a page for book information.
- Automatically generated table of contents with support for nested chapters.
- Automatically adds book part and page number to each page's footer.
- Sanitizes the book HTML from unnecessary elements and classes.
- Converts inline CSS color styles to CSS classes.

## Known Issues

- Books that have a last nested section with level deeper (e.g. 3) than its next section (e.g. 2) and both have the same
  page number (e.g. `page_017.xhtml`) cannot be converted to KFX unless that last nested section is removed.

## TODO

### Next

- Make the gui re-sizes dynamically
- Add Pyinstaller Actions to the repo
- Tag releases

### Maybe

- Fix TOC conversion problem when last nested section with level deeper than its next has the same page number by
  removing it from the TOC

## Thanks

- GUI icons are made by the amazing [Phosphor Icons](https://phosphoricons.com/) (books - duotone - `#AB8B64`).