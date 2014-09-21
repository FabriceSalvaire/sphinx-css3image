=============================
 Css3image plugin for Sphinx
=============================

This plugin provides an enhanced ``image`` directive with additional CSS properties for `Sphinx`_
Documentation Generator.

Written by `Fabrice Salvaire <http://fabrice-salvaire.pagesperso-orange.fr>`_.

Installation
------------

See `sphinx-contrib`_ for more details.

To install the plugin, you have to run these commands:

.. code-block:: bash

    python setup.py build
    python setup.py install

The PySpice source code is hosted at https://github.com/FabriceSalvaire/sphinx-css3image

To clone the Git repository, run this command in a terminal:

.. code-block:: sh

  git clone git@github.com:FabriceSalvaire/sphinx-css3image

Usage
-----

To load the plugin, you have to add it in your ``conf.py`` file.

.. code-block:: python

    extensions = [
      ...
      'sphinxcontrib.css3image',
      ]

Directives
----------

This plugin adds a new directive ``css3image`` which is equivalent to the original, but with
additional CSS properties:

  .. code-block:: ReST

    .. css3image:: /_images/foo.png
      :margin: 10px 10px 10px 10px
      :margin-left: 10px
      :margin-right: 10px
      :margin-top: 10px
      :border-radius: 10px
      :transform-origin: 10px 10px
      :translate: 10px 10px
      :translateY: 10px
      :translateX: 10px
      :scaleX: 2.0
      :scaleY: 2.0
      :rotate: -10deg

.. :scale: 2. 2.

Unit is mandatory for length value.

.. .............................................................................

.. _Sphinx: http://sphinx-doc.org
.. _sphinx-contrib:  https://bitbucket.org/birkenfeld/sphinx-contrib

.. End
