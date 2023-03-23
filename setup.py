# coding: utf-8
# flake8: noqa

'''
Pure Storage Python clients for FlashArray, FlashBlade, and Pure1 APIs
'''
import sys

from setuptools import setup, find_packages  # noqa: H301

NAME = 'py-pure-client'
VERSION = '1.33.1'

REQUIRES = [
    'certifi >= 2022.9.24, <= 2022.12.7',
    'six >= 1.10, <= 1.16.0',
    'python-dateutil >= 2.5.3, <= 2.8.1',
    'urllib3 >= 1.26.5, <= 1.26.12',
    'paramiko >= 2.11.0, <= 2.12.0',
    'PyJWT >= 2.0.0, <=2.4.0',
    'requests >= 2.20.1, <= 2.28.1',
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
    author_email='tvilcu@purestorage.com',
    url='https://github.com/PureStorage-OpenConnect/py-pure-client',
    download_url='https://github.com/PureStorage-OpenConnect/py-pure-client/archive/1.33.1.tar.gz',
    keywords=['Swagger', 'Pure Storage', 'Python', 'clients', 'REST', 'API', 'FlashArray', 'FlashBlade', 'Pure1'],
    license='BSD 2-Clause',
    license_files = ('LICENSE.txt',),
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description=README_TEXT,
    long_description_content_type='text/markdown'
)
