#!/usr/bin/env python

from distutils.core import setup

setup(
    name='cm-azure',
    version='0.1',
    description='Bright CoD image Azure integration',
    packages=['cmazure'],
    install_requires=["azure"]
)
