from distutils.core import setup
from setuptools import find_packages
import os
import json

setup(
    name='tactile',
    version='0.1',
    description='Control experimental devices with MIDI controllers',
    author='Robert Fasano',
    author_email='robert.j.fasano@colorado.edu',
    packages=find_packages(exclude=['docs']),
    license='MIT',
    long_description=open('README.md').read(),
    install_requires=['pygame']
)


