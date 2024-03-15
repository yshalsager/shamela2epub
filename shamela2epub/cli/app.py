import logging
from pathlib import Path

import click

from shamela2epub import OUT_DIR
from shamela2epub.main import BookDownloader

logger = logging.getLogger(__name__)


@click.command()
@click.argument("url", type=str)
@click.option("-o", "--output", type=str, help="ePub output book custom name", default="")
@click.option("-x", "--connections", type=int, default=16, help="Max number of connections")
@click.option(
    "-f", "--force", is_flag=True, default=False, help="Force download even if the file exists"
)
def download(url: str, output: str, connections: int, force: bool) -> None:
    """Download Shamela book form URL to ePub."""
    downloader = BookDownloader(url, connections)
    if not downloader.valid:
        logger.error("The URL you entered is invalid! Exiting...")
        return
    logger.info(f"Got valid URL: {url}")
    downloader.create_info_page()
    book_name = f"{downloader.book_info_page.title} - {downloader.book_info_page.author}"
    logger.info(f"Working on book {book_name}")
    output_path = (
        output
        if output.endswith(".epub")
        else f"{output}/{book_name}.epub"
        if output
        else f"{OUT_DIR}/{book_name}.epub"
    )
    if Path(output_path).exists() and not force:
        logger.info("The file already exists! Exiting...")
        return
    downloader.download()
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
