# coding: utf-8
# flake8: noqa

'''
Pure Storage Python clients for FlashArray, FlashBlade, and Pure1 APIs
'''
import sys

from setuptools import setup, find_packages  # noqa: H301

NAME = 'py-pure-client'
VERSION = '1.73.1'

REQUIRES = [
    'certifi >= 2024.07.04',
    'python_dateutil >=2.8.2',
    'setuptools >=70.0.0',
    'urllib3 >= 1.26.17',
    'paramiko >= 3.4.0',
    'pyjwt >=2.0.0',
    'pydantic >= 1.10.14',
    'aenum >= 3.1.15'
]

readme = open('README.md', 'r')
README_TEXT = readme.read()
readme.close()

setup(
    name=NAME,
    version=VERSION,
    description='Pure Storage Python clients for FlashArray, FlashBlade, and Pure1 APIs',
    author='Pure Storage',
    author_email='openconnect@purestorage.com',
    url='https://github.com/PureStorage-OpenConnect/py-pure-client',
    download_url='https://github.com/PureStorage-OpenConnect/py-pure-client/archive/1.73.1.tar.gz',
    keywords=['Swagger', 'Pure Storage', 'Python', 'clients', 'REST', 'API', 'FlashArray', 'FlashBlade', 'Pure1'],
    license='BSD 2-Clause',
    license_files = ('LICENSE.txt',),
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description=README_TEXT,
    long_description_content_type='text/markdown',
    package_data={"": ["py.typed"]},
)
