"""
command-line interface for scrap2rst
"""
import logging
import argparse

from scrap2rst import __version__
from scrap2rst.logging import setup_logger

logger = logging.getLogger(__name__)


def get_argparser():
    p = argparse.ArgumentParser()
    p.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__)
    p.add_argument('-d', '--debug', action='store_true', default=False, help='debug mode')

    return p


def main():
    args = get_argparser().parse_args()
    setup_logger(args.debug)
    logger.error('No features are provided yet.')


if __name__ == '__main__':
    main()
