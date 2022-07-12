""" Entry Point """
import click

from shamela2epub.cli.app import download
from shamela2epub.gui.app import gui


@click.group()
def click_cli() -> None:
    pass


if __name__ == "__main__":
    click_cli.add_command(download)
    click_cli.add_command(gui)
    click_cli()
