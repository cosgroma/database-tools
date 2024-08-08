"""
logging utility
"""

import logging

import coloredlogs
from termcolor import colored

LOG_NAME = "work.cosgroma.db-man"

logger = logging.getLogger(LOG_NAME)


class LoggerArgs:
    def __init__(self, verbose=False, quiet=False):
        self.verbose = verbose
        self.quiet = quiet

    def __str__(self):
        return f"LoggerArgs(verbose={self.verbose}, quiet={self.quiet})"

    def __repr__(self):
        return f"LoggerArgs(verbose={self.verbose}, quiet={self.quiet})"


def init_logger(args: LoggerArgs):
    """Inits logger based on commandline args"""
    coloredlogs.install(
        level="WARN" if args.quiet else ("DEBUG" if args.verbose else "INFO"),
        logger=logger,
        fmt="%(asctime)s %(programname)s %(message)s",
        programname=">",
        datefmt="%H:%m:%S",
        field_styles={
            "asctime": {"color": "black", "bright": True},
            "hostname": {"color": "magenta"},
            "levelname": {"bold": True, "color": "black"},
            "name": {"color": "blue"},
            "programname": {"color": "black", "bright": True},
            "username": {"color": "yellow"},
        },
        level_styles={
            "critical": {"bold": True, "color": "red"},
            "debug": {"color": "white", "faint": True},
            "error": {"color": "red"},
            "info": {"color": "white", "faint": False},
            "notice": {"color": "magenta"},
            "warning": {"color": "yellow"},
        },
    )

    logging.getLogger(LOG_NAME).level = logging.WARN if args.quiet else (logging.DEBUG if args.verbose else logging.INFO)


def headline(msg: str):
    """Bold headline"""
    logger.info(colored(f" {msg:80}", "blue", attrs=["reverse"]))
