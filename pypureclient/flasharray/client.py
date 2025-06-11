import importlib
from typing import Union, Tuple

from .__modules_dict import __modules_dict as fa_modules_dict
from ..client_settings import resolve_ssl_validation, get_target_versions

fa_modules = {}

MW_DEV_VERSION = '2.DEV'
CLIENT_DEV_VERSION = '2.X'

DEFAULT_RETRIES = 5


def Client(target, version=None, id_token=None, private_key_file=None, private_key_password=None,
           username=None, client_id=None, key_id=None, issuer=None, api_token=None,
           retries=DEFAULT_RETRIES, timeout=None, ssl_cert=None, user_agent=None,
           verify_ssl=None, model_attribute_error_on_none: bool = True):
    """
    Initialize a FlashArray Client.

    Keyword args:
        target (str, required):
            The target array's IP or hostname.
        version (str, optional):
            REST API version to use. Defaults to the most recent version
            supported by both the client and the target array.
        id_token (str, optional):
            The security token that represents the identity of the party on
            behalf of whom the request is being made, issued by an enabled
            API client on the array. Overrides given private key.
        private_key_file (str, optional):
            The path of the private key to use. Defaults to None.
        private_key_password (str, optional):
            The password of the private key. Defaults to None.
        username (str, optional):
            Username of the user the token should be issued for. This must
            be a valid user in the system.
        client_id (str, optional):
            ID of API client that issued the identity token.
        key_id (str, optional):
            Key ID of API client that issued the identity token.
        issuer (str, optional):
            API client's trusted identity issuer on the array.
        api_token (str, optional):
            API token for the user.
        retries (int, optional):
            The number of times to retry an API call if it fails for a
            non-blocking reason. Defaults to 5.
        timeout int or (float, float), optional:
            The timeout duration in seconds, either in total time or
            (connect and read) times. Defaults to None.
        ssl_cert (str, optional):
            SSL certificate to use. Defaults to None.
        user_agent (str, optional):
            User-Agent request header to use.
        verify_ssl (bool | str, optional):
            Controls SSL certificate validation.
            `True` specifies that the server validation uses default trust anchors;
            `False` switches certificate validation off, **not safe!**;
            It also accepts string value for a path to directory with certificates.
        model_attribute_error_on_none (bool, optional):
            Controls model instance behaviour with regard to accessing attributes with None value.
            raise an AttributeError if attribute value is None, otherwise returns None.
            Defaults to True for backward compatibility with older versions of the SDK.

    Raises:
        PureError: If it could not create an ID or access token
    """
    array_versions = get_array_versions(target, verify_ssl, timeout)
    if version is not None:
        version = validate_version(array_versions, version)
    else:
        version = choose_version(array_versions)

    fa_module = version_to_module(version)
    setattr(fa_module, '_attribute_error_on_none', model_attribute_error_on_none)
    client = fa_module.Client(target=target, id_token=id_token, private_key_file=private_key_file,
                              private_key_password=private_key_password, username=username, client_id=client_id,
                              key_id=key_id, issuer=issuer, api_token=api_token, retries=retries, timeout=timeout,
                              ssl_cert=ssl_cert, user_agent=user_agent, verify_ssl=resolve_ssl_validation(verify_ssl))
    return client

def get_array_versions(target, verify_ssl=None, timeout: Union[int, Tuple[float, float]]=None):
    return get_target_versions(target, 'flasharray', 'version', verify_ssl, timeout)

def validate_version(array_versions, version):
    if version == MW_DEV_VERSION:
        version = CLIENT_DEV_VERSION
    if version not in set(fa_modules_dict.keys()):
        msg = "version {} not supported by client.".format(version)
        raise ValueError(msg.format(version))
    if version not in array_versions:
        msg = "version {} not supported by array."
        raise ValueError(msg.format(version))
    return version

def choose_version(array_versions):
    client_versions = set(fa_modules_dict.keys())
    for version in array_versions[::-1]:
        if version.upper() == MW_DEV_VERSION:
            version = CLIENT_DEV_VERSION
        if version in client_versions:
            return version
    raise ValueError(f"No compatible REST version found between the client SDK and the target array.\n"
                     f"Client SDK versions: {[v for v in client_versions]}\n"
                     f"Target array versions: {array_versions}")

def version_to_module(version):
    if version not in set(fa_modules.keys()):
        fa_modules[version] = importlib.import_module(fa_modules_dict[version])
    fa_module = fa_modules.get(version, None)
    return fa_module
