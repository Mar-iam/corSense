from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='corsense',
    version='0.0.1',  # Required
    description='An interface to communicate with CorSense device',
    long_description=long_description,  # Optional
    url='https://github.com/mar-iam/corSense',
    author='Mariam',
    author_email='mbahameish@gmail.com',
    keywords='hrv signal corsense',
    py_modules=["corsense"],
)