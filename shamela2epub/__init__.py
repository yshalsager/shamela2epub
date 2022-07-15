""" Module initialization"""
import logging
from importlib import metadata
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from sys import stderr, stdout

import toml

# Use __file__ so PyInstaller bundle can access files too
PKG_DIR = Path(__file__).absolute().parent
PARENT_DIR = PKG_DIR.parent

# Set package version dynamically
try:
    # In production use package metadata
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # otherwise, read version from pyproject

    __version__ = toml.loads((PARENT_DIR / "pyproject.toml").read_text())["tool"][
        "poetry"
    ]["version"]


OUT_DIR = PARENT_DIR / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)
# Logging
LOG_FILE = PARENT_DIR / "last_run.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s"
FORMATTER: logging.Formatter = logging.Formatter(LOG_FORMAT)
handler = TimedRotatingFileHandler(LOG_FILE, when="d", interval=1, backupCount=3)
logging.basicConfig(filename=str(LOG_FILE), filemode="w", format=LOG_FORMAT)
OUT = logging.StreamHandler(stdout)
ERR = logging.StreamHandler(stderr)
OUT.setFormatter(FORMATTER)
ERR.setFormatter(FORMATTER)
OUT.setLevel(logging.INFO)
ERR.setLevel(logging.WARNING)
LOGGER = logging.getLogger()
LOGGER.addHandler(OUT)
LOGGER.addHandler(ERR)
LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)
