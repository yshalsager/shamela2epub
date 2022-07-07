"""
shamela2epub main
"""
from pathlib import Path

import click

from shamela2epub.utils import get_book_first_page_url, is_valid_url


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("url", type=str)
@click.option("-o", "--output", type=str, help="ePub output book custom name")
def convert(url: str, output: str) -> None:
    """Convert Shamela book form URL to ePub"""
    if not is_valid_url(url):
        print("The URL you entered is invalid! Exiting...")
        return
    book_first_page_url = get_book_first_page_url(url)
