from . import FA_2_0
from . import FA_2_1

fa_modules = {
    '2.0': FA_2_0,
    '2.1': FA_2_1,
}


DEFAULT_TIMEOUT = 15.0
DEFAULT_RETRIES = 5


def Client(target, version="2.1", id_token=None, private_key_file=None, private_key_password=None,
           username=None, client_id=None, key_id=None, issuer=None,
           retries=DEFAULT_RETRIES, timeout=DEFAULT_TIMEOUT, ssl_cert=None):
    """
    Initialize a FlashArray Client.

    Keyword args:
        target (str, required):
            The target array's IP or hostname.
        version (str, optional):
            REST API version to use. Defaults to the most recent version.
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
        retries (int, optional):
            The number of times to retry an API call if it fails for a
            non-blocking reason. Defaults to 5.
        timeout (float or (float, float), optional):
            The timeout duration in seconds, either in total time or
            (connect and read) times. Defaults to 15.0 total.
        ssl_cert (str, optional):
            SSL certificate to use. Defaults to None.

    Raises:
        PureError: If it could not create an ID or access token
    """
    fa_module = version_to_module(version)
    client = fa_module.Client(target=target, id_token=id_token, private_key_file=private_key_file,
                              private_key_password=private_key_password, username=username, client_id=client_id,
                              key_id=key_id, issuer=issuer, retries=retries, timeout=timeout, ssl_cert=ssl_cert)
    return client


def version_to_module(version):
    fa_module = fa_modules.get(version, None)
    if fa_module is None:
        msg = "version {} not supported".format(version)
        raise ValueError(msg.format(version))
    return fa_module
