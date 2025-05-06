import json
import time
import urllib3
import uuid
import warnings

from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import Field, StrictBool, StrictFloat, StrictInt, StrictStr, conint, conlist, constr, validator
from typing_extensions import Annotated

from pypureclient.reference_type import ReferenceType
from pypureclient._version import __default_user_agent__ as DEFAULT_USER_AGENT
from pypureclient.api_token_manager import APITokenManager
from pypureclient.client_settings import resolve_ssl_validation
from pypureclient.exceptions import PureError
from pypureclient.keywords import Headers, Responses
from pypureclient.properties import Property, Filter
from pypureclient.responses import ValidResponse, ErrorResponse, ApiError, ItemIterator
from pypureclient.responses import ValidResponse, ErrorResponse, ApiError, ResponseHeaders
from pypureclient.token_manager import TokenManager

from .api_client import ApiClient
from .api_response import ApiResponse
from .rest import ApiException
from .configuration import Configuration

from . import api
from . import models


class Client(object):
    DEFAULT_RETRIES = 5
    USER_AGENT = DEFAULT_USER_AGENT

    def __init__(self, target, id_token=None, private_key_file=None, private_key_password=None,
                 username=None, client_id=None, key_id=None, issuer=None, api_token=None,
                 retries=DEFAULT_RETRIES, timeout=None, ssl_cert=None,
                 user_agent=None, verify_ssl=None):
        """
        Initialize a FlashArray Client. id_token is generated based on app ID and private
        key info. Either id_token or api_token could be used for authentication. Only one
        authentication option is allowed.

        Keyword args:
            target (str, required):
                The target array's IP or hostname.
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
            api_token (str, optional):
                API token for the user.
            retries (int, optional):
                The number of times to retry an API call if it fails for a
                non-blocking reason. Defaults to 5.
            timeout int or (float, float), optional:
                The timeout duration in seconds, either in total time or
                (connect and read) times. Defaults to None.
            ssl_cert (str, optional):
                SSL certificate to use. Defaults to None.
            user_agent (str, optional):
                User-Agent request header to use.
            verify_ssl (bool | str, optional):
                Controls SSL certificate validation.
                `True` specifies that the server validation uses default trust anchors;
                `False` switches certificate validation off, **not safe!**;
                It also accepts string value for a path to directory with certificates.

        Raises:
            PureError: If it could not create an ID or access token
        """
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        config = Configuration()
        config.verify_ssl = resolve_ssl_validation(verify_ssl)
        config.ssl_ca_cert = ssl_cert
        config.host = self._get_base_url(target)

        effective_user_agent = user_agent or self.USER_AGENT

        if id_token and api_token:
            raise PureError("Only one authentication option is allowed. Please use either id_token or api_token and try again!")
        elif private_key_file and private_key_password and username and \
                key_id and client_id and issuer and api_token:
            raise PureError("id_token is generated based on app ID and private key info. Please use either id_token or api_token and try again!")
        elif api_token:
            api_token_auth_endpoint = self._get_api_token_endpoint(target)
            api_token_dispose_endpoint = self._get_api_token_dispose_endpoint(target)
            self._token_man = APITokenManager(
                api_token_auth_endpoint,
                api_token,
                verify_ssl=config.verify_ssl,
                token_dispose_endpoint=api_token_dispose_endpoint,
                user_agent=effective_user_agent
            )
        else:
            auth_endpoint = 'https://{}/oauth2/1.0/token'.format(target)
            headers = {
                'kid': key_id
            }
            payload = {
                'iss': issuer,
                'aud': client_id,
                'sub': username,
            }
            self._token_man = TokenManager(auth_endpoint, id_token, private_key_file, private_key_password,
                                           payload=payload, headers=headers, verify_ssl=config.verify_ssl)

        self._api_client = ApiClient(configuration=config)
        self._api_client.user_agent = effective_user_agent
        self._set_agent_header()
        self._set_auth_header()

        # Read timeout and retries
        self._retries = retries
        self._timeout = timeout
        self.__apis_instances = {}

    def __del__(self):
        # Cleanup this REST API client resources
        _api_client_attr = getattr(self, '_api_client', None) # using getattr to avoid raising exception, if we failed too early
        if _api_client_attr:
            _api_client_attr.close()

    def get_rest_version(self):
        """Get the REST API version being used by this client.

        Returns:
            str

        """
        return '2.0'

    def get_access_token(self, refresh=False):
        """
        Get the last used access token.

        Args:
            refresh (bool, optional):
                Whether to retrieve a new access token. Defaults to False.

        Returns:
            str

        Raises:
            PureError: If there was an error retrieving an access token.
        """
        return self._token_man.get_access_token(refresh)

    def delete_connections(
        self,
        volumes: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        hosts: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        host_groups: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        host_group_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the host group specified. Enter multiple names in comma-separated format. A request cannot include a mix of multiple objects with multiple names. For example, a request cannot include a mix of multiple host group names and volume names; instead, at least one of the objects (e.g., `host_group_names`) must be set to only one name (e.g., `hgroup01`).")] = None,
        host_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the hosts specified. Enter multiple names in comma-separated format. For example, `host01,host02`. A request cannot include a mix of multiple objects with multiple names. For example, a request cannot include a mix of multiple host names and volume names; instead, at least one of the objects (e.g., `host_names`) must be set to only one name (e.g., `host01`).")] = None,
        volume_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the volume specified. Enter multiple names in comma-separated format. For example, `vol01,vol02`. A request cannot include a mix of multiple objects with multiple names. For example, a request cannot include a mix of multiple volume names and host names; instead, at least one of the objects (e.g., `volume_names`) must be set to only one name (e.g., `vol01`).")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Break a connection between a volume and its host or host group
        
        Break the connection between a volume and its associated host or host group. The `volume_names` and `host_names` or `host_group_names` query parameters are required.
        
        :param volumes: A list of volumes to query for. Overrides volume_names keyword argument.
        :type volumes: ReferenceType or List[ReferenceType], optional
        :param hosts: A list of hosts to query for. Overrides host_names keyword argument.
        :type hosts: ReferenceType or List[ReferenceType], optional
        :param host_groups: A list of host_groups to query for. Overrides host_group_names keyword argument.
        :type host_groups: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param host_group_names: Performs the operation on the host group specified. Enter multiple names in
                                comma-separated format. A request cannot include a mix of multiple objects
                                with multiple names. For example, a request cannot include a mix of
                                multiple host group names and volume names; instead, at least one of the
                                objects (e.g., `host_group_names`) must be set to only one name (e.g.,
                                `hgroup01`).
        :type host_group_names: List[str]
        :param host_names: Performs the operation on the hosts specified. Enter multiple names in comma-
                        separated format. For example, `host01,host02`. A request cannot include a
                        mix of multiple objects with multiple names. For example, a request cannot
                        include a mix of multiple host names and volume names; instead, at least one
                        of the objects (e.g., `host_names`) must be set to only one name (e.g.,
                        `host01`).
        :type host_names: List[str]
        :param volume_names: Performs the operation on the volume specified. Enter multiple names in comma-
                            separated format. For example, `vol01,vol02`. A request cannot include a
                            mix of multiple objects with multiple names. For example, a request cannot
                            include a mix of multiple volume names and host names; instead, at least
                            one of the objects (e.g., `volume_names`) must be set to only one name
                            (e.g., `vol01`).
        :type volume_names: List[str]
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            host_group_names=host_group_names,
            host_names=host_names,
            volume_names=volume_names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(host_groups, ['host_group_names'], kwargs)
        _process_references(hosts, ['host_names'], kwargs)
        _process_references(volumes, ['volume_names'], kwargs)
        _fixup_list_type_params(['host_group_names', 'host_names', 'volume_names'], kwargs)
        return self._call_api('ConnectionsApi', 'api20_connections_delete_with_http_info', kwargs)

    def get_connections(
        self,
        volumes: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        protocol_endpoints: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        hosts: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        host_groups: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        host_group_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the host group specified. Enter multiple names in comma-separated format. A request cannot include a mix of multiple objects with multiple names. For example, a request cannot include a mix of multiple host group names and volume names; instead, at least one of the objects (e.g., `host_group_names`) must be set to only one name (e.g., `hgroup01`).")] = None,
        host_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the hosts specified. Enter multiple names in comma-separated format. For example, `host01,host02`. A request cannot include a mix of multiple objects with multiple names. For example, a request cannot include a mix of multiple host names and volume names; instead, at least one of the objects (e.g., `host_names`) must be set to only one name (e.g., `host01`).")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        protocol_endpoint_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the protocol endpoints specified. Enter multiple names in comma-separated format. For example, `pe01,pe02`. A request cannot include a mix of multiple objects with multiple names. For example, a request cannot include a mix of multiple protocol endpoint names and host names; instead, at least one of the objects (e.g., `protocol_endpoint_names`) must be set to one name (e.g., `pe01`).")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        volume_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the volume specified. Enter multiple names in comma-separated format. For example, `vol01,vol02`. A request cannot include a mix of multiple objects with multiple names. For example, a request cannot include a mix of multiple volume names and host names; instead, at least one of the objects (e.g., `volume_names`) must be set to only one name (e.g., `vol01`).")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """List volume connections
        
        Return a list of connections between a volume and its hosts and host groups, and the LUNs used by the associated hosts to address these volumes.
        
        :param volumes: A list of volumes to query for. Overrides volume_names keyword argument.
        :type volumes: ReferenceType or List[ReferenceType], optional
        :param protocol_endpoints: A list of protocol_endpoints to query for. Overrides protocol_endpoint_names keyword argument.
        :type protocol_endpoints: ReferenceType or List[ReferenceType], optional
        :param hosts: A list of hosts to query for. Overrides host_names keyword argument.
        :type hosts: ReferenceType or List[ReferenceType], optional
        :param host_groups: A list of host_groups to query for. Overrides host_group_names keyword argument.
        :type host_groups: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param filter: Narrows down the results to only the response objects that satisfy the filter
                    criteria.
        :type filter: str
        :param host_group_names: Performs the operation on the host group specified. Enter multiple names in
                                comma-separated format. A request cannot include a mix of multiple objects
                                with multiple names. For example, a request cannot include a mix of
                                multiple host group names and volume names; instead, at least one of the
                                objects (e.g., `host_group_names`) must be set to only one name (e.g.,
                                `hgroup01`).
        :type host_group_names: List[str]
        :param host_names: Performs the operation on the hosts specified. Enter multiple names in comma-
                        separated format. For example, `host01,host02`. A request cannot include a
                        mix of multiple objects with multiple names. For example, a request cannot
                        include a mix of multiple host names and volume names; instead, at least one
                        of the objects (e.g., `host_names`) must be set to only one name (e.g.,
                        `host01`).
        :type host_names: List[str]
        :param limit: Limits the size of the response to the specified number of objects on each page.
                    To return the total number of resources, set `limit=0`. The total number of
                    resources is returned as a `total_item_count` value. If the page size
                    requested is larger than the system maximum limit, the server returns the
                    maximum limit, disregarding the requested page size.
        :type limit: int
        :param offset: The starting position based on the results of the query in relation to the full
                    set of response objects returned.
        :type offset: int
        :param protocol_endpoint_names: Performs the operation on the protocol endpoints specified. Enter multiple names
                                        in comma-separated format. For example, `pe01,pe02`. A request cannot
                                        include a mix of multiple objects with multiple names. For example, a
                                        request cannot include a mix of multiple protocol endpoint names and
                                        host names; instead, at least one of the objects (e.g.,
                                        `protocol_endpoint_names`) must be set to one name (e.g., `pe01`).
        :type protocol_endpoint_names: List[str]
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in
                    the response by which to sort. Sorting can be performed on any of the names
                    in the response, and the objects can be sorted in ascending or descending
                    order. By default, the response objects are sorted in ascending order. To
                    sort in descending order, append the minus sign (`-`) to the name. A single
                    request can be sorted on multiple objects. For example, you can sort all
                    volumes from largest to smallest volume size, and then sort volumes of the
                    same size in ascending order by volume name. To sort on multiple names, list
                    the names as comma-separated values.
        :type sort: List[str]
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters
                                is calculated and returned in the response. If set to `false`, the
                                `total_item_count` is `null` in the response. This may speed up queries
                                where the `total_item_count` is large. If not specified, defaults to
                                `false`.
        :type total_item_count: bool
        :param volume_names: Performs the operation on the volume specified. Enter multiple names in comma-
                            separated format. For example, `vol01,vol02`. A request cannot include a
                            mix of multiple objects with multiple names. For example, a request cannot
                            include a mix of multiple volume names and host names; instead, at least
                            one of the objects (e.g., `volume_names`) must be set to only one name
                            (e.g., `vol01`).
        :type volume_names: List[str]
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            filter=filter,
            host_group_names=host_group_names,
            host_names=host_names,
            limit=limit,
            offset=offset,
            protocol_endpoint_names=protocol_endpoint_names,
            sort=sort,
            total_item_count=total_item_count,
            volume_names=volume_names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(host_groups, ['host_group_names'], kwargs)
        _process_references(hosts, ['host_names'], kwargs)
        _process_references(protocol_endpoints, ['protocol_endpoint_names'], kwargs)
        _process_references(volumes, ['volume_names'], kwargs)
        _fixup_list_type_params(['host_group_names', 'host_names', 'protocol_endpoint_names', 'sort', 'volume_names'], kwargs)
        return self._call_api('ConnectionsApi', 'api20_connections_get_with_http_info', kwargs)

    def post_connections(
        self,
        volumes: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        hosts: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        host_groups: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        host_group_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the host group specified. Enter multiple names in comma-separated format. A request cannot include a mix of multiple objects with multiple names. For example, a request cannot include a mix of multiple host group names and volume names; instead, at least one of the objects (e.g., `host_group_names`) must be set to only one name (e.g., `hgroup01`).")] = None,
        host_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the hosts specified. Enter multiple names in comma-separated format. For example, `host01,host02`. A request cannot include a mix of multiple objects with multiple names. For example, a request cannot include a mix of multiple host names and volume names; instead, at least one of the objects (e.g., `host_names`) must be set to only one name (e.g., `host01`).")] = None,
        volume_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the volume specified. Enter multiple names in comma-separated format. For example, `vol01,vol02`. A request cannot include a mix of multiple objects with multiple names. For example, a request cannot include a mix of multiple volume names and host names; instead, at least one of the objects (e.g., `volume_names`) must be set to only one name (e.g., `vol01`).")] = None,
        connection: Optional['models.ConnectionPost'] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Create a connection between a volume and host or host group
        
        Create a connection between a volume and a host or host group. The `volume_names` and `host_names` or `host_group_names` query parameters are required.
        
        :param volumes: A list of volumes to query for. Overrides volume_names keyword argument.
        :type volumes: ReferenceType or List[ReferenceType], optional
        :param hosts: A list of hosts to query for. Overrides host_names keyword argument.
        :type hosts: ReferenceType or List[ReferenceType], optional
        :param host_groups: A list of host_groups to query for. Overrides host_group_names keyword argument.
        :type host_groups: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param host_group_names: Performs the operation on the host group specified. Enter multiple names in
                                comma-separated format. A request cannot include a mix of multiple objects
                                with multiple names. For example, a request cannot include a mix of
                                multiple host group names and volume names; instead, at least one of the
                                objects (e.g., `host_group_names`) must be set to only one name (e.g.,
                                `hgroup01`).
        :type host_group_names: List[str]
        :param host_names: Performs the operation on the hosts specified. Enter multiple names in comma-
                        separated format. For example, `host01,host02`. A request cannot include a
                        mix of multiple objects with multiple names. For example, a request cannot
                        include a mix of multiple host names and volume names; instead, at least one
                        of the objects (e.g., `host_names`) must be set to only one name (e.g.,
                        `host01`).
        :type host_names: List[str]
        :param volume_names: Performs the operation on the volume specified. Enter multiple names in comma-
                            separated format. For example, `vol01,vol02`. A request cannot include a
                            mix of multiple objects with multiple names. For example, a request cannot
                            include a mix of multiple volume names and host names; instead, at least
                            one of the objects (e.g., `volume_names`) must be set to only one name
                            (e.g., `vol01`).
        :type volume_names: List[str]
        :param connection:
        :type connection: ConnectionPost
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            host_group_names=host_group_names,
            host_names=host_names,
            volume_names=volume_names,
            connection=connection,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(host_groups, ['host_group_names'], kwargs)
        _process_references(hosts, ['host_names'], kwargs)
        _process_references(volumes, ['volume_names'], kwargs)
        _fixup_list_type_params(['host_group_names', 'host_names', 'volume_names'], kwargs)
        return self._call_api('ConnectionsApi', 'api20_connections_post_with_http_info', kwargs)

    def delete_host_groups(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Delete a host group
        
        Delete a host group. The `names` query parameter is required.
        
        :param references: A list of references to query for. Overrides names keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            names=names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['names'], kwargs)
        _fixup_list_type_params(['names'], kwargs)
        return self._call_api('HostGroupsApi', 'api20_host_groups_delete_with_http_info', kwargs)

    def get_host_groups(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """List host groups
        
        Return a list of host groups.
        
        :param references: A list of references to query for. Overrides names keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param filter: Narrows down the results to only the response objects that satisfy the filter
                    criteria.
        :type filter: str
        :param limit: Limits the size of the response to the specified number of objects on each page.
                    To return the total number of resources, set `limit=0`. The total number of
                    resources is returned as a `total_item_count` value. If the page size
                    requested is larger than the system maximum limit, the server returns the
                    maximum limit, disregarding the requested page size.
        :type limit: int
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param offset: The starting position based on the results of the query in relation to the full
                    set of response objects returned.
        :type offset: int
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in
                    the response by which to sort. Sorting can be performed on any of the names
                    in the response, and the objects can be sorted in ascending or descending
                    order. By default, the response objects are sorted in ascending order. To
                    sort in descending order, append the minus sign (`-`) to the name. A single
                    request can be sorted on multiple objects. For example, you can sort all
                    volumes from largest to smallest volume size, and then sort volumes of the
                    same size in ascending order by volume name. To sort on multiple names, list
                    the names as comma-separated values.
        :type sort: List[str]
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters
                                is calculated and returned in the response. If set to `false`, the
                                `total_item_count` is `null` in the response. This may speed up queries
                                where the `total_item_count` is large. If not specified, defaults to
                                `false`.
        :type total_item_count: bool
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            filter=filter,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['names'], kwargs)
        _fixup_list_type_params(['names', 'sort'], kwargs)
        return self._call_api('HostGroupsApi', 'api20_host_groups_get_with_http_info', kwargs)

    def get_host_groups_hosts(
        self,
        members: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        groups: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        group_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique group name specified. Examples of groups include host groups, pods, protection groups, and volume groups. Enter multiple names in comma-separated format. For example, `hgroup01,hgroup02`.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        member_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique member name specified. Examples of members include volumes, hosts, host groups, and directories. Enter multiple names in comma-separated format. For example, `vol01,vol02`.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """List host groups associated with hosts
        
        Returns a list of host groups that are associated with hosts.
        
        :param members: A list of members to query for. Overrides member_names keyword argument.
        :type members: ReferenceType or List[ReferenceType], optional
        :param groups: A list of groups to query for. Overrides group_names keyword argument.
        :type groups: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param filter: Narrows down the results to only the response objects that satisfy the filter
                    criteria.
        :type filter: str
        :param group_names: Performs the operation on the unique group name specified. Examples of groups
                            include host groups, pods, protection groups, and volume groups. Enter
                            multiple names in comma-separated format. For example, `hgroup01,hgroup02`.
        :type group_names: List[str]
        :param limit: Limits the size of the response to the specified number of objects on each page.
                    To return the total number of resources, set `limit=0`. The total number of
                    resources is returned as a `total_item_count` value. If the page size
                    requested is larger than the system maximum limit, the server returns the
                    maximum limit, disregarding the requested page size.
        :type limit: int
        :param member_names: Performs the operation on the unique member name specified. Examples of members
                            include volumes, hosts, host groups, and directories. Enter multiple names
                            in comma-separated format. For example, `vol01,vol02`.
        :type member_names: List[str]
        :param offset: The starting position based on the results of the query in relation to the full
                    set of response objects returned.
        :type offset: int
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in
                    the response by which to sort. Sorting can be performed on any of the names
                    in the response, and the objects can be sorted in ascending or descending
                    order. By default, the response objects are sorted in ascending order. To
                    sort in descending order, append the minus sign (`-`) to the name. A single
                    request can be sorted on multiple objects. For example, you can sort all
                    volumes from largest to smallest volume size, and then sort volumes of the
                    same size in ascending order by volume name. To sort on multiple names, list
                    the names as comma-separated values.
        :type sort: List[str]
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters
                                is calculated and returned in the response. If set to `false`, the
                                `total_item_count` is `null` in the response. This may speed up queries
                                where the `total_item_count` is large. If not specified, defaults to
                                `false`.
        :type total_item_count: bool
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            filter=filter,
            group_names=group_names,
            limit=limit,
            member_names=member_names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        _fixup_list_type_params(['group_names', 'member_names', 'sort'], kwargs)
        return self._call_api('HostGroupsApi', 'api20_host_groups_hosts_get_with_http_info', kwargs)

    def patch_host_groups(
        self,
        host_group: 'models.HostGroupPatch',
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Manage a host group
        
        Manage a host group. The `names` query parameter is required.
        
        :param host_group: (required)
        :type host_group: HostGroupPatch
        :param references: A list of references to query for. Overrides names keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            host_group=host_group,
            authorization=authorization,
            x_request_id=x_request_id,
            names=names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['names'], kwargs)
        _fixup_list_type_params(['names'], kwargs)
        return self._call_api('HostGroupsApi', 'api20_host_groups_patch_with_http_info', kwargs)

    def get_host_groups_performance_by_array(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        total_only: Annotated[Optional[StrictBool], Field(description="If set to `true`, returns the aggregate value of all items after filtering. Where it makes more sense, the average value is displayed instead. The values are displayed for each name where meaningful. If `total_only=true`, the `items` list will be empty.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """List host group performance data by array
        
        Return real-time and historical performance data, real-time latency data, and average I/O size data. The data returned is for each volume that is connected to a host group on the current array and for each volume that is connected to a host group on any remote arrays that are visible to the current array. The data is displayed as a total across all host groups on each array and by individual host group.
        
        :param references: A list of references to query for. Overrides names keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param filter: Narrows down the results to only the response objects that satisfy the filter
                    criteria.
        :type filter: str
        :param limit: Limits the size of the response to the specified number of objects on each page.
                    To return the total number of resources, set `limit=0`. The total number of
                    resources is returned as a `total_item_count` value. If the page size
                    requested is larger than the system maximum limit, the server returns the
                    maximum limit, disregarding the requested page size.
        :type limit: int
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param offset: The starting position based on the results of the query in relation to the full
                    set of response objects returned.
        :type offset: int
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in
                    the response by which to sort. Sorting can be performed on any of the names
                    in the response, and the objects can be sorted in ascending or descending
                    order. By default, the response objects are sorted in ascending order. To
                    sort in descending order, append the minus sign (`-`) to the name. A single
                    request can be sorted on multiple objects. For example, you can sort all
                    volumes from largest to smallest volume size, and then sort volumes of the
                    same size in ascending order by volume name. To sort on multiple names, list
                    the names as comma-separated values.
        :type sort: List[str]
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters
                                is calculated and returned in the response. If set to `false`, the
                                `total_item_count` is `null` in the response. This may speed up queries
                                where the `total_item_count` is large. If not specified, defaults to
                                `false`.
        :type total_item_count: bool
        :param total_only: If set to `true`, returns the aggregate value of all items after filtering.
                        Where it makes more sense, the average value is displayed instead. The
                        values are displayed for each name where meaningful. If `total_only=true`,
                        the `items` list will be empty.
        :type total_only: bool
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            filter=filter,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            total_only=total_only,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['names'], kwargs)
        _fixup_list_type_params(['names', 'sort'], kwargs)
        return self._call_api('HostGroupsApi', 'api20_host_groups_performance_by_array_get_with_http_info', kwargs)

    def get_host_groups_performance(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        total_only: Annotated[Optional[StrictBool], Field(description="If set to `true`, returns the aggregate value of all items after filtering. Where it makes more sense, the average value is displayed instead. The values are displayed for each name where meaningful. If `total_only=true`, the `items` list will be empty.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """List host group performance data
        
        Return real-time and historical performance data, real-time latency data, and average I/O sizes across all volumes, displayed both by host group and as a total across all host groups.
        
        :param references: A list of references to query for. Overrides names keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param filter: Narrows down the results to only the response objects that satisfy the filter
                    criteria.
        :type filter: str
        :param limit: Limits the size of the response to the specified number of objects on each page.
                    To return the total number of resources, set `limit=0`. The total number of
                    resources is returned as a `total_item_count` value. If the page size
                    requested is larger than the system maximum limit, the server returns the
                    maximum limit, disregarding the requested page size.
        :type limit: int
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param offset: The starting position based on the results of the query in relation to the full
                    set of response objects returned.
        :type offset: int
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in
                    the response by which to sort. Sorting can be performed on any of the names
                    in the response, and the objects can be sorted in ascending or descending
                    order. By default, the response objects are sorted in ascending order. To
                    sort in descending order, append the minus sign (`-`) to the name. A single
                    request can be sorted on multiple objects. For example, you can sort all
                    volumes from largest to smallest volume size, and then sort volumes of the
                    same size in ascending order by volume name. To sort on multiple names, list
                    the names as comma-separated values.
        :type sort: List[str]
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters
                                is calculated and returned in the response. If set to `false`, the
                                `total_item_count` is `null` in the response. This may speed up queries
                                where the `total_item_count` is large. If not specified, defaults to
                                `false`.
        :type total_item_count: bool
        :param total_only: If set to `true`, returns the aggregate value of all items after filtering.
                        Where it makes more sense, the average value is displayed instead. The
                        values are displayed for each name where meaningful. If `total_only=true`,
                        the `items` list will be empty.
        :type total_only: bool
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            filter=filter,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            total_only=total_only,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['names'], kwargs)
        _fixup_list_type_params(['names', 'sort'], kwargs)
        return self._call_api('HostGroupsApi', 'api20_host_groups_performance_get_with_http_info', kwargs)

    def post_host_groups(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Create a host group
        
        Create a host group. The `names` query parameter is required.
        
        :param references: A list of references to query for. Overrides names keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            names=names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['names'], kwargs)
        _fixup_list_type_params(['names'], kwargs)
        return self._call_api('HostGroupsApi', 'api20_host_groups_post_with_http_info', kwargs)

    def delete_hosts(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Delete a host
        
        Deletes an existing host. All volumes that are connected to the host, either through private or shared connections, must be disconnected from the host before the host can be deleted. The `names` query parameter is required.
        
        :param references: A list of references to query for. Overrides names keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            names=names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['names'], kwargs)
        _fixup_list_type_params(['names'], kwargs)
        return self._call_api('HostsApi', 'api20_hosts_delete_with_http_info', kwargs)

    def get_hosts(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """List hosts
        
        Returns a list of hosts.
        
        :param references: A list of references to query for. Overrides names keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param filter: Narrows down the results to only the response objects that satisfy the filter
                    criteria.
        :type filter: str
        :param limit: Limits the size of the response to the specified number of objects on each page.
                    To return the total number of resources, set `limit=0`. The total number of
                    resources is returned as a `total_item_count` value. If the page size
                    requested is larger than the system maximum limit, the server returns the
                    maximum limit, disregarding the requested page size.
        :type limit: int
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param offset: The starting position based on the results of the query in relation to the full
                    set of response objects returned.
        :type offset: int
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in
                    the response by which to sort. Sorting can be performed on any of the names
                    in the response, and the objects can be sorted in ascending or descending
                    order. By default, the response objects are sorted in ascending order. To
                    sort in descending order, append the minus sign (`-`) to the name. A single
                    request can be sorted on multiple objects. For example, you can sort all
                    volumes from largest to smallest volume size, and then sort volumes of the
                    same size in ascending order by volume name. To sort on multiple names, list
                    the names as comma-separated values.
        :type sort: List[str]
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters
                                is calculated and returned in the response. If set to `false`, the
                                `total_item_count` is `null` in the response. This may speed up queries
                                where the `total_item_count` is large. If not specified, defaults to
                                `false`.
        :type total_item_count: bool
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            filter=filter,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['names'], kwargs)
        _fixup_list_type_params(['names', 'sort'], kwargs)
        return self._call_api('HostsApi', 'api20_hosts_get_with_http_info', kwargs)

    def get_hosts_host_groups(
        self,
        members: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        groups: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        group_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique group name specified. Examples of groups include host groups, pods, protection groups, and volume groups. Enter multiple names in comma-separated format. For example, `hgroup01,hgroup02`.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        member_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique member name specified. Examples of members include volumes, hosts, host groups, and directories. Enter multiple names in comma-separated format. For example, `vol01,vol02`.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """List hosts associated with host groups
        
        Returns a list of hosts that are associated with host groups.
        
        :param members: A list of members to query for. Overrides member_names keyword argument.
        :type members: ReferenceType or List[ReferenceType], optional
        :param groups: A list of groups to query for. Overrides group_names keyword argument.
        :type groups: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param filter: Narrows down the results to only the response objects that satisfy the filter
                    criteria.
        :type filter: str
        :param group_names: Performs the operation on the unique group name specified. Examples of groups
                            include host groups, pods, protection groups, and volume groups. Enter
                            multiple names in comma-separated format. For example, `hgroup01,hgroup02`.
        :type group_names: List[str]
        :param limit: Limits the size of the response to the specified number of objects on each page.
                    To return the total number of resources, set `limit=0`. The total number of
                    resources is returned as a `total_item_count` value. If the page size
                    requested is larger than the system maximum limit, the server returns the
                    maximum limit, disregarding the requested page size.
        :type limit: int
        :param member_names: Performs the operation on the unique member name specified. Examples of members
                            include volumes, hosts, host groups, and directories. Enter multiple names
                            in comma-separated format. For example, `vol01,vol02`.
        :type member_names: List[str]
        :param offset: The starting position based on the results of the query in relation to the full
                    set of response objects returned.
        :type offset: int
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in
                    the response by which to sort. Sorting can be performed on any of the names
                    in the response, and the objects can be sorted in ascending or descending
                    order. By default, the response objects are sorted in ascending order. To
                    sort in descending order, append the minus sign (`-`) to the name. A single
                    request can be sorted on multiple objects. For example, you can sort all
                    volumes from largest to smallest volume size, and then sort volumes of the
                    same size in ascending order by volume name. To sort on multiple names, list
                    the names as comma-separated values.
        :type sort: List[str]
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters
                                is calculated and returned in the response. If set to `false`, the
                                `total_item_count` is `null` in the response. This may speed up queries
                                where the `total_item_count` is large. If not specified, defaults to
                                `false`.
        :type total_item_count: bool
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            filter=filter,
            group_names=group_names,
            limit=limit,
            member_names=member_names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        _fixup_list_type_params(['group_names', 'member_names', 'sort'], kwargs)
        return self._call_api('HostsApi', 'api20_hosts_host_groups_get_with_http_info', kwargs)

    def patch_hosts(
        self,
        host: 'models.HostPatch',
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Manage a host
        
        Manages an existing host, including its storage network addresses, CHAP, host personality, and preferred arrays, or associate a host to a host group. The `names` query parameter is required.
        
        :param host: (required)
        :type host: HostPatch
        :param references: A list of references to query for. Overrides names keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            host=host,
            authorization=authorization,
            x_request_id=x_request_id,
            names=names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['names'], kwargs)
        _fixup_list_type_params(['names'], kwargs)
        return self._call_api('HostsApi', 'api20_hosts_patch_with_http_info', kwargs)

    def get_hosts_performance_by_array(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        total_only: Annotated[Optional[StrictBool], Field(description="If set to `true`, returns the aggregate value of all items after filtering. Where it makes more sense, the average value is displayed instead. The values are displayed for each name where meaningful. If `total_only=true`, the `items` list will be empty.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """List host performance data by array
        
        Return real-time and historical performance data, real-time latency data, and average I/O size data. The data returned is for each volume that is connected to a host on the current array and for each volume that is connected to a host on any remote arrays that are visible to the current array. The data is displayed as a total across all hosts on each array and by individual host.
        
        :param references: A list of references to query for. Overrides names keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param filter: Narrows down the results to only the response objects that satisfy the filter
                    criteria.
        :type filter: str
        :param limit: Limits the size of the response to the specified number of objects on each page.
                    To return the total number of resources, set `limit=0`. The total number of
                    resources is returned as a `total_item_count` value. If the page size
                    requested is larger than the system maximum limit, the server returns the
                    maximum limit, disregarding the requested page size.
        :type limit: int
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param offset: The starting position based on the results of the query in relation to the full
                    set of response objects returned.
        :type offset: int
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in
                    the response by which to sort. Sorting can be performed on any of the names
                    in the response, and the objects can be sorted in ascending or descending
                    order. By default, the response objects are sorted in ascending order. To
                    sort in descending order, append the minus sign (`-`) to the name. A single
                    request can be sorted on multiple objects. For example, you can sort all
                    volumes from largest to smallest volume size, and then sort volumes of the
                    same size in ascending order by volume name. To sort on multiple names, list
                    the names as comma-separated values.
        :type sort: List[str]
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters
                                is calculated and returned in the response. If set to `false`, the
                                `total_item_count` is `null` in the response. This may speed up queries
                                where the `total_item_count` is large. If not specified, defaults to
                                `false`.
        :type total_item_count: bool
        :param total_only: If set to `true`, returns the aggregate value of all items after filtering.
                        Where it makes more sense, the average value is displayed instead. The
                        values are displayed for each name where meaningful. If `total_only=true`,
                        the `items` list will be empty.
        :type total_only: bool
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            filter=filter,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            total_only=total_only,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['names'], kwargs)
        _fixup_list_type_params(['names', 'sort'], kwargs)
        return self._call_api('HostsApi', 'api20_hosts_performance_by_array_get_with_http_info', kwargs)

    def get_hosts_performance(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        total_only: Annotated[Optional[StrictBool], Field(description="If set to `true`, returns the aggregate value of all items after filtering. Where it makes more sense, the average value is displayed instead. The values are displayed for each name where meaningful. If `total_only=true`, the `items` list will be empty.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """List host performance data
        
        Return real-time and historical performance data, real-time latency data, and average I/O sizes across all volumes, displayed both by host and as a total across all hosts.
        
        :param references: A list of references to query for. Overrides names keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param filter: Narrows down the results to only the response objects that satisfy the filter
                    criteria.
        :type filter: str
        :param limit: Limits the size of the response to the specified number of objects on each page.
                    To return the total number of resources, set `limit=0`. The total number of
                    resources is returned as a `total_item_count` value. If the page size
                    requested is larger than the system maximum limit, the server returns the
                    maximum limit, disregarding the requested page size.
        :type limit: int
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param offset: The starting position based on the results of the query in relation to the full
                    set of response objects returned.
        :type offset: int
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in
                    the response by which to sort. Sorting can be performed on any of the names
                    in the response, and the objects can be sorted in ascending or descending
                    order. By default, the response objects are sorted in ascending order. To
                    sort in descending order, append the minus sign (`-`) to the name. A single
                    request can be sorted on multiple objects. For example, you can sort all
                    volumes from largest to smallest volume size, and then sort volumes of the
                    same size in ascending order by volume name. To sort on multiple names, list
                    the names as comma-separated values.
        :type sort: List[str]
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters
                                is calculated and returned in the response. If set to `false`, the
                                `total_item_count` is `null` in the response. This may speed up queries
                                where the `total_item_count` is large. If not specified, defaults to
                                `false`.
        :type total_item_count: bool
        :param total_only: If set to `true`, returns the aggregate value of all items after filtering.
                        Where it makes more sense, the average value is displayed instead. The
                        values are displayed for each name where meaningful. If `total_only=true`,
                        the `items` list will be empty.
        :type total_only: bool
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            filter=filter,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            total_only=total_only,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['names'], kwargs)
        _fixup_list_type_params(['names', 'sort'], kwargs)
        return self._call_api('HostsApi', 'api20_hosts_performance_get_with_http_info', kwargs)

    def post_hosts(
        self,
        host: 'models.HostPost',
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Create a host
        
        Creates a host. The `names` query parameter is required.
        
        :param host: (required)
        :type host: HostPost
        :param references: A list of references to query for. Overrides names keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            host=host,
            authorization=authorization,
            x_request_id=x_request_id,
            names=names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['names'], kwargs)
        _fixup_list_type_params(['names'], kwargs)
        return self._call_api('HostsApi', 'api20_hosts_post_with_http_info', kwargs)

    def delete_volume_snapshots(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique resource IDs specified. Enter multiple resource IDs in comma-separated format. The `ids` or `names` parameter is required, but they cannot be set together.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Eradicate a volume snapshot
        
        Eradicate a volume snapshot that has been destroyed and is pending eradication. Eradicated volumes snapshots cannot be recovered. Volume snapshots are destroyed through the `PATCH` method. The `ids` or `names` parameter is required, but they cannot be set together.
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param ids: Performs the operation on the unique resource IDs specified. Enter multiple
                    resource IDs in comma-separated format. The `ids` or `names` parameter is
                    required, but they cannot be set together.
        :type ids: List[str]
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            ids=ids,
            names=names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names'], kwargs)
        return self._call_api('VolumeSnapshotsApi', 'api20_volume_snapshots_delete_with_http_info', kwargs)

    def get_volume_snapshots(
        self,
        sources: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        destroyed: Annotated[Optional[StrictBool], Field(description="If set to `true`, lists only destroyed objects that are in the eradication pending state. If set to `false`, lists only objects that are not destroyed. For destroyed objects, the time remaining is displayed in milliseconds.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique resource IDs specified. Enter multiple resource IDs in comma-separated format. The `ids` or `names` parameter is required, but they cannot be set together.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        source_ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the source ID specified. Enter multiple source IDs in comma-separated format.")] = None,
        source_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the source name specified. Enter multiple source names in comma-separated format. For example, `name01,name02`.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        total_only: Annotated[Optional[StrictBool], Field(description="If set to `true`, returns the aggregate value of all items after filtering. Where it makes more sense, the average value is displayed instead. The values are displayed for each name where meaningful. If `total_only=true`, the `items` list will be empty.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """List volume snapshots
        
        Return a list of volume snapshots, including those pending eradication.
        
        :param sources: A list of sources to query for. Overrides source_ids and source_names keyword arguments.
        :type sources: ReferenceType or List[ReferenceType], optional
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param destroyed: If set to `true`, lists only destroyed objects that are in the eradication
                        pending state. If set to `false`, lists only objects that are not destroyed.
                        For destroyed objects, the time remaining is displayed in milliseconds.
        :type destroyed: bool
        :param filter: Narrows down the results to only the response objects that satisfy the filter
                    criteria.
        :type filter: str
        :param ids: Performs the operation on the unique resource IDs specified. Enter multiple
                    resource IDs in comma-separated format. The `ids` or `names` parameter is
                    required, but they cannot be set together.
        :type ids: List[str]
        :param limit: Limits the size of the response to the specified number of objects on each page.
                    To return the total number of resources, set `limit=0`. The total number of
                    resources is returned as a `total_item_count` value. If the page size
                    requested is larger than the system maximum limit, the server returns the
                    maximum limit, disregarding the requested page size.
        :type limit: int
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param offset: The starting position based on the results of the query in relation to the full
                    set of response objects returned.
        :type offset: int
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in
                    the response by which to sort. Sorting can be performed on any of the names
                    in the response, and the objects can be sorted in ascending or descending
                    order. By default, the response objects are sorted in ascending order. To
                    sort in descending order, append the minus sign (`-`) to the name. A single
                    request can be sorted on multiple objects. For example, you can sort all
                    volumes from largest to smallest volume size, and then sort volumes of the
                    same size in ascending order by volume name. To sort on multiple names, list
                    the names as comma-separated values.
        :type sort: List[str]
        :param source_ids: Performs the operation on the source ID specified. Enter multiple source IDs in
                        comma-separated format.
        :type source_ids: List[str]
        :param source_names: Performs the operation on the source name specified. Enter multiple source names
                            in comma-separated format. For example, `name01,name02`.
        :type source_names: List[str]
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters
                                is calculated and returned in the response. If set to `false`, the
                                `total_item_count` is `null` in the response. This may speed up queries
                                where the `total_item_count` is large. If not specified, defaults to
                                `false`.
        :type total_item_count: bool
        :param total_only: If set to `true`, returns the aggregate value of all items after filtering.
                        Where it makes more sense, the average value is displayed instead. The
                        values are displayed for each name where meaningful. If `total_only=true`,
                        the `items` list will be empty.
        :type total_only: bool
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            destroyed=destroyed,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            source_ids=source_ids,
            source_names=source_names,
            total_item_count=total_item_count,
            total_only=total_only,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort', 'source_ids', 'source_names'], kwargs)
        return self._call_api('VolumeSnapshotsApi', 'api20_volume_snapshots_get_with_http_info', kwargs)

    def patch_volume_snapshots(
        self,
        volume_snapshot: 'models.VolumeSnapshotPatch',
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique resource IDs specified. Enter multiple resource IDs in comma-separated format. The `ids` or `names` parameter is required, but they cannot be set together.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Manage a volume snapshot
        
        Rename, destroy, or recover a volume snapshot. To rename the suffix of a volume snapshot, set `name` to the new suffix name. To recover a volume snapshot that has been destroyed and is pending eradication, set `destroyed=true`. The `ids` or `names` parameter is required, but they cannot be set together.
        
        :param volume_snapshot: (required)
        :type volume_snapshot: VolumeSnapshotPatch
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param ids: Performs the operation on the unique resource IDs specified. Enter multiple
                    resource IDs in comma-separated format. The `ids` or `names` parameter is
                    required, but they cannot be set together.
        :type ids: List[str]
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            volume_snapshot=volume_snapshot,
            authorization=authorization,
            x_request_id=x_request_id,
            ids=ids,
            names=names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names'], kwargs)
        return self._call_api('VolumeSnapshotsApi', 'api20_volume_snapshots_patch_with_http_info', kwargs)

    def post_volume_snapshots(
        self,
        volume_snapshot: 'models.VolumeSnapshotPost',
        sources: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        on: Annotated[Optional[StrictStr], Field(description="Performs the operation on the target name specified. For example, `targetName01`.")] = None,
        source_ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the source ID specified. Enter multiple source IDs in comma-separated format.")] = None,
        source_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the source name specified. Enter multiple source names in comma-separated format. For example, `name01,name02`.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Generate a volume snapshot
        
        Create a point-in-time snapshot of the contents of a volume. The `source_ids` or `source_names` parameter is required, but they cannot be set together.
        
        :param volume_snapshot: (required)
        :type volume_snapshot: VolumeSnapshotPost
        :param sources: A list of sources to query for. Overrides source_ids and source_names keyword arguments.
        :type sources: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param on: Performs the operation on the target name specified. For example,
                `targetName01`.
        :type on: str
        :param source_ids: Performs the operation on the source ID specified. Enter multiple source IDs in
                        comma-separated format.
        :type source_ids: List[str]
        :param source_names: Performs the operation on the source name specified. Enter multiple source names
                            in comma-separated format. For example, `name01,name02`.
        :type source_names: List[str]
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            volume_snapshot=volume_snapshot,
            authorization=authorization,
            x_request_id=x_request_id,
            on=on,
            source_ids=source_ids,
            source_names=source_names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        _fixup_list_type_params(['source_ids', 'source_names'], kwargs)
        return self._call_api('VolumeSnapshotsApi', 'api20_volume_snapshots_post_with_http_info', kwargs)

    def get_volume_snapshots_transfer(
        self,
        sources: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        destroyed: Annotated[Optional[StrictBool], Field(description="If set to `true`, lists only destroyed objects that are in the eradication pending state. If set to `false`, lists only objects that are not destroyed. For destroyed objects, the time remaining is displayed in milliseconds.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique resource IDs specified. Enter multiple resource IDs in comma-separated format. The `ids` or `names` parameter is required, but they cannot be set together.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        source_ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the source ID specified. Enter multiple source IDs in comma-separated format.")] = None,
        source_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the source name specified. Enter multiple source names in comma-separated format. For example, `name01,name02`.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        total_only: Annotated[Optional[StrictBool], Field(description="If set to `true`, returns the aggregate value of all items after filtering. Where it makes more sense, the average value is displayed instead. The values are displayed for each name where meaningful. If `total_only=true`, the `items` list will be empty.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """List volume snapshots with transfer statistics
        
        Returns a list of volume snapshots and their transfer statistics.
        
        :param sources: A list of sources to query for. Overrides source_ids and source_names keyword arguments.
        :type sources: ReferenceType or List[ReferenceType], optional
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param destroyed: If set to `true`, lists only destroyed objects that are in the eradication
                        pending state. If set to `false`, lists only objects that are not destroyed.
                        For destroyed objects, the time remaining is displayed in milliseconds.
        :type destroyed: bool
        :param filter: Narrows down the results to only the response objects that satisfy the filter
                    criteria.
        :type filter: str
        :param ids: Performs the operation on the unique resource IDs specified. Enter multiple
                    resource IDs in comma-separated format. The `ids` or `names` parameter is
                    required, but they cannot be set together.
        :type ids: List[str]
        :param limit: Limits the size of the response to the specified number of objects on each page.
                    To return the total number of resources, set `limit=0`. The total number of
                    resources is returned as a `total_item_count` value. If the page size
                    requested is larger than the system maximum limit, the server returns the
                    maximum limit, disregarding the requested page size.
        :type limit: int
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param offset: The starting position based on the results of the query in relation to the full
                    set of response objects returned.
        :type offset: int
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in
                    the response by which to sort. Sorting can be performed on any of the names
                    in the response, and the objects can be sorted in ascending or descending
                    order. By default, the response objects are sorted in ascending order. To
                    sort in descending order, append the minus sign (`-`) to the name. A single
                    request can be sorted on multiple objects. For example, you can sort all
                    volumes from largest to smallest volume size, and then sort volumes of the
                    same size in ascending order by volume name. To sort on multiple names, list
                    the names as comma-separated values.
        :type sort: List[str]
        :param source_ids: Performs the operation on the source ID specified. Enter multiple source IDs in
                        comma-separated format.
        :type source_ids: List[str]
        :param source_names: Performs the operation on the source name specified. Enter multiple source names
                            in comma-separated format. For example, `name01,name02`.
        :type source_names: List[str]
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters
                                is calculated and returned in the response. If set to `false`, the
                                `total_item_count` is `null` in the response. This may speed up queries
                                where the `total_item_count` is large. If not specified, defaults to
                                `false`.
        :type total_item_count: bool
        :param total_only: If set to `true`, returns the aggregate value of all items after filtering.
                        Where it makes more sense, the average value is displayed instead. The
                        values are displayed for each name where meaningful. If `total_only=true`,
                        the `items` list will be empty.
        :type total_only: bool
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            destroyed=destroyed,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            source_ids=source_ids,
            source_names=source_names,
            total_item_count=total_item_count,
            total_only=total_only,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort', 'source_ids', 'source_names'], kwargs)
        return self._call_api('VolumeSnapshotsApi', 'api20_volume_snapshots_transfer_get_with_http_info', kwargs)

    def delete_volumes(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique resource IDs specified. Enter multiple resource IDs in comma-separated format. The `ids` or `names` parameter is required, but they cannot be set together.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Eradicate a volume
        
        Eradicate a volume that has been destroyed and is pending eradication. Eradicated volumes cannot be recovered. Volumes are destroyed through the `PATCH` method. The `ids` or `names` parameter is required, but they cannot be set together.
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param ids: Performs the operation on the unique resource IDs specified. Enter multiple
                    resource IDs in comma-separated format. The `ids` or `names` parameter is
                    required, but they cannot be set together.
        :type ids: List[str]
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            ids=ids,
            names=names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names'], kwargs)
        return self._call_api('VolumesApi', 'api20_volumes_delete_with_http_info', kwargs)

    def get_volumes(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        destroyed: Annotated[Optional[StrictBool], Field(description="If set to `true`, lists only destroyed objects that are in the eradication pending state. If set to `false`, lists only objects that are not destroyed. For destroyed objects, the time remaining is displayed in milliseconds.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique resource IDs specified. Enter multiple resource IDs in comma-separated format. The `ids` or `names` parameter is required, but they cannot be set together.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        total_only: Annotated[Optional[StrictBool], Field(description="If set to `true`, returns the aggregate value of all items after filtering. Where it makes more sense, the average value is displayed instead. The values are displayed for each name where meaningful. If `total_only=true`, the `items` list will be empty.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """List volumes
        
        Return a list of volumes, including those pending eradication.
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param destroyed: If set to `true`, lists only destroyed objects that are in the eradication
                        pending state. If set to `false`, lists only objects that are not destroyed.
                        For destroyed objects, the time remaining is displayed in milliseconds.
        :type destroyed: bool
        :param filter: Narrows down the results to only the response objects that satisfy the filter
                    criteria.
        :type filter: str
        :param ids: Performs the operation on the unique resource IDs specified. Enter multiple
                    resource IDs in comma-separated format. The `ids` or `names` parameter is
                    required, but they cannot be set together.
        :type ids: List[str]
        :param limit: Limits the size of the response to the specified number of objects on each page.
                    To return the total number of resources, set `limit=0`. The total number of
                    resources is returned as a `total_item_count` value. If the page size
                    requested is larger than the system maximum limit, the server returns the
                    maximum limit, disregarding the requested page size.
        :type limit: int
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param offset: The starting position based on the results of the query in relation to the full
                    set of response objects returned.
        :type offset: int
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in
                    the response by which to sort. Sorting can be performed on any of the names
                    in the response, and the objects can be sorted in ascending or descending
                    order. By default, the response objects are sorted in ascending order. To
                    sort in descending order, append the minus sign (`-`) to the name. A single
                    request can be sorted on multiple objects. For example, you can sort all
                    volumes from largest to smallest volume size, and then sort volumes of the
                    same size in ascending order by volume name. To sort on multiple names, list
                    the names as comma-separated values.
        :type sort: List[str]
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters
                                is calculated and returned in the response. If set to `false`, the
                                `total_item_count` is `null` in the response. This may speed up queries
                                where the `total_item_count` is large. If not specified, defaults to
                                `false`.
        :type total_item_count: bool
        :param total_only: If set to `true`, returns the aggregate value of all items after filtering.
                        Where it makes more sense, the average value is displayed instead. The
                        values are displayed for each name where meaningful. If `total_only=true`,
                        the `items` list will be empty.
        :type total_only: bool
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            destroyed=destroyed,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            total_only=total_only,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('VolumesApi', 'api20_volumes_get_with_http_info', kwargs)

    def patch_volumes(
        self,
        volume: 'models.VolumePatch',
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique resource IDs specified. Enter multiple resource IDs in comma-separated format. The `ids` or `names` parameter is required, but they cannot be set together.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        truncate: Annotated[Optional[StrictBool], Field(description="If set to `true`, reduces the size of a volume during a volume resize operation. When a volume is truncated, Purity automatically takes an undo snapshot, providing a 24-hour window during which the previous contents can be retrieved. After truncating a volume, its provisioned size can be subsequently increased, but the data in truncated sectors cannot be retrieved. If set to `false` or not set at all and the volume is being reduced in size, the volume copy operation fails. Required if the `provisioned` parameter is set to a volume size that is smaller than the original size.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Manage a volume
        
        Renames or destroys a volume. To rename a volume, set `name` to the new name. To move a volume, set the `pod` or `volume group` parameters. To destroy a volume, set `destroyed=true`. To recover a volume that has been destroyed and is pending eradication, set `destroyed=false`. Sets the bandwidth and IOPs limits of a volume group. The `ids` or `names` parameter is required, but they cannot be set together.
        
        :param volume: (required)
        :type volume: VolumePatch
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param ids: Performs the operation on the unique resource IDs specified. Enter multiple
                    resource IDs in comma-separated format. The `ids` or `names` parameter is
                    required, but they cannot be set together.
        :type ids: List[str]
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param truncate: If set to `true`, reduces the size of a volume during a volume resize operation.
                        When a volume is truncated, Purity automatically takes an undo snapshot,
                        providing a 24-hour window during which the previous contents can be
                        retrieved. After truncating a volume, its provisioned size can be
                        subsequently increased, but the data in truncated sectors cannot be
                        retrieved. If set to `false` or not set at all and the volume is being
                        reduced in size, the volume copy operation fails. Required if the
                        `provisioned` parameter is set to a volume size that is smaller than the
                        original size.
        :type truncate: bool
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            volume=volume,
            authorization=authorization,
            x_request_id=x_request_id,
            ids=ids,
            names=names,
            truncate=truncate,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names'], kwargs)
        return self._call_api('VolumesApi', 'api20_volumes_patch_with_http_info', kwargs)

    def get_volumes_performance_by_array(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        destroyed: Annotated[Optional[StrictBool], Field(description="If set to `true`, lists only destroyed objects that are in the eradication pending state. If set to `false`, lists only objects that are not destroyed. For destroyed objects, the time remaining is displayed in milliseconds.")] = None,
        end_time: Annotated[Optional[StrictInt], Field(description="Displays historical performance data for the specified time window, where `start_time` is the beginning of the time window, and `end_time` is the end of the time window. The `start_time` and `end_time` parameters are specified in milliseconds since the UNIX epoch. If `start_time` is not specified, the start time will default to one resolution before the end time, meaning that the most recent sample of performance data will be displayed. If `end_time`is not specified, the end time will default to the current time. Include the `resolution` parameter to display the performance data at the specified resolution. If not specified, `resolution` defaults to the lowest valid resolution.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique resource IDs specified. Enter multiple resource IDs in comma-separated format. The `ids` or `names` parameter is required, but they cannot be set together.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        resolution: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The number of milliseconds between samples of historical data. For array-wide performance metrics (`/arrays/performance` endpoint), valid values are `1000` (1 second), `30000` (30 seconds), `300000` (5 minutes), `1800000` (30 minutes), `7200000` (2 hours), `28800000` (8 hours), and `86400000` (24 hours). For performance metrics on storage objects (`<object name>/performance` endpoint), such as volumes, valid values are `30000` (30 seconds), `300000` (5 minutes), `1800000` (30 minutes), `7200000` (2 hours), `28800000` (8 hours), and `86400000` (24 hours). For space metrics, (`<object name>/space` endpoint), valid values are `300000` (5 minutes), `1800000` (30 minutes), `7200000` (2 hours), `28800000` (8 hours), and `86400000` (24 hours). Include the `start_time` parameter to display the performance data starting at the specified start time. If `start_time` is not specified, the start time will default to one resolution before the end time, meaning that the most recent sample of performance data will be displayed. Include the `end_time` parameter to display the performance data until the specified end time. If `end_time`is not specified, the end time will default to the current time. If the `resolution` parameter is not specified but either the `start_time` or `end_time` parameter is, then `resolution` will default to the lowest valid resolution.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        start_time: Annotated[Optional[StrictInt], Field(description="Displays historical performance data for the specified time window, where `start_time` is the beginning of the time window, and `end_time` is the end of the time window. The `start_time` and `end_time` parameters are specified in milliseconds since the UNIX epoch. If `start_time` is not specified, the start time will default to one resolution before the end time, meaning that the most recent sample of performance data will be displayed. If `end_time`is not specified, the end time will default to the current time. Include the `resolution` parameter to display the performance data at the specified resolution. If not specified, `resolution` defaults to the lowest valid resolution.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        total_only: Annotated[Optional[StrictBool], Field(description="If set to `true`, returns the aggregate value of all items after filtering. Where it makes more sense, the average value is displayed instead. The values are displayed for each name where meaningful. If `total_only=true`, the `items` list will be empty.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """List volume performance data by array
        
        Returns real-time and historical performance data, real-time latency data, and average I/O size data. The data returned is for each volume on the current array and for each volume on any remote arrays that are visible to the current array. The data is grouped by individual volumes and as a total across all volumes on each array.
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param destroyed: If set to `true`, lists only destroyed objects that are in the eradication
                        pending state. If set to `false`, lists only objects that are not destroyed.
                        For destroyed objects, the time remaining is displayed in milliseconds.
        :type destroyed: bool
        :param end_time: Displays historical performance data for the specified time window, where
                        `start_time` is the beginning of the time window, and `end_time` is the end
                        of the time window. The `start_time` and `end_time` parameters are specified
                        in milliseconds since the UNIX epoch. If `start_time` is not specified, the
                        start time will default to one resolution before the end time, meaning that
                        the most recent sample of performance data will be displayed. If
                        `end_time`is not specified, the end time will default to the current time.
                        Include the `resolution` parameter to display the performance data at the
                        specified resolution. If not specified, `resolution` defaults to the lowest
                        valid resolution.
        :type end_time: int
        :param filter: Narrows down the results to only the response objects that satisfy the filter
                    criteria.
        :type filter: str
        :param ids: Performs the operation on the unique resource IDs specified. Enter multiple
                    resource IDs in comma-separated format. The `ids` or `names` parameter is
                    required, but they cannot be set together.
        :type ids: List[str]
        :param limit: Limits the size of the response to the specified number of objects on each page.
                    To return the total number of resources, set `limit=0`. The total number of
                    resources is returned as a `total_item_count` value. If the page size
                    requested is larger than the system maximum limit, the server returns the
                    maximum limit, disregarding the requested page size.
        :type limit: int
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param offset: The starting position based on the results of the query in relation to the full
                    set of response objects returned.
        :type offset: int
        :param resolution: The number of milliseconds between samples of historical data. For array-wide
                        performance metrics (`/arrays/performance` endpoint), valid values are
                        `1000` (1 second), `30000` (30 seconds), `300000` (5 minutes), `1800000` (30
                        minutes), `7200000` (2 hours), `28800000` (8 hours), and `86400000` (24
                        hours). For performance metrics on storage objects (`<object
                        name>/performance` endpoint), such as volumes, valid values are `30000` (30
                        seconds), `300000` (5 minutes), `1800000` (30 minutes), `7200000` (2 hours),
                        `28800000` (8 hours), and `86400000` (24 hours). For space metrics,
                        (`<object name>/space` endpoint), valid values are `300000` (5 minutes),
                        `1800000` (30 minutes), `7200000` (2 hours), `28800000` (8 hours), and
                        `86400000` (24 hours). Include the `start_time` parameter to display the
                        performance data starting at the specified start time. If `start_time` is
                        not specified, the start time will default to one resolution before the end
                        time, meaning that the most recent sample of performance data will be
                        displayed. Include the `end_time` parameter to display the performance data
                        until the specified end time. If `end_time`is not specified, the end time
                        will default to the current time. If the `resolution` parameter is not
                        specified but either the `start_time` or `end_time` parameter is, then
                        `resolution` will default to the lowest valid resolution.
        :type resolution: int
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in
                    the response by which to sort. Sorting can be performed on any of the names
                    in the response, and the objects can be sorted in ascending or descending
                    order. By default, the response objects are sorted in ascending order. To
                    sort in descending order, append the minus sign (`-`) to the name. A single
                    request can be sorted on multiple objects. For example, you can sort all
                    volumes from largest to smallest volume size, and then sort volumes of the
                    same size in ascending order by volume name. To sort on multiple names, list
                    the names as comma-separated values.
        :type sort: List[str]
        :param start_time: Displays historical performance data for the specified time window, where
                        `start_time` is the beginning of the time window, and `end_time` is the end
                        of the time window. The `start_time` and `end_time` parameters are specified
                        in milliseconds since the UNIX epoch. If `start_time` is not specified, the
                        start time will default to one resolution before the end time, meaning that
                        the most recent sample of performance data will be displayed. If
                        `end_time`is not specified, the end time will default to the current time.
                        Include the `resolution` parameter to display the performance data at the
                        specified resolution. If not specified, `resolution` defaults to the lowest
                        valid resolution.
        :type start_time: int
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters
                                is calculated and returned in the response. If set to `false`, the
                                `total_item_count` is `null` in the response. This may speed up queries
                                where the `total_item_count` is large. If not specified, defaults to
                                `false`.
        :type total_item_count: bool
        :param total_only: If set to `true`, returns the aggregate value of all items after filtering.
                        Where it makes more sense, the average value is displayed instead. The
                        values are displayed for each name where meaningful. If `total_only=true`,
                        the `items` list will be empty.
        :type total_only: bool
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            destroyed=destroyed,
            end_time=end_time,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            resolution=resolution,
            sort=sort,
            start_time=start_time,
            total_item_count=total_item_count,
            total_only=total_only,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('VolumesApi', 'api20_volumes_performance_by_array_get_with_http_info', kwargs)

    def get_volumes_performance(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        destroyed: Annotated[Optional[StrictBool], Field(description="If set to `true`, lists only destroyed objects that are in the eradication pending state. If set to `false`, lists only objects that are not destroyed. For destroyed objects, the time remaining is displayed in milliseconds.")] = None,
        end_time: Annotated[Optional[StrictInt], Field(description="Displays historical performance data for the specified time window, where `start_time` is the beginning of the time window, and `end_time` is the end of the time window. The `start_time` and `end_time` parameters are specified in milliseconds since the UNIX epoch. If `start_time` is not specified, the start time will default to one resolution before the end time, meaning that the most recent sample of performance data will be displayed. If `end_time`is not specified, the end time will default to the current time. Include the `resolution` parameter to display the performance data at the specified resolution. If not specified, `resolution` defaults to the lowest valid resolution.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique resource IDs specified. Enter multiple resource IDs in comma-separated format. The `ids` or `names` parameter is required, but they cannot be set together.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        resolution: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The number of milliseconds between samples of historical data. For array-wide performance metrics (`/arrays/performance` endpoint), valid values are `1000` (1 second), `30000` (30 seconds), `300000` (5 minutes), `1800000` (30 minutes), `7200000` (2 hours), `28800000` (8 hours), and `86400000` (24 hours). For performance metrics on storage objects (`<object name>/performance` endpoint), such as volumes, valid values are `30000` (30 seconds), `300000` (5 minutes), `1800000` (30 minutes), `7200000` (2 hours), `28800000` (8 hours), and `86400000` (24 hours). For space metrics, (`<object name>/space` endpoint), valid values are `300000` (5 minutes), `1800000` (30 minutes), `7200000` (2 hours), `28800000` (8 hours), and `86400000` (24 hours). Include the `start_time` parameter to display the performance data starting at the specified start time. If `start_time` is not specified, the start time will default to one resolution before the end time, meaning that the most recent sample of performance data will be displayed. Include the `end_time` parameter to display the performance data until the specified end time. If `end_time`is not specified, the end time will default to the current time. If the `resolution` parameter is not specified but either the `start_time` or `end_time` parameter is, then `resolution` will default to the lowest valid resolution.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        start_time: Annotated[Optional[StrictInt], Field(description="Displays historical performance data for the specified time window, where `start_time` is the beginning of the time window, and `end_time` is the end of the time window. The `start_time` and `end_time` parameters are specified in milliseconds since the UNIX epoch. If `start_time` is not specified, the start time will default to one resolution before the end time, meaning that the most recent sample of performance data will be displayed. If `end_time`is not specified, the end time will default to the current time. Include the `resolution` parameter to display the performance data at the specified resolution. If not specified, `resolution` defaults to the lowest valid resolution.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        total_only: Annotated[Optional[StrictBool], Field(description="If set to `true`, returns the aggregate value of all items after filtering. Where it makes more sense, the average value is displayed instead. The values are displayed for each name where meaningful. If `total_only=true`, the `items` list will be empty.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """List volume performance data
        
        Returns real-time and historical performance data, real-time latency data, and average I/O sizes for each volume and and as a total of all volumes across the entire array.
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param destroyed: If set to `true`, lists only destroyed objects that are in the eradication
                        pending state. If set to `false`, lists only objects that are not destroyed.
                        For destroyed objects, the time remaining is displayed in milliseconds.
        :type destroyed: bool
        :param end_time: Displays historical performance data for the specified time window, where
                        `start_time` is the beginning of the time window, and `end_time` is the end
                        of the time window. The `start_time` and `end_time` parameters are specified
                        in milliseconds since the UNIX epoch. If `start_time` is not specified, the
                        start time will default to one resolution before the end time, meaning that
                        the most recent sample of performance data will be displayed. If
                        `end_time`is not specified, the end time will default to the current time.
                        Include the `resolution` parameter to display the performance data at the
                        specified resolution. If not specified, `resolution` defaults to the lowest
                        valid resolution.
        :type end_time: int
        :param filter: Narrows down the results to only the response objects that satisfy the filter
                    criteria.
        :type filter: str
        :param ids: Performs the operation on the unique resource IDs specified. Enter multiple
                    resource IDs in comma-separated format. The `ids` or `names` parameter is
                    required, but they cannot be set together.
        :type ids: List[str]
        :param limit: Limits the size of the response to the specified number of objects on each page.
                    To return the total number of resources, set `limit=0`. The total number of
                    resources is returned as a `total_item_count` value. If the page size
                    requested is larger than the system maximum limit, the server returns the
                    maximum limit, disregarding the requested page size.
        :type limit: int
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param offset: The starting position based on the results of the query in relation to the full
                    set of response objects returned.
        :type offset: int
        :param resolution: The number of milliseconds between samples of historical data. For array-wide
                        performance metrics (`/arrays/performance` endpoint), valid values are
                        `1000` (1 second), `30000` (30 seconds), `300000` (5 minutes), `1800000` (30
                        minutes), `7200000` (2 hours), `28800000` (8 hours), and `86400000` (24
                        hours). For performance metrics on storage objects (`<object
                        name>/performance` endpoint), such as volumes, valid values are `30000` (30
                        seconds), `300000` (5 minutes), `1800000` (30 minutes), `7200000` (2 hours),
                        `28800000` (8 hours), and `86400000` (24 hours). For space metrics,
                        (`<object name>/space` endpoint), valid values are `300000` (5 minutes),
                        `1800000` (30 minutes), `7200000` (2 hours), `28800000` (8 hours), and
                        `86400000` (24 hours). Include the `start_time` parameter to display the
                        performance data starting at the specified start time. If `start_time` is
                        not specified, the start time will default to one resolution before the end
                        time, meaning that the most recent sample of performance data will be
                        displayed. Include the `end_time` parameter to display the performance data
                        until the specified end time. If `end_time`is not specified, the end time
                        will default to the current time. If the `resolution` parameter is not
                        specified but either the `start_time` or `end_time` parameter is, then
                        `resolution` will default to the lowest valid resolution.
        :type resolution: int
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in
                    the response by which to sort. Sorting can be performed on any of the names
                    in the response, and the objects can be sorted in ascending or descending
                    order. By default, the response objects are sorted in ascending order. To
                    sort in descending order, append the minus sign (`-`) to the name. A single
                    request can be sorted on multiple objects. For example, you can sort all
                    volumes from largest to smallest volume size, and then sort volumes of the
                    same size in ascending order by volume name. To sort on multiple names, list
                    the names as comma-separated values.
        :type sort: List[str]
        :param start_time: Displays historical performance data for the specified time window, where
                        `start_time` is the beginning of the time window, and `end_time` is the end
                        of the time window. The `start_time` and `end_time` parameters are specified
                        in milliseconds since the UNIX epoch. If `start_time` is not specified, the
                        start time will default to one resolution before the end time, meaning that
                        the most recent sample of performance data will be displayed. If
                        `end_time`is not specified, the end time will default to the current time.
                        Include the `resolution` parameter to display the performance data at the
                        specified resolution. If not specified, `resolution` defaults to the lowest
                        valid resolution.
        :type start_time: int
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters
                                is calculated and returned in the response. If set to `false`, the
                                `total_item_count` is `null` in the response. This may speed up queries
                                where the `total_item_count` is large. If not specified, defaults to
                                `false`.
        :type total_item_count: bool
        :param total_only: If set to `true`, returns the aggregate value of all items after filtering.
                        Where it makes more sense, the average value is displayed instead. The
                        values are displayed for each name where meaningful. If `total_only=true`,
                        the `items` list will be empty.
        :type total_only: bool
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            destroyed=destroyed,
            end_time=end_time,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            resolution=resolution,
            sort=sort,
            start_time=start_time,
            total_item_count=total_item_count,
            total_only=total_only,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('VolumesApi', 'api20_volumes_performance_get_with_http_info', kwargs)

    def post_volumes(
        self,
        volume: 'models.VolumePost',
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        overwrite: Annotated[Optional[StrictBool], Field(description="If set to `true`, overwrites an existing object during an object copy operation. If set to `false` or not set at all and the target name is an existing object, the copy operation fails. Required if the `source` body parameter is set and the source overwrites an existing object during the copy operation.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Create a volume
        
        Create one or more virtual storage volumes of the specified size. If `provisioned` is not specified, the size of the new volume defaults to 1 MB in size. The `names` query parameter is required.
        
        :param volume: (required)
        :type volume: VolumePost
        :param references: A list of references to query for. Overrides names keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param overwrite: If set to `true`, overwrites an existing object during an object copy operation.
                        If set to `false` or not set at all and the target name is an existing
                        object, the copy operation fails. Required if the `source` body parameter is
                        set and the source overwrites an existing object during the copy operation.
        :type overwrite: bool
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            volume=volume,
            authorization=authorization,
            x_request_id=x_request_id,
            names=names,
            overwrite=overwrite,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['names'], kwargs)
        _fixup_list_type_params(['names'], kwargs)
        return self._call_api('VolumesApi', 'api20_volumes_post_with_http_info', kwargs)

    def get_volumes_space(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        destroyed: Annotated[Optional[StrictBool], Field(description="If set to `true`, lists only destroyed objects that are in the eradication pending state. If set to `false`, lists only objects that are not destroyed. For destroyed objects, the time remaining is displayed in milliseconds.")] = None,
        end_time: Annotated[Optional[StrictInt], Field(description="Displays historical performance data for the specified time window, where `start_time` is the beginning of the time window, and `end_time` is the end of the time window. The `start_time` and `end_time` parameters are specified in milliseconds since the UNIX epoch. If `start_time` is not specified, the start time will default to one resolution before the end time, meaning that the most recent sample of performance data will be displayed. If `end_time`is not specified, the end time will default to the current time. Include the `resolution` parameter to display the performance data at the specified resolution. If not specified, `resolution` defaults to the lowest valid resolution.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique resource IDs specified. Enter multiple resource IDs in comma-separated format. The `ids` or `names` parameter is required, but they cannot be set together.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        resolution: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The number of milliseconds between samples of historical data. For array-wide performance metrics (`/arrays/performance` endpoint), valid values are `1000` (1 second), `30000` (30 seconds), `300000` (5 minutes), `1800000` (30 minutes), `7200000` (2 hours), `28800000` (8 hours), and `86400000` (24 hours). For performance metrics on storage objects (`<object name>/performance` endpoint), such as volumes, valid values are `30000` (30 seconds), `300000` (5 minutes), `1800000` (30 minutes), `7200000` (2 hours), `28800000` (8 hours), and `86400000` (24 hours). For space metrics, (`<object name>/space` endpoint), valid values are `300000` (5 minutes), `1800000` (30 minutes), `7200000` (2 hours), `28800000` (8 hours), and `86400000` (24 hours). Include the `start_time` parameter to display the performance data starting at the specified start time. If `start_time` is not specified, the start time will default to one resolution before the end time, meaning that the most recent sample of performance data will be displayed. Include the `end_time` parameter to display the performance data until the specified end time. If `end_time`is not specified, the end time will default to the current time. If the `resolution` parameter is not specified but either the `start_time` or `end_time` parameter is, then `resolution` will default to the lowest valid resolution.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        start_time: Annotated[Optional[StrictInt], Field(description="Displays historical performance data for the specified time window, where `start_time` is the beginning of the time window, and `end_time` is the end of the time window. The `start_time` and `end_time` parameters are specified in milliseconds since the UNIX epoch. If `start_time` is not specified, the start time will default to one resolution before the end time, meaning that the most recent sample of performance data will be displayed. If `end_time`is not specified, the end time will default to the current time. Include the `resolution` parameter to display the performance data at the specified resolution. If not specified, `resolution` defaults to the lowest valid resolution.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        total_only: Annotated[Optional[StrictBool], Field(description="If set to `true`, returns the aggregate value of all items after filtering. Where it makes more sense, the average value is displayed instead. The values are displayed for each name where meaningful. If `total_only=true`, the `items` list will be empty.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """List volume space information
        
        Return provisioned size and physical storage consumption data for each volume.
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param destroyed: If set to `true`, lists only destroyed objects that are in the eradication
                        pending state. If set to `false`, lists only objects that are not destroyed.
                        For destroyed objects, the time remaining is displayed in milliseconds.
        :type destroyed: bool
        :param end_time: Displays historical performance data for the specified time window, where
                        `start_time` is the beginning of the time window, and `end_time` is the end
                        of the time window. The `start_time` and `end_time` parameters are specified
                        in milliseconds since the UNIX epoch. If `start_time` is not specified, the
                        start time will default to one resolution before the end time, meaning that
                        the most recent sample of performance data will be displayed. If
                        `end_time`is not specified, the end time will default to the current time.
                        Include the `resolution` parameter to display the performance data at the
                        specified resolution. If not specified, `resolution` defaults to the lowest
                        valid resolution.
        :type end_time: int
        :param filter: Narrows down the results to only the response objects that satisfy the filter
                    criteria.
        :type filter: str
        :param ids: Performs the operation on the unique resource IDs specified. Enter multiple
                    resource IDs in comma-separated format. The `ids` or `names` parameter is
                    required, but they cannot be set together.
        :type ids: List[str]
        :param limit: Limits the size of the response to the specified number of objects on each page.
                    To return the total number of resources, set `limit=0`. The total number of
                    resources is returned as a `total_item_count` value. If the page size
                    requested is larger than the system maximum limit, the server returns the
                    maximum limit, disregarding the requested page size.
        :type limit: int
        :param names: Performs the operation on the unique name specified. Enter multiple names in
                    comma-separated format. For example, `name01,name02`.
        :type names: List[str]
        :param offset: The starting position based on the results of the query in relation to the full
                    set of response objects returned.
        :type offset: int
        :param resolution: The number of milliseconds between samples of historical data. For array-wide
                        performance metrics (`/arrays/performance` endpoint), valid values are
                        `1000` (1 second), `30000` (30 seconds), `300000` (5 minutes), `1800000` (30
                        minutes), `7200000` (2 hours), `28800000` (8 hours), and `86400000` (24
                        hours). For performance metrics on storage objects (`<object
                        name>/performance` endpoint), such as volumes, valid values are `30000` (30
                        seconds), `300000` (5 minutes), `1800000` (30 minutes), `7200000` (2 hours),
                        `28800000` (8 hours), and `86400000` (24 hours). For space metrics,
                        (`<object name>/space` endpoint), valid values are `300000` (5 minutes),
                        `1800000` (30 minutes), `7200000` (2 hours), `28800000` (8 hours), and
                        `86400000` (24 hours). Include the `start_time` parameter to display the
                        performance data starting at the specified start time. If `start_time` is
                        not specified, the start time will default to one resolution before the end
                        time, meaning that the most recent sample of performance data will be
                        displayed. Include the `end_time` parameter to display the performance data
                        until the specified end time. If `end_time`is not specified, the end time
                        will default to the current time. If the `resolution` parameter is not
                        specified but either the `start_time` or `end_time` parameter is, then
                        `resolution` will default to the lowest valid resolution.
        :type resolution: int
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in
                    the response by which to sort. Sorting can be performed on any of the names
                    in the response, and the objects can be sorted in ascending or descending
                    order. By default, the response objects are sorted in ascending order. To
                    sort in descending order, append the minus sign (`-`) to the name. A single
                    request can be sorted on multiple objects. For example, you can sort all
                    volumes from largest to smallest volume size, and then sort volumes of the
                    same size in ascending order by volume name. To sort on multiple names, list
                    the names as comma-separated values.
        :type sort: List[str]
        :param start_time: Displays historical performance data for the specified time window, where
                        `start_time` is the beginning of the time window, and `end_time` is the end
                        of the time window. The `start_time` and `end_time` parameters are specified
                        in milliseconds since the UNIX epoch. If `start_time` is not specified, the
                        start time will default to one resolution before the end time, meaning that
                        the most recent sample of performance data will be displayed. If
                        `end_time`is not specified, the end time will default to the current time.
                        Include the `resolution` parameter to display the performance data at the
                        specified resolution. If not specified, `resolution` defaults to the lowest
                        valid resolution.
        :type start_time: int
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters
                                is calculated and returned in the response. If set to `false`, the
                                `total_item_count` is `null` in the response. This may speed up queries
                                where the `total_item_count` is large. If not specified, defaults to
                                `false`.
        :type total_item_count: bool
        :param total_only: If set to `true`, returns the aggregate value of all items after filtering.
                        Where it makes more sense, the average value is displayed instead. The
                        values are displayed for each name where meaningful. If `total_only=true`,
                        the `items` list will be empty.
        :type total_only: bool
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                 be set to none and raw_data will store the
                 HTTP response body without reading/decoding.
                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                 object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                 number provided, it will be total request
                 timeout. It can also be a pair (tuple) of
                 (connection, read) timeouts.
        :type _request_timeout: int or (float, float), optional
        
        :return: ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        :rtype: [Union[ValidResponse, ErrorResponse]]
        
        :raises: PureError: If calling the API fails.
        :raises: ValueError: If a parameter is of an invalid type.
        :raises: TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            destroyed=destroyed,
            end_time=end_time,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            resolution=resolution,
            sort=sort,
            start_time=start_time,
            total_item_count=total_item_count,
            total_only=total_only,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('VolumesApi', 'api20_volumes_space_get_with_http_info', kwargs)

    def _get_base_url(self, target):
        return 'https://{}'.format(target)

    def _get_api_token_endpoint(self, target):
        return self._get_base_url(target) + '/api/2.0/login'

    def _get_api_token_dispose_endpoint(self, target):
        return self._get_base_url(target) + '/api/2.0/logout'

    def _set_agent_header(self):
        """
        Set the user-agent header of the internal client.
        """
        self._api_client.set_default_header(Headers.user_agent, self._api_client.user_agent)

    def _set_auth_header(self, refresh=False):
        """
        Set the authorization or x-auth-token header of the internal client with the access
        token.

        Args:
            refresh (bool, optional): Whether to retrieve a new access token.
                Defaults to False.

        Raises:
            PureError: If there was an error retrieving the access token.
        """
        if isinstance(self._token_man, TokenManager):
            self._api_client.set_default_header(Headers.authorization,
                                                self._token_man.get_header(refresh=refresh))
        else:
            self._api_client.set_default_header(Headers.x_auth_token,
                                                self._token_man.get_session_token(refresh=refresh))

    def _call_api(self, api_class_name, api_function_name, kwargs):
        """
        Call the API function and process the response. May call the API
        repeatedly if the request failed for a reason that may not persist in
        the next call.

        Args:
            api_class_name (str): Swagger-generated api class to call.
            api_function_name (str): Swagger-generated function to call.
            kwargs (dict): kwargs to pass to the function.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        kwargs['_request_timeout'] = self._timeout
        if kwargs.get('x_request_id') is None:
            kwargs['x_request_id'] = str(uuid.uuid4())

        if kwargs.get('authorization') is not None:
            warnings.warn("authorization parameter is deprecated, and will be removed soon.", DeprecationWarning)
        retries = self._retries
        api_function = getattr(self.__get_api_instance(api_class_name), api_function_name)
        while True:
            try:
                response = api_function(**kwargs)
                # Call was successful (200)
                return self._create_valid_response(response, api_function, kwargs)
            except ApiException as error:
                # If no chance for retries, return the error
                if retries == 0:
                    return self._create_error_response(error)
                # If bad request or not found, return the error (it will never work)
                elif error.status in [400, 404]:
                    return self._create_error_response(error)
                # If authentication error, reset access token and retry
                elif error.status in [401, 403]:
                    self._set_auth_header(refresh=True)
                # If rate limit error, wait the proper time and try again
                elif error.status == 429:
                    # If the the minute limit hit, wait that long
                    if (int(error.headers.get(Headers.x_ratelimit_remaining_min))
                            == int(error.headers.get(Headers.x_ratelimit_min))):
                        time.sleep(60)
                    # Otherwise it was the second limit and only wait a second
                    time.sleep(1)
                # If some internal server error we know nothing about, return
                elif error.status == 500:
                    return self._create_error_response(error)
                # If internal server errors that has to do with timeouts, try again
                elif error.status > 500:
                    pass
                # If error with the swagger client, raise the error
                else:
                    raise PureError(error)
            retries = retries - 1

    def __get_api_instance(self, api_class):
        """
        Get the API instance for the given class.

        Args:
            api_class (class): Swagger-generated api class.

        Returns:
            class: API instance for the given class.
        """
        if api_class not in self.__apis_instances:
            self.__apis_instances[api_class] = getattr(api, api_class)(self._api_client)
        return self.__apis_instances[api_class]

    def _create_valid_response(self, response: ApiResponse, endpoint, kwargs):
        """
        Create a ValidResponse from a Swagger response.

        Args:
            response (ApiResponse):
                Body, status, header tuple as returned from Swagger client.
            endpoint (function):
                The function of the Swagger client that was called.
            kwargs (dict):
                The processed kwargs that were passed to the endpoint function.

        Returns:
            ValidResponse
        """
        body = response.data
        headers = response.headers
        continuation_token = getattr(body, "continuation_token", None)
        total_item_count = getattr(body, "total_item_count", None)
        total = getattr(body, "total", None)
        more_items_remaining = getattr(body, "more_items_remaining", None)
        errors = getattr(body, "errors", None)
        items = None
        if body is not None:
            items = iter(ItemIterator(self, endpoint, kwargs,
                                      continuation_token, total_item_count,
                                      body.items,
                                      headers.get(Headers.x_request_id, None),
                                      more_items_remaining or False))
        return ValidResponse(response.status_code, continuation_token, total_item_count,
                             items, headers, total, more_items_remaining, errors=errors)

    def _create_error_response(self, error):
        """
        Create an ErrorResponse from a Swagger error.

        Args:
            error (ApiException):
                Error returned by Swagger client.

        Returns:
            ErrorResponse
        """
        status = error.status
        try:
            body = json.loads(error.body)
        except Exception:
            body = {}
        if status in [403, 429]:
            # Parse differently if the error message came from kong
            errors = [ApiError(None, body.get(Responses.message, None), None)]
        else:
            errors = [ApiError(err.get(Responses.context, None),
                               err.get(Responses.message, None),
                               err.get(Responses.location_context, None))
                      for err in body.get(Responses.errors, {})]
        return ErrorResponse(status, errors, headers=error.headers)


def _process_references(
    references: Optional[Union[ReferenceType, List[ReferenceType]]],
    params: List[str],
    kwargs: Dict[str, Any]
) -> None:

    """Process reference objects into a list of ids or names.
    Removes ids and names arguments.

    :param references: The references from which to extract ids or names.
    :type references: ReferenceType or List[ReferenceType], optional

    :param params: The parameters to be overridden.
    :type params: List[str]

    :param kwargs: The kwargs to process.
    :type kwargs: Dict[str, Any]

    :raise PureError: If a reference does not have an id or name.

    """
    if references is not None:
        if not isinstance(references, list):
            references = [references]
        for param in params:
            kwargs.pop(param, None)
        all_have_id = all(ref.id is not None for ref in references)
        all_have_name = all(ref.name is not None for ref in references)
        id_param = [param for param in params if param.endswith("ids")]
        name_param = [param for param in params if param.endswith("names")]
        if all_have_id and len(id_param) > 0:
            kwargs[id_param[0]] = [ref.id for ref in references]
        elif all_have_name and len(name_param) > 0:
            kwargs[name_param[0]] = [ref.name for ref in references]
        else:
            raise PureError('Invalid reference for {}'.format(", ".join(params)))


def _fixup_list_type_params(
    params: List[str],
    kwargs: Dict[str, Any]
) -> None:

    """Process object into a list if it expected to be list type.

    :param params: The parameters to be overridden.
    :type params: List[str]

    :param kwargs: The kwargs to process.
    :type kwargs: Dict[str, Any]

    """
    for _param in params:
        _value = kwargs.get(_param, None)
        if _value is not None and not isinstance(_value, list):
            _param_type = type(_value).__name__.replace("'", '')
            warnings.warn(f"'{_param}' parameter, invalid type: expected List[{_param_type}] but received {_param_type}, converting to list. Please revisit code.", SyntaxWarning)
            kwargs[_param] = [_value]
