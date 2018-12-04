# py-pure-client
Pure Storage Python Client for Pure1 [and FlashArray, FlashBlade] APIs.

## Capabilities
Currently, only Pure1 is supported. In the future, FlashArray and FlashBlade will be bundled alongside and will mimic the Pure1 interface.

For the current FlashArray client, [see here](https://github.com/PureStorage-OpenConnect/rest-client), and for the current FlashBlade client, [see here](https://github.com/purestorage/purity_fb_python_client).

The Pure1 client gives a simple interface to the Pure1 Manage public API, as [documented here](https://support.purestorage.com/Pure1/Pure1_Manage/Pure1_Manage_-_REST_API/Pure1_Manage_-_REST_API__Reference). The same authorization steps are required to use the Pure1 client as the Pure1 public API.

## Requirements
The library requires Python 2.7 or higher, and supports Python 3. Third-party libraries are also required.

To use the Pure1 client, a valid ID token or private key and app ID pair are required. It is recommended that the private key filepath and app ID are exported as environment variables.

## Installation

### Using pip (coming soon)
`py-pure-client` will soon be published on `pypi` to pip install.

## Manually
After copying or cloning `py-pure-client`, run the following:

```
pip install -r requirements.txt
python setup.py install
```

## Documentation
Documentation will soon be available on [readthedocs](https://readthedocs.org).

## Examples

### Pure1
Setup:
```
export PURE1_APP_ID=[app_id]
export PURE1_PRIVATE_KEY_FILE=[private_key_file]
export PURE1_PRIVATE_KEY_PASSWORD=[password]
```
Python:
```
from pypureclient import pure1

client = pure1.Client()

response = client.get_arrays(filter=pure1.Array.model == 'FlashBlade', sort=pure1.Array.as_of.descending(), limit=10)
if response.status_code != 200:
  print response
flashblades = list(response.items)

response = client.get_file_systems(filter=pure1.Filter.in_(pure1.FileSystem.arrays.any().subproperty(pure1.Array.name), [blade.name for blade in blades]))
if response.status_code != 200:
  print response
attached_file_systems = list(response.items)
```
