import json
import os
import time
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
from pypureclient.responses import ValidResponse, ErrorResponse, ApiError, ItemIterator, ResponseHeaders
from pypureclient.token_manager import TokenManager

from .api_client import ApiClient
from .api_response import ApiResponse
from .rest import ApiException
from .configuration import Configuration

from . import api
from . import models

class Client(object):
    """
    A client for making REST API calls to Pure1.
    """
    APP_ID_KEY = 'app_id'
    APP_ID_ENV = 'PURE1_APP_ID'
    ID_TOKEN_KEY = 'id_token'
    ID_TOKEN_ENV = 'PURE1_ID_TOKEN'
    PRIVATE_KEY_FILE_KEY = 'private_key_file'
    PRIVATE_KEY_FILE_ENV = 'PURE1_PRIVATE_KEY_FILE'
    PRIVATE_KEY_PASSWORD_KEY = 'private_key_password'
    PRIVATE_KEY_PASSWORD_ENV = 'PURE1_PRIVATE_KEY_PASSWORD'
    RETRIES_KEY = 'retries'
    RETRIES_DEFAULT = 5
    TOKEN_ENDPOINT = 'https://api.pure1.purestorage.com/oauth2/1.0/token'
    TIMEOUT_KEY = 'timeout'
    TIMEOUT_DEFAULT = 15.0
    USER_AGENT = DEFAULT_USER_AGENT

    def __init__(self, **kwargs):
        """
        Initialize a Pure1 Client.

        Keyword args:
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
        app_id = (kwargs.get(self.APP_ID_KEY)
                  if self.APP_ID_KEY in kwargs
                  else os.getenv(self.APP_ID_ENV))
        private_key_file = (kwargs.get(self.PRIVATE_KEY_FILE_KEY)
                            if self.PRIVATE_KEY_FILE_KEY in kwargs
                            else os.getenv(self.PRIVATE_KEY_FILE_ENV))
        private_key_password = (kwargs.get(self.PRIVATE_KEY_PASSWORD_KEY)
                                if self.PRIVATE_KEY_PASSWORD_KEY in kwargs
                                else os.getenv(self.PRIVATE_KEY_PASSWORD_ENV))
        id_token = (kwargs.get(self.ID_TOKEN_KEY)
                    if self.ID_TOKEN_KEY in kwargs
                    else os.getenv(self.ID_TOKEN_ENV))
        self._token_man = TokenManager(self.TOKEN_ENDPOINT,
                                       id_token=id_token,
                                       private_key_file=private_key_file,
                                       private_key_password=private_key_password,
                                       payload={'iss': app_id})
        # Read timeout and retries from kwargs
        self._retries = (kwargs.get(self.RETRIES_KEY)
                         if self.RETRIES_KEY in kwargs
                         else self.RETRIES_DEFAULT)
        self._timeout = (kwargs.get(self.TIMEOUT_KEY)
                         if (self.TIMEOUT_KEY in kwargs and
                             isinstance(kwargs.get(self.TIMEOUT_KEY), (tuple, float)))
                         else self.TIMEOUT_DEFAULT)
        # Instantiate the client and authorize it
        self._api_client = ApiClient()
        self._api_client.configuration.host = "https://api.pure1.purestorage.com"
        self._set_agent_header()
        self._set_auth_header()
        self.__apis_instances = {}

    def __del__(self):
        # Cleanup this REST API client resources
        _api_client_attr = getattr(self, '_api_client', None) # using getattr to avoid raising exception, if we failed too early
        if _api_client_attr:
            _api_client_attr.close()

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

    def get_alerts(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get alerts  # noqa: E501
        
        Retrieves information about alerts generated by Pure1-monitored appliances.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_alerts_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('AlertsApi', 'api12_alerts_get_with_http_info', kwargs)

    def get_arrays(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        fqdns: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource FQDNs. If there is not at least one resource that matches each `fqdn` element, an error is returned. Single quotes are required around all strings.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get arrays  # noqa: E501
        
        Retrieves information about FlashArray and FlashBlade storage appliances.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_arrays_get_with_http_info(authorization, x_request_id, continuation_token, filter, fqdns, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param fqdns: A comma-separated list of resource FQDNs. If there is not at least one resource
                    that matches each `fqdn` element, an error is returned. Single quotes are
                    required around all strings.
        :type fqdns: List[str]
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            fqdns=fqdns,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['fqdns', 'ids', 'names', 'sort'], kwargs)
        return self._call_api('ArraysApi', 'api12_arrays_get_with_http_info', kwargs)

    def get_arrays_support_contracts(
        self,
        resources: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        resource_fqdns: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource FQDNs. If there is not at least one resource that matches each `resource_fqdn` element, an error is returned. Single quotes are required around all strings.")] = None,
        resource_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `resource_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        resource_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `resource_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get array support contracts  # noqa: E501
        
        Retrieves the support contracts associated with arrays.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_arrays_support_contracts_get_with_http_info(authorization, x_request_id, continuation_token, filter, limit, offset, resource_fqdns, resource_ids, resource_names, sort, async_req=True)
        >>> result = thread.get()
        
        :param resources: A list of resources to query for. Overrides resource_ids and resource_names keyword arguments.
        :type resources: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param resource_fqdns: A comma-separated list of resource FQDNs. If there is not at least one resource
                            that matches each `resource_fqdn` element, an error is returned. Single
                            quotes are required around all strings.
        :type resource_fqdns: List[str]
        :param resource_ids: A comma-separated list of resource IDs. If there is not at least one resource
                            that matches each `resource_id` element, an error is returned. Single
                            quotes are required around all strings.
        :type resource_ids: List[str]
        :param resource_names: A comma-separated list of resource names. If there is not at least one resource
                            that matches each `resource_name` element, an error is returned. Single
                            quotes are required around all strings.
        :type resource_names: List[str]
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            offset=offset,
            resource_fqdns=resource_fqdns,
            resource_ids=resource_ids,
            resource_names=resource_names,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(resources, ['resource_ids', 'resource_names'], kwargs)
        _fixup_list_type_params(['resource_fqdns', 'resource_ids', 'resource_names', 'sort'], kwargs)
        return self._call_api('ArraysApi', 'api12_arrays_support_contracts_get_with_http_info', kwargs)

    def put_arrays_tags(
        self,
        tag_put: conlist('models.TagPut'),
        resources: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        namespaces: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of namespaces. Single quotes are required around all strings.")] = None,
        resource_ids: Annotated[Optional[conlist(StrictStr)], Field(description="REQUIRED: either `resource_ids` or `resource_names`. A comma-separated list of resource IDs. If there is not at least one resource that matches each `resource_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        resource_names: Annotated[Optional[conlist(StrictStr)], Field(description="REQUIRED: either `resource_ids` or `resource_names`. A comma-separated list of resource names. If there is not at least one resource that matches each `resource_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Create or update array tags  # noqa: E501
        
        Creates or updates array tags contextual to Pure1 only.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_arrays_tags_batch_put_with_http_info(tag_put, authorization, x_request_id, namespaces, resource_ids, resource_names, async_req=True)
        >>> result = thread.get()
        
        :param tag_put: (required)
        :type tag_put: List[models.TagPut]
        :param resources: A list of resources to query for. Overrides resource_ids and resource_names keyword arguments.
        :type resources: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param namespaces: A comma-separated list of namespaces. Single quotes are required around all
                        strings.
        :type namespaces: List[str]
        :param resource_ids: REQUIRED: either `resource_ids` or `resource_names`. A comma-separated list of resource
                                    IDs. If there is not at least one resource that matches each
                                    `resource_id` element, an error is returned. Single quotes are required
                                    around all strings.
        :type resource_ids: List[str]
        :param resource_names: REQUIRED: either `resource_ids` or `resource_names`. A comma-separated list of resource
                                        names. If there is not at least one resource that matches each
                                        `resource_name` element, an error is returned. Single quotes are
                                        required around all strings.
        :type resource_names: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            tag_put=tag_put,
            authorization=authorization,
            x_request_id=x_request_id,
            namespaces=namespaces,
            resource_ids=resource_ids,
            resource_names=resource_names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(resources, ['resource_ids', 'resource_names'], kwargs)
        _fixup_list_type_params(['tag_put', 'namespaces', 'resource_ids', 'resource_names'], kwargs)
        return self._call_api('ArraysApi', 'api12_arrays_tags_batch_put_with_http_info', kwargs)

    def delete_arrays_tags(
        self,
        resources: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        keys: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of tag keys. Single quotes are required around all strings.")] = None,
        namespaces: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of namespaces. Single quotes are required around all strings.")] = None,
        resource_ids: Annotated[Optional[conlist(StrictStr)], Field(description="REQUIRED: either `resource_ids` or `resource_names`. A comma-separated list of resource IDs. If there is not at least one resource that matches each `resource_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        resource_names: Annotated[Optional[conlist(StrictStr)], Field(description="REQUIRED: either `resource_ids` or `resource_names`. A comma-separated list of resource names. If there is not at least one resource that matches each `resource_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Delete array tags  # noqa: E501
        
        Deletes array tags from Pure1.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_arrays_tags_delete_with_http_info(authorization, x_request_id, keys, namespaces, resource_ids, resource_names, async_req=True)
        >>> result = thread.get()
        
        :param resources: A list of resources to query for. Overrides resource_ids and resource_names keyword arguments.
        :type resources: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param keys: A comma-separated list of tag keys. Single quotes are required around all
                    strings.
        :type keys: List[str]
        :param namespaces: A comma-separated list of namespaces. Single quotes are required around all
                        strings.
        :type namespaces: List[str]
        :param resource_ids: REQUIRED: either `resource_ids` or `resource_names`. A comma-separated list of resource
                                    IDs. If there is not at least one resource that matches each
                                    `resource_id` element, an error is returned. Single quotes are required
                                    around all strings.
        :type resource_ids: List[str]
        :param resource_names: REQUIRED: either `resource_ids` or `resource_names`. A comma-separated list of resource
                                        names. If there is not at least one resource that matches each
                                        `resource_name` element, an error is returned. Single quotes are
                                        required around all strings.
        :type resource_names: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            keys=keys,
            namespaces=namespaces,
            resource_ids=resource_ids,
            resource_names=resource_names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(resources, ['resource_ids', 'resource_names'], kwargs)
        _fixup_list_type_params(['keys', 'namespaces', 'resource_ids', 'resource_names'], kwargs)
        return self._call_api('ArraysApi', 'api12_arrays_tags_delete_with_http_info', kwargs)

    def get_arrays_tags(
        self,
        resources: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        keys: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of tag keys. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        namespaces: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of namespaces. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        resource_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `resource_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        resource_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `resource_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get array tags  # noqa: E501
        
        Retrieves the tags associated with specified arrays.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_arrays_tags_get_with_http_info(authorization, x_request_id, continuation_token, filter, keys, limit, namespaces, offset, resource_ids, resource_names, async_req=True)
        >>> result = thread.get()
        
        :param resources: A list of resources to query for. Overrides resource_ids and resource_names keyword arguments.
        :type resources: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param keys: A comma-separated list of tag keys. Single quotes are required around all
                    strings.
        :type keys: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param namespaces: A comma-separated list of namespaces. Single quotes are required around all
                        strings.
        :type namespaces: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param resource_ids: A comma-separated list of resource IDs. If there is not at least one resource
                            that matches each `resource_id` element, an error is returned. Single
                            quotes are required around all strings.
        :type resource_ids: List[str]
        :param resource_names: A comma-separated list of resource names. If there is not at least one resource
                            that matches each `resource_name` element, an error is returned. Single
                            quotes are required around all strings.
        :type resource_names: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            keys=keys,
            limit=limit,
            namespaces=namespaces,
            offset=offset,
            resource_ids=resource_ids,
            resource_names=resource_names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(resources, ['resource_ids', 'resource_names'], kwargs)
        _fixup_list_type_params(['keys', 'namespaces', 'resource_ids', 'resource_names'], kwargs)
        return self._call_api('ArraysApi', 'api12_arrays_tags_get_with_http_info', kwargs)

    def get_audits(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get audits  # noqa: E501
        
        Retrieves audit objects.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_audits_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('AuditsApi', 'api12_audits_get_with_http_info', kwargs)

    def get_blades(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get blades  # noqa: E501
        
        Retrieves information about FlashBlade blades.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_blades_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('BladesApi', 'api12_blades_get_with_http_info', kwargs)

    def get_bucket_replica_links(
        self,
        targets: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        sources: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        members: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        member_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A list of member IDs. Member IDs separated by a `+` indicate that both members must be present in each element. Member IDs separated by a `,` indicate that at least one member must be present in each element. If there is not at least one resource that matches each `member_id` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of member IDs separated by a `+` must be entered in the same item cell.")] = None,
        member_names: Annotated[Optional[conlist(StrictStr)], Field(description="A list of member names. Member names separated by a `+` indicate that both members must be present in each element. Member names separated by a `,` indicate that at least one member must be present in each element. If there is not at least one resource that matches each `member_name` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of member names separated by a `+` must be entered in the same item cell.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        source_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A list of source IDs. Source IDs separated by a `+` indicate that both sources must be present in each element. Source IDs separated by a `,` indicate that at least one source must be present in each element. If there is not at least one resource that matches each `source_id` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of source IDs separated by a `+` must be entered in the same item cell.")] = None,
        source_names: Annotated[Optional[conlist(StrictStr)], Field(description="A list of source names. Source names separated by a `+` indicate that both sources must be present in each element. Source names separated by a `,` indicate that at least one source must be present in each element. If there is not at least one resource that matches each `source_name` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of source names separated by a `+` must be entered in the same item cell.")] = None,
        target_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A list of target IDs. Target IDs separated by a `+` indicate that both targets must be present in each element. Target IDs separated by a `,` indicate that at least one target must be present in each element. If there is not at least one resource that matches each `target_id` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of target IDs separated by a `+` must be entered in the same item cell.")] = None,
        target_names: Annotated[Optional[conlist(StrictStr)], Field(description="A list of target names. Target names separated by a `+` indicate that both targets must be present in each element. Target names separated by a `,` indicate that at least one target must be present in each element. If there is not at least one resource that matches each `target_name` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of target names separated by a `+` must be entered in the same item cell.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get bucket replica links  # noqa: E501
        
        Retrieves information about bucket replica links.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_bucket_replica_links_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, member_ids, member_names, offset, sort, source_ids, source_names, target_ids, target_names, async_req=True)
        >>> result = thread.get()
        
        :param targets: A list of targets to query for. Overrides target_ids and target_names keyword arguments.
        :type targets: ReferenceType or List[ReferenceType], optional
        :param sources: A list of sources to query for. Overrides source_ids and source_names keyword arguments.
        :type sources: ReferenceType or List[ReferenceType], optional
        :param members: A list of members to query for. Overrides member_ids and member_names keyword arguments.
        :type members: ReferenceType or List[ReferenceType], optional
        :param references: A list of references to query for. Overrides ids keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param member_ids: A list of member IDs. Member IDs separated by a `+` indicate that both members
                        must be present in each element. Member IDs separated by a `,` indicate that
                        at least one member must be present in each element. If there is not at
                        least one resource that matches each `member_id` element, an error is
                        returned. Single quotes are required around all strings. When using Try it
                        Out in Swagger, a list of member IDs separated by a `+` must be entered in
                        the same item cell.
        :type member_ids: List[str]
        :param member_names: A list of member names. Member names separated by a `+` indicate that both
                            members must be present in each element. Member names separated by a `,`
                            indicate that at least one member must be present in each element. If there
                            is not at least one resource that matches each `member_name` element, an
                            error is returned. Single quotes are required around all strings. When
                            using Try it Out in Swagger, a list of member names separated by a `+` must
                            be entered in the same item cell.
        :type member_names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
        :param source_ids: A list of source IDs. Source IDs separated by a `+` indicate that both sources
                        must be present in each element. Source IDs separated by a `,` indicate that
                        at least one source must be present in each element. If there is not at
                        least one resource that matches each `source_id` element, an error is
                        returned. Single quotes are required around all strings. When using Try it
                        Out in Swagger, a list of source IDs separated by a `+` must be entered in
                        the same item cell.
        :type source_ids: List[str]
        :param source_names: A list of source names. Source names separated by a `+` indicate that both
                            sources must be present in each element. Source names separated by a `,`
                            indicate that at least one source must be present in each element. If there
                            is not at least one resource that matches each `source_name` element, an
                            error is returned. Single quotes are required around all strings. When
                            using Try it Out in Swagger, a list of source names separated by a `+` must
                            be entered in the same item cell.
        :type source_names: List[str]
        :param target_ids: A list of target IDs. Target IDs separated by a `+` indicate that both targets
                        must be present in each element. Target IDs separated by a `,` indicate that
                        at least one target must be present in each element. If there is not at
                        least one resource that matches each `target_id` element, an error is
                        returned. Single quotes are required around all strings. When using Try it
                        Out in Swagger, a list of target IDs separated by a `+` must be entered in
                        the same item cell.
        :type target_ids: List[str]
        :param target_names: A list of target names. Target names separated by a `+` indicate that both
                            targets must be present in each element. Target names separated by a `,`
                            indicate that at least one target must be present in each element. If there
                            is not at least one resource that matches each `target_name` element, an
                            error is returned. Single quotes are required around all strings. When
                            using Try it Out in Swagger, a list of target names separated by a `+` must
                            be entered in the same item cell.
        :type target_names: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            offset=offset,
            sort=sort,
            source_ids=source_ids,
            source_names=source_names,
            target_ids=target_ids,
            target_names=target_names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids'], kwargs)
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        _process_references(targets, ['target_ids', 'target_names'], kwargs)
        _fixup_list_type_params(['ids', 'member_ids', 'member_names', 'sort', 'source_ids', 'source_names', 'target_ids', 'target_names'], kwargs)
        return self._call_api('BucketReplicaLinksApi', 'api12_bucket_replica_links_get_with_http_info', kwargs)

    def get_buckets(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get buckets  # noqa: E501
        
        Retrieves buckets.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_buckets_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('BucketsApi', 'api12_buckets_get_with_http_info', kwargs)

    def get_controllers(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get controllers  # noqa: E501
        
        Retrieves information about controllers.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_controllers_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('ControllersApi', 'api12_controllers_get_with_http_info', kwargs)

    def get_directories(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        file_systems: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        file_system_ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the file system ID specified. Enter multiple file system IDs in comma-separated format. The `file_system_ids` and `file_system_names` parameters cannot be provided together. Single quotes are required around all strings.")] = None,
        file_system_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the file system name specified. Enter multiple file system names in comma-separated format. For example, `filesystem1,filesystem2`. The `file_system_ids` and `file_system_names` parameters cannot be provided together. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get managed directories  # noqa: E501
        
        Retrieves information about FlashArray managed directory objects.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_directories_get_with_http_info(authorization, x_request_id, continuation_token, file_system_ids, file_system_names, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param file_systems: A list of file_systems to query for. Overrides file_system_ids and file_system_names keyword arguments.
        :type file_systems: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param file_system_ids: Performs the operation on the file system ID specified. Enter multiple file
                                system IDs in comma-separated format. The `file_system_ids` and
                                `file_system_names` parameters cannot be provided together. Single quotes
                                are required around all strings.
        :type file_system_ids: List[str]
        :param file_system_names: Performs the operation on the file system name specified. Enter multiple file
                                system names in comma-separated format. For example,
                                `filesystem1,filesystem2`. The `file_system_ids` and `file_system_names`
                                parameters cannot be provided together. Single quotes are required around
                                all strings.
        :type file_system_names: List[str]
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            file_system_ids=file_system_ids,
            file_system_names=file_system_names,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(file_systems, ['file_system_ids', 'file_system_names'], kwargs)
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['file_system_ids', 'file_system_names', 'ids', 'names', 'sort'], kwargs)
        return self._call_api('DirectoriesApi', 'api12_directories_get_with_http_info', kwargs)

    def get_drives(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get drives  # noqa: E501
        
        Retrieves information about FlashArray drives.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_drives_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('DrivesApi', 'api12_drives_get_with_http_info', kwargs)

    def get_file_system_replica_links(
        self,
        targets: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        sources: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        members: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        member_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A list of member IDs. Member IDs separated by a `+` indicate that both members must be present in each element. Member IDs separated by a `,` indicate that at least one member must be present in each element. If there is not at least one resource that matches each `member_id` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of member IDs separated by a `+` must be entered in the same item cell.")] = None,
        member_names: Annotated[Optional[conlist(StrictStr)], Field(description="A list of member names. Member names separated by a `+` indicate that both members must be present in each element. Member names separated by a `,` indicate that at least one member must be present in each element. If there is not at least one resource that matches each `member_name` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of member names separated by a `+` must be entered in the same item cell.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        source_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A list of source IDs. Source IDs separated by a `+` indicate that both sources must be present in each element. Source IDs separated by a `,` indicate that at least one source must be present in each element. If there is not at least one resource that matches each `source_id` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of source IDs separated by a `+` must be entered in the same item cell.")] = None,
        source_names: Annotated[Optional[conlist(StrictStr)], Field(description="A list of source names. Source names separated by a `+` indicate that both sources must be present in each element. Source names separated by a `,` indicate that at least one source must be present in each element. If there is not at least one resource that matches each `source_name` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of source names separated by a `+` must be entered in the same item cell.")] = None,
        target_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A list of target IDs. Target IDs separated by a `+` indicate that both targets must be present in each element. Target IDs separated by a `,` indicate that at least one target must be present in each element. If there is not at least one resource that matches each `target_id` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of target IDs separated by a `+` must be entered in the same item cell.")] = None,
        target_names: Annotated[Optional[conlist(StrictStr)], Field(description="A list of target names. Target names separated by a `+` indicate that both targets must be present in each element. Target names separated by a `,` indicate that at least one target must be present in each element. If there is not at least one resource that matches each `target_name` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of target names separated by a `+` must be entered in the same item cell.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get FlashBlade file system replica links  # noqa: E501
        
        Retrieves information about FlashBlade file system replica links.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_file_system_replica_links_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, member_ids, member_names, offset, sort, source_ids, source_names, target_ids, target_names, async_req=True)
        >>> result = thread.get()
        
        :param targets: A list of targets to query for. Overrides target_ids and target_names keyword arguments.
        :type targets: ReferenceType or List[ReferenceType], optional
        :param sources: A list of sources to query for. Overrides source_ids and source_names keyword arguments.
        :type sources: ReferenceType or List[ReferenceType], optional
        :param members: A list of members to query for. Overrides member_ids and member_names keyword arguments.
        :type members: ReferenceType or List[ReferenceType], optional
        :param references: A list of references to query for. Overrides ids keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param member_ids: A list of member IDs. Member IDs separated by a `+` indicate that both members
                        must be present in each element. Member IDs separated by a `,` indicate that
                        at least one member must be present in each element. If there is not at
                        least one resource that matches each `member_id` element, an error is
                        returned. Single quotes are required around all strings. When using Try it
                        Out in Swagger, a list of member IDs separated by a `+` must be entered in
                        the same item cell.
        :type member_ids: List[str]
        :param member_names: A list of member names. Member names separated by a `+` indicate that both
                            members must be present in each element. Member names separated by a `,`
                            indicate that at least one member must be present in each element. If there
                            is not at least one resource that matches each `member_name` element, an
                            error is returned. Single quotes are required around all strings. When
                            using Try it Out in Swagger, a list of member names separated by a `+` must
                            be entered in the same item cell.
        :type member_names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
        :param source_ids: A list of source IDs. Source IDs separated by a `+` indicate that both sources
                        must be present in each element. Source IDs separated by a `,` indicate that
                        at least one source must be present in each element. If there is not at
                        least one resource that matches each `source_id` element, an error is
                        returned. Single quotes are required around all strings. When using Try it
                        Out in Swagger, a list of source IDs separated by a `+` must be entered in
                        the same item cell.
        :type source_ids: List[str]
        :param source_names: A list of source names. Source names separated by a `+` indicate that both
                            sources must be present in each element. Source names separated by a `,`
                            indicate that at least one source must be present in each element. If there
                            is not at least one resource that matches each `source_name` element, an
                            error is returned. Single quotes are required around all strings. When
                            using Try it Out in Swagger, a list of source names separated by a `+` must
                            be entered in the same item cell.
        :type source_names: List[str]
        :param target_ids: A list of target IDs. Target IDs separated by a `+` indicate that both targets
                        must be present in each element. Target IDs separated by a `,` indicate that
                        at least one target must be present in each element. If there is not at
                        least one resource that matches each `target_id` element, an error is
                        returned. Single quotes are required around all strings. When using Try it
                        Out in Swagger, a list of target IDs separated by a `+` must be entered in
                        the same item cell.
        :type target_ids: List[str]
        :param target_names: A list of target names. Target names separated by a `+` indicate that both
                            targets must be present in each element. Target names separated by a `,`
                            indicate that at least one target must be present in each element. If there
                            is not at least one resource that matches each `target_name` element, an
                            error is returned. Single quotes are required around all strings. When
                            using Try it Out in Swagger, a list of target names separated by a `+` must
                            be entered in the same item cell.
        :type target_names: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            offset=offset,
            sort=sort,
            source_ids=source_ids,
            source_names=source_names,
            target_ids=target_ids,
            target_names=target_names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids'], kwargs)
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        _process_references(targets, ['target_ids', 'target_names'], kwargs)
        _fixup_list_type_params(['ids', 'member_ids', 'member_names', 'sort', 'source_ids', 'source_names', 'target_ids', 'target_names'], kwargs)
        return self._call_api('FileSystemReplicaLinksApi', 'api12_file_system_replica_links_get_with_http_info', kwargs)

    def get_file_system_replica_links_policies(
        self,
        policies: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        members: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        member_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of member IDs. If there is not at least one resource that matches each `member_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        member_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of member names. If there is not at least one resource that matches each `member_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        policy_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of policy IDs. If there is not at least one resource that matches each `policy_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        policy_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of policy names. If there is not at least one resource that matches each `policy_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get FlashBlade file system replica link / policy pairs  # noqa: E501
        
        Retrieves pairs of FlashBlade file system replica link members and their policies.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_file_system_replica_links_policies_get_with_http_info(authorization, x_request_id, continuation_token, filter, limit, member_ids, member_names, offset, policy_ids, policy_names, sort, async_req=True)
        >>> result = thread.get()
        
        :param policies: A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.
        :type policies: ReferenceType or List[ReferenceType], optional
        :param members: A list of members to query for. Overrides member_ids and member_names keyword arguments.
        :type members: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param member_ids: A comma-separated list of member IDs. If there is not at least one resource that
                        matches each `member_id` element, an error is returned. Single quotes are
                        required around all strings.
        :type member_ids: List[str]
        :param member_names: A comma-separated list of member names. If there is not at least one resource
                            that matches each `member_name` element, an error is returned. Single
                            quotes are required around all strings.
        :type member_names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param policy_ids: A comma-separated list of policy IDs. If there is not at least one resource that
                        matches each `policy_id` element, an error is returned. Single quotes are
                        required around all strings.
        :type policy_ids: List[str]
        :param policy_names: A comma-separated list of policy names. If there is not at least one resource
                            that matches each `policy_name` element, an error is returned. Single
                            quotes are required around all strings.
        :type policy_names: List[str]
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            offset=offset,
            policy_ids=policy_ids,
            policy_names=policy_names,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        _fixup_list_type_params(['member_ids', 'member_names', 'policy_ids', 'policy_names', 'sort'], kwargs)
        return self._call_api('FileSystemReplicaLinksApi', 'api12_file_system_replica_links_policies_get_with_http_info', kwargs)

    def get_file_system_snapshots(
        self,
        sources: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        source_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of ids for the source of the object. If there is not at least one resource that matches each `source_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        source_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of names for the source of the object. If there is not at least one resource that matches each `source_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get FlashBlade file system snapshots  # noqa: E501
        
        Retrieves snapshots of FlashBlade file systems.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_file_system_snapshots_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, source_ids, source_names, async_req=True)
        >>> result = thread.get()
        
        :param sources: A list of sources to query for. Overrides source_ids and source_names keyword arguments.
        :type sources: ReferenceType or List[ReferenceType], optional
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
        :param source_ids: A comma-separated list of ids for the source of the object. If there is not at
                        least one resource that matches each `source_id` element, an error is
                        returned. Single quotes are required around all strings.
        :type source_ids: List[str]
        :param source_names: A comma-separated list of names for the source of the object. If there is not at
                            least one resource that matches each `source_name` element, an error is
                            returned. Single quotes are required around all strings.
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            source_ids=source_ids,
            source_names=source_names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort', 'source_ids', 'source_names'], kwargs)
        return self._call_api('FileSystemSnapshotsApi', 'api12_file_system_snapshots_get_with_http_info', kwargs)

    def get_file_system_snapshots_policies(
        self,
        policies: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        members: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        member_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of member IDs. If there is not at least one resource that matches each `member_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        member_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of member names. If there is not at least one resource that matches each `member_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        policy_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of policy IDs. If there is not at least one resource that matches each `policy_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        policy_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of policy names. If there is not at least one resource that matches each `policy_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get FlashBlade file system snapshot / policy pairs  # noqa: E501
        
        Retrieves pairs of FlashBlade file system snapshot members and their policies.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_file_system_snapshots_policies_get_with_http_info(authorization, x_request_id, continuation_token, filter, limit, member_ids, member_names, offset, policy_ids, policy_names, sort, async_req=True)
        >>> result = thread.get()
        
        :param policies: A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.
        :type policies: ReferenceType or List[ReferenceType], optional
        :param members: A list of members to query for. Overrides member_ids and member_names keyword arguments.
        :type members: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param member_ids: A comma-separated list of member IDs. If there is not at least one resource that
                        matches each `member_id` element, an error is returned. Single quotes are
                        required around all strings.
        :type member_ids: List[str]
        :param member_names: A comma-separated list of member names. If there is not at least one resource
                            that matches each `member_name` element, an error is returned. Single
                            quotes are required around all strings.
        :type member_names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param policy_ids: A comma-separated list of policy IDs. If there is not at least one resource that
                        matches each `policy_id` element, an error is returned. Single quotes are
                        required around all strings.
        :type policy_ids: List[str]
        :param policy_names: A comma-separated list of policy names. If there is not at least one resource
                            that matches each `policy_name` element, an error is returned. Single
                            quotes are required around all strings.
        :type policy_names: List[str]
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            offset=offset,
            policy_ids=policy_ids,
            policy_names=policy_names,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        _fixup_list_type_params(['member_ids', 'member_names', 'policy_ids', 'policy_names', 'sort'], kwargs)
        return self._call_api('FileSystemSnapshotsApi', 'api12_file_system_snapshots_policies_get_with_http_info', kwargs)

    def get_file_systems(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get FlashArray and FlashBlade file systems  # noqa: E501
        
        Retrieves information about FlashArray and FlashBlade file system objects.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_file_systems_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('FileSystemsApi', 'api12_file_systems_get_with_http_info', kwargs)

    def get_file_systems_policies(
        self,
        policies: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        members: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        member_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of member IDs. If there is not at least one resource that matches each `member_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        member_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of member names. If there is not at least one resource that matches each `member_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        policy_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of policy IDs. If there is not at least one resource that matches each `policy_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        policy_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of policy names. If there is not at least one resource that matches each `policy_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get FlashBlade file system / policy pairs  # noqa: E501
        
        Retrieves pairs of FlashBlade file system members and their policies.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_file_systems_policies_get_with_http_info(authorization, x_request_id, continuation_token, filter, limit, member_ids, member_names, offset, policy_ids, policy_names, sort, async_req=True)
        >>> result = thread.get()
        
        :param policies: A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.
        :type policies: ReferenceType or List[ReferenceType], optional
        :param members: A list of members to query for. Overrides member_ids and member_names keyword arguments.
        :type members: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param member_ids: A comma-separated list of member IDs. If there is not at least one resource that
                        matches each `member_id` element, an error is returned. Single quotes are
                        required around all strings.
        :type member_ids: List[str]
        :param member_names: A comma-separated list of member names. If there is not at least one resource
                            that matches each `member_name` element, an error is returned. Single
                            quotes are required around all strings.
        :type member_names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param policy_ids: A comma-separated list of policy IDs. If there is not at least one resource that
                        matches each `policy_id` element, an error is returned. Single quotes are
                        required around all strings.
        :type policy_ids: List[str]
        :param policy_names: A comma-separated list of policy names. If there is not at least one resource
                            that matches each `policy_name` element, an error is returned. Single
                            quotes are required around all strings.
        :type policy_names: List[str]
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            offset=offset,
            policy_ids=policy_ids,
            policy_names=policy_names,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        _fixup_list_type_params(['member_ids', 'member_names', 'policy_ids', 'policy_names', 'sort'], kwargs)
        return self._call_api('FileSystemsApi', 'api12_file_systems_policies_get_with_http_info', kwargs)

    def get_hardware(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get hardware  # noqa: E501
        
        Retrieves information about hardware components.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_hardware_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('HardwareApi', 'api12_hardware_get_with_http_info', kwargs)

    def get_hardware_connectors(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get hardware connectors  # noqa: E501
        
        Retrieves information about FlashBlade hardware connectors.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_hardware_connectors_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('HardwareConnectorsApi', 'api12_hardware_connectors_get_with_http_info', kwargs)

    def get_invoices(
        self,
        subscriptions: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        partner_purchase_orders: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of partner purchase order numbers. If there is not at least one resource that matches each `partner_purchase_order` element, an error is returned. Single quotes are required around all strings.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        subscription_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of subscription IDs. If there is not at least one resource that matches each `subscription.id` element, an error is returned. Single quotes are required around all strings.")] = None,
        subscription_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of subscription names. If there is not at least one resource that matches each `subscription.name` element, an error is returned. Single quotes are required around all strings.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get invoices  # noqa: E501
        
        Retrieves information about Pure1 subscription invoices.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_invoices_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, offset, partner_purchase_orders, sort, subscription_ids, subscription_names, async_req=True)
        >>> result = thread.get()
        
        :param subscriptions: A list of subscriptions to query for. Overrides subscription_ids and subscription_names keyword arguments.
        :type subscriptions: ReferenceType or List[ReferenceType], optional
        :param references: A list of references to query for. Overrides ids keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param partner_purchase_orders: A comma-separated list of partner purchase order numbers. If there is not at
                                        least one resource that matches each `partner_purchase_order` element,
                                        an error is returned. Single quotes are required around all strings.
        :type partner_purchase_orders: List[str]
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
        :param subscription_ids: A comma-separated list of subscription IDs. If there is not at least one
                                resource that matches each `subscription.id` element, an error is
                                returned. Single quotes are required around all strings.
        :type subscription_ids: List[str]
        :param subscription_names: A comma-separated list of subscription names. If there is not at least one
                                resource that matches each `subscription.name` element, an error is
                                returned. Single quotes are required around all strings.
        :type subscription_names: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            offset=offset,
            partner_purchase_orders=partner_purchase_orders,
            sort=sort,
            subscription_ids=subscription_ids,
            subscription_names=subscription_names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids'], kwargs)
        _process_references(subscriptions, ['subscription_ids', 'subscription_names'], kwargs)
        _fixup_list_type_params(['ids', 'partner_purchase_orders', 'sort', 'subscription_ids', 'subscription_names'], kwargs)
        return self._call_api('InvoicesApi', 'api12_invoices_get_with_http_info', kwargs)

    def get_metrics(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        resource_types: Annotated[Optional[conlist(StrictStr)], Field(description="The resource types to list the available metrics. Valid values are `arrays`, `buckets`, `directories`, `file-systems`, `pods`, `subscription-licenses` and `volumes`. A metric can belong to a combination of resources, e.g., write-iops from array to pod. In that case, query by ['arrays', 'pods']. Single quotes are required around all strings.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get metrics  # noqa: E501
        
        Retrieves information about metrics that can be queried for.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_metrics_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, resource_types, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param resource_types: The resource types to list the available metrics. Valid values are `arrays`,
                            `buckets`, `directories`, `file-systems`, `pods`, `subscription-licenses`
                            and `volumes`. A metric can belong to a combination of resources, e.g.,
                            write-iops from array to pod. In that case, query by ['arrays', 'pods'].
                            Single quotes are required around all strings.
        :type resource_types: List[str]
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            resource_types=resource_types,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'resource_types', 'sort'], kwargs)
        return self._call_api('MetricsApi', 'api12_metrics_get_with_http_info', kwargs)

    def get_metrics_history(
        self,
        aggregation: Annotated[StrictStr, Field(..., description="Aggregation needed on the metric data. Valid values are `avg` and `max`. Single quotes are required around all strings. Latency metrics averages are weighted by the IOPS.")],
        end_time: Annotated[StrictInt, Field(..., description="Timestamp of when the time window ends. Measured in milliseconds since the UNIX epoch.")],
        resolution: Annotated[StrictInt, Field(..., description="The duration of time between individual data points, in milliseconds.")],
        start_time: Annotated[StrictInt, Field(..., description="Timestamp of when the time window starts. Measured in milliseconds since the UNIX epoch.")],
        resources: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="REQUIRED: either `ids` or `names`. A comma-separated list of object IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="REQUIRED: either `names` or `ids`. A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        resource_ids: Annotated[Optional[conlist(StrictStr)], Field(description="REQUIRED: either `resource_ids` or `resource_names`. A comma-separated list of resource IDs. If there is not at least one resource that matches each `resource_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        resource_names: Annotated[Optional[conlist(StrictStr)], Field(description="REQUIRED: either `resource_ids` or `resource_names`. A comma-separated list of resource names. If there is not at least one resource that matches each `resource_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get metrics history  # noqa: E501
        
        Retrieves historical metric data for resources. This endpoint supports batching: Up to 32 time series can be retrieved in one call. It can be multiple metrics for one resource, (e.g., load and bandwidth for one array - 2 time series), one metric for multiple resource (e.g., load for arrayA and arrayB - 2 time series), or a combination of both, multiple metrics for multiple resources, (e.g., load and bandwidth for arrayA and arrayB - 4 time series).  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_metrics_history_get_with_http_info(aggregation, end_time, resolution, start_time, authorization, x_request_id, ids, names, resource_ids, resource_names, async_req=True)
        >>> result = thread.get()
        
        :param aggregation: Aggregation needed on the metric data. Valid values are `avg` and `max`. Single
                            quotes are required around all strings. Latency metrics averages are
                            weighted by the IOPS. (required)
        :type aggregation: str
        :param end_time: Timestamp of when the time window ends. Measured in milliseconds since the UNIX
                        epoch. (required)
        :type end_time: int
        :param resolution: The duration of time between individual data points, in milliseconds. (required)
        :type resolution: int
        :param start_time: Timestamp of when the time window starts. Measured in milliseconds since the
                        UNIX epoch. (required)
        :type start_time: int
        :param resources: A list of resources to query for. Overrides resource_ids and resource_names keyword arguments.
        :type resources: ReferenceType or List[ReferenceType], optional
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param ids: REQUIRED: either `ids` or `names`. A comma-separated list of object IDs. If there is not
                            at least one resource that matches each `id` element, an error is returned.
                            Single quotes are required around all strings.
        :type ids: List[str]
        :param names: REQUIRED: either `names` or `ids`. A comma-separated list of resource names. If there is
                                not at least one resource that matches each `name` element, an error is
                                returned. Single quotes are required around all strings.
        :type names: List[str]
        :param resource_ids: REQUIRED: either `resource_ids` or `resource_names`. A comma-separated list of resource
                                    IDs. If there is not at least one resource that matches each
                                    `resource_id` element, an error is returned. Single quotes are required
                                    around all strings.
        :type resource_ids: List[str]
        :param resource_names: REQUIRED: either `resource_ids` or `resource_names`. A comma-separated list of resource
                                        names. If there is not at least one resource that matches each
                                        `resource_name` element, an error is returned. Single quotes are
                                        required around all strings.
        :type resource_names: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            aggregation=aggregation,
            end_time=end_time,
            resolution=resolution,
            start_time=start_time,
            authorization=authorization,
            x_request_id=x_request_id,
            ids=ids,
            names=names,
            resource_ids=resource_ids,
            resource_names=resource_names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(resources, ['resource_ids', 'resource_names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'resource_ids', 'resource_names'], kwargs)
        return self._call_api('MetricsApi', 'api12_metrics_history_get_with_http_info', kwargs)

    def get_network_interfaces(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get network interfaces  # noqa: E501
        
        Retrieves information about physical and virtual network interface objects.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_network_interfaces_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('NetworkInterfacesApi', 'api12_network_interfaces_get_with_http_info', kwargs)

    def get_object_store_accounts(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get object store accounts  # noqa: E501
        
        Retrieves object store accounts.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_object_store_accounts_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('ObjectStoreAccountsApi', 'api12_object_store_accounts_get_with_http_info', kwargs)

    def get_pod_replica_links(
        self,
        targets: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        sources: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        members: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        member_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A list of member IDs. Member IDs separated by a `+` indicate that both members must be present in each element. Member IDs separated by a `,` indicate that at least one member must be present in each element. If there is not at least one resource that matches each `member_id` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of member IDs separated by a `+` must be entered in the same item cell.")] = None,
        member_names: Annotated[Optional[conlist(StrictStr)], Field(description="A list of member names. Member names separated by a `+` indicate that both members must be present in each element. Member names separated by a `,` indicate that at least one member must be present in each element. If there is not at least one resource that matches each `member_name` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of member names separated by a `+` must be entered in the same item cell.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        source_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A list of source IDs. Source IDs separated by a `+` indicate that both sources must be present in each element. Source IDs separated by a `,` indicate that at least one source must be present in each element. If there is not at least one resource that matches each `source_id` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of source IDs separated by a `+` must be entered in the same item cell.")] = None,
        source_names: Annotated[Optional[conlist(StrictStr)], Field(description="A list of source names. Source names separated by a `+` indicate that both sources must be present in each element. Source names separated by a `,` indicate that at least one source must be present in each element. If there is not at least one resource that matches each `source_name` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of source names separated by a `+` must be entered in the same item cell.")] = None,
        target_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A list of target IDs. Target IDs separated by a `+` indicate that both targets must be present in each element. Target IDs separated by a `,` indicate that at least one target must be present in each element. If there is not at least one resource that matches each `target_id` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of target IDs separated by a `+` must be entered in the same item cell.")] = None,
        target_names: Annotated[Optional[conlist(StrictStr)], Field(description="A list of target names. Target names separated by a `+` indicate that both targets must be present in each element. Target names separated by a `,` indicate that at least one target must be present in each element. If there is not at least one resource that matches each `target_name` element, an error is returned. Single quotes are required around all strings. When using Try it Out in Swagger, a list of target names separated by a `+` must be entered in the same item cell.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get pod replica links  # noqa: E501
        
        Retrieves information about pod replica links.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_pod_replica_links_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, member_ids, member_names, offset, sort, source_ids, source_names, target_ids, target_names, async_req=True)
        >>> result = thread.get()
        
        :param targets: A list of targets to query for. Overrides target_ids and target_names keyword arguments.
        :type targets: ReferenceType or List[ReferenceType], optional
        :param sources: A list of sources to query for. Overrides source_ids and source_names keyword arguments.
        :type sources: ReferenceType or List[ReferenceType], optional
        :param members: A list of members to query for. Overrides member_ids and member_names keyword arguments.
        :type members: ReferenceType or List[ReferenceType], optional
        :param references: A list of references to query for. Overrides ids keyword argument.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param member_ids: A list of member IDs. Member IDs separated by a `+` indicate that both members
                        must be present in each element. Member IDs separated by a `,` indicate that
                        at least one member must be present in each element. If there is not at
                        least one resource that matches each `member_id` element, an error is
                        returned. Single quotes are required around all strings. When using Try it
                        Out in Swagger, a list of member IDs separated by a `+` must be entered in
                        the same item cell.
        :type member_ids: List[str]
        :param member_names: A list of member names. Member names separated by a `+` indicate that both
                            members must be present in each element. Member names separated by a `,`
                            indicate that at least one member must be present in each element. If there
                            is not at least one resource that matches each `member_name` element, an
                            error is returned. Single quotes are required around all strings. When
                            using Try it Out in Swagger, a list of member names separated by a `+` must
                            be entered in the same item cell.
        :type member_names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
        :param source_ids: A list of source IDs. Source IDs separated by a `+` indicate that both sources
                        must be present in each element. Source IDs separated by a `,` indicate that
                        at least one source must be present in each element. If there is not at
                        least one resource that matches each `source_id` element, an error is
                        returned. Single quotes are required around all strings. When using Try it
                        Out in Swagger, a list of source IDs separated by a `+` must be entered in
                        the same item cell.
        :type source_ids: List[str]
        :param source_names: A list of source names. Source names separated by a `+` indicate that both
                            sources must be present in each element. Source names separated by a `,`
                            indicate that at least one source must be present in each element. If there
                            is not at least one resource that matches each `source_name` element, an
                            error is returned. Single quotes are required around all strings. When
                            using Try it Out in Swagger, a list of source names separated by a `+` must
                            be entered in the same item cell.
        :type source_names: List[str]
        :param target_ids: A list of target IDs. Target IDs separated by a `+` indicate that both targets
                        must be present in each element. Target IDs separated by a `,` indicate that
                        at least one target must be present in each element. If there is not at
                        least one resource that matches each `target_id` element, an error is
                        returned. Single quotes are required around all strings. When using Try it
                        Out in Swagger, a list of target IDs separated by a `+` must be entered in
                        the same item cell.
        :type target_ids: List[str]
        :param target_names: A list of target names. Target names separated by a `+` indicate that both
                            targets must be present in each element. Target names separated by a `,`
                            indicate that at least one target must be present in each element. If there
                            is not at least one resource that matches each `target_name` element, an
                            error is returned. Single quotes are required around all strings. When
                            using Try it Out in Swagger, a list of target names separated by a `+` must
                            be entered in the same item cell.
        :type target_names: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            offset=offset,
            sort=sort,
            source_ids=source_ids,
            source_names=source_names,
            target_ids=target_ids,
            target_names=target_names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids'], kwargs)
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        _process_references(targets, ['target_ids', 'target_names'], kwargs)
        _fixup_list_type_params(['ids', 'member_ids', 'member_names', 'sort', 'source_ids', 'source_names', 'target_ids', 'target_names'], kwargs)
        return self._call_api('PodReplicaLinksApi', 'api12_pod_replica_links_get_with_http_info', kwargs)

    def get_pods(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get pods  # noqa: E501
        
        Retrieves information about pod objects.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_pods_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('PodsApi', 'api12_pods_get_with_http_info', kwargs)

    def get_policies_file_system_replica_links(
        self,
        policies: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        members: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        member_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of member IDs. If there is not at least one resource that matches each `member_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        member_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of member names. If there is not at least one resource that matches each `member_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        policy_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of policy IDs. If there is not at least one resource that matches each `policy_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        policy_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of policy names. If there is not at least one resource that matches each `policy_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get policy / FlashBlade file system replica link pairs  # noqa: E501
        
        Retrieves pairs of policy references and their FlashBlade file system replica link members.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_policies_file_system_replica_links_get_with_http_info(authorization, x_request_id, continuation_token, filter, limit, member_ids, member_names, offset, policy_ids, policy_names, sort, async_req=True)
        >>> result = thread.get()
        
        :param policies: A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.
        :type policies: ReferenceType or List[ReferenceType], optional
        :param members: A list of members to query for. Overrides member_ids and member_names keyword arguments.
        :type members: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param member_ids: A comma-separated list of member IDs. If there is not at least one resource that
                        matches each `member_id` element, an error is returned. Single quotes are
                        required around all strings.
        :type member_ids: List[str]
        :param member_names: A comma-separated list of member names. If there is not at least one resource
                            that matches each `member_name` element, an error is returned. Single
                            quotes are required around all strings.
        :type member_names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param policy_ids: A comma-separated list of policy IDs. If there is not at least one resource that
                        matches each `policy_id` element, an error is returned. Single quotes are
                        required around all strings.
        :type policy_ids: List[str]
        :param policy_names: A comma-separated list of policy names. If there is not at least one resource
                            that matches each `policy_name` element, an error is returned. Single
                            quotes are required around all strings.
        :type policy_names: List[str]
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            offset=offset,
            policy_ids=policy_ids,
            policy_names=policy_names,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        _fixup_list_type_params(['member_ids', 'member_names', 'policy_ids', 'policy_names', 'sort'], kwargs)
        return self._call_api('PoliciesApi', 'api12_policies_file_system_replica_links_get_with_http_info', kwargs)

    def get_policies_file_system_snapshots(
        self,
        policies: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        members: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        member_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of member IDs. If there is not at least one resource that matches each `member_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        member_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of member names. If there is not at least one resource that matches each `member_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        policy_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of policy IDs. If there is not at least one resource that matches each `policy_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        policy_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of policy names. If there is not at least one resource that matches each `policy_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get policy / FlashBlade file system snapshot pairs  # noqa: E501
        
        Retrieves pairs of policy references and their FlashBlade file system snapshot members.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_policies_file_system_snapshots_get_with_http_info(authorization, x_request_id, continuation_token, filter, limit, member_ids, member_names, offset, policy_ids, policy_names, sort, async_req=True)
        >>> result = thread.get()
        
        :param policies: A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.
        :type policies: ReferenceType or List[ReferenceType], optional
        :param members: A list of members to query for. Overrides member_ids and member_names keyword arguments.
        :type members: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param member_ids: A comma-separated list of member IDs. If there is not at least one resource that
                        matches each `member_id` element, an error is returned. Single quotes are
                        required around all strings.
        :type member_ids: List[str]
        :param member_names: A comma-separated list of member names. If there is not at least one resource
                            that matches each `member_name` element, an error is returned. Single
                            quotes are required around all strings.
        :type member_names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param policy_ids: A comma-separated list of policy IDs. If there is not at least one resource that
                        matches each `policy_id` element, an error is returned. Single quotes are
                        required around all strings.
        :type policy_ids: List[str]
        :param policy_names: A comma-separated list of policy names. If there is not at least one resource
                            that matches each `policy_name` element, an error is returned. Single
                            quotes are required around all strings.
        :type policy_names: List[str]
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            offset=offset,
            policy_ids=policy_ids,
            policy_names=policy_names,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        _fixup_list_type_params(['member_ids', 'member_names', 'policy_ids', 'policy_names', 'sort'], kwargs)
        return self._call_api('PoliciesApi', 'api12_policies_file_system_snapshots_get_with_http_info', kwargs)

    def get_policies_file_systems(
        self,
        policies: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        members: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        member_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of member IDs. If there is not at least one resource that matches each `member_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        member_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of member names. If there is not at least one resource that matches each `member_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        policy_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of policy IDs. If there is not at least one resource that matches each `policy_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        policy_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of policy names. If there is not at least one resource that matches each `policy_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get policy / FlashBlade file system pairs  # noqa: E501
        
        Retrieves pairs of policy references and their FlashBlade file system members.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_policies_file_systems_get_with_http_info(authorization, x_request_id, continuation_token, filter, limit, member_ids, member_names, offset, policy_ids, policy_names, sort, async_req=True)
        >>> result = thread.get()
        
        :param policies: A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.
        :type policies: ReferenceType or List[ReferenceType], optional
        :param members: A list of members to query for. Overrides member_ids and member_names keyword arguments.
        :type members: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param member_ids: A comma-separated list of member IDs. If there is not at least one resource that
                        matches each `member_id` element, an error is returned. Single quotes are
                        required around all strings.
        :type member_ids: List[str]
        :param member_names: A comma-separated list of member names. If there is not at least one resource
                            that matches each `member_name` element, an error is returned. Single
                            quotes are required around all strings.
        :type member_names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param policy_ids: A comma-separated list of policy IDs. If there is not at least one resource that
                        matches each `policy_id` element, an error is returned. Single quotes are
                        required around all strings.
        :type policy_ids: List[str]
        :param policy_names: A comma-separated list of policy names. If there is not at least one resource
                            that matches each `policy_name` element, an error is returned. Single
                            quotes are required around all strings.
        :type policy_names: List[str]
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            offset=offset,
            policy_ids=policy_ids,
            policy_names=policy_names,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        _fixup_list_type_params(['member_ids', 'member_names', 'policy_ids', 'policy_names', 'sort'], kwargs)
        return self._call_api('PoliciesApi', 'api12_policies_file_systems_get_with_http_info', kwargs)

    def get_policies(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get policies  # noqa: E501
        
        Retrieves policies and their rules.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_policies_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('PoliciesApi', 'api12_policies_get_with_http_info', kwargs)

    def get_policies_members(
        self,
        policies: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        members: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        member_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of member IDs. If there is not at least one resource that matches each `member_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        member_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of member names. If there is not at least one resource that matches each `member_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        policy_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of policy IDs. If there is not at least one resource that matches each `policy_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        policy_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of policy names. If there is not at least one resource that matches each `policy_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get policy / member pairs  # noqa: E501
        
        Retrieves pairs of policy references and their members.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_policies_members_get_with_http_info(authorization, x_request_id, continuation_token, filter, limit, member_ids, member_names, offset, policy_ids, policy_names, sort, async_req=True)
        >>> result = thread.get()
        
        :param policies: A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.
        :type policies: ReferenceType or List[ReferenceType], optional
        :param members: A list of members to query for. Overrides member_ids and member_names keyword arguments.
        :type members: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param member_ids: A comma-separated list of member IDs. If there is not at least one resource that
                        matches each `member_id` element, an error is returned. Single quotes are
                        required around all strings.
        :type member_ids: List[str]
        :param member_names: A comma-separated list of member names. If there is not at least one resource
                            that matches each `member_name` element, an error is returned. Single
                            quotes are required around all strings.
        :type member_names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param policy_ids: A comma-separated list of policy IDs. If there is not at least one resource that
                        matches each `policy_id` element, an error is returned. Single quotes are
                        required around all strings.
        :type policy_ids: List[str]
        :param policy_names: A comma-separated list of policy names. If there is not at least one resource
                            that matches each `policy_name` element, an error is returned. Single
                            quotes are required around all strings.
        :type policy_names: List[str]
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            offset=offset,
            policy_ids=policy_ids,
            policy_names=policy_names,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        _fixup_list_type_params(['member_ids', 'member_names', 'policy_ids', 'policy_names', 'sort'], kwargs)
        return self._call_api('PoliciesApi', 'api12_policies_members_get_with_http_info', kwargs)

    def get_ports(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get ports  # noqa: E501
        
        Retrieves information about FlashArray ports.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_ports_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('PortsApi', 'api12_ports_get_with_http_info', kwargs)

    def get_subscription_assets(
        self,
        subscriptions: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        licenses: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        advanced_space: Annotated[Optional[StrictBool], Field(description="If `true`, returns the `advanced_space` field containing physical and effective space information.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        license_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of subscriptionLicense IDs. If there is not at least one resource that matches each `license.id` element, an error is returned. Single quotes are required around all strings.")] = None,
        license_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of subscriptionLicense names. If there is not at least one resource that matches each `license.name` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        subscription_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of subscription IDs. If there is not at least one resource that matches each `subscription.id` element, an error is returned. Single quotes are required around all strings.")] = None,
        subscription_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of subscription names. If there is not at least one resource that matches each `subscription.name` element, an error is returned. Single quotes are required around all strings.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get subscription assets  # noqa: E501
        
        Retrieves information about Pure1 subscription assets.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_subscription_assets_get_with_http_info(authorization, x_request_id, advanced_space, continuation_token, filter, ids, license_ids, license_names, limit, names, offset, sort, subscription_ids, subscription_names, async_req=True)
        >>> result = thread.get()
        
        :param subscriptions: A list of subscriptions to query for. Overrides subscription_ids and subscription_names keyword arguments.
        :type subscriptions: ReferenceType or List[ReferenceType], optional
        :param licenses: A list of licenses to query for. Overrides license_ids and license_names keyword arguments.
        :type licenses: ReferenceType or List[ReferenceType], optional
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param advanced_space: If `true`, returns the `advanced_space` field containing physical and effective
                            space information.
        :type advanced_space: bool
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param license_ids: A comma-separated list of subscriptionLicense IDs. If there is not at least one
                            resource that matches each `license.id` element, an error is returned.
                            Single quotes are required around all strings.
        :type license_ids: List[str]
        :param license_names: A comma-separated list of subscriptionLicense names. If there is not at least
                            one resource that matches each `license.name` element, an error is
                            returned. Single quotes are required around all strings.
        :type license_names: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
        :param subscription_ids: A comma-separated list of subscription IDs. If there is not at least one
                                resource that matches each `subscription.id` element, an error is
                                returned. Single quotes are required around all strings.
        :type subscription_ids: List[str]
        :param subscription_names: A comma-separated list of subscription names. If there is not at least one
                                resource that matches each `subscription.name` element, an error is
                                returned. Single quotes are required around all strings.
        :type subscription_names: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            advanced_space=advanced_space,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            license_ids=license_ids,
            license_names=license_names,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            subscription_ids=subscription_ids,
            subscription_names=subscription_names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(licenses, ['license_ids', 'license_names'], kwargs)
        _process_references(subscriptions, ['subscription_ids', 'subscription_names'], kwargs)
        _fixup_list_type_params(['ids', 'license_ids', 'license_names', 'names', 'sort', 'subscription_ids', 'subscription_names'], kwargs)
        return self._call_api('SubscriptionsApi', 'api12_subscription_assets_get_with_http_info', kwargs)

    def get_subscription_licenses(
        self,
        subscriptions: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        marketplace_partner_references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        marketplace_partner_reference_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of marketplace partner reference IDs. If there is not at least one resource that matches each `marketplace_partner.reference_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        subscription_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of subscription IDs. If there is not at least one resource that matches each `subscription.id` element, an error is returned. Single quotes are required around all strings.")] = None,
        subscription_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of subscription names. If there is not at least one resource that matches each `subscription.name` element, an error is returned. Single quotes are required around all strings.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get subscription licenses  # noqa: E501
        
        Retrieves information about Pure1 subscription licenses.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_subscription_licenses_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, marketplace_partner_reference_ids, names, offset, sort, subscription_ids, subscription_names, async_req=True)
        >>> result = thread.get()
        
        :param subscriptions: A list of subscriptions to query for. Overrides subscription_ids and subscription_names keyword arguments.
        :type subscriptions: ReferenceType or List[ReferenceType], optional
        :param marketplace_partner_references: A list of marketplace_partner_references to query for. Overrides marketplace_partner_reference_ids keyword argument.
        :type marketplace_partner_references: ReferenceType or List[ReferenceType], optional
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param marketplace_partner_reference_ids: A comma-separated list of marketplace partner reference IDs. If there is not at
                                                least one resource that matches each
                                                `marketplace_partner.reference_id` element, an error is returned.
                                                Single quotes are required around all strings.
        :type marketplace_partner_reference_ids: List[str]
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
        :param subscription_ids: A comma-separated list of subscription IDs. If there is not at least one
                                resource that matches each `subscription.id` element, an error is
                                returned. Single quotes are required around all strings.
        :type subscription_ids: List[str]
        :param subscription_names: A comma-separated list of subscription names. If there is not at least one
                                resource that matches each `subscription.name` element, an error is
                                returned. Single quotes are required around all strings.
        :type subscription_names: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            marketplace_partner_reference_ids=marketplace_partner_reference_ids,
            names=names,
            offset=offset,
            sort=sort,
            subscription_ids=subscription_ids,
            subscription_names=subscription_names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(marketplace_partner_references, ['marketplace_partner_reference_ids'], kwargs)
        _process_references(subscriptions, ['subscription_ids', 'subscription_names'], kwargs)
        _fixup_list_type_params(['ids', 'marketplace_partner_reference_ids', 'names', 'sort', 'subscription_ids', 'subscription_names'], kwargs)
        return self._call_api('SubscriptionsApi', 'api12_subscription_licenses_get_with_http_info', kwargs)

    def get_subscriptions(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get subscriptions  # noqa: E501
        
        Retrieves information about Pure1 subscriptions.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_subscriptions_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('SubscriptionsApi', 'api12_subscriptions_get_with_http_info', kwargs)

    def get_assessment_sustainability_arrays(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        fqdns: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource FQDNs. If there is not at least one resource that matches each `fqdn` element, an error is returned. Single quotes are required around all strings.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get appliance sustainability information.  # noqa: E501
        
        Retrieves information about FlashArray and FlashBlade size, power consumption, heat generation and its sustainability assessment.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_assessment_sustainability_arrays_get_with_http_info(authorization, x_request_id, continuation_token, filter, fqdns, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param fqdns: A comma-separated list of resource FQDNs. If there is not at least one resource
                    that matches each `fqdn` element, an error is returned. Single quotes are
                    required around all strings.
        :type fqdns: List[str]
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            fqdns=fqdns,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['fqdns', 'ids', 'names', 'sort'], kwargs)
        return self._call_api('SustainabilityApi', 'api12_assessment_sustainability_arrays_get_with_http_info', kwargs)

    def get_assessment_sustainability_insights_arrays(
        self,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get appliance sustainability insights information.  # noqa: E501
        
        Retrieves information about FlashArray and FlashBlade insights connected to sustainability assessment.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_assessment_sustainability_insights_arrays_get_with_http_info(authorization, x_request_id, continuation_token, filter, limit, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _fixup_list_type_params(['sort'], kwargs)
        return self._call_api('SustainabilityApi', 'api12_assessment_sustainability_insights_arrays_get_with_http_info', kwargs)

    def get_targets(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get targets  # noqa: E501
        
        Retrieves information about targets.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_targets_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('TargetsApi', 'api12_targets_get_with_http_info', kwargs)

    def get_volume_snapshots(
        self,
        sources: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        source_ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of ids for the source of the object. If there is not at least one resource that matches each `source_id` element, an error is returned. Single quotes are required around all strings.")] = None,
        source_names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of names for the source of the object. If there is not at least one resource that matches each `source_name` element, an error is returned. Single quotes are required around all strings.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get volume snapshots  # noqa: E501
        
        Retrieves information about snapshots of volumes.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_volume_snapshots_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, source_ids, source_names, async_req=True)
        >>> result = thread.get()
        
        :param sources: A list of sources to query for. Overrides source_ids and source_names keyword arguments.
        :type sources: ReferenceType or List[ReferenceType], optional
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
        :param source_ids: A comma-separated list of ids for the source of the object. If there is not at
                        least one resource that matches each `source_id` element, an error is
                        returned. Single quotes are required around all strings.
        :type source_ids: List[str]
        :param source_names: A comma-separated list of names for the source of the object. If there is not at
                            least one resource that matches each `source_name` element, an error is
                            returned. Single quotes are required around all strings.
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            source_ids=source_ids,
            source_names=source_names,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort', 'source_ids', 'source_names'], kwargs)
        return self._call_api('VolumeSnapshotsApi', 'api12_volume_snapshots_get_with_http_info', kwargs)

    def get_volumes(
        self,
        references: Optional[Union[ReferenceType, List[ReferenceType]]] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings.")] = None,
        limit: Annotated[Optional[StrictInt], Field(description="Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The offset of the first resource to return from a collection.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response.")] = None,
        async_req: Optional[bool] = None,
        _preload_content: bool = True,
        _return_http_data_only: Optional[bool] = None,
        _request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> Union[ValidResponse, ErrorResponse]:
        """Get volumes  # noqa: E501
        
        Retrieves information about FlashArray volume objects.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        
        >>> thread = api.api12_volumes_get_with_http_info(authorization, x_request_id, continuation_token, filter, ids, limit, names, offset, sort, async_req=True)
        >>> result = thread.get()
        
        :param references: A list of references to query for. Overrides ids and names keyword arguments.
        :type references: ReferenceType or List[ReferenceType], optional
        :param authorization: Deprecated. Please use Client level authorization
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param continuation_token: An opaque token used to iterate over a collection. The token to use on the next
                                request is returned in the `continuation_token` field of the result.
                                Single quotes are required around all strings.
        :type continuation_token: str
        :param filter: Exclude resources that don't match the specified criteria. Single quotes are
                    required around all strings inside the filters.
        :type filter: str
        :param ids: A comma-separated list of resource IDs. If there is not at least one resource
                    that matches each `id` element, an error is returned. Single quotes are
                    required around all strings.
        :type ids: List[str]
        :param limit: Limit the size of the response to the specified number of resources. A limit of
                    0 can be used to get the number of resources without getting all of the
                    resources. It will be returned in the total_item_count field. If a client
                    asks for a page size larger than the maximum number, the request is still
                    valid. In that case the server just returns the maximum number of items,
                    disregarding the client's page size request. If not specified, defaults to
                    1000.
        :type limit: int
        :param names: A comma-separated list of resource names. If there is not at least one resource
                    that matches each `name` element, an error is returned. Single quotes are
                    required around all strings.
        :type names: List[str]
        :param offset: The offset of the first resource to return from a collection.
        :type offset: int
        :param sort: Sort the response by the specified fields (in descending order if '-' is
                    appended to the field name). If you provide a sort you will not get a
                    continuation token in the response.
        :type sort: List[str]
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
        
        :returns ValidResponse: If the call was successful.
                 ErrorResponse: If the call was not successful.
        
        :raises PureError: If calling the API fails.
        :raises ValueError: If a parameter is of an invalid type.
        :raises TypeError: If invalid or missing parameters are used.
        """ # noqa: E501

        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _preload_content=_preload_content,
            _return_http_data_only=_return_http_data_only,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        _process_references(references, ['ids', 'names'], kwargs)
        _fixup_list_type_params(['ids', 'names', 'sort'], kwargs)
        return self._call_api('VolumesApi', 'api12_volumes_get_with_http_info', kwargs)

    def _set_agent_header(self):
        """
        Set the user-agent header of the internal client.
        """
        self._api_client.set_default_header(Headers.user_agent, self.USER_AGENT)

    def _set_auth_header(self, refresh=False):
        """
        Set the authorization header of the internal client with the access
        token.

        Args:
            refresh (bool, optional): Whether to retrieve a new access token.
                Defaults to False.

        Raises:
            PureError: If there was an error retrieving the access token.
        """
        self._api_client.set_default_header('Authorization',
                                            self._token_man.get_header(refresh=refresh))

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
                elif error.status == 403:
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

    def _create_valid_response(self, response: ApiResponse, endpoint, kwargs):
        """
        Create a ValidResponse from a Swagger response.

        Args:
            response ApiResponse: Body, status, header tuple as returned from a
                Swagger client.
            endpoint (function): The function of the Swagger client that was
                called.
            kwargs (dict): The processed kwargs that were passed to the
                endpoint function.

        Returns:
            ValidResponse
        """
        body = response.data
        headers = response.headers

        if body is None:
            continuation_token = None
            total_item_count = None
            items = None
        else:
            continuation_token = getattr(body, "continuation_token", None)
            total_item_count = getattr(body, "total_item_count", None)

            # *-get-response models have "continuation_token" attribute. Other models don't have them.
            # None means that attribute is ignored in ItemIterator
            # Only GET responses are paged.
            more_items_remaining = None if hasattr(body, 'continuation_token') else False

            items = iter(ItemIterator(
                client=self,
                api_endpoint=endpoint,
                kwargs=kwargs,
                continuation_token=continuation_token,
                total_item_count=total_item_count,
                items=body.items,
                x_request_id=headers.get(Headers.x_request_id),
                more_items_remaining=more_items_remaining,
            ))
        return ValidResponse(
            status_code=response.status_code,
            continuation_token=continuation_token,
            total_item_count=total_item_count,
            items=items,
            headers=headers,
        )

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
        body = json.loads(error.body)
        if status in [403, 429]:
            # Parse differently if the error message came from kong
            errors = [ApiError(None, body.get(Responses.message, None))]
        else:
            errors = [ApiError(err.get(Responses.context, None),
                               err.get(Responses.message, None))
                      for err in body.get(Responses.errors, None)]
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
