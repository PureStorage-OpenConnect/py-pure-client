import requests
import importlib


from ..client_settings import resolve_ssl_validation
from . import PureError

fb_modules_dict = {
    '2.10': 'FB_2_10',
    '2.3': 'FB_2_3',
    '2.1': 'FB_2_1',
    '2.7': 'FB_2_7',
    '2.0': 'FB_2_0',
    '2.4': 'FB_2_4',
    '2.2': 'FB_2_2',
    '2.12': 'FB_2_12',
    '2.13': 'FB_2_13',
    '2.15': 'FB_2_15',
    '2.8': 'FB_2_8',
    '2.6': 'FB_2_6',
    '2.14': 'FB_2_14',
    '2.9': 'FB_2_9',
    '2.11': 'FB_2_11',
    '2.5': 'FB_2_5',
}

fb_modules = {}

MW_DEV_VERSION = '2.latest'

DEFAULT_TIMEOUT = 15.0
DEFAULT_RETRIES = 5


def Client(target, version=None, id_token=None, private_key_file=None, private_key_password=None,
           username=None, client_id=None, key_id=None, issuer=None, api_token=None,
           retries=DEFAULT_RETRIES, timeout=DEFAULT_TIMEOUT, ssl_cert=None, user_agent=None,
           verify_ssl=None):
    """
    Initialize a FlashBlade Client.

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
        timeout (float or (float, float), optional):
            The timeout duration in seconds, either in total time or
            (connect and read) times. Defaults to 15.0 total.
        ssl_cert (str, optional):
            SSL certificate to use. Defaults to None.
        user_agent (str, optional):
            User-Agent request header to use.
        verify_ssl (bool | str, optional):
            Controls SSL certificate validation.
            `True` specifies that the server validation uses default trust anchors;
            `False` switches certificate validation off, **not safe!**;
            It also accepts string value for a path to directory with certificates.

    Raises:
        PureError: If it could not create an ID or access token
    """
    array_versions = get_array_versions(target, verify_ssl)
    if version is not None:
        validate_version(array_versions, version)
    else:
        version = choose_version(array_versions)
    fb_module = version_to_module(version)
    client = fb_module.Client(target=target, id_token=id_token, private_key_file=private_key_file,
                              private_key_password=private_key_password, username=username, client_id=client_id,
                              key_id=key_id, issuer=issuer, api_token=api_token, retries=retries, timeout=timeout,
                              ssl_cert=ssl_cert, user_agent=user_agent, verify_ssl=resolve_ssl_validation(verify_ssl))
    return client


def get_array_versions(target, verify_ssl=None):
    url = 'https://{}/api/api_version'.format(target)
    response = requests.get(url, verify=resolve_ssl_validation(verify_ssl))
    if response.status_code == requests.codes.ok:
        return response.json()['versions']
    else:
        raise PureError("Failed to retrieve supported REST versions from target array {}. status code: {}, error: {}"
                        .format(target, response.status_code, response.text))


def validate_version(array_versions, version):
    if str(version).lower() == MW_DEV_VERSION and MW_DEV_VERSION in fb_modules_dict.keys():
        return
    if version not in set(fb_modules_dict.keys()):
        msg = "version {} not supported by client.".format(version)
        raise ValueError(msg.format(version))
    if version not in array_versions:
        msg = "version {} not supported by array."
        raise ValueError(msg.format(version))


def choose_version(array_versions):
    client_versions = set(fb_modules_dict.keys())
    for version in array_versions[::-1]:
        if version in client_versions:
            return version
    raise ValueError("No compatible REST version found between the client SDK and the target array.")


def version_to_module(version):
    if version not in set(fb_modules.keys()):
        parent_module_name = '.'.join(__name__.split('.')[:-1])
        fb_modules[version] = importlib.import_module("{}.{}".format(parent_module_name,fb_modules_dict[version]))
    fb_module = fb_modules.get(version, None)
    return fb_module
