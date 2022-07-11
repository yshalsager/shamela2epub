"""
shamela2epub main
"""
import logging

import click

from shamela2epub import OUT_DIR
from shamela2epub.misc.utils import (
    get_book_first_page_url,
    get_book_info_page_url,
    is_valid_url,
)
from shamela2epub.models.book_html_page import BookHTMLPage
from shamela2epub.models.book_info_html_page import BookInfoHTMLPage
from shamela2epub.models.epub_book import EPUBBook

logger = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("url", type=str)
@click.option("-o", "--output", type=str, help="ePub output book custom name")
def download(url: str, output: str) -> None:
    """Download Shamela book form URL to ePub"""
    if not is_valid_url(url):
        print("The URL you entered is invalid! Exiting...")
        return
    logger.info(f"Got valid URL: {url}")
    # Info Page
    book_info_page = BookInfoHTMLPage(get_book_info_page_url(url))
    epub_book = EPUBBook()
    epub_book.create_info_page(book_info_page)
    logger.info(f"Working on book {book_info_page.title} by {book_info_page.author}")
    # First Page
    first_page_url = get_book_first_page_url(url)
    logger.info(f"Getting page {first_page_url}.")
    book_html_page = BookHTMLPage(first_page_url)
    epub_book.set_page_count(book_html_page.last_page)
    epub_book.set_parts_map(book_html_page.parts_map)
    epub_book.add_page(book_html_page)
    # Other pages
    has_next = book_html_page.has_next_page
    next_page_url = book_html_page.next_page_url
    while has_next:
        logger.info(f"Getting page {next_page_url}.")
        book_html_page = BookHTMLPage(next_page_url)
        epub_book.add_page(book_html_page)
        if not book_html_page.has_next_page:
            has_next = False
        next_page_url = book_html_page.next_page_url
    # Generate TOC
    epub_book.generate_toc(book_html_page.toc)
    # Save new book
    logger.info("Saving the new book")
    output_book = (
        output or f"{OUT_DIR}/{book_info_page.title} - {book_info_page.author}.epub"
    )
    epub_book.save_book(output_book)
    logger.info(f"Done! You can find the book at: {output_book}")
