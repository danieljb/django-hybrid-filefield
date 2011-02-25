#!/usr/bin/env python

from distutils.core import setup

setup(
    name='hybrid_filefield',
    version='0.2.0',
    description='A combination of Django\'s FileField and FilePathField.',
    long_description=open('README.md').read(),
    author='Daniel J. Becker',
    url='http://github.com/danieljb/django-hybrid-filefield',
    packages=('hybrid_filefield',),
    license='GPL',
)