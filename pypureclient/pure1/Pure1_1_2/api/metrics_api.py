# coding: utf-8

"""
    Pure1 Public REST API

    Pure1 Public REST API, developed by [Pure Storage, Inc.](https://www.purestorage.com)   The Pure1 REST API 2.0 offers one single form of authentication: OAuth 2.0 via the [Token Exchange protocol](https://datatracker.ietf.org/doc/draft-ietf-oauth-token-exchange).  OAuth 2.0 is an open protocol to allow secure authorization in a simple and standard method from web, mobile, desktop and background applications.  Note that the [Authentication](#section/Authentication) section below mentions 'API Key' as the security scheme type. This is solely for the purpose of allowing testing this API with [Swagger UI](https://static.pure1.purestorage.com/api-swagger/index.html).  [Knowledge base reference documentation](https://support.purestorage.com/Pure1/Pure1_Manage/Pure1_Manage_-_REST_API/Pure1_Manage_-_REST_API__Reference)

    OpenAPI spec version: 1.2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import re

# python 2 and python 3 compatibility library
import six
import uuid
from typing import List, Optional

from .. import models

class MetricsApi(object):

    def __init__(self, api_client):
        self.api_client = api_client

    def api12_metrics_get_with_http_info(
        self,
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        resource_types=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.MetricGetResponse
        """Get metrics

        Retrieves information about metrics that can be queried for. 
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.api12_metrics_get_with_http_info(async_req=True)
        >>> result = thread.get()

        :param str authorization: Access token (in JWT format) required to use any API endpoint (except `/oauth2`) 
        :param str x_request_id: Supplied by client during request or generated by server. 
        :param str continuation_token: An opaque token used to iterate over a collection. The token to use on the next request is returned in the `continuation_token` field of the result. Single quotes are required around all strings. 
        :param str filter: Exclude resources that don't match the specified criteria. Single quotes are required around all strings inside the filters. 
        :param list[str] ids: A comma-separated list of resource IDs. If there is not at least one resource that matches each `id` element, an error is returned. Single quotes are required around all strings. 
        :param int limit: Limit the size of the response to the specified number of resources. A limit of 0 can be used to get the number of resources without getting all of the resources. It will be returned in the total_item_count field. If a client asks for a page size larger than the maximum number, the request is still valid. In that case the server just returns the maximum number of items, disregarding the client's page size request. If not specified, defaults to 1000. 
        :param list[str] names: A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings. 
        :param int offset: The offset of the first resource to return from a collection. 
        :param list[str] resource_types: The resource types to list the available metrics. Valid values are `arrays`, `buckets`, `directories`, `file-systems`, `pods`, `subscription-licenses` and `volumes`.  A metric can belong to a combination of resources, e.g., write-iops from array to pod. In that case, query by ['arrays', 'pods']. Single quotes are required around all strings. 
        :param list[str] sort: Sort the response by the specified fields (in descending order if '-' is appended to the field name). If you provide a sort you will not get a continuation token in the response. 
        :param bool async_req: Request runs in separate thread and method returns multiprocessing.pool.ApplyResult.
        :param bool _return_http_data_only: Returns only data field.
        :param bool _preload_content: Response is converted into objects.
        :param int _request_timeout: Total request timeout in seconds.
                 It can also be a tuple of (connection time, read time) timeouts.
        :return: MetricGetResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """
        continuation_token = models.quoteString(continuation_token)
        if ids is not None:
            if not isinstance(ids, list):
                ids = [ids]
        ids = models.quoteStrings(ids)
        if names is not None:
            if not isinstance(names, list):
                names = [names]
        names = models.quoteStrings(names)
        if resource_types is not None:
            if not isinstance(resource_types, list):
                resource_types = [resource_types]
        resource_types = models.quoteStrings(resource_types)
        if sort is not None:
            if not isinstance(sort, list):
                sort = [sort]
        params = {k: v for k, v in six.iteritems(locals()) if v is not None}

        # Convert the filter into a string
        if params.get('filter'):
            params['filter'] = str(params['filter'])
        if params.get('sort'):
            params['sort'] = [str(_x) for _x in params['sort']]
        # Assign a value to X-Request-Id if it is not specified
        if params.get('x_request_id') is None:
            params['x_request_id'] = str(uuid.uuid4())

        if 'offset' in params and params['offset'] < 0:
            raise ValueError("Invalid value for parameter `offset` when calling `api12_metrics_get`, must be a value greater than or equal to `0`")
        collection_formats = {}
        path_params = {}

        query_params = []
        if 'continuation_token' in params:
            query_params.append(('continuation_token', params['continuation_token']))
        if 'filter' in params:
            query_params.append(('filter', params['filter']))
        if 'ids' in params:
            query_params.append(('ids', params['ids']))
            collection_formats['ids'] = 'csv'
        if 'limit' in params:
            query_params.append(('limit', params['limit']))
        if 'names' in params:
            query_params.append(('names', params['names']))
            collection_formats['names'] = 'csv'
        if 'offset' in params:
            query_params.append(('offset', params['offset']))
        if 'resource_types' in params:
            query_params.append(('resource_types', params['resource_types']))
            collection_formats['resource_types'] = 'csv'
        if 'sort' in params:
            query_params.append(('sort', params['sort']))
            collection_formats['sort'] = 'csv'

        header_params = {}
        if 'authorization' in params:
            header_params['Authorization'] = params['authorization']
        if 'x_request_id' in params:
            header_params['X-Request-ID'] = params['x_request_id']

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(
            ['application/json'])

        # Authentication setting
        auth_settings = ['AuthorizationHeader']

        return self.api_client.call_api(
            '/api/1.2/metrics', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='MetricGetResponse',
            auth_settings=auth_settings,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
            collection_formats=collection_formats,
        )

    def api12_metrics_history_get_with_http_info(
        self,
        aggregation=None,  # type: str
        end_time=None,  # type: int
        resolution=None,  # type: int
        start_time=None,  # type: int
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        resource_ids=None,  # type: List[str]
        resource_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.MetricHistoryGetResponse
        """Get metrics history

        Retrieves historical metric data for resources. This endpoint supports batching: Up to 32 time series can be retrieved in one call. It can be multiple metrics for one resource, (e.g., load and bandwidth for one array - 2 time series), one metric for multiple resource (e.g., load for arrayA and arrayB - 2 time series), or a combination of both, multiple metrics for multiple resources, (e.g., load and bandwidth for arrayA and arrayB - 4 time series). 
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.api12_metrics_history_get_with_http_info(aggregation, end_time, resolution, start_time, async_req=True)
        >>> result = thread.get()

        :param str aggregation: Aggregation needed on the metric data. Valid values are `avg` and `max`. Single quotes are required around all strings. Latency metrics averages are weighted by the IOPS.  (required)
        :param int end_time: Timestamp of when the time window ends. Measured in milliseconds since the UNIX epoch.  (required)
        :param int resolution: The duration of time between individual data points, in milliseconds.  (required)
        :param int start_time: Timestamp of when the time window starts. Measured in milliseconds since the UNIX epoch.  (required)
        :param str authorization: Access token (in JWT format) required to use any API endpoint (except `/oauth2`) 
        :param str x_request_id: Supplied by client during request or generated by server. 
        :param list[str] ids: REQUIRED: either `ids` or `names`. A comma-separated list of object IDs. If there is not at least one resource that matches each `id` element, an error is returned.  Single quotes are required around all strings. 
        :param list[str] names: REQUIRED: either `names` or `ids`. A comma-separated list of resource names. If there is not at least one resource that matches each `name` element, an error is returned. Single quotes are required around all strings. 
        :param list[str] resource_ids: REQUIRED: either `resource_ids` or `resource_names`. A comma-separated list of resource IDs. If there is not at least one resource that matches each `resource_id` element, an error is returned. Single quotes are required around all strings. 
        :param list[str] resource_names: REQUIRED: either `resource_ids` or `resource_names`. A comma-separated list of resource names. If there is not at least one resource that matches each `resource_name`  element, an error is returned. Single quotes are required around all strings. 
        :param bool async_req: Request runs in separate thread and method returns multiprocessing.pool.ApplyResult.
        :param bool _return_http_data_only: Returns only data field.
        :param bool _preload_content: Response is converted into objects.
        :param int _request_timeout: Total request timeout in seconds.
                 It can also be a tuple of (connection time, read time) timeouts.
        :return: MetricHistoryGetResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """
        aggregation = models.quoteString(aggregation)
        if ids is not None:
            if not isinstance(ids, list):
                ids = [ids]
        ids = models.quoteStrings(ids)
        if names is not None:
            if not isinstance(names, list):
                names = [names]
        names = models.quoteStrings(names)
        if resource_ids is not None:
            if not isinstance(resource_ids, list):
                resource_ids = [resource_ids]
        resource_ids = models.quoteStrings(resource_ids)
        if resource_names is not None:
            if not isinstance(resource_names, list):
                resource_names = [resource_names]
        resource_names = models.quoteStrings(resource_names)
        params = {k: v for k, v in six.iteritems(locals()) if v is not None}

        # Convert the filter into a string
        if params.get('filter'):
            params['filter'] = str(params['filter'])
        if params.get('sort'):
            params['sort'] = [str(_x) for _x in params['sort']]
        # Assign a value to X-Request-Id if it is not specified
        if params.get('x_request_id') is None:
            params['x_request_id'] = str(uuid.uuid4())
        # verify the required parameter 'aggregation' is set
        if aggregation is None:
            raise TypeError("Missing the required parameter `aggregation` when calling `api12_metrics_history_get`")
        # verify the required parameter 'end_time' is set
        if end_time is None:
            raise TypeError("Missing the required parameter `end_time` when calling `api12_metrics_history_get`")
        # verify the required parameter 'resolution' is set
        if resolution is None:
            raise TypeError("Missing the required parameter `resolution` when calling `api12_metrics_history_get`")
        # verify the required parameter 'start_time' is set
        if start_time is None:
            raise TypeError("Missing the required parameter `start_time` when calling `api12_metrics_history_get`")

        collection_formats = {}
        path_params = {}

        query_params = []
        if 'aggregation' in params:
            query_params.append(('aggregation', params['aggregation']))
        if 'end_time' in params:
            query_params.append(('end_time', params['end_time']))
        if 'ids' in params:
            query_params.append(('ids', params['ids']))
            collection_formats['ids'] = 'csv'
        if 'names' in params:
            query_params.append(('names', params['names']))
            collection_formats['names'] = 'csv'
        if 'resolution' in params:
            query_params.append(('resolution', params['resolution']))
        if 'resource_ids' in params:
            query_params.append(('resource_ids', params['resource_ids']))
            collection_formats['resource_ids'] = 'csv'
        if 'resource_names' in params:
            query_params.append(('resource_names', params['resource_names']))
            collection_formats['resource_names'] = 'csv'
        if 'start_time' in params:
            query_params.append(('start_time', params['start_time']))

        header_params = {}
        if 'authorization' in params:
            header_params['Authorization'] = params['authorization']
        if 'x_request_id' in params:
            header_params['X-Request-ID'] = params['x_request_id']

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(
            ['application/json'])

        # Authentication setting
        auth_settings = ['AuthorizationHeader']

        return self.api_client.call_api(
            '/api/1.2/metrics/history', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='MetricHistoryGetResponse',
            auth_settings=auth_settings,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
            collection_formats=collection_formats,
        )
