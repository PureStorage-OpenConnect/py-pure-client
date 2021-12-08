# coding: utf-8
# flake8: noqa

'''
Pure Storage Python clients for FlashArray, FlashBlade, and Pure1 APIs
'''


from setuptools import setup, find_packages  # noqa: H301

NAME = 'py-pure-client'
VERSION = '1.21.0'

REQUIRES = ['urllib3 == 1.26.5', 'six >= 1.10, <= 1.15.0', 'certifi >= 14.05.14, <= 2020.12.5',
            'python-dateutil >= 2.5.3, <= 2.8.1', 'paramiko == 2.7.1',
            'PyJWT >= 1.7.1, < 2.0.0', 'requests >= 2.20.1, <= 2.25.1', 'typing >=3.7.4.1, <= 3.7.4.3']

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
    download_url='https://github.com/PureStorage-OpenConnect/py-pure-client/archive/1.21.0.tar.gz',
    keywords=['Swagger', 'Pure Storage', 'Python', 'clients', 'REST', 'API', 'FlashArray', 'FlashBlade', 'Pure1'],
    license='BSD 2-Clause',
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description=README_TEXT,
    long_description_content_type='text/markdown'
)
