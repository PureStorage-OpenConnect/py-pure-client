import requests
import importlib

from ..client_settings import resolve_ssl_validation
from . import PureError

fa_modules_dict = {
    '2.5': 'FA_2_5',
    '2.28': 'FA_2_28',
    '2.31': 'FA_2_31',
    '2.4': 'FA_2_4',
    '2.24': 'FA_2_24',
    '2.14': 'FA_2_14',
    '2.17': 'FA_2_17',
    '2.20': 'FA_2_20',
    '2.32': 'FA_2_32',
    '2.2': 'FA_2_2',
    '2.1': 'FA_2_1',
    '2.8': 'FA_2_8',
    '2.15': 'FA_2_15',
    '2.13': 'FA_2_13',
    '2.26': 'FA_2_26',
    '2.21': 'FA_2_21',
    '2.16': 'FA_2_16',
    '2.35': 'FA_2_35',
    '2.27': 'FA_2_27',
    '2.29': 'FA_2_29',
    '2.22': 'FA_2_22',
    '2.11': 'FA_2_11',
    '2.9': 'FA_2_9',
    '2.33': 'FA_2_33',
    '2.34': 'FA_2_34',
    '2.19': 'FA_2_19',
    '2.10': 'FA_2_10',
    '2.7': 'FA_2_7',
    '2.30': 'FA_2_30',
    '2.23': 'FA_2_23',
    '2.36': 'FA_2_36',
    '2.25': 'FA_2_25',
    '2.0': 'FA_2_0',
    '2.6': 'FA_2_6',
    '2.3': 'FA_2_3',
}

fa_modules = {}

MW_DEV_VERSION = '2.DEV'
CLIENT_DEV_VERSION = '2.X'

DEFAULT_RETRIES = 5


def Client(target, version=None, id_token=None, private_key_file=None, private_key_password=None,
           username=None, client_id=None, key_id=None, issuer=None, api_token=None,
           retries=DEFAULT_RETRIES, timeout=None, ssl_cert=None, user_agent=None,
           verify_ssl=None):
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

    Raises:
        PureError: If it could not create an ID or access token
    """
    array_versions = get_array_versions(target, verify_ssl)
    if version is not None:
        version = validate_version(array_versions, version)
    else:
        version = choose_version(array_versions)

    fa_module = version_to_module(version)
    client = fa_module.Client(target=target, id_token=id_token, private_key_file=private_key_file,
                              private_key_password=private_key_password, username=username, client_id=client_id,
                              key_id=key_id, issuer=issuer, api_token=api_token, retries=retries, timeout=timeout,
                              ssl_cert=ssl_cert, user_agent=user_agent, verify_ssl=resolve_ssl_validation(verify_ssl))
    return client

def get_array_versions(target, verify_ssl=None):
    url = 'https://{}/api/api_version'.format(target)
    response = requests.get(url, verify=resolve_ssl_validation(verify_ssl))
    if response.status_code == requests.codes.ok:
        return response.json()['version']
    else:
        raise PureError("Failed to retrieve supported REST versions from target array {}. status code: {}, error: {}"
                        .format(target, response.status_code, response.text))

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
    raise ValueError("No compatible REST version found between the client SDK and the target array.")

def version_to_module(version):
    if version not in set(fa_modules.keys()):
        parent_module_name = '.'.join(__name__.split('.')[:-1])
        fa_modules[version] = importlib.import_module("{}.{}".format(parent_module_name,fa_modules_dict[version]))
    fa_module = fa_modules.get(version, None)
    return fa_module
