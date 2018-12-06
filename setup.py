# coding: utf-8
# flake8: noqa

'''
Pure Storage Python clients for FlashArray, FlashBlade, and Pure1 APIs
'''


from setuptools import setup, find_packages  # noqa: H301

NAME = 'py-pure-client'
VERSION = '1.0.0'

REQUIRES = ['urllib3 >= 1.15', 'six >= 1.10', 'certifi', 'python-dateutil', 'paramiko', 'PyJWT', 'requests']

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
    download_url='https://github.com/PureStorage-OpenConnect/py-pure-client/archive/1.0.0.tar.gz',
    keywords=['Swagger', 'Pure Storage', 'Python', 'clients', 'REST', 'API', 'FlashArray', 'FlashBlade', 'Pure1'],
    license='BSD 2-Clause',
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description=README_TEXT,
    long_description_content_type='text/markdown'
)
