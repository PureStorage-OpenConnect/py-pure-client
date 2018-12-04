import json
import os
import time

from pypureclient.pure1.api_client import ApiClient
from pypureclient.pure1.exceptions import PureError
from pypureclient.pure1.keywords import Parameters, Headers, Responses
from pypureclient.pure1.responses import ValidResponse, ErrorResponse, Pure1Headers, ApiError, ItemIterator
from pypureclient.pure1.rest import ApiException
from pypureclient.pure1.token_manager import TokenManager
from . import api
from . import models


class Client(object):
    '''
    A client for making REST API calls to Pure1.
    '''
    def __init__(self, **kwargs):
        '''
        Initialize a Pure1 Client.

        Keyword args:
            app_id (str, optional): The registered App ID for Pure1 to use.
                Defaults to the set envioronment variable under PURE1_APP_ID.
            id_token (str, optional): The ID token to use. Overrides given
                App ID and private key. Defaults to environment variable set
                under PURE1_ID_TOKEN.
            private_key_file (str, optional): The path of the private key to
                use. Defaults to the set envioronment variable under
                PURE1_PRIVATE_KEY_FILE.
            private_key_password (str, optional): The password of the private
                key, if encrypted. Defaults to the set envioronment variable
                under PURE1_PRIVATE_KEY_FILE. Defaults to None.
            retires (int, optional): The number of times to retry an API call if
                it failed for a non-blocking reason. Defaults to 5.
            timeout (float or (float, float), optional): The timeout
                duration in seconds, either in total time or (connect and read)
                times. Defaults to 15.0 total.

        Raises:
            PureError: If it could not create an ID or access token
        '''
        # Class constants
        self.APP_ID_KEY = 'app_id'
        self.APP_ID_ENV = 'PURE1_APP_ID'
        self.ID_TOKEN_KEY = 'id_token'
        self.ID_TOKEN_ENV = 'PURE1_ID_TOKEN'
        self.PRIVATE_KEY_FILE_KEY = 'private_key_file'
        self.PRIVATE_KEY_FILE_ENV = 'PURE1_PRIVATE_KEY_FILE'
        self.PRIVATE_KEY_PASSWORD_KEY = 'private_key_password'
        self.PRIVATE_KEY_PASSWORD_ENV = 'PURE1_PRIVATE_KEY_PASSWORD'
        self.RETRIES_KEY = 'retries'
        self.RETRIES_DEFAULT = 5
        self.TOKEN_ENDPOINT = 'https://api.pure1.purestorage.com/oauth2/1.0/token'
        self.TIMEOUT_KEY = 'timeout'
        self.TIMEOUT_DEFAULT = 15.0
        self.USER_AGENT = 'Pure1/PythonSDK/1.0.0'
        # Read ID and key from kwargs or env variables (kwargs override)
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
                                       app_id=app_id,
                                       private_key_file=private_key_file,
                                       private_key_password=private_key_password,
                                       id_token=id_token)
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
        self._set_agent_header()
        self._set_auth_header()
        # Instantiate the various APIs
        self._arrays_api = api.ArraysApi(self._api_client)
        self._file_systems_api = api.FileSystemsApi(self._api_client)
        self._file_system_snapshots_api = api.FileSystemSnapshotsApi(self._api_client)
        self._metrics_api = api.MetricsApi(self._api_client)
        self._network_interfaces_api = api.NetworkInterfacesApi(self._api_client)
        self._pods_api = api.PodsApi(self._api_client)
        self._volumes_api = api.VolumesApi(self._api_client)
        self._volume_snapshots_api = api.VolumeSnapshotsApi(self._api_client)

    def get_access_token(self, refresh=False):
        '''
        Get the last used access token.

        Args:
            refresh (bool, optional):
                Whether to retrieve a new access token. Defaults to False.

        Returns:
            str

        Raises:
            PureError: If there was an error retrieving an access token.
        '''
        return self._token_man.get_access_token(refresh)

    def get_arrays(self, references=None, **kwargs):
        '''
        Get FlashArray and FlashBlade objects.

        Args:
            references (list[FixedReference], optional):
                References to query for. Overrides ids and names keyword
                arguments. Can also be a single element.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional): A filter to include only resources
                that match the specified criteria.
            ids (list[str], optional): Resource IDs to query for. Can also be a
                single element.
            limit (int, optional): Limit the number of resources in the
                response.
            names (list[str], optional): Resource names to query for. Can also
                be a single element.
            offset (int): The offset of the first resource to return from a
                collection.
            sort (list[Property], optional): Sort the response by the specified
                Properties. Can also be a single element.
            x_request_id (str, optional): A header to provide to track the
                API call. Generated by the server if not provided.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            TypeError: If invalid or missing parameters are used.
            ValueError: If a parameter is of an invalid type.
            PureError: If there was an error unpacking parameters or an unknown
                error occurred when trying to call the API.
        '''
        ENDPOINT = self._arrays_api.api10_arrays_get_with_http_info
        if references is not None:
            kwargs = self._process_references_ids(references, kwargs)
        kwargs = self._process_kwargs(kwargs)
        response, is_error = self._call_api(ENDPOINT, kwargs, self._retries)
        return self._package_response(response, is_error, ENDPOINT, kwargs)

    def get_arrays_tags(self, resources=None, **kwargs):
        '''
        Get tags on arrays.

        Args:
            resources (list[FixedReference], optional): References to query
                for. Overrides resource_ids and resource_names keyword arguments.

        Keyword args:
            continuation_token (str, optional): An opaque token to iterate over
                a collection of resources.
            filter (Filter, optional): A filter to include only resources
                that match the specified criteria.
            keys (list[str], optional): A list of tag keys. Can also be a
                single element.
            limit (int, optional): Limit the number of resources in the
                response.
            namespaces (list[str], optional): Namespaces to query for. Can also
                be a single element.
            offset (int): The offset of the first resource to return from a
                collection.
            resource_ids (list[str], optional): Resource ids to get tags for.
                Can also be a single element.
            resource_names (list[str], optional): Resource names to get tags
                for. Can also be a single element.
            x_request_id (str, optional): A header to provide to track the
                API call. Generated by the server if not provided.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            TypeError: If invalid or missing parameters are used.
            ValueError: If a parameter is of an invalid type.
            PureError: If there was an error unpacking parameters or an unknown
                error occurred when trying to call the API.
        '''
        ENDPOINT = self._arrays_api.api10_arrays_tags_get_with_http_info
        if resources is not None:
            kwargs = self._process_references_resource_ids(resources, kwargs)
        kwargs = self._process_kwargs(kwargs)
        response, is_error = self._call_api(ENDPOINT, kwargs, self._retries)
        return self._package_response(response, is_error, ENDPOINT, kwargs)

    def delete_arrays_tags(self, resources=None, **kwargs):
        '''
        Delete tags from arrays.

        Args:
            resources (list[FixedReference], optional): References of resource
                to get tags for. Overrides resource_ids and resource_names.
                Can also be a single element.

        Keyword args:
            keys (list[str], optional): A list of tag keys. Can also be a
                single element.
            namespaces (list[str], optional): A list of namespaces. Can also
                be a single element.
            resource_ids (list[str], optional): Resource ids to get tags for.
                Can also be a single element.
            resource_names (list[str], optional): Resource names to get tags
                for. Can also be a single element.
            x_request_id (str, optional): A header to provide to track the
                API call. Generated by the server if not provided.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            TypeError: If invalid or missing parameters are used.
            ValueError: If a parameter is of an invalid type.
            PureError: If there was an error unpacking parameters or an unknown
                error occurred when trying to call the API.
        '''
        ENDPOINT = self._arrays_api.api10_arrays_tags_delete_with_http_info
        if resources is not None:
            kwargs = self._process_references_resource_ids(resources, kwargs)
        kwargs = self._process_kwargs(kwargs)
        response, is_error = self._call_api(ENDPOINT, kwargs, self._retries)
        return self._package_response(response, is_error, ENDPOINT, kwargs)

    def put_arrays_tags(self, resources=None, **kwargs):
        '''
        Put tags on arrays.

        Args:
            resources (list[FixedReference], optional): References of resources
                to put tags for. Overrides resource_ids and resource_names.
                Can also be a single element.

        Keyword args:
            namespaces (list[str], optional): A list of namespaces. Can also
                be a single element.
            resource_ids (list[str], optional): Resource ids to get tags for.
                Can also be a single element.
            resource_names (list[str], optional): Resource names to get tags
                for. Can also be a single element.
            tag (list[dict], required): A list of single key-value tags to put.
                Each dict must have one key-value pair. Can also be a single
                element.
            x_request_id (str, optional): A header to provide to track the
                API call. Generated by the server if not provided.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            TypeError: If invalid or missing parameters are used.
            ValueError: If a parameter is of an invalid type.
            PureError: If there was an error unpacking parameters or an unknown
                error occurred when trying to call the API.
        '''
        ENDPOINT = self._arrays_api.api10_arrays_tags_batch_put_with_http_info
        if Parameters.tag in kwargs:
            # Process array tags into the expected type
            raw_tags = kwargs.get(Parameters.tag)
            tag_list = []
            if not isinstance(raw_tags, list):
                raw_tags = [raw_tags]
            for tags in raw_tags:
            # There might be multiple key-value pairs in a single dict element
                for k, v in tags.items():
                    tag_list.append(models.Tag1(k, v))
            kwargs[Parameters.tag] = tag_list
        if resources is not None:
            kwargs = self._process_references_resource_ids(resources, kwargs)
        kwargs = self._process_kwargs(kwargs)
        response, is_error = self._call_api(ENDPOINT, kwargs, self._retries)
        return self._package_response(response, is_error, ENDPOINT, kwargs)

    def get_file_systems(self, references=None, **kwargs):
        '''
        Get FlashBlade file system objects.

        Args:
            references (list[FixedReference], optional): References to query
                for. Overrides ids and names keyword arguments.

        Keyword args:
            continuation_token (str, optional): An opaque token to iterate over
                a collection of resources.
            filter (Filter, optional): A filter to include only resources
                that match the specified criteria.
            ids (list[str], optional): Resource IDs to query for. Can also be a
                single element.
            limit (int, optional): Limit the number of resources in the
                response.
            names (list[str], optional): Resource names to query for. Can also
                be a single element.
            offset (int): The offset of the first resource to return from a
                collection.
            sort (list[Property], optional): Sort the response by the specified
                Properties. Can also be a single element.
            x_request_id (str, optional): A header to provide to track the
                API call. Generated by the server if not provided.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            TypeError: If invalid or missing parameters are used.
            ValueError: If a parameter is of an invalid type.
            PureError: If there was an error unpacking parameters or an unknown
                error occurred when trying to call the API.
        '''
        ENDPOINT = self._file_systems_api.api10_file_systems_get_with_http_info
        if references is not None:
            kwargs = self._process_references_ids(references, kwargs)
        kwargs = self._process_kwargs(kwargs)
        response, is_error = self._call_api(ENDPOINT, kwargs, self._retries)
        return self._package_response(response, is_error, ENDPOINT, kwargs)

    def get_file_system_snapshots(self, references=None, **kwargs):
        '''
        Get snapshots of file systems.

        Args:
            references (list[FixedReference], optional): References to query
                for. Overrides ids and names keyword arguments.

        Keyword args:
            continuation_token (str, optional): An opaque token to iterate over
                a collection of resources.
            filter (Filter, optional): A filter to include only resources
                that match the specified criteria.
            ids (list[str], optional): Resource IDs to query for. Can also be a
                single element.
            limit (int, optional): Limit the number of resources in the
                response.
            names (list[str], optional): Resource names to query for. Can also
                be a single element.
            offset (int): The offset of the first resource to return from a
                collection.
            sort (list[Property], optional): Sort the response by the specified
                Properties. Can also be a single element.
            source_ids (list[str], optional): IDs for source of the object
                to query for. Can also be a single element.
            source_names (list[str], optional): Names for source of the object
                to query for. Can also be a single element.
            x_request_id (str, optional): A header to provide to track the
                API call. Generated by the server if not provided.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            TypeError: If invalid or missing parameters are used.
            ValueError: If a parameter is of an invalid type.
            PureError: If there was an error unpacking parameters or an unknown
                error occurred when trying to call the API.
        '''
        ENDPOINT = self._file_system_snapshots_api.api10_file_system_snapshots_get_with_http_info
        if references is not None:
            kwargs = self._process_references_ids(references, kwargs)
        kwargs = self._process_kwargs(kwargs)
        response, is_error = self._call_api(ENDPOINT, kwargs, self._retries)
        return self._package_response(response, is_error, ENDPOINT, kwargs)

    def get_metrics(self, references=None, **kwargs):
        '''
        Get metrics which can be queried for.

        Args:
            references (list[FixedReference], optional): References to query
                for. Overrides ids and names keyword arguments.

        Keyword args:
            continuation_token (str, optional): An opaque token to iterate over
                a collection of resources.
            filter (Filter, optional): A filter to include only resources
                that match the specified criteria.
            ids (list[str], optional): Resource IDs to query for. Can also be a
                single element.
            limit (int, optional): Limit the number of resources in the
                response.
            names (list[str], optional): Resource names to query for. Can also
                be a single element.
            offset (int): The offset of the first resource to return from a
                collection.
            resource_types (list[str], optional): The resource types of the
                metrics to list. Currently accepted values are "arrays",
                "volumes", and "pods". Can also be a single element.
            sort (list[Property], optional): Sort the response by the specified
                Properties. Can also be a single element.
            x_request_id (str, optional): A header to provide to track the
                API call. Generated by the server if not provided.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            TypeError: If invalid or missing parameters are used.
            ValueError: If a parameter is of an invalid type.
            PureError: If there was an error unpacking parameters or an unknown
                error occurred when trying to call the API.
        '''
        ENDPOINT = self._metrics_api.api10_metrics_get_with_http_info
        if references is not None:
            kwargs = self._process_references_ids(references, kwargs)
        kwargs = self._process_kwargs(kwargs)
        response, is_error = self._call_api(ENDPOINT, kwargs, self._retries)
        return self._package_response(response, is_error, ENDPOINT, kwargs)

    def get_metrics_history(self, **kwargs):
        '''
        Get historical metric data for resources.

        Keyword args:
            aggregation (Property): Aggregation needed on the metric data.
            end_time (int): When the time window ends, in milliseconds since
                epoch.
            ids (list[str], optional): Resource IDs of metrics to query for.
                Can also be a single element.
            references (list[FixedReference], optional): References to metrics
                to get data for. Overrides ids and names. Can also be a single
                item.
            names (list[str], optional): Resource names of metrics to query for.
                Can also be a single element.
            resolution (int): Duration of time between data point, in
                milliseconds.
            resources (list[FixedReference], optional): References of resources
                to get metrics for. Overrides resource_ids and resource_names.
                Can also be a single element.
            resource_ids (list[str], optional): Resource ids to get metric
                data for. Can also be a single element.
            resource_names (list[str], optional): Resource names to get metric
                data for. Can also be a single element.
            sort (list[Property], optional): Sort the response by the specified
                Properties. Can also be a single element.
            start_time (int): When the time window start, in milliseconds since
                epoch.
            x_request_id (str, optional): A header to provide to track the
                API call. Generated by the server if not provided.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            TypeError: If invalid or missing parameters are used.
            ValueError: If a parameter is of an invalid type.
            PureError: If there was an error unpacking parameters or an unknown
                error occurred when trying to call the API.
        '''
        ENDPOINT = self._metrics_api.api10_metrics_history_get_with_http_info
        references = kwargs.get(Parameters.references, None)
        if references is not None:
            kwargs = self._process_references_ids(references, kwargs)
        resources = kwargs.get(Parameters.resources, None)
        if resources is not None:
            kwargs = self._process_references_resource_ids(resources, kwargs)
        kwargs = self._process_kwargs(kwargs)
        response, is_error = self._call_api(ENDPOINT, kwargs, self._retries)
        return self._package_response(response, is_error, ENDPOINT, kwargs)

    def get_network_interfaces(self, references=None, **kwargs):
        '''
        Get physical and virtual network interface objects.

        Args:
            references (list[FixedReference], optional): References to query
                for. Overrides ids and names keyword arguments.

        Keyword args:
            continuation_token (str, optional): An opaque token to iterate over
                a collection of resources.
            filter (Filter, optional): A filter to include only resources
                that match the specified criteria.
            ids (list[str], optional): Resource IDs to query for. Can also be a
                single element.
            limit (int, optional): Limit the number of resources in the
                response.
            names (list[str], optional): Resource names to query for. Can also
                be a single element.
            offset (int): The offset of the first resource to return from a
                collection.
            sort (list[Property], optional): Sort the response by the specified
                Properties. Can also be a single element.
            x_request_id (str, optional): A header to provide to track the
                API call. Generated by the server if not provided.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            TypeError: If invalid or missing parameters are used.
            ValueError: If a parameter is of an invalid type.
            PureError: If there was an error unpacking parameters or an unknown
                error occurred when trying to call the API.
        '''
        ENDPOINT = self._network_interfaces_api.api10_network_interfaces_get_with_http_info
        if references is not None:
            kwargs = self._process_references_ids(references, kwargs)
        kwargs = self._process_kwargs(kwargs)
        response, is_error = self._call_api(ENDPOINT, kwargs, self._retries)
        return self._package_response(response, is_error, ENDPOINT, kwargs)

    def get_pods(self, references=None, **kwargs):
        '''
        Get pod objects.

        Args:
            references (list[FixedReference], optional): References to query
                for. Overrides ids and names keyword arguments.

        Keyword args:
            continuation_token (str, optional): An opaque token to iterate over
                a collection of resources.
            filter (Filter, optional): A filter to include only resources
                that match the specified criteria.
            ids (list[str], optional): Resource IDs to query for. Can also be a
                single element.
            limit (int, optional): Limit the number of resources in the
                response.
            names (list[str], optional): Resource names to query for. Can also
                be a single element.
            offset (int): The offset of the first resource to return from a
                collection.
            sort (list[Property], optional): Sort the response by the specified
                Properties. Can also be a single element.
            x_request_id (str, optional): A header to provide to track the
                API call. Generated by the server if not provided.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            TypeError: If invalid or missing parameters are used.
            ValueError: If a parameter is of an invalid type.
            PureError: If there was an error unpacking parameters or an unknown
                error occurred when trying to call the API.
        '''
        ENDPOINT = self._pods_api.api10_pods_get_with_http_info
        if references is not None:
            kwargs = self._process_references_ids(references, kwargs)
        kwargs = self._process_kwargs(kwargs)
        response, is_error = self._call_api(ENDPOINT, kwargs, self._retries)
        return self._package_response(response, is_error, ENDPOINT, kwargs)

    def get_volumes(self, references=None, **kwargs):
        '''
        Get FlashArray volume objects.

        Args:
            references (list[FixedReference], optional): References to query
                for. Overrides ids and names keyword arguments.

        Keyword args:
            continuation_token (str, optional): An opaque token to iterate over
                a collection of resources.
            filter (Filter, optional): A filter to include only resources
                that match the specified criteria.
            ids (list[str], optional): Resource IDs to query for. Can also be a
                single element.
            limit (int, optional): Limit the number of resources in the
                response.
            names (list[str], optional): Resource names to query for. Can also
                be a single element.
            offset (int): The offset of the first resource to return from a
                collection.
            sort (list[Property], optional): Sort the response by the specified
                Properties. Can also be a single element.
            x_request_id (str, optional): A header to provide to track the
                API call. Generated by the server if not provided.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            TypeError: If invalid or missing parameters are used.
            ValueError: If a parameter is of an invalid type.
            PureError: If there was an error unpacking parameters or an unknown
                error occurred when trying to call the API.
        '''
        ENDPOINT = self._volumes_api.api10_volumes_get_with_http_info
        if references is not None:
            kwargs = self._process_references_ids(references, kwargs)
        kwargs = self._process_kwargs(kwargs)
        response, is_error = self._call_api(ENDPOINT, kwargs, self._retries)
        return self._package_response(response, is_error, ENDPOINT, kwargs)

    def get_volume_snapshots(self, references=None, **kwargs):
        '''
        Get snapshots of volumes.

        Args:
            references (list[FixedReference], optional): References to query
                for. Overrides ids and names keyword arguments.

        Keyword args:
            continuation_token (str, optional): An opaque token to iterate over
                a collection of resources.
            filter (Filter, optional): A filter to include only resources
                that match the specified criteria.
            ids (list[str], optional): Resource IDs to query for. Can also be a
                single element.
            limit (int, optional): Limit the number of resources in the
                response.
            names (list[str], optional): Resource names to query for. Can also
                be a single element.
            offset (int): The offset of the first resource to return from a
                collection.
            sort (list[Property], optional): Sort the response by the specified
                Properties. Can also be a single element.
            source_ids (list[str], optional): IDs for source of the object
                to query for. Can also be a single element.
            source_names (list[str], optional): Names for source of the object
                to query for. Can also be a single element.
            x_request_id (str, optional): A header to provide to track the
                API call. Generated by the server if not provided.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            TypeError: If invalid or missing parameters are used.
            ValueError: If a parameter is of an invalid type.
            PureError: If there was an error unpacking parameters or an unknown
                error occurred when trying to call the API.
        '''
        ENDPOINT = self._volume_snapshots_api.api10_volume_snapshots_get_with_http_info
        if references is not None:
            kwargs = self._process_references_ids(references, kwargs)
        kwargs = self._process_kwargs(kwargs)
        response, is_error = self._call_api(ENDPOINT, kwargs, self._retries)
        return self._package_response(response, is_error, ENDPOINT, kwargs)

    def _set_agent_header(self):
        '''
        Set the user-agent header of the internal client.
        '''
        self._api_client.set_default_header('User-Agent', self.USER_AGENT)

    def _set_auth_header(self, refresh=False):
        '''
        Set the authorization header of the internal client with the access
        token.

        Args:
            refresh (bool, optional): Whether to retrieve a new access token.
                Defaults to False.

        Raises:
            PureError: If there was an error retrieving the access token.
        '''
        self._api_client.set_default_header('Authorization',
                                            self._token_man.get_header(refresh=refresh))

    def _process_kwargs(self, kwargs):
        '''
        Process the client-defined kwargs into the format expected by swagger.

        Args:
            kwargs (dict): The kwargs to process.

        Returns:
            dict
        '''
        # NOTE: paramters that are lists are compressed into one single string
        #       then passed in as a list with a single element;
        #       this is so swagger does not improperly split the list and add
        #       a query parameter for each element in the list, but only once
        # Convert the filter into a string
        if Parameters.filter in kwargs:
            kwargs[Parameters.filter] = str(kwargs.get(Parameters.filter))
        # Convert list string parameters to lists with single quotes
        for param in Parameters.get_list_str_parameters():
            if param in kwargs:
                if isinstance(kwargs.get(param), list):
                    kwargs[param] = [','.join(['\'{}\''.format(element)
                                               for element in kwargs.get(param)])]
                else:
                    kwargs[param] = ['\'{}\''.format(kwargs.get(param))]
        # Convert list parameters to list (without quotes)
        for param in Parameters.get_list_parameters():
            if param in kwargs:
                if isinstance(kwargs.get(param), list):
                    kwargs[param] = [','.join([str(element)
                                               for element in kwargs.get(param)])]
                else:
                    kwargs[param] = [str(kwargs.get(param))]
        # Encapsulate simple string parameters with single quotes
        for param in Parameters.get_str_parameters():
            if param in kwargs:
                kwargs[param] = '\'{}\''.format(kwargs.get(param))
        # Add the timeout
        kwargs['_request_timeout'] = self._timeout
        return kwargs

    def _process_references_ids(self, references, kwargs):
        '''
        Process reference objects into a list of IDs. Removes other ID and name
        arguments.

        Args:
            references (list[FixedReference]): The references from which to
                extract IDs.
            kwargs (dict): The kwargs to process.

        Returns:
            dict

        Raises:
            PureError: If a reference does not have an ID attribute.
        '''
        self._verify_references(references)
        kwargs[Parameters.ids] = ([ref.id for ref in references]
                                   if isinstance(references, list)
                                   else [references.id])
        kwargs.pop(Parameters.references, None)
        kwargs.pop(Parameters.names, None)
        return kwargs

    def _process_references_resource_ids(self, references, kwargs):
        '''
        Process reference objects into a list of IDs. Removes other resource ID
        and resource name arguments.

        Args:
            references (list[FixedReference]): The references from which to
                extract IDs.
            kwargs (dict): The kwargs to process.

        Returns:
            dict

        Raises:
            PureError: If a reference does not have an ID attribute.
        '''
        self._verify_references(references)
        kwargs[Parameters.resource_ids] = ([ref.id for ref in references]
                                           if isinstance(references, list)
                                           else [references.id])
        kwargs.pop(Parameters.resources, None)
        kwargs.pop(Parameters.resource_names, None)
        return kwargs

    def _verify_references(self, references):
        '''
        Verify all references have an ID attribute.

        Args:
            references (list[FixedReference]): The references to verify. Can
                also be a single element.

        Raises:
            PureError: If a reference does not have an ID attribute.
        '''
        if isinstance(references, list):
            if not all(ref.id is not None for ref in references):
                PureError('References do not all contain IDs')
        else:
            if references.id is None:
                PureError('Reference does not contain an ID')

    def _call_api(self, api_function, kwargs, retries):
        '''
        Call the API function and process the response. May call the API
        repeatedly if the request failed for a resaon that may not persist in
        the next call.

        Args:
            api_function (function): The function of the Swagger client to
                call internally.
            kwargs (dict): The processed kwargs to pass to the function.
            retries (int): The number of retries left.

        Returns:
            tuple (body, status, headers)
            bool: Whether an error was encountered.

        Raises:
            PureError: If an unexpected error occurred.
        '''
        try:
            response = api_function(**kwargs)
            # Call was successful (200)
            return response, False
        except ApiException as error:
            # If no chance for retries, return the error
            if retries == 0:
                return error, True
            # If bad request or not found, return the error (it will never work)
            elif error.status in [400, 404]:
                return error, True
            # If authentication error, reset access token and retry
            elif error.status == 403:
                self._set_auth_header(refresh=True)
                return self._call_api(api_function, kwargs, retries - 1)
            # If rate limit error, wait the proper time and try again
            elif error.status == 429:
                # If the the minute limit hit, wait that long
                if (int(error.headers.get(Headers.x_ratelimit_remaining_min))
                    == int(error.headers.get(Headers.x_ratelimit_min))):
                    time.sleep(60)
                # Otherwise it was the second limit and only wait a second
                time.sleep(1)
                return self._call_api(api_function, kwargs, retries - 1)
            # If some internal server error we know nothing about, return
            elif error.status == 500:
                return error, True
            # If internal server errors that has to do with timeouts, try again
            elif error.status > 500:
                return self._call_api(api_function, kwargs, retries - 1)
            # If error with the swagger client, raise the error
            else:
                raise PureError(error)

    def _package_response(self, response, is_error, endpoint, kwargs):
        '''
        Package a response into a ValidResponse or ErrorResponse.

        Args:
            response (tuple, ApiException): Body, status, header tuple as
                returned from a Swagger client, or an ApiException.
            is_error (bool): Whether the response is an error.
            endpoint (function): The function of the Swagger client that was
                called.
            kwargs (dict): The processed kwargs that were passed to the
                endpoint function.

        Returns:
            ValidResponse or ErrorResponse
        '''
        return (self._create_valid_response(response, endpoint, kwargs)
                if is_error is False
                else self._create_error_response(response))

    def _create_valid_response(self, response, endpoint, kwargs):
        '''
        Create a ValidResponse from a Swagger response.

        Args:
            response (tuple): Body, status, header tuple as returned from a
                Swagger client.
            endpoint (function): The function of the Swagger client that was
                called.
            kwargs (dict): The processed kwargs that were passed to the
                endpoint function.

        Returns:
            ValidResponse
        '''
        body, status, headers = response
        if body is None:
            continuation_token = None
            total_item_count = None
            items = None
        else:
            if not hasattr(body, Parameters.continuation_token):
                continuation_token = None
                total_item_count = len(body.items)
            else:
                continuation_token = body.continuation_token
                total_item_count = body.total_item_count
            items = iter(ItemIterator(self, endpoint, kwargs,
                                      continuation_token, total_item_count,
                                      body.items,
                                      headers.get(Headers.x_request_id)))
        pure1_headers = Pure1Headers(headers.get(Headers.x_request_id, None),
                                     headers.get(Headers.x_ratelimit_sec, None),
                                     headers.get(Headers.x_ratelimit_min, None),
                                     headers.get(Headers.x_ratelimit_remaining_sec, None),
                                     headers.get(Headers.x_ratelimit_remaining_min, None))
        return ValidResponse(status, continuation_token, total_item_count,
                             items, headers=pure1_headers)

    def _create_error_response(self, error):
        '''
        Create an ErrorResponse from a Swagger error.

        Args:
            error (ApiException): Error returned raised by Swagger.

        Returns:
            ErrorResponse
        '''
        status = error.status
        body = json.loads(error.body)
        if status in [403, 429]:
            # Parse differently if the error message came from kong
            errors = [ApiError(None, body.get(Responses.message, None))]
        else:
            errors = [ApiError(err.get(Responses.context, None),
                               err.get(Responses.message, None))
                      for err in body.get(Responses.errors, None)]
        headers = error.headers
        pure1_headers = Pure1Headers(headers.get(Headers.x_request_id, None),
                                     headers.get(Headers.x_ratelimit_sec, None),
                                     headers.get(Headers.x_ratelimit_min, None),
                                     headers.get(Headers.x_ratelimit_remaining_sec, None),
                                     headers.get(Headers.x_ratelimit_remaining_min, None))
        return ErrorResponse(status, errors, headers=pure1_headers)
