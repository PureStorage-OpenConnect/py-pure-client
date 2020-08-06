from . import Pure1_1_0
from . import Pure1_1_1

pure1_modules = {
    '1.0': Pure1_1_0,
    '1.1': Pure1_1_1,
}

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

    Raises:
        PureError: If it could not create an ID or access token
    """
    version = (kwargs.get(VERSION_KEY)
                if VERSION_KEY in kwargs
                else "1.1")
    pure1_module = version_to_module(version)
    client = pure1_module.Client(**kwargs)
    return client


def version_to_module(version):
    pure1_module = pure1_modules.get(version, None)
    if pure1_module is None:
        msg = "version {} not supported".format(version)
        raise ValueError(msg.format(version))
    return pure1_module
