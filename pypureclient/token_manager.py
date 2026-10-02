import json
import time
import uuid

import jwt
from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_ssh_private_key

from ._helpers import create_api_client
from ._rate_limit import call_with_rate_limit_retries
from ._transport.configuration import Configuration
from ._transport.rest import ApiException
from .exceptions import PureError
from .keywords import Headers


class TokenManager:
    """
    A TokenManager is to handle authentication for API calls internally.
    It accepts an app ID and private key to be able to generate an internal ID
    token. Alternatively, the ID token itself can be provided.
    A valid access token is stored in memory and on disk. When an access token
    is expired, a new one is retrieved. Access tokens on disk are reused when
    a new TokenManager is instantiated.
    """

    ALGORITHM = "RS256"
    EXP_TIME_IN_SECONDS = 315360000  # 10 years

    def __init__(
        self,
        configuration: Configuration,
        token_endpoint: str = "/oauth2/1.0/token",
        id_token=None,
        private_key_file=None,
        private_key_password=None,
        payload=None,
        headers=None,
        timeout=None,
        user_agent=None,
    ):
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
        self._access_token_file = "{}.access_token".format(self._token_endpoint.replace("/", ""))
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
        _payload_to_encode = dict({k: v for k, v in payload.items() if v is not None}) if payload else {}
        _now = int(time.time())
        _payload_to_encode["iat"] = _now
        _payload_to_encode["exp"] = _now + self.EXP_TIME_IN_SECONDS
        new_jwt = jwt.encode(_payload_to_encode, private_key, algorithm=self.ALGORITHM, headers=headers)
        return new_jwt if isinstance(new_jwt, str) else new_jwt.decode()

    def _get_private_key(self, private_key_file, private_key_password):
        if private_key_file is None:
            raise PureError("Either an id_token or a private_key_file must be provided")
        try:
            with open(private_key_file, "rb") as file:
                key_data = file.read()
        except OSError as error:
            raise PureError(f"Could not read private key file {private_key_file}: {error}") from error
        password = private_key_password.encode() if isinstance(private_key_password, str) else private_key_password
        password = password or None  # an empty password means the key is not encrypted

        if b"-----BEGIN OPENSSH PRIVATE KEY-----" in key_data:
            loader, key_format = load_ssh_private_key, "OpenSSH"
        elif b"-----BEGIN" in key_data:
            loader, key_format = load_pem_private_key, "PEM"
        else:
            raise PureError(f"Could not load private key {private_key_file}: not a PEM or OpenSSH key")

        try:
            private_key = loader(key_data, password=password)
        except TypeError as error:
            # cryptography raises TypeError on a password mismatch
            hint = (
                "key is encrypted but no private_key_password was provided"
                if password is None
                else "a private_key_password was provided but the key is not encrypted"
            )
            raise PureError(f"Could not load {key_format} private key {private_key_file}: {hint}") from error
        except UnsupportedAlgorithm as error:
            raise PureError(
                f"Could not load {key_format} private key {private_key_file}: "
                f"unsupported algorithm or encryption: {error}"
            ) from error
        except ValueError as error:
            raise PureError(
                f"Could not load {key_format} private key {private_key_file}: "
                f"malformed or corrupt key data: {error}"
            ) from error
        if not isinstance(private_key, rsa.RSAPrivateKey):
            raise PureError(
                f"Private key {private_key_file} is not an RSA key (got {type(private_key).__name__}); "
                f"{self.ALGORITHM} requires an RSA private key"
            )
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
        return f"Bearer {self.get_access_token(refresh=refresh)}"

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
            with open(self._access_token_file, "r") as token_file:
                self._access_token = token_file.read().strip()
        except OSError:
            return self._refresh_access_token()
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
        with open(self._access_token_file, "w+") as token_file:
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
        post_data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
            "subject_token": self._id_token,
        }
        headers = {
            Headers.x_request_id: str(uuid.uuid4()),
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "application/json",
        }
        try:
            with create_api_client(self._configuration, self._user_agent) as api_client:
                response_data = call_with_rate_limit_retries(lambda: api_client.call_api(
                    resource_path=self._token_endpoint,
                    method="POST",
                    header_params=headers,
                    post_params=post_data,
                    response_types_map={"200": "bytearray"},
                    _return_http_data_only=True,
                    _request_timeout=self._timeout,
                ))
                response = json.loads(response_data.decode("utf-8"))
                if "access_token" in response:
                    return response["access_token"]
                elif "items" in response:
                    return response["items"][0]["access_token"]
                else:
                    raise PureError(f"Unable to parse response. {response_data}")
        except ApiException as error:
            raise PureError(f"Could not retrieve a new access token: {error}") from error

    def _is_token_expired(self):
        """
        Verify whether the access token is expired.

        Returns:
            bool

        Raises:
            PureError: If there was an error decoding the access token.
        """
        try:
            jwt_claims = jwt.decode(
                self._access_token.encode(),
                algorithms=self.ALGORITHM,
                options={
                    "verify_signature": False,
                    "verify_exp": False,
                    "verify_nbf": False,
                    "verify_iat": False,
                    "verify_aud": False,
                },
            )
        except jwt.PyJWTError:
            return True
        return jwt_claims["exp"] <= int(time.time())
