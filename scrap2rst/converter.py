import logging
import re
from urllib.request import urlopen
from urllib.parse import urlparse, urlunparse, quote
import unicodedata
import typing

logger = logging.getLogger(__name__)


def get_api_url(url: str) -> str:
    parts = urlparse(url)
    path = quote(parts.path)
    if not path.startswith('/api/'):
        path = '/'.join(['/api/pages', path.strip("/"), 'text'])
    api_url = urlunparse((*parts[:2], path, *parts[3:]))
    return api_url


def fetch(api_url: str) -> str:
    logger.info('fetch: %s', api_url)
    data = urlopen(api_url).read()
    data = data.decode('utf-8')
    return data


EAW = dict.fromkeys('AFW', 2)
"""
http://www.unicode.org/reports/tr44/tr44-6.html::

  A  2 Ambiguous
  F  2 Fullwidth
  H  1 Halfwidth
  N  1 Neutral
  Na 1 Narrow
  W  2 Wide
"""


def wlen(text: str) -> int:
    """calc text width with east asian width."""
    return sum(EAW.get(unicodedata.east_asian_width(c), 1) for c in text)


M = {
    'heading': re.compile(r'\[\* (.*)\]').match,
    'bullet': re.compile(r'([\s\t]+)(.*$)').match,
    'figure': re.compile(r'\[(https://gyazo.com/.*|.*\.(jpg|png|gif))\]$').match,
    'image': re.compile(r'\[(https://gyazo.com/.*|.*\.(jpg|png|gif))\]$').match,
    'link': re.compile(r'(.*)\[(https?://[^\s]+)\s+([^\]]+)\](.*)').match,
}


class Convert:
    def __init__(self, data: str):
        self.data = data
        self.line_states = []

    def _h1(self, line):
        hr = '=' * wlen(line)
        return '\n'.join((hr, line, hr))

    def _h2(self, line):
        hr = '=' * wlen(line)
        return '\n'.join((line, hr))

    def parse_paragraph_and_render(self, line: str, ln: int) -> 'typing.List[str]':
        if ln == 0:
            name = 'title'
            result = [
                self._h1(line),
                '',
            ]
            state = (name, None)
        elif M['heading'](line):
            name = 'heading'
            result = [
                self._h2(M['heading'](line).group(1)),
                '',
            ]
            state = (name, None)
        elif M['bullet'](line):
            name = 'bullet'
            m = M['bullet'](line)
            # FIXME: enumerated list has no 2 indented children.
            indent = (len(m.group(1)) - 1)
            pre = ' ' * 2 * indent
            body = self.parse_inline_and_render(m.group(2), ln)
            if self.line_states[ln-1] == (name, indent):
                result = [pre + '* ' + body]
            else:
                # when bullets level is changed, insert blank line before new indentation
                result = ['', pre + '* ' + body]
            state = (name, indent)
        elif M['figure'](line):
            name = 'figure'
            m = M['figure'](line)
            result = [
                '',
                '.. figure:: ' + m.group(1),
                '',
                ]
            state = (name, None)
        else:
            name = 'NOTHING'
            result = [self.parse_inline_and_render(line, ln)]
            state = (name, None)

        self.line_states.append(state)
        logger.debug('LINE %d match as %s\n     IN: %s\n    OUT: %s', ln+1, name, line, result)
        return result

    def parse_inline_and_render(self, line: str, ln: int) -> str:
        # FIXME: inline parser must parse whole line. currently parsing a first part.
        if M['image'](line):
            name = 'image'
            # FIXME: inline image must be `|name|` and `.. |name| image:: PATH`
            m = M['image'](line)
            result = '.. image:: ' + m.group(1)
        elif M['link'](line):
            name = 'link'
            m = M['link'](line)
            result = '{0} `{2} <{1}>`__ {3}'.format(*m.groups())
        else:
            name = 'NOTHING'
            result = line

        logger.debug('LINE %d match as %s\n IN: %s\nOUT: %s', ln+1, name, line, result)
        return result

    def run(self) -> str:
        output = []
        for ln, line in enumerate(self.data.splitlines()):
            output.extend(self.parse_paragraph_and_render(line, ln))

        return '\n'.join(output)


def convert(url: str) -> str:
    api_url = get_api_url(url)
    data = fetch(api_url)
    return Convert(data).run()