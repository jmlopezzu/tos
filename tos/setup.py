# -*- coding: utf-8 -*-

import sys

from setuptools import setup
from setuptools import find_packages

from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


if __name__ == '__main__':
    setup(
        name='tos',
        version='0.0.1',
        packages=find_packages(),
        entry_points={
            'console_scripts': [
                'tosopen = tos.scripts.url_opener:main'
            ]
        },
        install_requires=[
            'sphinx>=1.2.3',
            'sphinx_rtd_theme>=0.1.6',
            'jellyfish>=0.3.2',
            'python-igraph>=0.7'
        ],
        tests_require=[
            'pytest>=2.6.2',
            'pytest-cov>=1.8.0',
        ],
        cmdclass={'test': PyTest},
        author="Oscar David Arbeláez",
        author_email="odarbelaeze@unal.edu.co",
        description="Bibliographic tools and scienciometric analysis"
                    "made easy",
        url="https://bitbucket.org/odarbelaeze/tos"
    )
