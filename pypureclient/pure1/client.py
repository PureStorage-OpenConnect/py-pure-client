import os
import importlib

from typing import Union, Tuple

from .__modules_dict import __modules_dict as pure1_modules_dict
from .._version import __default_user_agent__
from .._helpers import create_transport_config
from ..configuration import Configuration


pure1_modules = {}


__DEFAULT_VERSION = sorted(pure1_modules_dict.keys())[-1]
__APP_ID_ENV = 'PURE1_APP_ID'
__ID_TOKEN_ENV = 'PURE1_ID_TOKEN'
__PRIVATE_KEY_FILE_ENV = 'PURE1_PRIVATE_KEY_FILE'
__PRIVATE_KEY_PASSWORD_ENV = 'PURE1_PRIVATE_KEY_PASSWORD'
__RETRIES_DEFAULT = 5
__TIMEOUT_DEFAULT = 15.0

def Client(
    version: str = __DEFAULT_VERSION,
    app_id: str = None,
    id_token: str = None,
    private_key_file: str = None,
    private_key_password: str = None,
    retries: int = __RETRIES_DEFAULT,
    timeout: Union[int, Tuple[float, float]] = __TIMEOUT_DEFAULT,
    configuration: Configuration = None,
    model_attribute_error_on_none: bool = True):
    """
    Initialize a Pure1 Client.

    :type version: str, optional
    :param version: REST API version to use. Defaults to the most recent version.

    :param app_id: The registered App ID for Pure1 to use.
        Defaults to the set environment variable under PURE1_APP_ID.
    :type app_id: str, optional

    :param id_token: The ID token to use. Overrides given
        App ID and private key. Defaults to environment variable set
        under PURE1_ID_TOKEN.
    :type id_token: str, optional

    :param private_key_file: The path of the private key to
        use. Defaults to the set environment variable under
        PURE1_PRIVATE_KEY_FILE.
    :type private_key_file: str, optional

    :param private_key_password: The password of the private
        key, if encrypted. Defaults to the set environment variable
        under PURE1_PRIVATE_KEY_PASSWORD. Defaults to None.
    :type private_key_password: str, optional

    :param retries: The number of times to retry an API call if
        it failed for a non-blocking reason. Defaults to 5.
    :type retries: int, optional

    :param timeout: The timeout
        duration in seconds, either in total time or (connect and read)
        times. Defaults to 15 total.
    :type timeout: int or (float, float), optional

    :param configuration: configuration object to use.
    :type configuration: Configuration, optional

    :param model_attribute_error_on_none: Controls model instance behaviour
        with regard to accessing attributes with None value.
        raise an AttributeError if attribute value is None, otherwise returns None.
        Defaults to True for backward compatibility with older versions of the SDK.
    :type model_attribute_error_on_none: bool, optional

    :raises PureError: If it could not create an ID or access token
    """
    pure1_module = __version_to_module(version or __DEFAULT_VERSION)
    setattr(pure1_module, '_attribute_error_on_none', model_attribute_error_on_none)
    client = pure1_module.Client(
                    configuration=create_transport_config(target='api.pure1.purestorage.com', configuration=configuration, ssl_cert=None, verify_ssl=None),
                    app_id=__arg_value_or_env(app_id, __APP_ID_ENV),
                    private_key_file=__arg_value_or_env(private_key_file, __PRIVATE_KEY_FILE_ENV),
                    private_key_password=__arg_value_or_env(private_key_password, __PRIVATE_KEY_PASSWORD_ENV),
                    id_token=__arg_value_or_env(id_token, __ID_TOKEN_ENV),
                    timeout=timeout or __TIMEOUT_DEFAULT,
                    retries=retries or __RETRIES_DEFAULT,
                    user_agent=__default_user_agent__)
    return client


def __version_to_module(version):
    if version not in set(pure1_modules_dict.keys()):
        msg = "version {} not supported".format(version)
        raise ValueError(msg.format(version))
    if version not in set(pure1_modules.keys()):
        pure1_modules[version] = importlib.import_module(pure1_modules_dict[version])
    pure1_module = pure1_modules.get(version, None)
    return pure1_module


def __arg_value_or_env(arg_value, env_variable_name):
    return arg_value if arg_value is not None else os.getenv(env_variable_name)
