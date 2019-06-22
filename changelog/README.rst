This directory contains changes fragment files that contains reST format description.
The name of files msut be ``<ISSUE>.<TYPE>.rst`` for example ``12.bugfix.rst``.

* feature: new/change feature
* bugfix: bug fix without feature changes
* doc: update documentation
* deprecation: changes have DeprecationWarning
* removal: remove feature
* vendor: update vendor packages
* trivial: fix typo or something else

Generating CHANGELOG.rst::

  $ git tag 1.0.0
  $ towncrier  --yes
  $ git add CHANGELOG.rst changelog
  $ git commit -m "update changes"

