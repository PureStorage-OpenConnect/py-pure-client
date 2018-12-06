# py-pure-client
Pure Storage Python Clients for Pure1, FlashArray, and FlashBlade APIs.

## Overview

The Python package has clients that use the Pure1, FlashArray, and FlashBlade APIs. Currently, only Pure1 is supported; FlashArray and FlashBlade will be added in the future.

For the current FlashArray client, [see here](https://github.com/PureStorage-OpenConnect/rest-client), and for the current FlashBlade client, [see here](https://github.com/purestorage/purity_fb_python_client).

The Pure1 client gives a simple interface to the Pure1 Manage public API.

## Requirements
The library requires Python 2.7 and higher or Python 3.3 and higher. Third-party libraries are also required.

## Installation

### pip Installation
```
$ pip install py-pure-client
```

### Manual Installation
```
$ git clone https://github.com/PureStorage-OpenConnect/py-pure-client.git
$ cd py-pure-client
$ pip install -r requirements.txt
$ python setup.py install
```

## Documentation
For full documentation, including a quick start guide and examples, see https://py-pure-client.readthedocs.io/en/latest/.
