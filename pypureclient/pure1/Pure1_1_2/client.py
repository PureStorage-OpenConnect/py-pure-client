import json
import platform
import os
import time
from typing import List, Optional

from ...exceptions import PureError
from ...keywords import Headers, Responses
from ...responses import ValidResponse, ErrorResponse, ApiError, ItemIterator
from ...token_manager import TokenManager
from ...client_settings import USER_AGENT_TEMPLATE
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
    USER_AGENT = USER_AGENT_TEMPLATE.format(prod='Pure1', rest_version='1.2', sys=platform.system(), rel=platform.release())

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
        self._blades_api = api.BladesApi(self._api_client)
        self._bucket_replica_links_api = api.BucketReplicaLinksApi(self._api_client)
        self._buckets_api = api.BucketsApi(self._api_client)
        self._controllers_api = api.ControllersApi(self._api_client)
        self._directories_api = api.DirectoriesApi(self._api_client)
        self._drives_api = api.DrivesApi(self._api_client)
        self._file_system_replica_links_api = api.FileSystemReplicaLinksApi(self._api_client)
        self._file_system_snapshots_api = api.FileSystemSnapshotsApi(self._api_client)
        self._file_systems_api = api.FileSystemsApi(self._api_client)
        self._hardware_api = api.HardwareApi(self._api_client)
        self._hardware_connectors_api = api.HardwareConnectorsApi(self._api_client)
        self._invoices_api = api.InvoicesApi(self._api_client)
        self._metrics_api = api.MetricsApi(self._api_client)
        self._network_interfaces_api = api.NetworkInterfacesApi(self._api_client)
        self._object_store_accounts_api = api.ObjectStoreAccountsApi(self._api_client)
        self._pod_replica_links_api = api.PodReplicaLinksApi(self._api_client)
        self._pods_api = api.PodsApi(self._api_client)
        self._policies_api = api.PoliciesApi(self._api_client)
        self._ports_api = api.PortsApi(self._api_client)
        self._subscriptions_api = api.SubscriptionsApi(self._api_client)
        self._sustainability_api = api.SustainabilityApi(self._api_client)
        self._targets_api = api.TargetsApi(self._api_client)
        self._volume_snapshots_api = api.VolumeSnapshotsApi(self._api_client)
        self._volumes_api = api.VolumesApi(self._api_client)

    def __del__(self):
        # Cleanup this REST API client resources
        self._api_client.close()

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
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.AlertsGetResponse
        """
        Retrieves information about alerts generated by Pure1-monitored appliances.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._alerts_api.api12_alerts_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_arrays(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        fqdns=None,  # type: List[str]
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ArrayGetResponse
        """
        Retrieves information about FlashArray and FlashBlade storage appliances.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            fqdns (list[str], optional):
                A list of resource FQDNs. If there is not at least one resource that matches
                each `fqdn` element, an error is returned.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._arrays_api.api12_arrays_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_arrays_support_contracts(
        self,
        resources=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        offset=None,  # type: int
        resource_ids=None,  # type: List[str]
        resource_fqdns=None,  # type: List[str]
        resource_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SupportContractGetResponse
        """
        Retrieves the support contracts associated with arrays.

        Args:
            resources (list[FixedReference], optional):
                A list of resources to query for. Overrides resource_ids and resource_names keyword arguments.

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
                `resource_id` element, an error is returned.
            resource_fqdns (list[str], optional):
                A list of resource FQDNs. If there is not at least one resource that matches
                each `resource_fqdn` element, an error is returned.
            resource_names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `resource_name` element, an error is returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            offset=offset,
            resource_ids=resource_ids,
            resource_fqdns=resource_fqdns,
            resource_names=resource_names,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._arrays_api.api12_arrays_support_contracts_get_with_http_info
        _process_references(resources, ['resource_ids', 'resource_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def put_arrays_tags(
        self,
        resources=None,  # type: List[models.ReferenceType]
        tag=None,  # type: List[models.TagPut]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        namespaces=None,  # type: List[str]
        resource_ids=None,  # type: List[str]
        resource_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.TagResponse
        """
        Creates or updates array tags contextual to Pure1 only.

        Args:
            resources (list[FixedReference], optional):
                A list of resources to query for. Overrides resource_ids and resource_names keyword arguments.

            tag (list[TagPut], required):
                A list of tags to be upserted.
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            namespaces (list[str], optional):
                A list of namespaces.
            resource_ids (list[str], optional):
                REQUIRED: either `resource_ids` or `resource_names`. A list of resource IDs. If
                there is not at least one resource that matches each `resource_id` element, an
                error is returned.
            resource_names (list[str], optional):
                REQUIRED: either `resource_ids` or `resource_names`. A list of resource names.
                If there is not at least one resource that matches each `resource_name` element,
                an error is returned.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        kwargs = dict(
            tag=tag,
            authorization=authorization,
            x_request_id=x_request_id,
            namespaces=namespaces,
            resource_ids=resource_ids,
            resource_names=resource_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._arrays_api.api12_arrays_tags_batch_put_with_http_info
        _process_references(resources, ['resource_ids', 'resource_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_arrays_tags(
        self,
        resources=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        keys=None,  # type: List[str]
        namespaces=None,  # type: List[str]
        resource_ids=None,  # type: List[str]
        resource_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Deletes array tags from Pure1.

        Args:
            resources (list[FixedReference], optional):
                A list of resources to query for. Overrides resource_ids and resource_names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            keys (list[str], optional):
                A list of tag keys.
            namespaces (list[str], optional):
                A list of namespaces.
            resource_ids (list[str], optional):
                REQUIRED: either `resource_ids` or `resource_names`. A list of resource IDs. If
                there is not at least one resource that matches each `resource_id` element, an
                error is returned.
            resource_names (list[str], optional):
                REQUIRED: either `resource_ids` or `resource_names`. A list of resource names.
                If there is not at least one resource that matches each `resource_name` element,
                an error is returned.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            keys=keys,
            namespaces=namespaces,
            resource_ids=resource_ids,
            resource_names=resource_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._arrays_api.api12_arrays_tags_delete_with_http_info
        _process_references(resources, ['resource_ids', 'resource_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_arrays_tags(
        self,
        resources=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        keys=None,  # type: List[str]
        limit=None,  # type: int
        namespaces=None,  # type: List[str]
        offset=None,  # type: int
        resource_ids=None,  # type: List[str]
        resource_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.TagGetResponse
        """
        Retrieves the tags associated with specified arrays.

        Args:
            resources (list[FixedReference], optional):
                A list of resources to query for. Overrides resource_ids and resource_names keyword arguments.

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
                `resource_id` element, an error is returned.
            resource_names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `resource_name` element, an error is returned.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._arrays_api.api12_arrays_tags_get_with_http_info
        _process_references(resources, ['resource_ids', 'resource_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_audits(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.AuditsGetResponse
        """
        Retrieves audit objects.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._audits_api.api12_audits_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_blades(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.BladeGetResponse
        """
        Retrieves information about FlashBlade blades.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._blades_api.api12_blades_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_bucket_replica_links(
        self,
        references=None,  # type: List[models.ReferenceType]
        members=None,  # type: List[models.ReferenceType]
        sources=None,  # type: List[models.ReferenceType]
        targets=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        source_ids=None,  # type: List[str]
        source_names=None,  # type: List[str]
        target_ids=None,  # type: List[str]
        target_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.BucketReplicaLinkGetResponse
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

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. Member IDs separated by a `+` indicate that both members
                must be present in each element. Member IDs separated by a `,` indicate that at
                least one member must be present in each element. If there is not at least one
                resource that matches each `member_id` element, an error is returned.  When
                using Try it Out in Swagger, a list of member IDs separated by a `+` must be
                entered in the same item cell.
            member_names (list[str], optional):
                A list of member names. Member names separated by a `+` indicate that both
                members must be present in each element. Member names separated by a `,`
                indicate that at least one member must be present in each element. If there is
                not at least one resource that matches each `member_name` element, an error is
                returned.  When using Try it Out in Swagger, a list of member names separated by
                a `+` must be entered in the same item cell.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            source_ids (list[str], optional):
                A list of source IDs. Source IDs separated by a `+` indicate that both sources
                must be present in each element. Source IDs separated by a `,` indicate that at
                least one source must be present in each element. If there is not at least one
                resource that matches each `source_id` element, an error is returned.  When
                using Try it Out in Swagger, a list of source IDs separated by a `+` must be
                entered in the same item cell.
            source_names (list[str], optional):
                A list of source names. Source names separated by a `+` indicate that both
                sources must be present in each element. Source names separated by a `,`
                indicate that at least one source must be present in each element. If there is
                not at least one resource that matches each `source_name` element, an error is
                returned.  When using Try it Out in Swagger, a list of source names separated by
                a `+` must be entered in the same item cell.
            target_ids (list[str], optional):
                A list of target IDs. Target IDs separated by a `+` indicate that both targets
                must be present in each element. Target IDs separated by a `,` indicate that at
                least one target must be present in each element. If there is not at least one
                resource that matches each `target_id` element, an error is returned.  When
                using Try it Out in Swagger, a list of target IDs separated by a `+` must be
                entered in the same item cell.
            target_names (list[str], optional):
                A list of target names. Target names separated by a `+` indicate that both
                targets must be present in each element. Target names separated by a `,`
                indicate that at least one target must be present in each element. If there is
                not at least one resource that matches each `target_name` element, an error is
                returned.  When using Try it Out in Swagger, a list of target names separated by
                a `+` must be entered in the same item cell.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._bucket_replica_links_api.api12_bucket_replica_links_get_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        _process_references(targets, ['target_ids', 'target_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_buckets(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.BucketGetResponse
        """
        Retrieves buckets.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._buckets_api.api12_buckets_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_controllers(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ControllerGetResponse
        """
        Retrieves information about controllers.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._controllers_api.api12_controllers_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_directories(
        self,
        file_systems=None,  # type: List[models.ReferenceType]
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        file_system_ids=None,  # type: List[str]
        file_system_names=None,  # type: List[str]
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.DirectoryGetResponse
        """
        Retrieves information about FlashArray managed directory objects.

        Args:
            file_systems (list[FixedReference], optional):
                A list of file_systems to query for. Overrides file_system_ids and file_system_names keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            file_system_ids (list[str], optional):
                Performs the operation on the file system ID specified. Enter multiple file
                system IDs in comma-separated format. The `file_system_ids` and
                `file_system_names` parameters cannot be provided together.
            file_system_names (list[str], optional):
                Performs the operation on the file system name specified. Enter multiple file
                system names in comma-separated format. For example, `filesystem1,filesystem2`.
                The `file_system_ids` and `file_system_names` parameters cannot be provided
                together.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._directories_api.api12_directories_get_with_http_info
        _process_references(file_systems, ['file_system_ids', 'file_system_names'], kwargs)
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_drives(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.DriveGetResponse
        """
        Retrieves information about FlashArray drives.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._drives_api.api12_drives_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_system_replica_links(
        self,
        references=None,  # type: List[models.ReferenceType]
        members=None,  # type: List[models.ReferenceType]
        sources=None,  # type: List[models.ReferenceType]
        targets=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        source_ids=None,  # type: List[str]
        source_names=None,  # type: List[str]
        target_ids=None,  # type: List[str]
        target_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemReplicaLinkGetResponse
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

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. Member IDs separated by a `+` indicate that both members
                must be present in each element. Member IDs separated by a `,` indicate that at
                least one member must be present in each element. If there is not at least one
                resource that matches each `member_id` element, an error is returned.  When
                using Try it Out in Swagger, a list of member IDs separated by a `+` must be
                entered in the same item cell.
            member_names (list[str], optional):
                A list of member names. Member names separated by a `+` indicate that both
                members must be present in each element. Member names separated by a `,`
                indicate that at least one member must be present in each element. If there is
                not at least one resource that matches each `member_name` element, an error is
                returned.  When using Try it Out in Swagger, a list of member names separated by
                a `+` must be entered in the same item cell.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            source_ids (list[str], optional):
                A list of source IDs. Source IDs separated by a `+` indicate that both sources
                must be present in each element. Source IDs separated by a `,` indicate that at
                least one source must be present in each element. If there is not at least one
                resource that matches each `source_id` element, an error is returned.  When
                using Try it Out in Swagger, a list of source IDs separated by a `+` must be
                entered in the same item cell.
            source_names (list[str], optional):
                A list of source names. Source names separated by a `+` indicate that both
                sources must be present in each element. Source names separated by a `,`
                indicate that at least one source must be present in each element. If there is
                not at least one resource that matches each `source_name` element, an error is
                returned.  When using Try it Out in Swagger, a list of source names separated by
                a `+` must be entered in the same item cell.
            target_ids (list[str], optional):
                A list of target IDs. Target IDs separated by a `+` indicate that both targets
                must be present in each element. Target IDs separated by a `,` indicate that at
                least one target must be present in each element. If there is not at least one
                resource that matches each `target_id` element, an error is returned.  When
                using Try it Out in Swagger, a list of target IDs separated by a `+` must be
                entered in the same item cell.
            target_names (list[str], optional):
                A list of target names. Target names separated by a `+` indicate that both
                targets must be present in each element. Target names separated by a `,`
                indicate that at least one target must be present in each element. If there is
                not at least one resource that matches each `target_name` element, an error is
                returned.  When using Try it Out in Swagger, a list of target names separated by
                a `+` must be entered in the same item cell.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_replica_links_api.api12_file_system_replica_links_get_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        _process_references(targets, ['target_ids', 'target_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_system_replica_links_policies(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMembersGetResponse
        """
        Retrieves pairs of FlashBlade file system replica link members and their
        policies.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

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
                A list of member IDs. If there is not at least one resource that matches each
                `member_id` element, an error is returned.
            member_names (list[str], optional):
                A list of member names. If there is not at least one resource that matches each
                `member_name` element, an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If there is not at least one resource that matches each
                `policy_id` element, an error is returned.
            policy_names (list[str], optional):
                A list of policy names. If there is not at least one resource that matches each
                `policy_name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_replica_links_api.api12_file_system_replica_links_policies_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_system_snapshots(
        self,
        references=None,  # type: List[models.ReferenceType]
        sources=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        source_ids=None,  # type: List[str]
        source_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemSnapshotGetResponse
        """
        Retrieves snapshots of FlashBlade file systems.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_ids and source_names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            source_ids (list[str], optional):
                A list of ids for the source of the object. If there is not at least one
                resource that matches each `source_id` element, an error is returned.
            source_names (list[str], optional):
                A list of names for the source of the object. If there is not at least one
                resource that matches each `source_name` element, an error is returned.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_snapshots_api.api12_file_system_snapshots_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_system_snapshots_policies(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMembersGetResponse
        """
        Retrieves pairs of FlashBlade file system snapshot members and their policies.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

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
                A list of member IDs. If there is not at least one resource that matches each
                `member_id` element, an error is returned.
            member_names (list[str], optional):
                A list of member names. If there is not at least one resource that matches each
                `member_name` element, an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If there is not at least one resource that matches each
                `policy_id` element, an error is returned.
            policy_names (list[str], optional):
                A list of policy names. If there is not at least one resource that matches each
                `policy_name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_snapshots_api.api12_file_system_snapshots_policies_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_systems(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemGetResponse
        """
        Retrieves information about FlashArray and FlashBlade file system objects.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api12_file_systems_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_systems_policies(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMembersGetResponse
        """
        Retrieves pairs of FlashBlade file system members and their policies.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

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
                A list of member IDs. If there is not at least one resource that matches each
                `member_id` element, an error is returned.
            member_names (list[str], optional):
                A list of member names. If there is not at least one resource that matches each
                `member_name` element, an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If there is not at least one resource that matches each
                `policy_id` element, an error is returned.
            policy_names (list[str], optional):
                A list of policy names. If there is not at least one resource that matches each
                `policy_name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api12_file_systems_policies_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_hardware(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.HardwareGetResponse
        """
        Retrieves information about hardware components.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._hardware_api.api12_hardware_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_hardware_connectors(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.HardwareConnectorGetResponse
        """
        Retrieves information about FlashBlade hardware connectors.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._hardware_connectors_api.api12_hardware_connectors_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_invoices(
        self,
        references=None,  # type: List[models.ReferenceType]
        subscriptions=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        offset=None,  # type: int
        sort=None,  # type: List[str]
        partner_purchase_orders=None,  # type: List[str]
        subscription_ids=None,  # type: List[str]
        subscription_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.InvoiceGetResponse
        """
        Retrieves information about Pure1 subscription invoices.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            subscriptions (list[FixedReference], optional):
                A list of subscriptions to query for. Overrides subscription_ids and subscription_names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            partner_purchase_orders (list[str], optional):
                A list of partner purchase order numbers. If there is not at least one resource
                that matches each `partner_purchase_order` element, an error is returned.
            subscription_ids (list[str], optional):
                A list of subscription IDs. If there is not at least one resource that matches
                each `subscription.id` element, an error is returned.
            subscription_names (list[str], optional):
                A list of subscription names. If there is not at least one resource that matches
                each `subscription.name` element, an error is returned.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            offset=offset,
            sort=sort,
            partner_purchase_orders=partner_purchase_orders,
            subscription_ids=subscription_ids,
            subscription_names=subscription_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._invoices_api.api12_invoices_get_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(subscriptions, ['subscription_ids', 'subscription_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_metrics(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        """
        Retrieves information about metrics that can be queried for.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            resource_types (list[str], optional):
                The resource types to list the available metrics. Valid values are `arrays`,
                `volumes`, and `pods`. A metric can belong to a combination of resources, e.g.,
                write-iops from array to pod. In that case, query by ['arrays', 'pods'].
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._metrics_api.api12_metrics_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_metrics_history(
        self,
        references=None,  # type: List[models.ReferenceType]
        resources=None,  # type: List[models.ReferenceType]
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
        """
        Retrieves historical metric data for resources. This endpoint supports batching:
        Up to 32 time series can be retrieved in one call. It can be multiple metrics
        for one resource, (e.g., load and bandwidth for one array - 2 time series), one
        metric for multiple resource (e.g., load for arrayA and arrayB - 2 time series),
        or a combination of both, multiple metrics for multiple resources, (e.g., load
        and bandwidth for arrayA and arrayB - 4 time series).

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            resources (list[FixedReference], optional):
                A list of resources to query for. Overrides resource_ids and resource_names keyword arguments.

            aggregation (str, required):
                Aggregation needed on the metric data. Valid values are `avg` and `max`.
                Latency metrics averages are weighted by the IOPS.
            end_time (int, required):
                Timestamp of when the time window ends. Measured in milliseconds since the UNIX
                epoch.
            resolution (int, required):
                The duration of time between individual data points, in milliseconds.
            start_time (int, required):
                Timestamp of when the time window starts. Measured in milliseconds since the
                UNIX epoch.
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            ids (list[str], optional):
                REQUIRED: either `ids` or `names`. A list of object IDs. If there is not at
                least one resource that matches each `id` element, an error is returned.
            names (list[str], optional):
                REQUIRED: either `names` or `ids`. A list of resource names. If there is not at
                least one resource that matches each `name` element, an error is returned.
            resource_ids (list[str], optional):
                REQUIRED: either `resource_ids` or `resource_names`. A list of resource IDs. If
                there is not at least one resource that matches each `resource_id` element, an
                error is returned.
            resource_names (list[str], optional):
                REQUIRED: either `resource_ids` or `resource_names`. A list of resource names.
                If there is not at least one resource that matches each `resource_name` element,
                an error is returned.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._metrics_api.api12_metrics_history_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(resources, ['resource_ids', 'resource_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_network_interfaces(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.NetworkInterfaceGetResponse
        """
        Retrieves information about physical and virtual network interface objects.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._network_interfaces_api.api12_network_interfaces_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_object_store_accounts(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreAccountGetResponse
        """
        Retrieves object store accounts.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_accounts_api.api12_object_store_accounts_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_pod_replica_links(
        self,
        references=None,  # type: List[models.ReferenceType]
        members=None,  # type: List[models.ReferenceType]
        sources=None,  # type: List[models.ReferenceType]
        targets=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        source_ids=None,  # type: List[str]
        source_names=None,  # type: List[str]
        target_ids=None,  # type: List[str]
        target_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PodReplicaLinkGetResponse
        """
        Retrieves information about pod replica links.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_ids and source_names keyword arguments.
            targets (list[FixedReference], optional):
                A list of targets to query for. Overrides target_ids and target_names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. Member IDs separated by a `+` indicate that both members
                must be present in each element. Member IDs separated by a `,` indicate that at
                least one member must be present in each element. If there is not at least one
                resource that matches each `member_id` element, an error is returned.  When
                using Try it Out in Swagger, a list of member IDs separated by a `+` must be
                entered in the same item cell.
            member_names (list[str], optional):
                A list of member names. Member names separated by a `+` indicate that both
                members must be present in each element. Member names separated by a `,`
                indicate that at least one member must be present in each element. If there is
                not at least one resource that matches each `member_name` element, an error is
                returned.  When using Try it Out in Swagger, a list of member names separated by
                a `+` must be entered in the same item cell.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            source_ids (list[str], optional):
                A list of source IDs. Source IDs separated by a `+` indicate that both sources
                must be present in each element. Source IDs separated by a `,` indicate that at
                least one source must be present in each element. If there is not at least one
                resource that matches each `source_id` element, an error is returned.  When
                using Try it Out in Swagger, a list of source IDs separated by a `+` must be
                entered in the same item cell.
            source_names (list[str], optional):
                A list of source names. Source names separated by a `+` indicate that both
                sources must be present in each element. Source names separated by a `,`
                indicate that at least one source must be present in each element. If there is
                not at least one resource that matches each `source_name` element, an error is
                returned.  When using Try it Out in Swagger, a list of source names separated by
                a `+` must be entered in the same item cell.
            target_ids (list[str], optional):
                A list of target IDs. Target IDs separated by a `+` indicate that both targets
                must be present in each element. Target IDs separated by a `,` indicate that at
                least one target must be present in each element. If there is not at least one
                resource that matches each `target_id` element, an error is returned.  When
                using Try it Out in Swagger, a list of target IDs separated by a `+` must be
                entered in the same item cell.
            target_names (list[str], optional):
                A list of target names. Target names separated by a `+` indicate that both
                targets must be present in each element. Target names separated by a `,`
                indicate that at least one target must be present in each element. If there is
                not at least one resource that matches each `target_name` element, an error is
                returned.  When using Try it Out in Swagger, a list of target names separated by
                a `+` must be entered in the same item cell.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._pod_replica_links_api.api12_pod_replica_links_get_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        _process_references(targets, ['target_ids', 'target_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_pods(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PodGetResponse
        """
        Retrieves information about pod objects.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._pods_api.api12_pods_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_policies_file_system_replica_links(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMembersGetResponse
        """
        Retrieves pairs of policy references and their FlashBlade file system replica
        link members.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

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
                A list of member IDs. If there is not at least one resource that matches each
                `member_id` element, an error is returned.
            member_names (list[str], optional):
                A list of member names. If there is not at least one resource that matches each
                `member_name` element, an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If there is not at least one resource that matches each
                `policy_id` element, an error is returned.
            policy_names (list[str], optional):
                A list of policy names. If there is not at least one resource that matches each
                `policy_name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies_api.api12_policies_file_system_replica_links_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_policies_file_system_snapshots(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMembersGetResponse
        """
        Retrieves pairs of policy references and their FlashBlade file system snapshot
        members.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

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
                A list of member IDs. If there is not at least one resource that matches each
                `member_id` element, an error is returned.
            member_names (list[str], optional):
                A list of member names. If there is not at least one resource that matches each
                `member_name` element, an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If there is not at least one resource that matches each
                `policy_id` element, an error is returned.
            policy_names (list[str], optional):
                A list of policy names. If there is not at least one resource that matches each
                `policy_name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies_api.api12_policies_file_system_snapshots_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_policies_file_systems(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMembersGetResponse
        """
        Retrieves pairs of policy references and their FlashBlade file system members.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

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
                A list of member IDs. If there is not at least one resource that matches each
                `member_id` element, an error is returned.
            member_names (list[str], optional):
                A list of member names. If there is not at least one resource that matches each
                `member_name` element, an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If there is not at least one resource that matches each
                `policy_id` element, an error is returned.
            policy_names (list[str], optional):
                A list of policy names. If there is not at least one resource that matches each
                `policy_name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies_api.api12_policies_file_systems_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyGetResponse
        """
        Retrieves policies and their rules.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies_api.api12_policies_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_policies_members(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMembersGetResponse
        """
        Retrieves pairs of policy references and their members.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

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
                A list of member IDs. If there is not at least one resource that matches each
                `member_id` element, an error is returned.
            member_names (list[str], optional):
                A list of member names. If there is not at least one resource that matches each
                `member_name` element, an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If there is not at least one resource that matches each
                `policy_id` element, an error is returned.
            policy_names (list[str], optional):
                A list of policy names. If there is not at least one resource that matches each
                `policy_name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies_api.api12_policies_members_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_ports(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PortGetResponse
        """
        Retrieves information about FlashArray ports.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._ports_api.api12_ports_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_subscription_assets(
        self,
        references=None,  # type: List[models.ReferenceType]
        subscriptions=None,  # type: List[models.ReferenceType]
        licenses=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        advanced_space=None,  # type: bool
        subscription_ids=None,  # type: List[str]
        subscription_names=None,  # type: List[str]
        license_ids=None,  # type: List[str]
        license_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SubscriptionAssetGetResponse
        """
        Retrieves information about Pure1 subscription assets.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            subscriptions (list[FixedReference], optional):
                A list of subscriptions to query for. Overrides subscription_ids and subscription_names keyword arguments.
            licenses (list[FixedReference], optional):
                A list of licenses to query for. Overrides license_ids and license_names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            advanced_space (bool, optional):
                If `true`, returns the `advanced_space` field containing physical and effective
                space information.
            subscription_ids (list[str], optional):
                A list of subscription IDs. If there is not at least one resource that matches
                each `subscription.id` element, an error is returned.
            subscription_names (list[str], optional):
                A list of subscription names. If there is not at least one resource that matches
                each `subscription.name` element, an error is returned.
            license_ids (list[str], optional):
                A list of subscriptionLicense IDs. If there is not at least one resource that
                matches each `license.id` element, an error is returned.
            license_names (list[str], optional):
                A list of subscriptionLicense names. If there is not at least one resource that
                matches each `license.name` element, an error is returned.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            advanced_space=advanced_space,
            subscription_ids=subscription_ids,
            subscription_names=subscription_names,
            license_ids=license_ids,
            license_names=license_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._subscriptions_api.api12_subscription_assets_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(subscriptions, ['subscription_ids', 'subscription_names'], kwargs)
        _process_references(licenses, ['license_ids', 'license_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_subscription_licenses(
        self,
        references=None,  # type: List[models.ReferenceType]
        marketplace_partner_references=None,  # type: List[models.ReferenceType]
        subscriptions=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        marketplace_partner_reference_ids=None,  # type: List[str]
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        subscription_ids=None,  # type: List[str]
        subscription_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SubscriptionLicenseGetResponse
        """
        Retrieves information about Pure1 subscription licenses.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            marketplace_partner_references (list[FixedReference], optional):
                A list of marketplace_partner_references to query for. Overrides marketplace_partner_reference_ids keyword arguments.
            subscriptions (list[FixedReference], optional):
                A list of subscriptions to query for. Overrides subscription_ids and subscription_names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            marketplace_partner_reference_ids (list[str], optional):
                A list of marketplace partner reference IDs. If there is not at least one
                resource that matches each `marketplace_partner.reference_id` element, an error
                is returned.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            subscription_ids (list[str], optional):
                A list of subscription IDs. If there is not at least one resource that matches
                each `subscription.id` element, an error is returned.
            subscription_names (list[str], optional):
                A list of subscription names. If there is not at least one resource that matches
                each `subscription.name` element, an error is returned.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._subscriptions_api.api12_subscription_licenses_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(marketplace_partner_references, ['marketplace_partner_reference_ids'], kwargs)
        _process_references(subscriptions, ['subscription_ids', 'subscription_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_subscriptions(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SubscriptionGetResponse
        """
        Retrieves information about Pure1 subscriptions.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._subscriptions_api.api12_subscriptions_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_assessment_sustainability_arrays(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        fqdns=None,  # type: List[str]
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SustainabilityArrayGetResponse
        """
        Retrieves information about FlashArray and FlashBlade size, power consumption,
        heat generation and its sustainability assessment.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            fqdns (list[str], optional):
                A list of resource FQDNs. If there is not at least one resource that matches
                each `fqdn` element, an error is returned.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._sustainability_api.api12_assessment_sustainability_arrays_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_assessment_sustainability_insights_arrays(
        self,
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SustainabilityInsightArrayGetResponse
        """
        Retrieves information about FlashArray and FlashBlade insights connected to
        sustainability assessment.

        Args:

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
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        kwargs = dict(
            authorization=authorization,
            x_request_id=x_request_id,
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._sustainability_api.api12_assessment_sustainability_insights_arrays_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_targets(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.TargetGetResponse
        """
        Retrieves information about targets.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._targets_api.api12_targets_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_volume_snapshots(
        self,
        references=None,  # type: List[models.ReferenceType]
        sources=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        source_ids=None,  # type: List[str]
        source_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.VolumeSnapshotGetResponse
        """
        Retrieves information about snapshots of volumes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_ids and source_names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            source_ids (list[str], optional):
                A list of ids for the source of the object. If there is not at least one
                resource that matches each `source_id` element, an error is returned.
            source_names (list[str], optional):
                A list of names for the source of the object. If there is not at least one
                resource that matches each `source_name` element, an error is returned.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._volume_snapshots_api.api12_volume_snapshots_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_volumes(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.VolumeGetResponse
        """
        Retrieves information about FlashArray volume objects.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If there is not at least one resource that matches each
                `id` element, an error is returned.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each `name` element, an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            async_req (bool, optional):
                Request runs in separate thread and method returns
                multiprocessing.pool.ApplyResult.
            _return_http_data_only (bool, optional):
                Returns only data field.
            _preload_content (bool, optional):
                Response is converted into objects.
            _request_timeout (int, optional):
                Total request timeout in seconds.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._volumes_api.api12_volumes_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

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
            # *-get-response models have "continuation_token" attribute. Other models don't have them.
            if "continuation_token" in body.attribute_map:
                # None means that attribute is ignored in ItemIterator
                more_items_remaining = None
            else:
                # Only GET responses are paged.
                more_items_remaining = False
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
            status_code=status,
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
