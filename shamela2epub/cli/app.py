import logging

import click

from shamela2epub.main import BookDownloader

logger = logging.getLogger(__name__)


@click.command()
@click.argument("url", type=str)
@click.option("-o", "--output", type=str, help="ePub output book custom name")
def download(url: str, output: str) -> None:
    """Download Shamela book form URL to ePub."""
    downloader = BookDownloader(url)
    if not downloader.valid:
        print("The URL you entered is invalid! Exiting...")
        return
    logger.info(f"Got valid URL: {url}")
    downloader.create_info_page()
    logger.info(
        f"Working on book {downloader.book_info_page.title} by {downloader.book_info_page.author}"
    )
    first_page_url = downloader.create_first_page()
    logger.info(f"Getting page {first_page_url}.")
    for page in downloader.download():
        logger.info(f"Getting page {page}.")
    # Save new book
    logger.info("Saving the new book")
    output_book = downloader.save_book(output)
    logger.info(f"Done! You can find the book at: {output_book}")


if __name__ == "__main__":

    @click.group()
    def cli() -> None:
        pass

    cli.add_command(download)
    cli()
