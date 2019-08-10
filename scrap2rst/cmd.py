"""
command-line interface for scrap2rst
"""
import sys
import logging
import argparse

from scrap2rst import __version__
from scrap2rst.logging import setup_logger
from scrap2rst.converter import convert

logger = logging.getLogger(__name__)


def get_argparser():
    p = argparse.ArgumentParser()
    p.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__)
    p.add_argument('-d', '--debug', action='store_true', default=False, help='debug mode')
    p.add_argument('url', metavar='URL', help='url to convert')
    p.add_argument('-o', '--output', type=argparse.FileType(mode='w', encoding='utf-8'),
                   default=sys.stdout, help='output filename')

    return p


def main():
    args = get_argparser().parse_args()
    setup_logger(args.debug)

    output = convert(args.url)
    if args.output:
        args.output.write(output)
    else:
        print(output)


if __name__ == '__main__':
    main()
