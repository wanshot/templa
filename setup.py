# -*- coding:utf-8 -*-
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="tempra",
    version="0.0.0",
    author="wanshot",
    author_email="",
    description="",
    license="MIT",
    keywords="",
    long_description=read('README.rst'),
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
    packages=['tempra'],
    entry_points={
        'console_scripts': ['tempra = tempra.main:main']
    },
#     install_requires=["argparse", "six"],
#     test_suite="tests",
)
