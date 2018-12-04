import jwt
import requests
import time
from io import StringIO
from paramiko import RSAKey

from pypureclient.pure1.exceptions import PureError


class TokenManager(object):
    '''
    A TokenManager is to handle authentication for API calls internally.
    It accepts an app ID and private key to be able to generate an internal ID
    token. Alternatively, the ID token itself can be provided.
    A valid access token is stored in memory and on disk. When an access token
    is expired, a new one is retrieved. Access tokens on disk are reused when
    a new TokenManager is instantiated.
    '''

    def __init__(self, token_endpoint, app_id=None, private_key_file=None,
                 private_key_password=None, id_token=None):
        '''
        Initialize a TokenManager. Should be treated as a static object.

        Args:
            token_endpoint (str): URL to POST to for exchanging an ID token for
                an access token.
            app_id (str, optional): Pure1 registered app ID to use in the ID
                token.
            private_key_file (str, optional): Filepath to the private key that
                matches the public key used to register the app ID.
            private_key_password (str, optional): Password to the private key
                file, if encrypted.
            id_token (str, optional): The ID token to use rather than creating
                one. If expired, all requests to get an access token will fail.
                Required if app ID and private key information not given.

        Raises:
            PureError: If there was any issue generating an ID token or
                retrieving an access token.
        '''
        # Class constants
        self.ALGORITHM = 'RS256'
        self.EXP_TIME_IN_SECONDS = 315360000 # 10 years
        # Verify we can either create an ID token or use a given one
        if (app_id is None or private_key_file is None) and id_token is None:
            raise PureError('Incomplete authorization information provided')
        self._token_endpoint = token_endpoint
        self._access_token_file = ('{}.access_token'
                                   .format(self._token_endpoint.replace('/', '')))
        self._access_token = None
        # If we already have an ID token, just use that
        if id_token is not None:
            self._id_token = id_token
            self.get_access_token()
            return
        # Read the private key otherwise
        try:
            rsa_key = RSAKey.from_private_key_file(private_key_file,
                                                   private_key_password)
        except:
            raise PureError('Could not read private key file')
        with StringIO() as buf:
            rsa_key.write_private_key(buf)
            private_key = buf.getvalue()
        # Generate and store an ID token
        new_jwt = jwt.encode({'iss': app_id,
                              'iat': int(time.time()),
                              'exp': int(time.time()) + self.EXP_TIME_IN_SECONDS},
                             private_key,
                             algorithm=self.ALGORITHM)
        self._id_token = new_jwt.decode()
        # Get a first access token
        self.get_access_token()

    def get_access_token(self, refresh=False):
        '''
        Get the last used access token. Tries to read from memory, read from
        disk, or retrieve a new one, in that order.

        Args:
            refresh (bool, optional): Whether to retrieve a new access token.
                Defaults to False.

        Returns:
            str

        Raises:
            PureError: If there was an error retrieving an access token.
        '''
        if refresh:
            return self._refresh_access_token()
        if self._access_token is None:
            return self._load_cached_access_token()
        if self._is_expired(self._access_token):
            return self._refresh_access_token()
        return self._access_token

    def get_header(self, refresh=False):
        '''
        Get the bearer Authorization header.

        Args:
            refresh (bool, optional): Whether to retrieve a new access token.
                Defaults to False.

        Returns:
            str

        Raises:
            PureError: If there was an error retrieving an access token.
        '''
        return 'Bearer {}'.format(self.get_access_token(refresh=refresh))

    def _load_cached_access_token(self):
        '''
        Load the access token saved in a file. If reading fails or the access
        token is expired, a new one is retrieved.

        Returns:
            str

        Raises:
            PureError: If there was an error retrieving an access token.
        '''
        try:
            with open(self._access_token_file, 'r') as file:
                self._access_token = file.read().strip()
        except:
            self._refresh_access_token()
        if self._is_expired(self._access_token):
            return self._refresh_access_token()
        return self._access_token

    def _refresh_access_token(self):
        '''
        Retrieve an access token and save it in memory and on disk.

        Returns:
            str

        Raises:
            PureError: If there was an error retrieving an access token.
        '''
        self._access_token = self._request_access_token()
        with open(self._access_token_file, 'w+') as file:
            file.write(self._access_token)
        return self._access_token

    def _request_access_token(self):
        '''
        Retrieve an access token from the token exchange endpoint.

        Returns:
            str

        Raises:
            PureError: If there was an error retrieving an access token.
        '''
        post_data = {'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
                     'subject_token_type': 'urn:ietf:params:oauth:token-type:jwt',
                     'subject_token': self._id_token}
        response = requests.post(self._token_endpoint, data=post_data)
        if response:
            return str(response.json()['access_token'])
        else:
            raise PureError('Could not retreive a new access token')

    def _is_expired(self, token):
        '''
        Verify whether the access token is expired.

        Returns:
            bool

        Raises:
            PureError: If there was an error decoding the access token.
        '''
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
