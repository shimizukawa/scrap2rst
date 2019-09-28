from textwrap import dedent as d
import pytest


@pytest.fixture
def converter(src):
    from scrap2rst.converter import Convert
    converter = Convert(src, 'https://example.com/proj')
    return converter


@pytest.fixture
def get_api_url():
    from scrap2rst.converter import get_api_url
    return get_api_url


@pytest.mark.parametrize(
    'page_url,api_url',
    [(
        'https://scrapbox.io/proj/page',
        'https://scrapbox.io/api/pages/proj/page/text',
    ), (
        # #10: encode special chars for URL: /
        'https://scrapbox.io/proj/page/with/slash',
        'https://scrapbox.io/api/pages/proj/page%2Fwith%2Fslash/text',
    )]
)
def test_get_api_url(get_api_url, page_url, api_url):
    assert get_api_url(page_url) == api_url


parametrize = [(
    # 0.1.0, Page header
    '''\
title
body
''',
    '''\
=====
title
=====

body
'''), (

    # 0.1.0, Heading level2 if the line is strong text.
    '''\
title
[* heading2]
body
''',
    '''\
=====
title
=====

heading2
========

body
'''
    ), (

    # 0.1.0, Figure if the line is link to image.
    '''\
title
[https://example.com/image.png]
''',
    '''\
=====
title
=====


.. figure:: https://example.com/image.png

'''
    ), (

    # 0.1.0, Link if the line contains link excluding to image url.
    '''\
title
text [https://example.com/] text
''',
    '''\
=====
title
=====

text https://example.com/ text
'''
    ), (

    # #3: notation: links
    '''\
title
text [target] text
''',
    '''\
=====
title
=====

text `target`_ text


.. _target: https://example.com/proj/target
''',
), (

    # #6: notation: code block
    '''\
title

 code:python
  block
  block
''',
    '''\
=====
title
=====



* 
.. code:: python

    block
    block
''',
    ), (

    # #13 page link with link text will have unnecessary prefix "http://scrapbox.io/proj/" on conversion.
    '''\
title
text [https://example.com/ Example] text
''',
    '''\
=====
title
=====

text `Example`_ text


.. _Example: https://example.com/
''',
    ), (

    # #15 image url for gyazo should have `.png` extension on figure directive.
    '''\
title
[https://gyazo.com/image]
''',
    '''\
=====
title
=====


.. figure:: https://gyazo.com/image.png

''',
)
]


@pytest.mark.parametrize('src,rst', parametrize)
def test_page_header(src, rst, converter):
    assert converter.run() == rst
