"""
    Author: André Bento
    Date last modified: 26-02-2019
"""
import subprocess
import sys
from os.path import dirname, abspath, join

from setuptools import find_packages, Command, setup
from setuptools.command.test import test as TestCommand

this_dir = abspath(dirname(__file__))

NAME = 'graphy'
VERSION = '0.0.1'

# Readme
with open(join(this_dir, 'README.md'), encoding='utf-8') as file:
    readme = file.read()

# License
with open(join(this_dir, 'LICENSE'), encoding='utf-8') as file:
    license_file = file.read()

# Requirements
with open(join(this_dir, 'requirements.txt')) as file:
    requirements = file.read().splitlines()


class Install(Command):
    user_options = [
        ['pip3', 'install', '-r', 'requirements.txt']
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run_install(self):
        for command in self.user_options:
            subprocess.run(command)


class Run(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print()
        from graphy.app import Graphy
        Graphy.run()


class Test(TestCommand):
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

        err = pytest.main(self.pytest_args)
        sys.exit(err)


setup(
    name=NAME,
    version=VERSION,
    description='A micro-services system monitor command line program in Python.',
    long_description=readme,
    # long_description_content_type='text/markdown',
    url='https://github.com/andrepbento/MScThesis/tree/master/Graphy',
    author='André Bento',
    author_email='apbento@student.dei.uc.pt',
    license=license_file,
    classifiers=[
        # How mature is this project? Common values are
        #   1 - Project setup
        #   2 - Prototype
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 2 - Prototype',
        'Intended Audience :: Developers',
        'Topic :: Observing and Controlling Performance in  Micro-services',
        'License :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='cli',
    packages=find_packages(exclude=('tests*', 'docs')),
    install_requires=requirements,
    tests_require=['pytest'],
    extras_require={
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    cmdclass={
        'install': Install,
        'run': Run,
        'test': Test
    },
)
