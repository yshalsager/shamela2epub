"""
shamela2epub main
"""
import logging

import click

from shamela2epub import OUT_DIR
from shamela2epub.misc.utils import get_book_first_page_url, is_valid_url
from shamela2epub.models.book_html_page import BookHTMLPage
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
    # First Page
    next_page_url = get_book_first_page_url(url)
    logger.info(f"Getting page {next_page_url}.")
    book_html_page = BookHTMLPage(next_page_url)
    epub_book = EPUBBook(book_html_page.last_page)
    logger.info(f"Working on book {book_html_page.title} by {book_html_page.author}")
    epub_book.create_first_page(book_html_page)
    print(book_html_page.toc)
    has_next = True
    # Other pages
    next_page_url = book_html_page.next_page_url
    while has_next:
        logger.info(f"Getting page {next_page_url}.")
        book_html_page = BookHTMLPage(next_page_url)
        epub_book.add_page(book_html_page)
        if not book_html_page.has_next_page:
            has_next = False
        next_page_url = book_html_page.next_page_url
        # if book_html_page.next_page == "5":
        #     break
    # Save new book
    logger.info("Saving the new book")
    output_book = (
        output or f"{OUT_DIR}/{book_html_page.title} - {book_html_page.author}.epub"
    )
    epub_book.save_book(output_book)
    logger.info(f"Done! You can find the book at: {output_book}")
