import requests
import uuid

from typing import Union, Tuple
from .keywords import Headers


def resolve_ssl_validation(verify_ssl):
    """
        Translates verify_ssl parameter of py-pure-client to verify parameter of the requests package
    """
    return verify_ssl if verify_ssl is not None else False


def get_target_versions(target, target_type, key_to_check, verify_ssl=None, timeout: Union[int, Tuple[float, float]]=None):
    from ._version import __default_user_agent__
    from . import PureError
    url = 'https://{target}/api/api_version'.format(target=target)
    response = requests.get(url,
                            timeout=timeout,
                            verify=resolve_ssl_validation(verify_ssl),
                            headers={
                                Headers.user_agent: __default_user_agent__,
                                Headers.x_request_id: str(uuid.uuid4())}
                            )
    if response.status_code == requests.codes.ok:
        data = response.json()
        if key_to_check in data:
            return data[key_to_check]
        else:
            raise PureError("Failed to retrieve '{}' from response ('{}').\nPlease make sure {} is {}.".format(key_to_check, data, target, target_type))
    else:
        raise PureError("Failed to retrieve supported REST versions from target array {}. status code: {}, error: {}"
                        .format(target, response.status_code, response.text))
