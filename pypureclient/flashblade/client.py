import requests

from . import PureError

from . import FB_2_2
from . import FB_2_3
from . import FB_2_1
from . import FB_2_0

fb_modules = {
    '2.2': FB_2_2,
    '2.3': FB_2_3,
    '2.1': FB_2_1,
    '2.0': FB_2_0,
}

MW_DEV_VERSION = '2.latest'

DEFAULT_TIMEOUT = 15.0
DEFAULT_RETRIES = 5


def Client(target, version=None, id_token=None, private_key_file=None, private_key_password=None,
           username=None, client_id=None, key_id=None, issuer=None, api_token=None,
           retries=DEFAULT_RETRIES, timeout=DEFAULT_TIMEOUT, ssl_cert=None, user_agent=None):
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

    Raises:
        PureError: If it could not create an ID or access token
    """
    array_versions = get_array_versions(target)
    if version is not None:
        validate_version(array_versions, version)
    else:
        version = choose_version(array_versions)
    fb_module = version_to_module(version)
    client = fb_module.Client(target=target, id_token=id_token, private_key_file=private_key_file,
                              private_key_password=private_key_password, username=username, client_id=client_id,
                              key_id=key_id, issuer=issuer, api_token=api_token, retries=retries, timeout=timeout,
                              ssl_cert=ssl_cert, user_agent=user_agent)
    return client


def get_array_versions(target):
    url = 'https://{}/api/api_version'.format(target)
    response = requests.get(url, verify=False)
    if response.status_code == requests.codes.ok:
        return response.json()['versions']
    else:
        raise PureError("Failed to retrieve supported REST versions from target array {}. status code: {}, error: {}"
                        .format(target, response.status_code, response.text))


def validate_version(array_versions, version):
    if str(version).lower() == MW_DEV_VERSION and MW_DEV_VERSION in fb_modules.keys():
        return
    if version not in set(fb_modules.keys()):
        msg = "version {} not supported by client.".format(version)
        raise ValueError(msg.format(version))
    if version not in array_versions:
        msg = "version {} not supported by array."
        raise ValueError(msg.format(version))


def choose_version(array_versions):
    client_versions = set(fb_modules.keys())
    for version in array_versions[::-1]:
        if version in client_versions:
            return version
    raise ValueError("No compatible REST version found between the client SDK and the target array.")


def version_to_module(version):
    fb_module = fb_modules.get(version, None)
    return fb_module
