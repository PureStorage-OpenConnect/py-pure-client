import atexit
import requests

from .exceptions import PureError
from .keywords import Headers

class APITokenManager(object):
    """
    A APITokenManager is to handle api token-based authentication for REST 2.X API
    calls internally.
    A valid session token is stored in memory.
    """

    def __init__(self, token_endpoint, api_token, verify_ssl=True, token_dispose_endpoint=None, user_agent=None):
        """
        Initialize a APITokenManager. Should be treated as a static object.

        Args:
            token_endpoint (str): URL to POST to for exchanging an API token for
                a session token.
            api_token (str): API token for the user.

        Raises:
            PureError: If there was any issue retrieving an session token.
        """
        self._token_endpoint = token_endpoint
        self._token_dispose_endpoint = token_dispose_endpoint
        self._api_token = api_token
        self._verify_ssl = verify_ssl
        self._session_token = None
        self._user_agent = user_agent
        self.get_session_token(refresh=True)
        # Register a function to close the session when the program exits
        atexit.register(self.close_session)

    def get_session_token(self, refresh=False):
        """
        Get the last used session token, updates it if needed.

        Args:
            refresh (bool, optional): Whether to retrieve a new session token.
                Defaults to False.

        Returns:
            str

        Raises:
            PureError: If there was an error retrieving an session token.
        """
        if refresh or self._session_token is None:
            self.close_session()
            self._session_token = self._request_session_token()
        return self._session_token

    def _request_session_token(self):
        """
        Retrieve an session token from the API token exchange endpoint.

        Returns:
            str

        Raises:
            PureError: If there was an error retrieving an session token.
        """
        post_headers = {
            Headers.api_token: self._api_token,
            Headers.user_agent: self._user_agent
        }
        response = requests.post(self._token_endpoint, headers=post_headers, verify=self._verify_ssl)
        if response.status_code == requests.codes.ok:
            return str(response.headers[Headers.x_auth_token])
        else:
            raise PureError("Failed to retrieve session token with error: " + response.text)

    def close_session(self):
        """
        Close the session by calling logout endpoint.
        """
        if not (self._token_dispose_endpoint and self._session_token):
            return
        try:
            delete_headers = {
                Headers.x_auth_token: self._session_token,
                Headers.user_agent: self._user_agent
            }
            requests.post(self._token_dispose_endpoint, headers=delete_headers, verify=self._verify_ssl)
            self._session_token = None
        except:
            pass

    def __del__(self):
        # Ignore any exceptions when deleting
        # As some of the resources might be inaccessable when the program exits
        # For details please ref to:
        # https://docs.python.org/3/reference/datamodel.html#object.__del__
        try:
            self.close_session()
            # Avoid calling close_session() again when the program exits for this object
            atexit.unregister(self.close_session)
        except:
            pass