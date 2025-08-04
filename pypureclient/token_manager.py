import jwt
import time
import uuid
import json

from io import StringIO
from paramiko import RSAKey

from .exceptions import PureError
from .keywords import Headers

from ._helpers import create_api_client

from ._transport.rest import ApiException
from ._transport.configuration import Configuration

class TokenManager(object):
    """
    A TokenManager is to handle authentication for API calls internally.
    It accepts an app ID and private key to be able to generate an internal ID
    token. Alternatively, the ID token itself can be provided.
    A valid access token is stored in memory and on disk. When an access token
    is expired, a new one is retrieved. Access tokens on disk are reused when
    a new TokenManager is instantiated.
    """
    ALGORITHM = 'RS256'
    EXP_TIME_IN_SECONDS = 315360000  # 10 years

    def __init__(self,
                 configuration: Configuration,
                 token_endpoint: str = '/oauth2/1.0/token',
                 id_token = None,
                 private_key_file = None,
                 private_key_password=None,
                 payload=None,
                 headers=None,
                 timeout=None,
                 user_agent=None):
        """
        Initialize a TokenManager. Should be treated as a static object.

        Args:
            token_endpoint (str): URL to POST to for exchanging an ID token for
                an access token.
            id_token (str, optional): The ID token to use rather than creating
                one. If expired, all requests to get an access token will fail.
                Required if app ID and private key information not given.
            private_key_file (str, optional): Filepath to the private key that
                matches the public key used to register the app ID.
            private_key_password (str, optional): Password to the private key
                file, if encrypted.
            payload (dict): a dictionary that contains key-values for JSON Web
                Token claims, like iss(issuer), aud(audience), etc.
            headers (dict): a dictionary that contains key-values for JSON Web
                Token header.

        Raises:
            PureError: If there was any issue generating an ID token or
                retrieving an access token.
        """
        # Verify we can either create an ID token or use a given one
        self._configuration = configuration
        self._token_endpoint = token_endpoint
        self._access_token_file = ('{}.access_token'
                                   .format(self._token_endpoint.replace('/', '')))
        self._access_token = None
        self._timeout = timeout
        self._user_agent = user_agent
        # If we already have an ID token, just use that
        if id_token is not None:
            self._id_token = id_token
        else:
            private_key = self._get_private_key(private_key_file, private_key_password)
            self._id_token = self._generate_id_token(headers, payload, private_key)
        self.get_access_token(refresh=True)

    def _generate_id_token(self, headers, payload, private_key):
        _payload_to_encode = dict(payload) if payload else {}
        _now = int(time.time())
        _payload_to_encode['iat'] = _now
        _payload_to_encode['exp'] = _now + self.EXP_TIME_IN_SECONDS
        new_jwt = jwt.encode(_payload_to_encode, private_key, algorithm=self.ALGORITHM, headers=headers)
        return new_jwt if isinstance(new_jwt, str) else new_jwt.decode()

    def _get_private_key(self, private_key_file, private_key_password):
        try:
            rsa_key = RSAKey.from_private_key_file(private_key_file, private_key_password)
        except:
            # todo: https://github.com/PureStorage-OpenConnect/py-pure-client/issues/124
            #  py-pure-client shouldn't swallow original error here to provide better understanding what is wrong
            raise PureError('Could not read private key file')
        with StringIO() as buf:
            rsa_key.write_private_key(buf)
            private_key = buf.getvalue()
        return private_key

    def get_access_token(self, refresh=False):
        """
        Get the last used access token. Tries to read from memory, read from
        disk, or retrieve a new one, in that order.

        Args:
            refresh (bool, optional): Whether to retrieve a new access token.
                Defaults to False.

        Returns:
            str

        Raises:
            PureError: If there was an error retrieving an access token.
        """
        if refresh:
            return self._refresh_access_token()
        if self._access_token is None:
            return self._load_cached_access_token()
        if self._is_token_expired():
            return self._refresh_access_token()
        return self._access_token

    def get_header(self, refresh=False):
        """
        Get the bearer Authorization header.

        Args:
            refresh (bool, optional): Whether to retrieve a new access token.
                Defaults to False.

        Returns:
            str

        Raises:
            PureError: If there was an error retrieving an access token.
        """
        return 'Bearer {}'.format(self.get_access_token(refresh=refresh))

    def _load_cached_access_token(self):
        """
        Load the access token saved in a file. If reading fails or the access
        token is expired, a new one is retrieved.

        Returns:
            str

        Raises:
            PureError: If there was an error retrieving an access token.
        """
        try:
            with open(self._access_token_file, 'r') as token_file:
                self._access_token = token_file.read().strip()
        except:
            self._refresh_access_token()
        if self._is_token_expired():
            return self._refresh_access_token()
        return self._access_token

    def _refresh_access_token(self):
        """
        Retrieve an access token and save it in memory and on disk.

        Returns:
            str

        Raises:
            PureError: If there was an error retrieving an access token.
        """
        self._access_token = self._request_access_token()
        with open(self._access_token_file, 'w+') as token_file:
            token_file.write(self._access_token)
        return self._access_token

    def _request_access_token(self):
        """
        Retrieve an access token from the token exchange endpoint.

        Returns:
            str

        Raises:
            PureError: If there was an error retrieving an access token.
        """
        post_data = {'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
                     'subject_token_type': 'urn:ietf:params:oauth:token-type:jwt',
                     'subject_token': self._id_token}
        headers = {
            Headers.x_request_id: str(uuid.uuid4()),
            'Content-Type': 'application/x-www-form-urlencoded',
            'accept': 'application/json',
        }
        try:
            with create_api_client(self._configuration, self._user_agent) as api_client:
                response_data = api_client.call_api(
                                    resource_path=self._token_endpoint,
                                    method="POST",
                                    header_params=headers,
                                    post_params=post_data,
                                    response_types_map = {'200': "bytearray"},
                                    _return_http_data_only=True,
                                    _request_timeout=self._timeout
                                )
                response = json.loads(response_data.decode("utf-8"))
                if 'access_token' in response:
                    return response['access_token']
                elif 'items' in response:
                    return response['items'][0]['access_token']
                else:
                    raise PureError('Unable to parse response. {}'.format(response_data))
        except ApiException:
            raise PureError('Could not retrieve a new access token')

    def _is_token_expired(self):
        """
        Verify whether the access token is expired.

        Returns:
            bool

        Raises:
            PureError: If there was an error decoding the access token.
        """
        try:
            jwt_claims = jwt.decode(self._access_token.encode(),
                                    algorithms=self.ALGORITHM,
                                    options={
                                        'verify_signature': False,
                                        'verify_exp': False,
                                        'verify_nbf': False,
                                        'verify_iat': False,
                                        'verify_aud': False
                                    })
        except:
            return True
        return jwt_claims['exp'] <= int(time.time())
