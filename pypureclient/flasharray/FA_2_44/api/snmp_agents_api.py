
# coding: utf-8

"""
    FlashArray REST API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 2.44
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import re  # noqa: F401
import io
import warnings


from typing_extensions import Annotated
from pydantic import Field, StrictBool, StrictStr, conint, conlist, constr, validator

from typing import Optional

from pypureclient.flasharray.FA_2_44.models.snmp_agent_get_response import SnmpAgentGetResponse
from pypureclient.flasharray.FA_2_44.models.snmp_agent_mib_get_response import SnmpAgentMibGetResponse
from pypureclient.flasharray.FA_2_44.models.snmp_agent_patch import SnmpAgentPatch
from pypureclient.flasharray.FA_2_44.models.snmp_agent_response import SnmpAgentResponse
from typing import Optional
from pypureclient.flasharray.FA_2_44.api_client import ApiClient as _TransportApiClient
from pypureclient.flasharray.FA_2_44.api_response import ApiResponse
from pypureclient.flasharray.FA_2_44.exceptions import (  # noqa: F401
    ApiTypeError,
    ApiValueError
)
from pypureclient.reference_type import quote_string_parameter

class SNMPAgentsApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client: Optional[_TransportApiClient] = None) -> None:
        self.api_client = api_client if api_client else _TransportApiClient.get_default()

    def api244_snmp_agents_get_with_http_info(
        self,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        **kwargs
    ) -> ApiResponse:  # noqa: E501
        """List SNMP agent

        Displays the SNMP agent name and protocol attributes.

        :param authorization: Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param filter: Narrows down the results to only the response objects that satisfy the filter criteria.
        :type filter: str
        :param limit: Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.
        :type limit: int
        :param offset: The starting position based on the results of the query in relation to the full set of response objects returned.
        :type offset: int
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.
        :type sort: List[str]
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.
        :type total_item_count: bool
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
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: tuple(SnmpAgentGetResponse, status_code(int), headers(HTTPHeaderDict))
        """

        _params = locals()

        _all_params = [
            'authorization',
            'x_request_id',
            'filter',
            'limit',
            'offset',
            'sort',
            'total_item_count'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method api244_snmp_agents_get" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}

        # process the query parameters
        _query_params = []
        if _params.get('filter') is not None:  # noqa: E501
            _query_params.append(('filter', _params['filter']))

        if _params.get('limit') is not None:  # noqa: E501
            _query_params.append(('limit', _params['limit']))

        if _params.get('offset') is not None:  # noqa: E501
            _query_params.append(('offset', _params['offset']))

        if _params.get('sort') is not None:  # noqa: E501
            _query_params.append(('sort', _params['sort']))
            _collection_formats['sort'] = 'csv'

        if _params.get('total_item_count') is not None:  # noqa: E501
            _query_params.append(('total_item_count', _params['total_item_count']))

        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))
        if _params['authorization'] is not None:
            _header_params['Authorization'] = _params['authorization']

        if _params['x_request_id'] is not None:
            _header_params['X-Request-ID'] = _params['x_request_id']

        # process the form parameters
        _form_params = []
        _files = {}
        # process the body parameter
        _body_params = None
        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # authentication setting
        _auth_settings = []  # noqa: E501

        _response_types_map = {
            '200': "SnmpAgentGetResponse",
        }

        return self.api_client.call_api(
            '/api/2.44/snmp-agents', 'GET',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))

    def api244_snmp_agents_mib_get_with_http_info(
        self,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        **kwargs
    ) -> ApiResponse:  # noqa: E501
        """List SNMP agent MIB text

        Displays the SNMP MIB text.

        :param authorization: Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param filter: Narrows down the results to only the response objects that satisfy the filter criteria.
        :type filter: str
        :param limit: Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.
        :type limit: int
        :param offset: The starting position based on the results of the query in relation to the full set of response objects returned.
        :type offset: int
        :param sort: Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.
        :type sort: List[str]
        :param total_item_count: If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.
        :type total_item_count: bool
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
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: tuple(SnmpAgentMibGetResponse, status_code(int), headers(HTTPHeaderDict))
        """

        _params = locals()

        _all_params = [
            'authorization',
            'x_request_id',
            'filter',
            'limit',
            'offset',
            'sort',
            'total_item_count'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method api244_snmp_agents_mib_get" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}

        # process the query parameters
        _query_params = []
        if _params.get('filter') is not None:  # noqa: E501
            _query_params.append(('filter', _params['filter']))

        if _params.get('limit') is not None:  # noqa: E501
            _query_params.append(('limit', _params['limit']))

        if _params.get('offset') is not None:  # noqa: E501
            _query_params.append(('offset', _params['offset']))

        if _params.get('sort') is not None:  # noqa: E501
            _query_params.append(('sort', _params['sort']))
            _collection_formats['sort'] = 'csv'

        if _params.get('total_item_count') is not None:  # noqa: E501
            _query_params.append(('total_item_count', _params['total_item_count']))

        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))
        if _params['authorization'] is not None:
            _header_params['Authorization'] = _params['authorization']

        if _params['x_request_id'] is not None:
            _header_params['X-Request-ID'] = _params['x_request_id']

        # process the form parameters
        _form_params = []
        _files = {}
        # process the body parameter
        _body_params = None
        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # authentication setting
        _auth_settings = []  # noqa: E501

        _response_types_map = {
            '200': "SnmpAgentMibGetResponse",
        }

        return self.api_client.call_api(
            '/api/2.44/snmp-agents/mib', 'GET',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))

    def api244_snmp_agents_patch_with_http_info(
        self,
        snmp_agent: SnmpAgentPatch,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        **kwargs
    ) -> ApiResponse:  # noqa: E501
        """Modify SNMP agent

        Modifies the name or the protocol attributes of the SNMP agent.

        :param snmp_agent: (required)
        :type snmp_agent: SnmpAgentPatch
        :param authorization: Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
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
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: tuple(SnmpAgentResponse, status_code(int), headers(HTTPHeaderDict))
        """

        _params = locals()

        _all_params = [
            'snmp_agent',
            'authorization',
            'x_request_id'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method api244_snmp_agents_patch" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}

        # process the query parameters
        _query_params = []
        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))
        if _params['authorization'] is not None:
            _header_params['Authorization'] = _params['authorization']

        if _params['x_request_id'] is not None:
            _header_params['X-Request-ID'] = _params['x_request_id']

        # process the form parameters
        _form_params = []
        _files = {}
        # process the body parameter
        _body_params = None
        if _params['snmp_agent'] is not None:
            _body_params = _params['snmp_agent']

        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # set the HTTP header `Content-Type`
        _content_types_list = _params.get('_content_type',
            self.api_client.select_header_content_type(
                ['application/json']))
        if _content_types_list:
                _header_params['Content-Type'] = _content_types_list

        # authentication setting
        _auth_settings = []  # noqa: E501

        _response_types_map = {
            '200': "SnmpAgentResponse",
        }

        return self.api_client.call_api(
            '/api/2.44/snmp-agents', 'PATCH',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))
