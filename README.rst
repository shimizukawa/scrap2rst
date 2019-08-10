=========
scrap2rst
=========

.. image:: https://img.shields.io/pypi/v/scrap2rst.svg
   :alt: PyPI
   :target: http://pypi.org/p/scrap2rst

.. image:: https://img.shields.io/pypi/pyversions/scrap2rst.svg
   :alt: PyPI - Python Version

.. image:: https://img.shields.io/github/license/shimizukawa/scrap2rst.svg
   :alt: License
   :target: https://github.com/shimizukawa/scrap2rst/blob/master/LICENSE

.. image:: https://img.shields.io/github/stars/shimizukawa/scrap2rst.svg?style=social&label=Stars
   :alt: GitHub stars
   :target: https://github.com/shimizukawa/scrap2rst


``scrap2rst`` is an markup syntax converter from scrapbox into reStructuredText.

Feature
=======

* Page header
* Heading level2 if the line is strong text.
* Figure if the line is link to image.
* Image if the line contains link to image.
* Link if the line contains link excluding to image url.

Still many limitation are exist.

Command
=======

Convert from scrapbox into reStructuredText::

  $ scrap2rst URL -o output.rst


License
=======
Licensed under the MIT Licence.


CHANGES
=======

See: https://github.com/shimizukawa/scrap2rst/blob/master/CHANGELOG.rst

