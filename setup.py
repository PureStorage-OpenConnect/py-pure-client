# coding: utf-8
# flake8: noqa

'''
Pure Storage Python clients for FlashArray, FlashBlade, and Pure1 APIs
'''


from setuptools import setup, find_packages  # noqa: H301

NAME = 'pypureclient'
VERSION = '1.0'
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ['urllib3 >= 1.15', 'six >= 1.10', 'certifi', 'python-dateutil']

setup(
    name=NAME,
    version=VERSION,
    description='Pure Storage Python clients',
    author_email='',
    url='',
    keywords=['Swagger', 'Pure Storage Python Clients REST API SDK'],
    install_requires=REQUIRES,
    packages=['pypureclient'],
    include_package_data=True,
    long_description='''\
    Pure Storage Python clients, developed by
    [Pure Storage, Inc.](http://www.purestorage.com/)
    '''
)
