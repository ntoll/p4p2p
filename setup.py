#!/usr/bin/env python
from setuptools import setup, find_packages
from p4p2p.version import get_version

setup(
    name='p4p2p',
    version=get_version(),
    description='A platform for peer-to-peer application development.',
    long_description=open('README.rst').read(),
    author=open('AUTHORS').read(),
    author_email='dev@p4p2p.net',
    url='http://p4p2p.net/',
    package_dir={'': 'p4p2p'},
    packages=find_packages('p4p2p'),
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: No Input/Output (Daemon)',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: System :: Distributed Computing',
    ],
    install_requires=['twisted', ]
)
