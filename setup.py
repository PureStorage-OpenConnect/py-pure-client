# coding: utf-8
# flake8: noqa

'''
Pure Storage Python clients for FlashArray, FlashBlade, and Pure1 APIs
'''
import sys

from setuptools import setup, find_packages  # noqa: H301

NAME = 'py-pure-client'
VERSION = '1.50.0'

REQUIRES = [
    'certifi >=2022.9.24',
    'six >=1.10',
    'python_dateutil >=2.5.3',
    'setuptools >=21.0.0',
    'urllib3 >= 1.26.17',
    'paramiko >=2.11.0',
    'pyjwt >=2.0.0',
    'requests >=2.20.1',
    ]

if sys.version_info < (3, 5):
    REQUIRES.append('typing >=3.7.4.1, <= 3.7.4.3')

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
    download_url='https://github.com/PureStorage-OpenConnect/py-pure-client/archive/1.50.0.tar.gz',
    keywords=['Swagger', 'Pure Storage', 'Python', 'clients', 'REST', 'API', 'FlashArray', 'FlashBlade', 'Pure1'],
    license='BSD 2-Clause',
    license_files = ('LICENSE.txt',),
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description=README_TEXT,
    long_description_content_type='text/markdown'
)
