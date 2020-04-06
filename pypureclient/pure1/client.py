import json
import os
import platform
import time

from ..exceptions import PureError
from ..keywords import Parameters, Headers, Responses
from ..responses import ValidResponse, ErrorResponse, ApiError, ItemIterator
from ..token_manager import TokenManager
from .api_client import ApiClient
from .rest import ApiException
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
    # Format: client/client_version/endpoint/endpoint_version/system/release
    USER_AGENT = ('pypureclient/1.4.0/Pure1/1.0/{sys}/{rel}'
                  .format(sys=platform.system(), rel=platform.release()))

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
        # Instantiate APIs
        self._alerts_api = api.AlertsApi(self._api_client)
        self._arrays_api = api.ArraysApi(self._api_client)
        self._audits_api = api.AuditsApi(self._api_client)
        self._bucket_replica_links_api = api.BucketReplicaLinksApi(self._api_client)
        self._buckets_api = api.BucketsApi(self._api_client)
        self._file_system_replica_links_api = api.FileSystemReplicaLinksApi(self._api_client)
        self._file_system_snapshots_api = api.FileSystemSnapshotsApi(self._api_client)
        self._file_systems_api = api.FileSystemsApi(self._api_client)
        self._metrics_api = api.MetricsApi(self._api_client)
        self._network_interfaces_api = api.NetworkInterfacesApi(self._api_client)
        self._object_store_accounts_api = api.ObjectStoreAccountsApi(self._api_client)
        self._pods_api = api.PodsApi(self._api_client)
        self._policies_api = api.PoliciesApi(self._api_client)
        self._targets_api = api.TargetsApi(self._api_client)
        self._volume_snapshots_api = api.VolumeSnapshotsApi(self._api_client)
        self._volumes_api = api.VolumesApi(self._api_client)

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

    def get_alerts(self, references=None, **kwargs):
        """
        Retrieves information about alerts generated by Pure1-monitored appliances.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of ids, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of names, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._alerts_api.api10_alerts_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = ['continuation_token', 'ids', 'names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_arrays(self, references=None, **kwargs):
        """
        Retrieves information about FlashArray and FlashBlade storage appliances.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of ids, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of names, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._arrays_api.api10_arrays_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = ['continuation_token', 'ids', 'names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_arrays_support_contracts(self, resources=None, **kwargs):
        """
        Retrieves the support contracts associated with arrays.

        Args:
            resources (list[FixedReference], optional):
                A list of resources to query for. Overrides resource_ids and resource_names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            resource_ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of names, an error is returned.
            resource_names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of names, an error is returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._arrays_api.api10_arrays_support_contracts_get_with_http_info
        _process_references(resources, ['resource_ids', 'resource_names'], kwargs)
        list_params = ['resource_ids', 'resource_names', 'sort']
        quoted_params = ['continuation_token', 'resource_ids', 'resource_names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def put_arrays_tags(self, resources=None, **kwargs):
        """
        Creates or updates array tags contextual to Pure1 only.

        Args:
            resources (list[FixedReference], optional):
                A list of resources to query for. Overrides resource_ids and resource_names keyword arguments.

        Keyword args:
            tag (list[TagPut], required):
                A list of tags to be upserted.
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            namespaces (list[str], optional):
                A list of namespaces.
            resource_ids (list[str], optional):
                REQUIRED: either resource_ids or resource_names. A list of resource IDs.
            resource_names (list[str], optional):
                REQUIRED: either resource_ids or resource_names. A list of resource names. If
                there is not at least one resource that matches each of the elements of names,
                an error is returned.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._arrays_api.api10_arrays_tags_batch_put_with_http_info
        _process_references(resources, ['resource_ids', 'resource_names'], kwargs)
        list_params = ['tag', 'namespaces', 'resource_ids', 'resource_names']
        quoted_params = ['namespaces', 'resource_ids', 'resource_names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_arrays_tags(self, resources=None, **kwargs):
        """
        Deletes array tags from Pure1.

        Args:
            resources (list[FixedReference], optional):
                A list of resources to query for. Overrides resource_ids and resource_names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            keys (list[str], optional):
                A list of tag keys.
            namespaces (list[str], optional):
                A list of namespaces.
            resource_ids (list[str], optional):
                REQUIRED: either resource_ids or resource_names. A list of resource IDs.
            resource_names (list[str], optional):
                REQUIRED: either resource_ids or resource_names. A list of resource names. If
                there is not at least one resource that matches each of the elements of names,
                an error is returned.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._arrays_api.api10_arrays_tags_delete_with_http_info
        _process_references(resources, ['resource_ids', 'resource_names'], kwargs)
        list_params = ['keys', 'namespaces', 'resource_ids', 'resource_names']
        quoted_params = ['keys', 'namespaces', 'resource_ids', 'resource_names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_arrays_tags(self, resources=None, **kwargs):
        """
        Retrieves the tags associated with specified arrays.

        Args:
            resources (list[FixedReference], optional):
                A list of resources to query for. Overrides resource_ids and resource_names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            keys (list[str], optional):
                A list of tag keys.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            namespaces (list[str], optional):
                A list of namespaces.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            resource_ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of names, an error is returned.
            resource_names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of names, an error is returned.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._arrays_api.api10_arrays_tags_get_with_http_info
        _process_references(resources, ['resource_ids', 'resource_names'], kwargs)
        list_params = ['keys', 'namespaces', 'resource_ids', 'resource_names']
        quoted_params = ['continuation_token', 'keys', 'namespaces', 'resource_ids', 'resource_names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_audits(self, references=None, **kwargs):
        """
        Retrieves audit objects.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of ids, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of names, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._audits_api.api10_audits_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = ['continuation_token', 'ids', 'names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_bucket_replica_links(self, references=None, members=None, sources=None, targets=None, **kwargs):
        """
        Retrieves information about bucket replica links.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_ids and source_names keyword arguments.
            targets (list[FixedReference], optional):
                A list of targets to query for. Overrides target_ids and target_names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of ids, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. Member IDs separated by a `+` indicate that both members
                must be present in each element. Member IDs separated by a `,` indicate that at
                least one member must be present in each element. If there is not at least one
                member that matches each of the elements of `member_ids`, an error is returned.
                When using Try it Out in Swagger, a list of member IDs separated by a `+` must
                be entered in the same item cell.
            member_names (list[str], optional):
                A list of member names. Member names separated by a `+` indicate that both
                members must be present in each element. Member names separated by a `,`
                indicate that at least one member must be present in each element. If there is
                not at least one member that matches each of the elements of `member_ids`, an
                error is returned.  When using Try it Out in Swagger, a list of member names
                separated by a `+` must be entered in the same item cell.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            source_ids (list[str], optional):
                A list of source IDs. Source IDs separated by a `+` indicate that both sources
                must be present in each element. Source IDs separated by a `,` indicate that at
                least one source must be present in each element. If there is not at least one
                source that matches each of the elements of `source_ids`, an error is returned.
                When using Try it Out in Swagger, a list of source IDs separated by a `+` must
                be entered in the same item cell.
            source_names (list[str], optional):
                A list of source names. Source names separated by a `+` indicate that both
                sources must be present in each element. Source names separated by a `,`
                indicate that at least one source must be present in each element. If there is
                not at least one source that matches each of the elements of `source_ids`, an
                error is returned.  When using Try it Out in Swagger, a list of source names
                separated by a `+` must be entered in the same item cell.
            target_ids (list[str], optional):
                A list of target IDs. Target IDs separated by a `+` indicate that both targets
                must be present in each element. Target IDs separated by a `,` indicate that at
                least one target must be present in each element. If there is not at least one
                target that matches each of the elements of `target_ids`, an error is returned.
                When using Try it Out in Swagger, a list of target IDs separated by a `+` must
                be entered in the same item cell.
            target_names (list[str], optional):
                A list of target names. Target names separated by a `+` indicate that both
                targets must be present in each element. Target names separated by a `,`
                indicate that at least one target must be present in each element. If there is
                not at least one target that matches each of the elements of `target_ids`, an
                error is returned.  When using Try it Out in Swagger, a list of target names
                separated by a `+` must be entered in the same item cell.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._bucket_replica_links_api.api10_bucket_replica_links_get_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        _process_references(targets, ['target_ids', 'target_names'], kwargs)
        list_params = ['ids', 'member_ids', 'member_names', 'sort', 'source_ids', 'source_names', 'target_ids', 'target_names']
        quoted_params = ['continuation_token', 'ids', 'member_ids', 'member_names', 'source_ids', 'source_names', 'target_ids', 'target_names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_buckets(self, references=None, **kwargs):
        """
        Retrieves buckets.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of ids, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of names, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._buckets_api.api10_buckets_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = ['continuation_token', 'ids', 'names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_file_system_replica_links(self, references=None, members=None, sources=None, targets=None, **kwargs):
        """
        Retrieves information about FlashBlade file system replica links.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_ids and source_names keyword arguments.
            targets (list[FixedReference], optional):
                A list of targets to query for. Overrides target_ids and target_names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of ids, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. Member IDs separated by a `+` indicate that both members
                must be present in each element. Member IDs separated by a `,` indicate that at
                least one member must be present in each element. If there is not at least one
                member that matches each of the elements of `member_ids`, an error is returned.
                When using Try it Out in Swagger, a list of member IDs separated by a `+` must
                be entered in the same item cell.
            member_names (list[str], optional):
                A list of member names. Member names separated by a `+` indicate that both
                members must be present in each element. Member names separated by a `,`
                indicate that at least one member must be present in each element. If there is
                not at least one member that matches each of the elements of `member_ids`, an
                error is returned.  When using Try it Out in Swagger, a list of member names
                separated by a `+` must be entered in the same item cell.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            source_ids (list[str], optional):
                A list of source IDs. Source IDs separated by a `+` indicate that both sources
                must be present in each element. Source IDs separated by a `,` indicate that at
                least one source must be present in each element. If there is not at least one
                source that matches each of the elements of `source_ids`, an error is returned.
                When using Try it Out in Swagger, a list of source IDs separated by a `+` must
                be entered in the same item cell.
            source_names (list[str], optional):
                A list of source names. Source names separated by a `+` indicate that both
                sources must be present in each element. Source names separated by a `,`
                indicate that at least one source must be present in each element. If there is
                not at least one source that matches each of the elements of `source_ids`, an
                error is returned.  When using Try it Out in Swagger, a list of source names
                separated by a `+` must be entered in the same item cell.
            target_ids (list[str], optional):
                A list of target IDs. Target IDs separated by a `+` indicate that both targets
                must be present in each element. Target IDs separated by a `,` indicate that at
                least one target must be present in each element. If there is not at least one
                target that matches each of the elements of `target_ids`, an error is returned.
                When using Try it Out in Swagger, a list of target IDs separated by a `+` must
                be entered in the same item cell.
            target_names (list[str], optional):
                A list of target names. Target names separated by a `+` indicate that both
                targets must be present in each element. Target names separated by a `,`
                indicate that at least one target must be present in each element. If there is
                not at least one target that matches each of the elements of `target_ids`, an
                error is returned.  When using Try it Out in Swagger, a list of target names
                separated by a `+` must be entered in the same item cell.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._file_system_replica_links_api.api10_file_system_replica_links_get_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        _process_references(targets, ['target_ids', 'target_names'], kwargs)
        list_params = ['ids', 'member_ids', 'member_names', 'sort', 'source_ids', 'source_names', 'target_ids', 'target_names']
        quoted_params = ['continuation_token', 'ids', 'member_ids', 'member_names', 'source_ids', 'source_names', 'target_ids', 'target_names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_file_system_replica_links_policies(self, members=None, policies=None, **kwargs):
        """
        Retrieves pairs of file system replica link members and their policies.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. If there is not at least one member that matches each of
                the elements of `member_ids`, an error is returned.
            member_names (list[str], optional):
                A list of member names. If there is not at least one member that matches each of
                the elements of `member_names`, an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If there is not at least one policy that matches each of
                the elements of `policy_ids`, an error is returned.
            policy_names (list[str], optional):
                A list of policy names. If there is not at least one policy that matches each of
                the elements of `policy_names`, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._file_system_replica_links_api.api10_file_system_replica_links_policies_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        list_params = ['member_ids', 'member_names', 'policy_ids', 'policy_names', 'sort']
        quoted_params = ['continuation_token', 'member_ids', 'member_names', 'policy_ids', 'policy_names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_file_system_snapshots(self, references=None, sources=None, **kwargs):
        """
        Retrieves snapshots of file systems.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_ids and source_names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of ids, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of names, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            source_ids (list[str], optional):
                A list of ids for the source of the object. If there is not at least one
                resource that matches each of the elements of names, an error is returned.
            source_names (list[str], optional):
                A list of names for the source of the object. If there is not at least one
                resource that matches each of the elements of names, an error is returned.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._file_system_snapshots_api.api10_file_system_snapshots_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        list_params = ['ids', 'names', 'sort', 'source_ids', 'source_names']
        quoted_params = ['continuation_token', 'ids', 'names', 'source_ids', 'source_names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_file_system_snapshots_policies(self, members=None, policies=None, **kwargs):
        """
        Retrieves pairs of file system snapshot members and their policies.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. If there is not at least one member that matches each of
                the elements of `member_ids`, an error is returned.
            member_names (list[str], optional):
                A list of member names. If there is not at least one member that matches each of
                the elements of `member_names`, an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If there is not at least one policy that matches each of
                the elements of `policy_ids`, an error is returned.
            policy_names (list[str], optional):
                A list of policy names. If there is not at least one policy that matches each of
                the elements of `policy_names`, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._file_system_snapshots_api.api10_file_system_snapshots_policies_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        list_params = ['member_ids', 'member_names', 'policy_ids', 'policy_names', 'sort']
        quoted_params = ['continuation_token', 'member_ids', 'member_names', 'policy_ids', 'policy_names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_file_systems(self, references=None, **kwargs):
        """
        Retrieves information about file system objects.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of ids, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of names, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._file_systems_api.api10_file_systems_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = ['continuation_token', 'ids', 'names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_file_systems_policies(self, members=None, policies=None, **kwargs):
        """
        Retrieves pairs of file system members and their policies.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. If there is not at least one member that matches each of
                the elements of `member_ids`, an error is returned.
            member_names (list[str], optional):
                A list of member names. If there is not at least one member that matches each of
                the elements of `member_names`, an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If there is not at least one policy that matches each of
                the elements of `policy_ids`, an error is returned.
            policy_names (list[str], optional):
                A list of policy names. If there is not at least one policy that matches each of
                the elements of `policy_names`, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._file_systems_api.api10_file_systems_policies_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        list_params = ['member_ids', 'member_names', 'policy_ids', 'policy_names', 'sort']
        quoted_params = ['continuation_token', 'member_ids', 'member_names', 'policy_ids', 'policy_names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_metrics(self, references=None, **kwargs):
        """
        Retrieves information about metrics that can be queried for.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of ids, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of names, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            resource_types (list[str], optional):
                The resource types to list the available metrics. Valid values are `arrays`,
                `volumes`, and `pods`. A metric can belong to a combination of resources, e.g.,
                write-iops from array to pod. In that case, query by ['arrays', 'pods'].
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._metrics_api.api10_metrics_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'resource_types', 'sort']
        quoted_params = ['continuation_token', 'ids', 'names', 'resource_types']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_metrics_history(self, references=None, resources=None, **kwargs):
        """
        Retrieves historical metric data for resources.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            resources (list[FixedReference], optional):
                A list of resources to query for. Overrides resource_ids and resource_names keyword arguments.

        Keyword args:
            aggregation (str, required):
                Aggregation needed on the metric data. Valid values are `avg` and `max`.
            end_time (int, required):
                When the time window ends (in milliseconds since epoch).
            resolution (int, required):
                The duration of time between individual data points, in milliseconds.
            start_time (int, required):
                When the time window starts (in milliseconds since epoch).
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            ids (list[str], optional):
                REQUIRED: either ids or names. A list of object IDs. If there is not at least
                one resource that matches each of the elements of ids, an error is returned.
            names (list[str], optional):
                REQUIRED: either names or ids. A list of resource names. If there is not at
                least one resource that matches each of the elements of names, an error is
                returned.
            resource_ids (list[str], optional):
                REQUIRED: either resource_ids or resource_names. A list of resource IDs.
            resource_names (list[str], optional):
                REQUIRED: either resource_ids or resource_names. A list of resource names. If
                there is not at least one resource that matches each of the elements of names,
                an error is returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._metrics_api.api10_metrics_history_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(resources, ['resource_ids', 'resource_names'], kwargs)
        list_params = ['ids', 'names', 'resource_ids', 'resource_names', 'sort']
        quoted_params = ['aggregation', 'ids', 'names', 'resource_ids', 'resource_names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_network_interfaces(self, references=None, **kwargs):
        """
        Retrieves information about physical and virtual network interface objects.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of ids, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of names, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._network_interfaces_api.api10_network_interfaces_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = ['continuation_token', 'ids', 'names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_object_store_accounts(self, references=None, **kwargs):
        """
        Retrieves object store accounts.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of ids, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of names, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._object_store_accounts_api.api10_object_store_accounts_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = ['continuation_token', 'ids', 'names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_pods(self, references=None, **kwargs):
        """
        Retrieves information about pod objects.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of ids, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of names, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._pods_api.api10_pods_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = ['continuation_token', 'ids', 'names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_policies_file_system_replica_links(self, members=None, policies=None, **kwargs):
        """
        Retrieves pairs of policy references and their file system replica link members.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. If there is not at least one member that matches each of
                the elements of `member_ids`, an error is returned.
            member_names (list[str], optional):
                A list of member names. If there is not at least one member that matches each of
                the elements of `member_names`, an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If there is not at least one policy that matches each of
                the elements of `policy_ids`, an error is returned.
            policy_names (list[str], optional):
                A list of policy names. If there is not at least one policy that matches each of
                the elements of `policy_names`, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._policies_api.api10_policies_file_system_replica_links_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        list_params = ['member_ids', 'member_names', 'policy_ids', 'policy_names', 'sort']
        quoted_params = ['continuation_token', 'member_ids', 'member_names', 'policy_ids', 'policy_names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_policies_file_system_snapshots(self, members=None, policies=None, **kwargs):
        """
        Retrieves pairs of policy references and their file system snapshot members.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. If there is not at least one member that matches each of
                the elements of `member_ids`, an error is returned.
            member_names (list[str], optional):
                A list of member names. If there is not at least one member that matches each of
                the elements of `member_names`, an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If there is not at least one policy that matches each of
                the elements of `policy_ids`, an error is returned.
            policy_names (list[str], optional):
                A list of policy names. If there is not at least one policy that matches each of
                the elements of `policy_names`, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._policies_api.api10_policies_file_system_snapshots_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        list_params = ['member_ids', 'member_names', 'policy_ids', 'policy_names', 'sort']
        quoted_params = ['continuation_token', 'member_ids', 'member_names', 'policy_ids', 'policy_names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_policies_file_systems(self, members=None, policies=None, **kwargs):
        """
        Retrieves pairs of policy references and their file system members.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. If there is not at least one member that matches each of
                the elements of `member_ids`, an error is returned.
            member_names (list[str], optional):
                A list of member names. If there is not at least one member that matches each of
                the elements of `member_names`, an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If there is not at least one policy that matches each of
                the elements of `policy_ids`, an error is returned.
            policy_names (list[str], optional):
                A list of policy names. If there is not at least one policy that matches each of
                the elements of `policy_names`, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._policies_api.api10_policies_file_systems_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        list_params = ['member_ids', 'member_names', 'policy_ids', 'policy_names', 'sort']
        quoted_params = ['continuation_token', 'member_ids', 'member_names', 'policy_ids', 'policy_names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_policies(self, references=None, **kwargs):
        """
        Retrieves policies and their rules.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of ids, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of names, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._policies_api.api10_policies_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = ['continuation_token', 'ids', 'names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_policies_members(self, members=None, policies=None, **kwargs):
        """
        Retrieves pairs of policy references and their members.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. If there is not at least one member that matches each of
                the elements of `member_ids`, an error is returned.
            member_names (list[str], optional):
                A list of member names. If there is not at least one member that matches each of
                the elements of `member_names`, an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If there is not at least one policy that matches each of
                the elements of `policy_ids`, an error is returned.
            policy_names (list[str], optional):
                A list of policy names. If there is not at least one policy that matches each of
                the elements of `policy_names`, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._policies_api.api10_policies_members_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        list_params = ['member_ids', 'member_names', 'policy_ids', 'policy_names', 'sort']
        quoted_params = ['continuation_token', 'member_ids', 'member_names', 'policy_ids', 'policy_names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_targets(self, references=None, **kwargs):
        """
        Retrieves information about targets.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of ids, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of names, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._targets_api.api10_targets_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = ['continuation_token', 'ids', 'names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_volume_snapshots(self, references=None, sources=None, **kwargs):
        """
        Retrieves information about snapshots of volumes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_ids and source_names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of ids, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of names, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            source_ids (list[str], optional):
                A list of ids for the source of the object. If there is not at least one
                resource that matches each of the elements of names, an error is returned.
            source_names (list[str], optional):
                A list of names for the source of the object. If there is not at least one
                resource that matches each of the elements of names, an error is returned.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volume_snapshots_api.api10_volume_snapshots_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        list_params = ['ids', 'names', 'sort', 'source_ids', 'source_names']
        quoted_params = ['continuation_token', 'ids', 'names', 'source_ids', 'source_names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_volumes(self, references=None, **kwargs):
        """
        Retrieves information about volume objects.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                of the elements of ids, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of names, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volumes_api.api10_volumes_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = ['continuation_token', 'ids', 'names']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def _set_agent_header(self):
        """
        Set the user-agent header of the internal client.
        """
        self._api_client.set_default_header('User-Agent', self.USER_AGENT)

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

    def _call_api(self, api_function, kwargs):
        """
        Call the API function and process the response. May call the API
        repeatedly if the request failed for a reason that may not persist in
        the next call.

        Args:
            api_function (function): Swagger-generated function to call.
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
        retries = self._retries
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

    def _create_valid_response(self, response, endpoint, kwargs):
        """
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
        """
        body, status, headers = response
        if body is None:
            continuation_token = None
            total_item_count = None
            items = None
        else:
            continuation_token = getattr(body, "continuation_token", None)
            total_item_count = getattr(body, "total_item_count", None)
            items = iter(ItemIterator(self, endpoint, kwargs,
                                      continuation_token, total_item_count,
                                      body.items,
                                      headers.get(Headers.x_request_id)))
        return ValidResponse(status, continuation_token, total_item_count,
                             items, headers=headers)

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


def _process_references(references, params, kwargs):
    """
    Process reference objects into a list of ids or names.
    Removes ids and names arguments.

    Args:
        references (list[FixedReference]):
            The references from which to extract ids or names.
        params (list[Parameter]):
            The parameters to be overridden.
        kwargs (dict):
            The kwargs to process.

    Raises:
        PureError: If a reference does not have an id or name.
    """
    if references is not None:
        if not isinstance(references, list):
            references = [references]
        for param in params:
            kwargs.pop(param, None)
        all_have_id = all(getattr(ref, 'id', None) is not None for ref in references)
        all_have_name = all(getattr(ref, 'name', None) is not None for ref in references)
        id_param = [param for param in params if param.endswith("ids")]
        name_param = [param for param in params if param.endswith("names")]
        if all_have_id and len(id_param) > 0:
            kwargs[id_param[0]] = [getattr(ref, 'id') for ref in references]
        elif all_have_name and len(name_param) > 0:
            kwargs[name_param[0]] = [getattr(ref, 'name') for ref in references]
        else:
            raise PureError('Invalid reference for {}'.format(", ".join(params)))


def _process_kwargs(kwargs, list_params=[], quoted_params=[]):
    """
    Process the client-defined kwargs into the format expected by swagger.

    Args:
        kwargs (dict):
            The kwargs to process.
        list_params (list[str]):
            List of parameters that should be list.
        quoted_params (list[str]):
            List of parameters that should be quoted.
    """
    # Convert list parameters to lists
    for param in list_params:
        if param in kwargs:
            if not isinstance(kwargs.get(param), list):
                kwargs[param] = [kwargs[param]]
    # Add quotes for quoted params
    for param in quoted_params:
        if param in kwargs:
            if param in list_params:
                kwargs[param] = ["'{}'".format(x) for x in kwargs[param]]
            else:
                kwargs[param] = "'{}'".format(kwargs[param])
    # Convert the filter into a string
    if Parameters.filter in kwargs:
        kwargs[Parameters.filter] = str(kwargs.get(Parameters.filter))
    if Parameters.sort in kwargs:
        kwargs[Parameters.sort] = [str(x) for x in kwargs[Parameters.sort]]
