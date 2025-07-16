import uuid
import json

from typing import Union, Tuple, Optional

from .keywords import Headers
from .exceptions import PureError
from ._version import __default_user_agent__
from .configuration import Configuration

from ._transport.exceptions import ApiException
from ._transport.api_client import ApiClient
from ._transport.configuration import Configuration as _TransportConfiguration


def create_transport_config(target: str, configuration: Configuration, ssl_cert: Optional[str], verify_ssl: Optional[bool]) -> _TransportConfiguration:
    _transport_configuration = _TransportConfiguration.based_on(configuration)
    _transport_configuration.host = 'https://{}'.format(target)
    if verify_ssl is not None:
        _transport_configuration.verify_ssl = verify_ssl
    elif _transport_configuration.verify_ssl is None:
        # legacy, if both verify_ssl is set to None (meaning unset), we're falling back to the legacy default
        _transport_configuration.verify_ssl = False
    if ssl_cert:
        _transport_configuration.ssl_cert = ssl_cert
    return _transport_configuration


def create_api_client(configuration: Configuration, user_agent: str, _models_package = None) -> ApiClient:
    _api_client = ApiClient(configuration=configuration, models_package=_models_package)
    _api_client.user_agent = user_agent or __default_user_agent__
    return _api_client


def get_target_versions(configuration: Configuration, target_type, key_to_check, user_agent: str = None, timeout: Union[int, Tuple[float, float]]=None):
    try:
        with create_api_client(configuration=configuration, user_agent=user_agent) as _client:
            _response_data = _client.call_api(
                                '/api/api_version',
                                'GET',
                                header_params={Headers.x_request_id: str(uuid.uuid4())},
                                response_types_map = {'200': "bytearray"},
                                _request_timeout=timeout,
                                _return_http_data_only=True)
            _data = json.loads(_response_data)
            if key_to_check in _data:
                return _data[key_to_check]
            else:
                raise PureError("Failed to retrieve '{}' from response ('{}').\nPlease make sure {} is {}.".format(key_to_check, _data, configuration.host, target_type))
    except ApiException as e:
        raise PureError("Failed to retrieve supported REST versions from target array {}. status code: {}, error: {}"
                        .format(configuration.host, e.status, e.body))
