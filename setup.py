#!/usr/bin/env python

from distutils.core import setup

setup(
    name='cm-azure',
    version='0.1',
    description='Bright CoD image Azure integration',
    packages=['cmazure'],
    install_requires=[
        "msrest<0.5.0,>=0.4.0",
        "azure==2.0.0rc6"
    ],
    entry_points={
        "console_scripts":
        "cmazure=cmazure.cli:main"
    }
)
