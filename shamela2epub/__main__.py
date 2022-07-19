"""Entry Point."""
import click

from shamela2epub.cli.app import download
from shamela2epub.gui.app import gui


@click.group()
def click_cli() -> None:
    pass


def main() -> None:
    click_cli.add_command(download)
    click_cli.add_command(gui)
    click_cli()


if __name__ == "__main__":
    main()
