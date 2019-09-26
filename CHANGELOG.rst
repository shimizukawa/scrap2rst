0.3.0 (2019-09-26)
==================

Deprecation
-----------

- `#16 <https://github.com/shimizukawa/scrap2rst/issues/16>`_: remove ``--sphinx`` and ``--toctree`` options.

   
New Feature
-----------

- `#11 <https://github.com/shimizukawa/scrap2rst/issues/11>`_: display 404 error message instead of python traceback

   
Bug Fix
-------

- `#10 <https://github.com/shimizukawa/scrap2rst/issues/10>`_: encode special chars for URL: /

- `#13 <https://github.com/shimizukawa/scrap2rst/issues/13>`_: page link with link text will have unnecessary prefix "http://scrapbox.io/proj/" on conversion.

- `#15 <https://github.com/shimizukawa/scrap2rst/issues/15>`_: image url for gyazo should have `.png` extension on figure directive.


0.2.0 (2019-09-13)
==================

New Feature
-----------

- `#12 <https://github.com/shimizukawa/scrap2rst/issues/12>`_: option: sphinx style internal links

  * ``--sphinx``, ``-s`` option converts scrapbox internal links to `:doc:` role.
  * ``--toctree``, ``-t`` option generates toctree directive for scrapbox internal links.

- `#3 <https://github.com/shimizukawa/scrap2rst/issues/3>`_: notation: links

- `#6 <https://github.com/shimizukawa/scrap2rst/issues/6>`_: notation: code block


0.1.1 (2019-08-10)
==================

* update trove classifiers

0.1.0 (2019-08-10)
==================

The first release of scrap2rst.

Support features:

* Page header
* Heading level2 if the line is strong text.
* Figure if the line is link to image.
* Image if the line contains link to image.
* Link if the line contains link excluding to image url.

Still many limitation are exist.


0.0.0 (2019-06-22)
==================

Zero feature release.

