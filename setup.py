import os
import sys

from setuptools import setup, find_packages


setup(
    name='Python Media Center',
    version='2.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pymediacenter=PyMediaCenter.mediaCenter:main',
        ]
    }
)

