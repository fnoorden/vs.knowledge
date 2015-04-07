# -*- coding: utf-8 -*-
"""Installer for the vs.knowledge package."""

from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt') +
    read('docs', 'CHANGELOG.txt') +
    read('docs', 'LICENSE.txt'))

setup(
    name='vs.knowledge',
    version='0.1',
    description="Knowledge Profiles",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='Python Zope Plone VirtualSciences',
    author='Virtual Sciences',
    author_email='info@virtualsciences.nl',
    url='https://github.com/virtualsciences/vs.knowledge',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['vs'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
    )