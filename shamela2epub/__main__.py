"""Entry Point."""

import click
from trogon import tui

from shamela2epub.cli.app import download


@tui()  # type: ignore[misc]
@click.group()
def click_cli() -> None:
    pass


def main() -> None:
    click_cli.add_command(download)
    try:
        from shamela2epub.gui.app import gui  # noqa: PLC0415

        click_cli.add_command(gui)
    except ImportError:
        pass
    click_cli()


if __name__ == "__main__":
    main()
