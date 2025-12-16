import importlib

from .__modules_dict import __modules_dict as pure1_modules_dict
from ..properties import Property


pure1_modules = {}


DEFAULT_VERSION = sorted(pure1_modules_dict.keys())[-1]

VERSION_KEY = 'version'

def Client(**kwargs):
    """
    Initialize a Pure1 Client.

    Keyword args:
        version (str, optional):
            REST API version to use. Defaults to the most recent version.
        app_id (str, optional): The registered App ID for Pure1 to use.
            Defaults to the set environment variable under PURE1_APP_ID.
        id_token (str, optional): The ID token to use. Overrides given
            App ID and private key. Defaults to environment variable set
            under PURE1_ID_TOKEN.
        private_key_file (str, optional): The path of the private key to
            use. Defaults to the set environment variable under
            PURE1_PRIVATE_KEY_FILE.
        private_key_password (str, optional): The password of the private
            key, if encrypted. Defaults to the set environment variable
            under PURE1_PRIVATE_KEY_FILE. Defaults to None.
        retries (int, optional): The number of times to retry an API call if
            it failed for a non-blocking reason. Defaults to 5.
        timeout (float or (float, float), optional): The timeout
            duration in seconds, either in total time or (connect and read)
            times. Defaults to 15.0 total.
        model_attribute_error_on_none (bool, optional):
            Controls model instance behaviour with regard to accessing attributes with None value.
            raise an AttributeError if attribute value is None, otherwise returns None.
            Defaults to True for backward compatibility with older versions of the SDK.

    Raises:
        PureError: If it could not create an ID or access token
    """
    version = (kwargs.get(VERSION_KEY)
                if VERSION_KEY in kwargs
                else DEFAULT_VERSION)
    pure1_module = version_to_module(version)
    setattr(pure1_module, '_attribute_error_on_none', kwargs.get('model_attribute_error_on_none', True))
    client = pure1_module.Client(**kwargs)
    return client


def version_to_module(version):
    if version not in set(pure1_modules_dict.keys()):
        msg = "version {} not supported".format(version)
        raise ValueError(msg.format(version))
    if version not in set(pure1_modules.keys()):
        pure1_modules[version] = importlib.import_module(pure1_modules_dict[version])
    pure1_module = pure1_modules.get(version, None)
    return pure1_module
