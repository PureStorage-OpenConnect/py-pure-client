
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

from pypureclient.flasharray.FA_2_44.models.file_system_get_response import FileSystemGetResponse
from pypureclient.flasharray.FA_2_44.models.file_system_patch import FileSystemPatch
from pypureclient.flasharray.FA_2_44.models.file_system_response import FileSystemResponse
from typing import Optional
from pypureclient.flasharray.FA_2_44.api_client import ApiClient as _TransportApiClient
from pypureclient.flasharray.FA_2_44.api_response import ApiResponse
from pypureclient.flasharray.FA_2_44.exceptions import (  # noqa: F401
    ApiTypeError,
    ApiValueError
)
from pypureclient.reference_type import quote_string_parameter

class FileSystemsApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client: Optional[_TransportApiClient] = None) -> None:
        self.api_client = api_client if api_client else _TransportApiClient.get_default()

    def api244_file_systems_delete_with_http_info(
        self,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        context_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the context specified. If specified, the context names must be an array of size 1, and the single element must be the name of an array in the same fleet. If not specified, the context will default to the array that received this request. Other parameters provided with the request, such as names of volumes or snapshots, are resolved relative to the provided `context`.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique resource IDs specified. Enter multiple resource IDs in comma-separated format. The `ids` or `names` parameter is required, but they cannot be set together.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        **kwargs
    ) -> ApiResponse:  # noqa: E501
        """Delete file system

        Deletes a file system that has been destroyed and is pending eradication. Eradicated file systems cannot be recovered. File systems are destroyed using the PATCH method.

        :param authorization: Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param context_names: Performs the operation on the context specified. If specified, the context names must be an array of size 1, and the single element must be the name of an array in the same fleet. If not specified, the context will default to the array that received this request. Other parameters provided with the request, such as names of volumes or snapshots, are resolved relative to the provided `context`.
        :type context_names: List[str]
        :param ids: Performs the operation on the unique resource IDs specified. Enter multiple resource IDs in comma-separated format. The `ids` or `names` parameter is required, but they cannot be set together.
        :type ids: List[str]
        :param names: Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.
        :type names: List[str]
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
        :rtype: None
        """

        _params = locals()

        _all_params = [
            'authorization',
            'x_request_id',
            'context_names',
            'ids',
            'names'
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
                    " to method api244_file_systems_delete" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}

        # process the query parameters
        _query_params = []
        if _params.get('context_names') is not None:  # noqa: E501
            _query_params.append(('context_names', _params['context_names']))
            _collection_formats['context_names'] = 'csv'

        if _params.get('ids') is not None:  # noqa: E501
            _query_params.append(('ids', _params['ids']))
            _collection_formats['ids'] = 'csv'

        if _params.get('names') is not None:  # noqa: E501
            _query_params.append(('names', _params['names']))
            _collection_formats['names'] = 'csv'

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
        # authentication setting
        _auth_settings = []  # noqa: E501

        _response_types_map = {}

        return self.api_client.call_api(
            '/api/2.44/file-systems', 'DELETE',
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

    def api244_file_systems_get_with_http_info(
        self,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        allow_errors: Annotated[Optional[StrictBool], Field(description="If set to `true`, the API will allow the operation to continue even if there are errors. Any errors will be returned in the `errors` field of the response. If set to `false`, the operation will fail if there are any errors.")] = None,
        context_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique contexts specified. If specified, each context name must be the name of an array in the same fleet. If not specified, the context will default to the array that received this request. Other parameters provided with the request, such as names of volumes or snapshots, are resolved relative to the provided `context`. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        continuation_token: Annotated[Optional[StrictStr], Field(description="A token used to retrieve the next page of data with some consistency guaranteed. The token is a Base64 encoded value. Set `continuation_token` to the system-generated token taken from the `x-next-token` header field of the response. A query has reached its last page when the response does not include a token. Pagination requires the `limit` and `continuation_token` query parameters.")] = None,
        destroyed: Annotated[Optional[StrictBool], Field(description="If set to `true`, lists only destroyed objects that are in the eradication pending state. If set to `false`, lists only objects that are not destroyed. For destroyed objects, the time remaining is displayed in milliseconds.")] = None,
        filter: Annotated[Optional[StrictStr], Field(description="Narrows down the results to only the response objects that satisfy the filter criteria.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique resource IDs specified. Enter multiple resource IDs in comma-separated format. The `ids` or `names` parameter is required, but they cannot be set together.")] = None,
        limit: Annotated[Optional[conint(strict=True, ge=0)], Field(description="Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        offset: Annotated[Optional[conint(strict=True, ge=0)], Field(description="The starting position based on the results of the query in relation to the full set of response objects returned.")] = None,
        sort: Annotated[Optional[conlist(constr(strict=True))], Field(description="Returns the response objects in the order specified. Set `sort` to the name in the response by which to sort. Sorting can be performed on any of the names in the response, and the objects can be sorted in ascending or descending order. By default, the response objects are sorted in ascending order. To sort in descending order, append the minus sign (`-`) to the name. A single request can be sorted on multiple objects. For example, you can sort all volumes from largest to smallest volume size, and then sort volumes of the same size in ascending order by volume name. To sort on multiple names, list the names as comma-separated values.")] = None,
        total_item_count: Annotated[Optional[StrictBool], Field(description="If set to `true`, the `total_item_count` matching the specified query parameters is calculated and returned in the response. If set to `false`, the `total_item_count` is `null` in the response. This may speed up queries where the `total_item_count` is large. If not specified, defaults to `false`.")] = None,
        **kwargs
    ) -> ApiResponse:  # noqa: E501
        """List file systems

        Displays a list of file systems, including those pending eradication.

        :param authorization: Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param allow_errors: If set to `true`, the API will allow the operation to continue even if there are errors. Any errors will be returned in the `errors` field of the response. If set to `false`, the operation will fail if there are any errors.
        :type allow_errors: bool
        :param context_names: Performs the operation on the unique contexts specified. If specified, each context name must be the name of an array in the same fleet. If not specified, the context will default to the array that received this request. Other parameters provided with the request, such as names of volumes or snapshots, are resolved relative to the provided `context`. Enter multiple names in comma-separated format. For example, `name01,name02`.
        :type context_names: List[str]
        :param continuation_token: A token used to retrieve the next page of data with some consistency guaranteed. The token is a Base64 encoded value. Set `continuation_token` to the system-generated token taken from the `x-next-token` header field of the response. A query has reached its last page when the response does not include a token. Pagination requires the `limit` and `continuation_token` query parameters.
        :type continuation_token: str
        :param destroyed: If set to `true`, lists only destroyed objects that are in the eradication pending state. If set to `false`, lists only objects that are not destroyed. For destroyed objects, the time remaining is displayed in milliseconds.
        :type destroyed: bool
        :param filter: Narrows down the results to only the response objects that satisfy the filter criteria.
        :type filter: str
        :param ids: Performs the operation on the unique resource IDs specified. Enter multiple resource IDs in comma-separated format. The `ids` or `names` parameter is required, but they cannot be set together.
        :type ids: List[str]
        :param limit: Limits the size of the response to the specified number of objects on each page. To return the total number of resources, set `limit=0`. The total number of resources is returned as a `total_item_count` value. If the page size requested is larger than the system maximum limit, the server returns the maximum limit, disregarding the requested page size.
        :type limit: int
        :param names: Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.
        :type names: List[str]
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
        :rtype: tuple(FileSystemGetResponse, status_code(int), headers(HTTPHeaderDict))
        """

        _params = locals()

        _all_params = [
            'authorization',
            'x_request_id',
            'allow_errors',
            'context_names',
            'continuation_token',
            'destroyed',
            'filter',
            'ids',
            'limit',
            'names',
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
                    " to method api244_file_systems_get" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}

        # process the query parameters
        _query_params = []
        if _params.get('allow_errors') is not None:  # noqa: E501
            _query_params.append(('allow_errors', _params['allow_errors']))

        if _params.get('context_names') is not None:  # noqa: E501
            _query_params.append(('context_names', _params['context_names']))
            _collection_formats['context_names'] = 'csv'

        if _params.get('continuation_token') is not None:  # noqa: E501
            _query_params.append(('continuation_token', _params['continuation_token']))

        if _params.get('destroyed') is not None:  # noqa: E501
            _query_params.append(('destroyed', _params['destroyed']))

        if _params.get('filter') is not None:  # noqa: E501
            _query_params.append(('filter', _params['filter']))

        if _params.get('ids') is not None:  # noqa: E501
            _query_params.append(('ids', _params['ids']))
            _collection_formats['ids'] = 'csv'

        if _params.get('limit') is not None:  # noqa: E501
            _query_params.append(('limit', _params['limit']))

        if _params.get('names') is not None:  # noqa: E501
            _query_params.append(('names', _params['names']))
            _collection_formats['names'] = 'csv'

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
            '200': "FileSystemGetResponse",
        }

        return self.api_client.call_api(
            '/api/2.44/file-systems', 'GET',
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

    def api244_file_systems_patch_with_http_info(
        self,
        file_system: FileSystemPatch,
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        context_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the context specified. If specified, the context names must be an array of size 1, and the single element must be the name of an array in the same fleet. If not specified, the context will default to the array that received this request. Other parameters provided with the request, such as names of volumes or snapshots, are resolved relative to the provided `context`.")] = None,
        ids: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique resource IDs specified. Enter multiple resource IDs in comma-separated format. The `ids` or `names` parameter is required, but they cannot be set together.")] = None,
        names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.")] = None,
        **kwargs
    ) -> ApiResponse:  # noqa: E501
        """Modify a file system

        Modifies a file system. You can rename, destroy, move, or recover a file system. To rename a file system, set `name` to the new name. To destroy a file system, set `destroyed=true`. To move a file system, set 'pod' to the destination pod reference. To recover a file system that has been destroyed and is pending eradication, set `destroyed=false`.

        :param file_system: (required)
        :type file_system: FileSystemPatch
        :param authorization: Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param context_names: Performs the operation on the context specified. If specified, the context names must be an array of size 1, and the single element must be the name of an array in the same fleet. If not specified, the context will default to the array that received this request. Other parameters provided with the request, such as names of volumes or snapshots, are resolved relative to the provided `context`.
        :type context_names: List[str]
        :param ids: Performs the operation on the unique resource IDs specified. Enter multiple resource IDs in comma-separated format. The `ids` or `names` parameter is required, but they cannot be set together.
        :type ids: List[str]
        :param names: Performs the operation on the unique name specified. Enter multiple names in comma-separated format. For example, `name01,name02`.
        :type names: List[str]
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
        :rtype: tuple(FileSystemResponse, status_code(int), headers(HTTPHeaderDict))
        """

        _params = locals()

        _all_params = [
            'file_system',
            'authorization',
            'x_request_id',
            'context_names',
            'ids',
            'names'
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
                    " to method api244_file_systems_patch" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}

        # process the query parameters
        _query_params = []
        if _params.get('context_names') is not None:  # noqa: E501
            _query_params.append(('context_names', _params['context_names']))
            _collection_formats['context_names'] = 'csv'

        if _params.get('ids') is not None:  # noqa: E501
            _query_params.append(('ids', _params['ids']))
            _collection_formats['ids'] = 'csv'

        if _params.get('names') is not None:  # noqa: E501
            _query_params.append(('names', _params['names']))
            _collection_formats['names'] = 'csv'

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
        if _params['file_system'] is not None:
            _body_params = _params['file_system']

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
            '200': "FileSystemResponse",
        }

        return self.api_client.call_api(
            '/api/2.44/file-systems', 'PATCH',
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

    def api244_file_systems_post_with_http_info(
        self,
        names: Annotated[conlist(StrictStr), Field(..., description="Performs the operation on the unique name specified. For example, `name01`. Enter multiple names in comma-separated format.")],
        authorization: Annotated[Optional[StrictStr], Field(description="Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)")] = None,
        x_request_id: Annotated[Optional[StrictStr], Field(description="Supplied by client during request or generated by server.")] = None,
        context_names: Annotated[Optional[conlist(StrictStr)], Field(description="Performs the operation on the context specified. If specified, the context names must be an array of size 1, and the single element must be the name of an array in the same fleet. If not specified, the context will default to the array that received this request. Other parameters provided with the request, such as names of volumes or snapshots, are resolved relative to the provided `context`.")] = None,
        **kwargs
    ) -> ApiResponse:  # noqa: E501
        """Create file system

        Creates one or more file systems.

        :param names: Performs the operation on the unique name specified. For example, `name01`. Enter multiple names in comma-separated format. (required)
        :type names: List[str]
        :param authorization: Access token (in JWT format) required to use any API endpoint (except `/oauth2`, `/login`, and `/logout`)
        :type authorization: str
        :param x_request_id: Supplied by client during request or generated by server.
        :type x_request_id: str
        :param context_names: Performs the operation on the context specified. If specified, the context names must be an array of size 1, and the single element must be the name of an array in the same fleet. If not specified, the context will default to the array that received this request. Other parameters provided with the request, such as names of volumes or snapshots, are resolved relative to the provided `context`.
        :type context_names: List[str]
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
        :rtype: tuple(FileSystemResponse, status_code(int), headers(HTTPHeaderDict))
        """

        _params = locals()

        _all_params = [
            'names',
            'authorization',
            'x_request_id',
            'context_names'
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
                    " to method api244_file_systems_post" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}

        # process the query parameters
        _query_params = []
        if _params.get('context_names') is not None:  # noqa: E501
            _query_params.append(('context_names', _params['context_names']))
            _collection_formats['context_names'] = 'csv'

        if _params.get('names') is not None:  # noqa: E501
            _query_params.append(('names', _params['names']))
            _collection_formats['names'] = 'csv'

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
            '200': "FileSystemResponse",
        }

        return self.api_client.call_api(
            '/api/2.44/file-systems', 'POST',
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
