import sys
import logging
import re
from urllib.request import urlopen
from urllib.parse import urlparse, urlunparse, quote
from urllib.error import HTTPError
import unicodedata
import typing
from dataclasses import dataclass
from enum import Enum
import os.path

logger = logging.getLogger(__name__)


def get_api_url(url: str) -> str:
    parts = urlparse(url)
    if parts.path.startswith('/api/'):
        return url

    paths = parts.path.strip('/').split('/')
    project = paths[0]
    pagename = '/'.join(paths[1:])
    path = '/'.join(['/api/pages', project, quote(pagename, safe=''), 'text'])
    api_url = urlunparse((*parts[:2], path, *parts[3:]))
    return api_url


def get_user_url(url: str) -> str:
    parts = urlparse(url)
    path = quote(parts.path)
    if path.startswith('/api/'):
        user = path.strip('/').split('/')[2]
    else:
        user = path.strip('/').split('/')[0]
    user_url = urlunparse((*parts[:2], user, '', '', ''))
    return user_url


def fetch(api_url: str) -> str:
    logger.info('fetch: %s', api_url)
    try:
        data = urlopen(api_url).read()
    except HTTPError as e:
        logger.error(e)
        sys.exit(-1)

    data = data.decode('utf-8')
    return data


def get_normalized_image_url(image_url):
    if image_url.startswith('https://gyazo.com/') and os.path.splitext(image_url)[1] == '':
        image_url += '.png'
    return image_url


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
    'link': re.compile(r'(.*)\[([^\]]+)\](.*)').match,
    'link_external': re.compile(r'^(https?://[^\s]+)(\s+([^\]]+))?$').match,
    'code': re.compile(r'code:(.+)$').match,
}


CODE_EXT_LANG = {
    '.py': 'python',
    '.sh': 'shell',
    '.bash': 'shell',
    '.rst': 'rst',
    '.yaml': 'yaml',
    '.html': 'html',
    '.diff': 'diff',
    '.log': 'text',
    '.conf': 'conf',
}


CODE_TYPE_LANG = {
    'bash': 'bash',
}
CODE_TYPE_LANG.update({k:k for k in CODE_EXT_LANG.values()})


class ModeType(Enum):
    NONE = 0
    CODE = 1


@dataclass
class Mode:
    type: ModeType = ModeType.NONE
    indent: typing.Optional[int] = None
    attr: typing.Any = None

    def set_code(self, indent, attr):
        self.type = ModeType.CODE
        self.indent = indent
        self.attr = attr

    def reset(self):
        self.type = ModeType.NONE
        self.indent = None
        self.attr = None


class Convert:
    def __init__(self, data: str, user_url: str):
        self.data = data
        self.user_url = user_url
        self.line_states = []
        self.link_targets = {}
        self.mode = Mode()

    def _h1(self, line):
        hr = '=' * wlen(line)
        return '\n'.join((hr, line, hr))

    def _h2(self, line):
        hr = '=' * wlen(line)
        return '\n'.join((line, hr))

    def parse_paragraph_and_render(self, line: str, ln: int) -> 'typing.List[str]':
        if self.mode.type == ModeType.CODE:
            m = re.match(r'([\s\t]+)', line)
            if not m:
                self.mode.reset()
            else:
                indent = len(m.group(1))
                if indent < self.mode.indent + 1:
                    self.mode.reset()
                else:
                    # import pdb;pdb.set_trace()
                    self.line_states.append(('code', indent))
                    return [' ' * 2 * (self.mode.indent + 1) + line[self.mode.indent:]]

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
            body = self.parse_inline_and_render(m.group(2), ln, indent)
            if self.line_states[ln-1] == (name, indent):
                result = [pre + '* ' + body]
            else:
                # when bullets level is changed, insert blank line before new indentation
                result = ['', pre + '* ' + body]
            state = (name, indent)
        elif M['figure'](line):
            name = 'figure'
            m = M['figure'](line)
            image_url = get_normalized_image_url(m.group(1))
            result = [
                '',
                f'.. figure:: {image_url}',
                '',
                ]
            state = (name, None)
        else:
            name = 'NOTHING'
            result = [self.parse_inline_and_render(line, ln, 0)]  # FIXME: 0?
            state = (name, None)

        self.line_states.append(state)
        logger.debug('LINE %d match as %s\n     IN: %s\n    OUT: %s', ln+1, name, line, result)
        return result

    def parse_inline_and_render(self, line: str, ln: int, indent: int) -> str:
        # FIXME: inline parser must parse whole line. currently parsing a first part.
        if M['code'](line):
            name = 'code'
            code_type = M['code'](line).group(1)
            self.mode.set_code(indent, code_type)
            ext = os.path.splitext(code_type)[1]
            if ext in CODE_EXT_LANG:
                code_lang = CODE_EXT_LANG[ext]
            elif code_type in CODE_TYPE_LANG:
                code_lang = CODE_TYPE_LANG[code_type]
            else:
                code_lang = code_type
                logger.warning('code type %r does not defined.', code_type)
            result = f'\n{indent * " " * 2}.. code:: {code_lang}\n'  # reST requires empty line before and after directive.
        elif M['image'](line):
            name = 'image'
            # FIXME: inline image must be `|name|` and `.. |name| image:: PATH`
            m = M['image'](line)
            image_url = get_normalized_image_url(m.group(1))
            result = f'.. image:: {image_url}'
        elif M['link'](line):
            name = 'link'
            m = M['link'](line)
            _pre, _target, _post = m.groups()
            if M['link_external'](_target):
                _link, _, _title = M['link_external'](_target).groups()
            else:
                _link = self.user_url + '/' + _target.replace(' ', '_')
                _title = _target

            if _pre:
                _pre = _pre + ' '
            if _post:
                _post = ' ' + _post
            if _title:
                # pre-text [https://example.com/foo title text] post-text
                result = '{0}`{1}`_{2}'.format(_pre, _title, _post)
                self.link_targets[_title] = _link
            else:
                # pre-text [https://example.com/foo] post-text
                result = '{0}{1}{2}'.format(_pre, _link, _post)
        else:
            name = 'NOTHING'
            result = line

        logger.debug('LINE %d match as %s\n IN: %s\nOUT: %s', ln+1, name, line, result)
        return result

    def run(self) -> str:
        output = []
        for ln, line in enumerate(self.data.splitlines()):
            output.extend(self.parse_paragraph_and_render(line, ln))

        for k, v in self.link_targets.items():
            output.extend([
                '',
                f".. _{k}: {v}",
            ])

        return '\n'.join(output)


def convert(url: str) -> str:
    api_url = get_api_url(url)
    user_url = get_user_url(url)
    logger.info('user url: %s', user_url)
    data = fetch(api_url)
    return Convert(data, user_url).run()
