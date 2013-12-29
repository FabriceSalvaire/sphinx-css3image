# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
This package contains the css3image Sphinx extension.

It provides an enhanced image directive.
'''

requires = ['Sphinx>=0.6']

setup(
    name='sphinxcontrib-css3image',
    version='0.1',
    url='http://bitbucket.org/birkenfeld/sphinx-contrib',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-css3image',
    license='LGPL v3',
    author='Fabrice Salvaire',
    author_email='fabrice.salvaire@orange.fr',
    description='Sphinx "css3image" extension',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
