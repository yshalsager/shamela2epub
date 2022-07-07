# shamela2epub

[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

[![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?style=flat&labelColor=00457C&logo=PayPal&logoColor=white&link=https://www.paypal.me/yshalsager)](https://www.paypal.me/yshalsager)
[![Patreon](https://img.shields.io/badge/Patreon-Support-F96854?style=flat&labelColor=F96854&logo=Patreon&logoColor=white&link=https://www.patreon.com/XiaomiFirmwareUpdater)](https://www.patreon.com/XiaomiFirmwareUpdater)
[![Liberapay](https://img.shields.io/badge/Liberapay-Support-F6C915?style=flat&labelColor=F6C915&logo=Liberapay&logoColor=white&link=https://liberapay.com/yshalsager)](https://liberapay.com/yshalsager)

A CLI tool to download a book on https://shamela.ws into an EPUB book.

## Installation

```bash
# Using poetry
poetry install

# or using pip 18+
pip install .
```

## Usage

```bash
python3 download URL
# python3 download "https://shamela.ws/book/823"

python3 -m shamela2epub download --help
Usage: python -m shamela2epub download [OPTIONS] URL

  Download Shamela book form URL to ePub

Options:
  -o, --output TEXT  ePub output book custom name
  --help             Show this message and exit.
```
