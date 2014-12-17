#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup

setup(
    name = "rod",
    packages = ["rod"],
    version = "0.141217.1",
    description = "Redis Object Database",
    author = "João Santos",
    author_email = "jmcs@jsantos.eu",
    url = "https://github.com/jmcs/redis-object-database",
    install_requires=["redis"],
    keywords = ["redis"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description = """\
Redis Object Database
---------------------

Use Redis as a python object database.
"""
)
