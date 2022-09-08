import jwt
import requests
import time
from io import StringIO
from paramiko import RSAKey

from .exceptions import PureError


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

    def __init__(self, token_endpoint, id_token=None, private_key_file=None,
                 private_key_password=None, payload=None, headers=None, verify_ssl=True):
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
        self._token_endpoint = token_endpoint
        self._access_token_file = ('{}.access_token'
                                   .format(self._token_endpoint.replace('/', '')))
        self._access_token = None
        self._verify_ssl = verify_ssl
        # If we already have an ID token, just use that
        if id_token is not None:
            self._id_token = id_token
        else:
            private_key = self._get_private_key(private_key_file, private_key_password)
            self._id_token = self._generate_id_token(headers, payload, private_key)
        self.get_access_token(refresh=True)

    def _generate_id_token(self, headers, payload, private_key):
        payload['iat'] = int(time.time())
        payload['exp'] = int(time.time()) + self.EXP_TIME_IN_SECONDS
        new_jwt = jwt.encode(payload, private_key, algorithm=self.ALGORITHM, headers=headers)
        return new_jwt if isinstance(new_jwt, str) else new_jwt.decode()

    def _get_private_key(self, private_key_file, private_key_password):
        try:
            rsa_key = RSAKey.from_private_key_file(private_key_file, private_key_password)
        except:
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
        response = requests.post(self._token_endpoint, data=post_data, verify=self._verify_ssl)
        if response:
            try:
                return str(response.json()['access_token'])
            except Exception:
                return str(response.json()['items'][0]['access_token'])
        else:
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
