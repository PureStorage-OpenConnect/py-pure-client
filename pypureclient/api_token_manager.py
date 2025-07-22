import uuid
import atexit

from .exceptions import PureError
from .keywords import Headers

from ._helpers import create_api_client
from ._transport.api_response import ApiResponse
from ._transport.rest import ApiException
from ._transport.configuration import Configuration


class APITokenManager(object):
    """
    A APITokenManager is to handle api token-based authentication for REST 2.X API
    calls internally.
    A valid session token is stored in memory.
    """

    def __init__(self, api_token, configuration: Configuration, version: str = None, user_agent: str = None, timeout=None):
        """
        Initialize a APITokenManager. Should be treated as a static object.

        Args:
            token_endpoint (str): URL to POST to for exchanging an API token for
                a session token.
            api_token (str): API token for the user.

        Raises:
            PureError: If there was any issue retrieving an session token.
        """
        _base_url = '/api'
        if version:
            _base_url = f'{_base_url}/{version}'
        self._token_endpoint = f'{_base_url}/login'
        self._token_dispose_endpoint = f'{_base_url}/logout'
        self._api_token = api_token
        self._configuration = configuration
        self._user_agent = user_agent
        self._session_token = None
        self._timeout = timeout
        self.get_session_token(refresh=True)
        # Register a function to close the session when the program exits
        atexit.register(self.__close_session_on_exit)

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
        try:
            response = self.__call_endpoint(self._token_endpoint, {Headers.api_token: self._api_token})
            return str(response.headers[Headers.x_auth_token])
        except ApiException as e:
            raise PureError("Failed to retrieve session token with error: {body} ({status})".format(body=e.body, status=e.status))

    def close_session(self):
        """
        Close the session by calling logout endpoint.
        """
        if not (self._token_dispose_endpoint and self._session_token):
            return
        try:
            self.__call_endpoint(self._token_dispose_endpoint, {Headers.x_auth_token: self._session_token})
        except ApiException:
            pass
        finally:
            self._session_token = None

    def __call_endpoint(self, endpoint: str, headers: dict) -> ApiResponse:
        _result = None
        with create_api_client(self._configuration, self._user_agent) as api_client:
            _result = api_client.call_api(
                        endpoint,
                        "POST",
                        header_params={**headers, **{Headers.x_request_id: str(uuid.uuid4())}},
                        response_types_map={'200': "bytearray"},
                        _request_timeout=self._timeout)
        return _result

    def __close_session_on_exit(self):
        try:
            self.close_session()
        except:
            # ignore all exceptions on exit
            pass

    def __del__(self):
        # As some of the resources might be inaccessable when the program exits
        # For details please ref to:
        # https://docs.python.org/3/reference/datamodel.html#object.__del__
        self.__close_session_on_exit()
        if atexit:
            # Avoid calling close_session() again when the program exits for this object
            atexit.unregister(self.__close_session_on_exit)
