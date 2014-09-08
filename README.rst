=============================
 Css3image plugin for Sphinx
=============================

This plugin provides an enhanced ``image`` directive with additional CSS properties for `Sphinx`_
Documentation Generator.

Installation
------------

See `sphinx-contrib`_ for more details.

To install the plugin, you have to run these commands:

.. code-block:: bash

    python setup.py build
    python setup.py install

Usage
-----

To load the plugin, you have to add it in your ``conf.py`` file.

.. code-block:: python

    extensions = [
      ...
      'sphinxcontrib.css3image',
      ]

Usage
-----

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
