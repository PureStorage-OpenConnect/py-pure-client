import importlib
from typing import Union, Tuple

from .__modules_dict import __modules_dict as fb_modules_dict
from .._helpers import create_transport_config, get_target_versions
from ..configuration import Configuration

fb_modules = {}

MW_DEV_VERSION = '2.latest'

DEFAULT_RETRIES = 5


def Client(
    target: str,
    version: str = None,
    id_token: str = None,
    private_key_file: str = None,
    private_key_password: str = None,
    username: str = None,
    client_id: str = None,
    key_id: str = None,
    issuer: str = None,
    api_token: str = None,
    retries: int = DEFAULT_RETRIES,
    timeout: Union[int, Tuple[float, float]] = None,
    ssl_cert: str = None,
    user_agent: str = None,
    verify_ssl: bool = None,
    configuration: Configuration = None):
    """
    Initialize a FlashBlade Client.

    :param target: The target array's IP or hostname.
    :type target: str, required

    :param version: REST API version to use. Defaults to the most recent version
        supported by both the client and the target array.
    :type version: str, optional

    :param id_token: The security token that represents the identity of the party on
        behalf of whom the request is being made, issued by an enabled
        API client on the array. Overrides given private key.
    :type id_token: str, optional

    :param private_key_file: The path of the private key to use. Defaults to None.
    :type private_key_file: str, optional

    :param private_key_password: The password of the private key. Defaults to None.
    :type private_key_password: str, optional

    :param username: Username of the user the token should be issued for. This must
        be a valid user in the system.
    :type username: str, optional

    :param client_id: ID of API client that issued the identity token.
    :type client_id: str, optional

    :param key_id: Key ID of API client that issued the identity token.
    :type key_id: str, optional

    :param issuer: API client's trusted identity issuer on the array.
    :type issuer: str, optional

    :param api_token: API token for the user.
    :type api_token: str, optional

    :param retries: The number of times to retry an API call if it fails for a
        non-blocking reason. Defaults to 5.
    :type retries: int, optional

    :param timeout: The timeout duration in seconds, either in total time or
        (connect and read) times. Defaults to None.
    :type timeout: int or (float, float), optional

    :param ssl_cert: The path to the SSL certificate to use. Defaults to None.
        **Deprecated** in favor of `configuration.ssl_cert`.
        If both `ssl_cert` and `configuration.ssl_cert` are specified, `ssl_cert` overrides `configuration.ssl_cert`
    :type ssl_cert: str, optional

    :param user_agent: User-Agent request header to use.
    :type user_agent: str, optional

    :param verify_ssl: Controls SSL certificate validation.
        `True` specifies that the server validation uses default trust anchors;
        `False` switches certificate validation off, **not safe!**;
        It also accepts string value for a path to directory with certificates.
        **Deprecated** in favor of `configuration.verify_ssl`.
        If both `verify_ssl` and `configuration.verify_ssl` are specified, `verify_ssl` overrides `configuration.verify_ssl`
    :type verify_ssl: bool, optional

    :param configuration: configuration object to use.
    :type configuration: Configuration, optional

    :raises PureError: If it could not create an ID or access token
    """

    _transport_cfg = create_transport_config(target=target, configuration=configuration, ssl_cert=ssl_cert, verify_ssl=verify_ssl)
    array_versions = get_target_versions(configuration=_transport_cfg, target_type='flashblade', key_to_check='versions',
                                            timeout=timeout, user_agent=user_agent)
    if version is not None:
        __validate_version(array_versions, version)
    else:
        version = __choose_version(array_versions)
    fb_module = __version_to_module(version)
    client = fb_module.Client(configuration=_transport_cfg,
                                id_token=id_token, private_key_file=private_key_file,
                                private_key_password=private_key_password, username=username, client_id=client_id,
                                key_id=key_id, issuer=issuer, api_token=api_token, retries=retries, timeout=timeout,
                                user_agent=user_agent)
    return client


def __validate_version(array_versions, version):
    if str(version).lower() == MW_DEV_VERSION and MW_DEV_VERSION in fb_modules_dict.keys():
        return
    if version not in set(fb_modules_dict.keys()):
        msg = "version {} not supported by client.".format(version)
        raise ValueError(msg.format(version))
    if version not in array_versions:
        msg = "version {} not supported by array."
        raise ValueError(msg.format(version))


def __choose_version(array_versions):
    client_versions = list(fb_modules_dict.keys())
    for version in array_versions[::-1]:
        if version in client_versions:
            return version
    raise ValueError(f"No compatible REST version found between the client SDK and the target array.\n"
                     f"Client SDK versions: {client_versions}\n"
                     f"Target array versions: {array_versions}")


def __version_to_module(version):
    if version not in set(fb_modules.keys()):
        fb_modules[version] = importlib.import_module(fb_modules_dict[version])
    fb_module = fb_modules.get(version, None)
    return fb_module


_attribute_error_on_none_value = False