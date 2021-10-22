import json
import platform
import time
import urllib3
from typing import List, Optional

from ...exceptions import PureError
from ...keywords import Headers, Responses
from ...responses import ValidResponse, ErrorResponse, ApiError, ItemIterator
from ...token_manager import TokenManager
from ...api_token_manager import APITokenManager
from .api_client import ApiClient
from .rest import ApiException
from .configuration import Configuration
from . import api
from . import models


class Client(object):
    DEFAULT_TIMEOUT = 15.0
    DEFAULT_RETRIES = 5
    # Format: client/client_version/endpoint/endpoint_version/system/release
    USER_AGENT = ('pypureclient/1.19.0/FA/2.0/{sys}/{rel}'
                  .format(sys=platform.system(), rel=platform.release()))

    def __init__(self, target, id_token=None, private_key_file=None, private_key_password=None,
                 username=None, client_id=None, key_id=None, issuer=None, api_token=None,
                 retries=DEFAULT_RETRIES, timeout=DEFAULT_TIMEOUT, ssl_cert=None, user_agent=None):
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
            timeout (float or (float, float), optional):
                The timeout duration in seconds, either in total time or
                (connect and read) times. Defaults to 15.0 total.
            ssl_cert (str, optional):
                SSL certificate to use. Defaults to None.
            user_agent (str, optional):
                User-Agent request header to use.

        Raises:
            PureError: If it could not create an ID or access token
        """
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        config = Configuration()
        config.verify_ssl = ssl_cert is not None
        config.ssl_ca_cert = ssl_cert
        config.host = self._get_base_url(target)

        if id_token and api_token:
            raise PureError("Only one authentication option is allowed. Please use either id_token or api_token and try again!")
        elif private_key_file and private_key_password and username and \
                key_id and client_id and issuer and api_token:
            raise PureError("id_token is generated based on app ID and private key info. Please use either id_token or api_token and try again!")
        elif api_token:
            api_token_auth_endpoint = self._get_api_token_endpoint(target)
            self._token_man = APITokenManager(api_token_auth_endpoint, api_token, verify_ssl=False)
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
                                           payload=payload, headers=headers, verify_ssl=False)

        self._api_client = ApiClient(configuration=config)
        self._api_client.user_agent = user_agent or self.USER_AGENT
        self._set_agent_header()
        self._set_auth_header()

        # Read timeout and retries
        self._retries = retries
        self._timeout = timeout

        # Instantiate APIs
        self._connections_api = api.ConnectionsApi(self._api_client)
        self._host_groups_api = api.HostGroupsApi(self._api_client)
        self._hosts_api = api.HostsApi(self._api_client)
        self._volume_snapshots_api = api.VolumeSnapshotsApi(self._api_client)
        self._volumes_api = api.VolumesApi(self._api_client)

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
        host_groups=None,  # type: List[models.ReferenceType]
        hosts=None,  # type: List[models.ReferenceType]
        volumes=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        host_group_names=None,  # type: List[str]
        host_names=None,  # type: List[str]
        volume_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Break the connection between a volume and its associated host or host group. The
        `volume_names` and `host_names` or `host_group_names` query parameters are
        required.

        Args:
            host_groups (list[FixedReference], optional):
                A list of host_groups to query for. Overrides host_group_names keyword arguments.
            hosts (list[FixedReference], optional):
                A list of hosts to query for. Overrides host_names keyword arguments.
            volumes (list[FixedReference], optional):
                A list of volumes to query for. Overrides volume_names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            host_group_names (list[str], optional):
                Performs the operation on the host group specified. Enter multiple names in
                comma-separated format. A request cannot include a mix of multiple objects with
                multiple names. For example, a request cannot include a mix of multiple host
                group names and volume names; instead, at least one of the objects (e.g.,
                `host_group_names`) must be set to only one name (e.g., `hgroup01`).
            host_names (list[str], optional):
                Performs the operation on the hosts specified. Enter multiple names in comma-
                separated format. For example, `host01,host02`. A request cannot include a mix
                of multiple objects with multiple names. For example, a request cannot include a
                mix of multiple host names and volume names; instead, at least one of the
                objects (e.g., `host_names`) must be set to only one name (e.g., `host01`).
            volume_names (list[str], optional):
                Performs the operation on the volume specified. Enter multiple names in comma-
                separated format. For example, `vol01,vol02`. A request cannot include a mix of
                multiple objects with multiple names. For example, a request cannot include a
                mix of multiple volume names and host names; instead, at least one of the
                objects (e.g., `volume_names`) must be set to only one name (e.g., `vol01`).
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
            host_group_names=host_group_names,
            host_names=host_names,
            volume_names=volume_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._connections_api.api20_connections_delete_with_http_info
        _process_references(host_groups, ['host_group_names'], kwargs)
        _process_references(hosts, ['host_names'], kwargs)
        _process_references(volumes, ['volume_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_connections(
        self,
        host_groups=None,  # type: List[models.ReferenceType]
        hosts=None,  # type: List[models.ReferenceType]
        protocol_endpoints=None,  # type: List[models.ReferenceType]
        volumes=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        filter=None,  # type: str
        host_group_names=None,  # type: List[str]
        host_names=None,  # type: List[str]
        limit=None,  # type: int
        offset=None,  # type: int
        protocol_endpoint_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        total_item_count=None,  # type: bool
        volume_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ConnectionGetResponse
        """
        Return a list of connections between a volume and its hosts and host groups, and
        the LUNs used by the associated hosts to address these volumes.

        Args:
            host_groups (list[FixedReference], optional):
                A list of host_groups to query for. Overrides host_group_names keyword arguments.
            hosts (list[FixedReference], optional):
                A list of hosts to query for. Overrides host_names keyword arguments.
            protocol_endpoints (list[FixedReference], optional):
                A list of protocol_endpoints to query for. Overrides protocol_endpoint_names keyword arguments.
            volumes (list[FixedReference], optional):
                A list of volumes to query for. Overrides volume_names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            host_group_names (list[str], optional):
                Performs the operation on the host group specified. Enter multiple names in
                comma-separated format. A request cannot include a mix of multiple objects with
                multiple names. For example, a request cannot include a mix of multiple host
                group names and volume names; instead, at least one of the objects (e.g.,
                `host_group_names`) must be set to only one name (e.g., `hgroup01`).
            host_names (list[str], optional):
                Performs the operation on the hosts specified. Enter multiple names in comma-
                separated format. For example, `host01,host02`. A request cannot include a mix
                of multiple objects with multiple names. For example, a request cannot include a
                mix of multiple host names and volume names; instead, at least one of the
                objects (e.g., `host_names`) must be set to only one name (e.g., `host01`).
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            protocol_endpoint_names (list[str], optional):
                Performs the operation on the protocol endpoints specified. Enter multiple names
                in comma-separated format. For example, `pe01,pe02`. A request cannot include a
                mix of multiple objects with multiple names. For example, a request cannot
                include a mix of multiple protocol endpoint names and host names; instead, at
                least one of the objects (e.g., `protocol_endpoint_names`) must be set to one
                name (e.g., `pe01`).
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                is calculated and returned in the response. If set to `false`, the
                `total_item_count` is `null` in the response. This may speed up queries where
                the `total_item_count` is large. If not specified, defaults to `false`.
            volume_names (list[str], optional):
                Performs the operation on the volume specified. Enter multiple names in comma-
                separated format. For example, `vol01,vol02`. A request cannot include a mix of
                multiple objects with multiple names. For example, a request cannot include a
                mix of multiple volume names and host names; instead, at least one of the
                objects (e.g., `volume_names`) must be set to only one name (e.g., `vol01`).
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._connections_api.api20_connections_get_with_http_info
        _process_references(host_groups, ['host_group_names'], kwargs)
        _process_references(hosts, ['host_names'], kwargs)
        _process_references(protocol_endpoints, ['protocol_endpoint_names'], kwargs)
        _process_references(volumes, ['volume_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_connections(
        self,
        host_groups=None,  # type: List[models.ReferenceType]
        hosts=None,  # type: List[models.ReferenceType]
        volumes=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        host_group_names=None,  # type: List[str]
        host_names=None,  # type: List[str]
        volume_names=None,  # type: List[str]
        connection=None,  # type: models.ConnectionPost
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ConnectionResponse
        """
        Create a connection between a volume and a host or host group. The
        `volume_names` and `host_names` or `host_group_names` query parameters are
        required.

        Args:
            host_groups (list[FixedReference], optional):
                A list of host_groups to query for. Overrides host_group_names keyword arguments.
            hosts (list[FixedReference], optional):
                A list of hosts to query for. Overrides host_names keyword arguments.
            volumes (list[FixedReference], optional):
                A list of volumes to query for. Overrides volume_names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            host_group_names (list[str], optional):
                Performs the operation on the host group specified. Enter multiple names in
                comma-separated format. A request cannot include a mix of multiple objects with
                multiple names. For example, a request cannot include a mix of multiple host
                group names and volume names; instead, at least one of the objects (e.g.,
                `host_group_names`) must be set to only one name (e.g., `hgroup01`).
            host_names (list[str], optional):
                Performs the operation on the hosts specified. Enter multiple names in comma-
                separated format. For example, `host01,host02`. A request cannot include a mix
                of multiple objects with multiple names. For example, a request cannot include a
                mix of multiple host names and volume names; instead, at least one of the
                objects (e.g., `host_names`) must be set to only one name (e.g., `host01`).
            volume_names (list[str], optional):
                Performs the operation on the volume specified. Enter multiple names in comma-
                separated format. For example, `vol01,vol02`. A request cannot include a mix of
                multiple objects with multiple names. For example, a request cannot include a
                mix of multiple volume names and host names; instead, at least one of the
                objects (e.g., `volume_names`) must be set to only one name (e.g., `vol01`).
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
            host_group_names=host_group_names,
            host_names=host_names,
            volume_names=volume_names,
            connection=connection,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._connections_api.api20_connections_post_with_http_info
        _process_references(host_groups, ['host_group_names'], kwargs)
        _process_references(hosts, ['host_names'], kwargs)
        _process_references(volumes, ['volume_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_host_groups(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete a host group. The `names` query parameter is required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
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
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._host_groups_api.api20_host_groups_delete_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_host_groups(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_item_count=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.HostGroupGetResponse
        """
        Return a list of host groups.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                is calculated and returned in the response. If set to `false`, the
                `total_item_count` is `null` in the response. This may speed up queries where
                the `total_item_count` is large. If not specified, defaults to `false`.
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
            filter=filter,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._host_groups_api.api20_host_groups_get_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_host_groups_hosts(
        self,
        groups=None,  # type: List[models.ReferenceType]
        members=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        filter=None,  # type: str
        group_names=None,  # type: List[str]
        limit=None,  # type: int
        member_names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_item_count=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.MemberNoIdAllGetResponse
        """
        Returns a list of host groups that are associated with hosts.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, host groups, and directories. Enter multiple names in
                comma-separated format. For example, `vol01,vol02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                is calculated and returned in the response. If set to `false`, the
                `total_item_count` is `null` in the response. This may speed up queries where
                the `total_item_count` is large. If not specified, defaults to `false`.
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
            filter=filter,
            group_names=group_names,
            limit=limit,
            member_names=member_names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._host_groups_api.api20_host_groups_hosts_get_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_host_groups(
        self,
        references=None,  # type: List[models.ReferenceType]
        host_group=None,  # type: models.HostGroupPatch
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.HostGroupResponse
        """
        Manage a host group. The `names` query parameter is required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            host_group (HostGroupPatch, required):
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
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
            host_group=host_group,
            authorization=authorization,
            x_request_id=x_request_id,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._host_groups_api.api20_host_groups_patch_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_host_groups_performance_by_array(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_item_count=None,  # type: bool
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ResourcePerformanceNoIdByArrayGetResponse
        """
        Return real-time and historical performance data, real-time latency data, and
        average I/O size data. The data returned is for each volume that is connected to
        a host group on the current array and for each volume that is connected to a
        host group on any remote arrays that are visible to the current array. The data
        is displayed as a total across all host groups on each array and by individual
        host group.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                is calculated and returned in the response. If set to `false`, the
                `total_item_count` is `null` in the response. This may speed up queries where
                the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.
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
            filter=filter,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._host_groups_api.api20_host_groups_performance_by_array_get_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_host_groups_performance(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_item_count=None,  # type: bool
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ResourcePerformanceNoIdGetResponse
        """
        Return real-time and historical performance data, real-time latency data, and
        average I/O sizes across all volumes, displayed both by host group and as a
        total across all host groups.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                is calculated and returned in the response. If set to `false`, the
                `total_item_count` is `null` in the response. This may speed up queries where
                the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.
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
            filter=filter,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._host_groups_api.api20_host_groups_performance_get_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_host_groups(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.HostGroupResponse
        """
        Create a host group. The `names` query parameter is required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
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
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._host_groups_api.api20_host_groups_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_hosts(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Deletes an existing host. All volumes that are connected to the host, either
        through private or shared connections, must be disconnected from the host before
        the host can be deleted. The `names` query parameter is required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
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
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._hosts_api.api20_hosts_delete_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_hosts(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_item_count=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.HostGetResponse
        """
        Returns a list of hosts.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                is calculated and returned in the response. If set to `false`, the
                `total_item_count` is `null` in the response. This may speed up queries where
                the `total_item_count` is large. If not specified, defaults to `false`.
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
            filter=filter,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._hosts_api.api20_hosts_get_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_hosts_host_groups(
        self,
        groups=None,  # type: List[models.ReferenceType]
        members=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        filter=None,  # type: str
        group_names=None,  # type: List[str]
        limit=None,  # type: int
        member_names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_item_count=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.MemberNoIdAllGetResponse
        """
        Returns a list of hosts that are associated with host groups.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, host groups, and directories. Enter multiple names in
                comma-separated format. For example, `vol01,vol02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                is calculated and returned in the response. If set to `false`, the
                `total_item_count` is `null` in the response. This may speed up queries where
                the `total_item_count` is large. If not specified, defaults to `false`.
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
            filter=filter,
            group_names=group_names,
            limit=limit,
            member_names=member_names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._hosts_api.api20_hosts_host_groups_get_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_hosts(
        self,
        references=None,  # type: List[models.ReferenceType]
        host=None,  # type: models.HostPatch
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.HostResponse
        """
        Manages an existing host, including its storage network addresses, CHAP, host
        personality, and preferred arrays, or associate a host to a host group. The
        `names` query parameter is required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            host (HostPatch, required):
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
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
            host=host,
            authorization=authorization,
            x_request_id=x_request_id,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._hosts_api.api20_hosts_patch_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_hosts_performance_by_array(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_item_count=None,  # type: bool
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ResourcePerformanceNoIdByArrayGetResponse
        """
        Return real-time and historical performance data, real-time latency data, and
        average I/O size data. The data returned is for each volume that is connected to
        a host on the current array and for each volume that is connected to a host on
        any remote arrays that are visible to the current array. The data is displayed
        as a total across all hosts on each array and by individual host.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                is calculated and returned in the response. If set to `false`, the
                `total_item_count` is `null` in the response. This may speed up queries where
                the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.
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
            filter=filter,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._hosts_api.api20_hosts_performance_by_array_get_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_hosts_performance(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_item_count=None,  # type: bool
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ResourcePerformanceNoIdGetResponse
        """
        Return real-time and historical performance data, real-time latency data, and
        average I/O sizes across all volumes, displayed both by host and as a total
        across all hosts.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                is calculated and returned in the response. If set to `false`, the
                `total_item_count` is `null` in the response. This may speed up queries where
                the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.
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
            filter=filter,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._hosts_api.api20_hosts_performance_get_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_hosts(
        self,
        references=None,  # type: List[models.ReferenceType]
        host=None,  # type: models.HostPost
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.HostResponse
        """
        Creates a host. The `names` query parameter is required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            host (HostPost, required):
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
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
            host=host,
            authorization=authorization,
            x_request_id=x_request_id,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._hosts_api.api20_hosts_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_volume_snapshots(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Eradicate a volume snapshot that has been destroyed and is pending eradication.
        Eradicated volumes snapshots cannot be recovered. Volume snapshots are destroyed
        through the `PATCH` method. The `ids` or `names` parameter is required, but
        cannot be set together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._volume_snapshots_api.api20_volume_snapshots_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_volume_snapshots(
        self,
        references=None,  # type: List[models.ReferenceType]
        sources=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        destroyed=None,  # type: bool
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        source_ids=None,  # type: List[str]
        source_names=None,  # type: List[str]
        total_item_count=None,  # type: bool
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.VolumeSnapshotGetResponse
        """
        Return a list of volume snapshots, including those pending eradication.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_ids and source_names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in milliseconds.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            source_ids (list[str], optional):
                Performs the operation on the source ID specified. Enter multiple source IDs in
                comma-separated format.
            source_names (list[str], optional):
                Performs the operation on the source name specified. Enter multiple source names
                in comma-separated format. For example, `name01,name02`.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                is calculated and returned in the response. If set to `false`, the
                `total_item_count` is `null` in the response. This may speed up queries where
                the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._volume_snapshots_api.api20_volume_snapshots_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_volume_snapshots(
        self,
        references=None,  # type: List[models.ReferenceType]
        volume_snapshot=None,  # type: models.VolumeSnapshotPatch
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.VolumeSnapshotResponse
        """
        Rename, destroy, or recover a volume snapshot. To rename the suffix of a volume
        snapshot, set `name` to the new suffix name. To recover a volume snapshot that
        has been destroyed and is pending eradication, set `destroyed=true`. The `ids`
        or `names` parameter is required, but cannot be set together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            volume_snapshot (VolumeSnapshotPatch, required):
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
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
            volume_snapshot=volume_snapshot,
            authorization=authorization,
            x_request_id=x_request_id,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._volume_snapshots_api.api20_volume_snapshots_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_volume_snapshots(
        self,
        sources=None,  # type: List[models.ReferenceType]
        volume_snapshot=None,  # type: models.VolumeSnapshotPost
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        on=None,  # type: str
        source_ids=None,  # type: List[str]
        source_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.VolumeSnapshotResponse
        """
        Create a point-in-time snapshot of the contents of a volume. The `source_ids` or
        `source_names` parameter is required, but cannot be set together.

        Args:
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_ids and source_names keyword arguments.

            volume_snapshot (VolumeSnapshotPost, required):
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            on (str, optional):
                Performs the operation on the target name specified. For example,
                `targetName01`.
            source_ids (list[str], optional):
                Performs the operation on the source ID specified. Enter multiple source IDs in
                comma-separated format.
            source_names (list[str], optional):
                Performs the operation on the source name specified. Enter multiple source names
                in comma-separated format. For example, `name01,name02`.
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
            volume_snapshot=volume_snapshot,
            authorization=authorization,
            x_request_id=x_request_id,
            on=on,
            source_ids=source_ids,
            source_names=source_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._volume_snapshots_api.api20_volume_snapshots_post_with_http_info
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_volume_snapshots_transfer(
        self,
        references=None,  # type: List[models.ReferenceType]
        sources=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        destroyed=None,  # type: bool
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        offset=None,  # type: int
        sort=None,  # type: List[str]
        source_ids=None,  # type: List[str]
        source_names=None,  # type: List[str]
        total_item_count=None,  # type: bool
        total_only=None,  # type: bool
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.VolumeSnapshotTransferGetResponse
        """
        Returns a list of volume snapshots and their transfer statistics.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_ids and source_names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in milliseconds.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            source_ids (list[str], optional):
                Performs the operation on the source ID specified. Enter multiple source IDs in
                comma-separated format.
            source_names (list[str], optional):
                Performs the operation on the source name specified. Enter multiple source names
                in comma-separated format. For example, `name01,name02`.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                is calculated and returned in the response. If set to `false`, the
                `total_item_count` is `null` in the response. This may speed up queries where
                the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
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
            destroyed=destroyed,
            filter=filter,
            ids=ids,
            limit=limit,
            offset=offset,
            sort=sort,
            source_ids=source_ids,
            source_names=source_names,
            total_item_count=total_item_count,
            total_only=total_only,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._volume_snapshots_api.api20_volume_snapshots_transfer_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_volumes(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Eradicate a volume that has been destroyed and is pending eradication.
        Eradicated volumes cannot be recovered. Volumes are destroyed through the
        `PATCH` method. The `ids` or `names` parameter is required, but cannot be set
        together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._volumes_api.api20_volumes_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_volumes(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        destroyed=None,  # type: bool
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_item_count=None,  # type: bool
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.VolumeGetResponse
        """
        Return a list of volumes, including those pending eradication.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in milliseconds.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                is calculated and returned in the response. If set to `false`, the
                `total_item_count` is `null` in the response. This may speed up queries where
                the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._volumes_api.api20_volumes_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_volumes(
        self,
        references=None,  # type: List[models.ReferenceType]
        volume=None,  # type: models.VolumePatch
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        truncate=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.VolumeResponse
        """
        Renames or destroys a volume. To rename a volume, set `name` to the new name. To
        move a volume, set the `pod` or `volume group` parameters. To destroy a volume,
        set `destroyed=true`. To recover a volume that has been destroyed and is pending
        eradication, set `destroyed=false`. Sets the bandwidth and IOPs limits of a
        volume group. The `ids` or `names` parameter is required, but cannot be set
        together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            volume (VolumePatch, required):
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            truncate (bool, optional):
                If set to `true`, reduces the size of a volume during a volume resize operation.
                When a volume is truncated, Purity automatically takes an undo snapshot,
                providing a 24-hour window during which the previous contents can be retrieved.
                After truncating a volume, its provisioned size can be subsequently increased,
                but the data in truncated sectors cannot be retrieved. If set to `false` or not
                set at all and the volume is being reduced in size, the volume copy operation
                fails. Required if the `provisioned` parameter is set to a volume size that is
                smaller than the original size.
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
            volume=volume,
            authorization=authorization,
            x_request_id=x_request_id,
            ids=ids,
            names=names,
            truncate=truncate,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._volumes_api.api20_volumes_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_volumes_performance_by_array(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        destroyed=None,  # type: bool
        filter=None,  # type: str
        end_time=None,  # type: int
        resolution=None,  # type: int
        start_time=None,  # type: int
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_item_count=None,  # type: bool
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ResourcePerformanceByArrayGetResponse
        """
        Returns real-time and historical performance data, real-time latency data, and
        average I/O size data. The data returned is for each volume on the current array
        and for each volume on any remote arrays that are visible to the current array.
        The data is grouped by individual volumes and as a total across all volumes on
        each array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in milliseconds.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            end_time (int, optional):
                Displays historical performance data for the specified time window, where
                `start_time` is the beginning of the time window, and `end_time` is the end of
                the time window. The `start_time` and `end_time` parameters are specified in
                milliseconds since the UNIX epoch. If `start_time` is not specified, the start
                time will default to one resolution before the end time, meaning that the most
                recent sample of performance data will be displayed. If `end_time`is not
                specified, the end time will default to the current time. Include the
                `resolution` parameter to display the performance data at the specified
                resolution. If not specified, `resolution` defaults to the lowest valid
                resolution.
            resolution (int, optional):
                The number of milliseconds between samples of historical data. For array-wide
                performance metrics (`/arrays/performance` endpoint), valid values are `1000` (1
                second), `30000` (30 seconds), `300000` (5 minutes), `1800000` (30 minutes),
                `7200000` (2 hours), `28800000` (8 hours), and `86400000` (24 hours). For
                performance metrics on storage objects (`<object name>/performance` endpoint),
                such as volumes, valid values are `30000` (30 seconds), `300000` (5 minutes),
                `1800000` (30 minutes), `7200000` (2 hours), `28800000` (8 hours), and
                `86400000` (24 hours). For space metrics, (`<object name>/space` endpoint),
                valid values are `300000` (5 minutes), `1800000` (30 minutes), `7200000` (2
                hours), `28800000` (8 hours), and `86400000` (24 hours). Include the
                `start_time` parameter to display the performance data starting at the specified
                start time. If `start_time` is not specified, the start time will default to one
                resolution before the end time, meaning that the most recent sample of
                performance data will be displayed. Include the `end_time` parameter to display
                the performance data until the specified end time. If `end_time`is not
                specified, the end time will default to the current time. If the `resolution`
                parameter is not specified but either the `start_time` or `end_time` parameter
                is, then `resolution` will default to the lowest valid resolution.
            start_time (int, optional):
                Displays historical performance data for the specified time window, where
                `start_time` is the beginning of the time window, and `end_time` is the end of
                the time window. The `start_time` and `end_time` parameters are specified in
                milliseconds since the UNIX epoch. If `start_time` is not specified, the start
                time will default to one resolution before the end time, meaning that the most
                recent sample of performance data will be displayed. If `end_time`is not
                specified, the end time will default to the current time. Include the
                `resolution` parameter to display the performance data at the specified
                resolution. If not specified, `resolution` defaults to the lowest valid
                resolution.
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                is calculated and returned in the response. If set to `false`, the
                `total_item_count` is `null` in the response. This may speed up queries where
                the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.
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
            destroyed=destroyed,
            filter=filter,
            end_time=end_time,
            resolution=resolution,
            start_time=start_time,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._volumes_api.api20_volumes_performance_by_array_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_volumes_performance(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        destroyed=None,  # type: bool
        filter=None,  # type: str
        end_time=None,  # type: int
        resolution=None,  # type: int
        start_time=None,  # type: int
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_item_count=None,  # type: bool
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ResourcePerformanceGetResponse
        """
        Returns real-time and historical performance data, real-time latency data, and
        average I/O sizes for each volume and and as a total of all volumes across the
        entire array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in milliseconds.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            end_time (int, optional):
                Displays historical performance data for the specified time window, where
                `start_time` is the beginning of the time window, and `end_time` is the end of
                the time window. The `start_time` and `end_time` parameters are specified in
                milliseconds since the UNIX epoch. If `start_time` is not specified, the start
                time will default to one resolution before the end time, meaning that the most
                recent sample of performance data will be displayed. If `end_time`is not
                specified, the end time will default to the current time. Include the
                `resolution` parameter to display the performance data at the specified
                resolution. If not specified, `resolution` defaults to the lowest valid
                resolution.
            resolution (int, optional):
                The number of milliseconds between samples of historical data. For array-wide
                performance metrics (`/arrays/performance` endpoint), valid values are `1000` (1
                second), `30000` (30 seconds), `300000` (5 minutes), `1800000` (30 minutes),
                `7200000` (2 hours), `28800000` (8 hours), and `86400000` (24 hours). For
                performance metrics on storage objects (`<object name>/performance` endpoint),
                such as volumes, valid values are `30000` (30 seconds), `300000` (5 minutes),
                `1800000` (30 minutes), `7200000` (2 hours), `28800000` (8 hours), and
                `86400000` (24 hours). For space metrics, (`<object name>/space` endpoint),
                valid values are `300000` (5 minutes), `1800000` (30 minutes), `7200000` (2
                hours), `28800000` (8 hours), and `86400000` (24 hours). Include the
                `start_time` parameter to display the performance data starting at the specified
                start time. If `start_time` is not specified, the start time will default to one
                resolution before the end time, meaning that the most recent sample of
                performance data will be displayed. Include the `end_time` parameter to display
                the performance data until the specified end time. If `end_time`is not
                specified, the end time will default to the current time. If the `resolution`
                parameter is not specified but either the `start_time` or `end_time` parameter
                is, then `resolution` will default to the lowest valid resolution.
            start_time (int, optional):
                Displays historical performance data for the specified time window, where
                `start_time` is the beginning of the time window, and `end_time` is the end of
                the time window. The `start_time` and `end_time` parameters are specified in
                milliseconds since the UNIX epoch. If `start_time` is not specified, the start
                time will default to one resolution before the end time, meaning that the most
                recent sample of performance data will be displayed. If `end_time`is not
                specified, the end time will default to the current time. Include the
                `resolution` parameter to display the performance data at the specified
                resolution. If not specified, `resolution` defaults to the lowest valid
                resolution.
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                is calculated and returned in the response. If set to `false`, the
                `total_item_count` is `null` in the response. This may speed up queries where
                the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.
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
            destroyed=destroyed,
            filter=filter,
            end_time=end_time,
            resolution=resolution,
            start_time=start_time,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._volumes_api.api20_volumes_performance_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_volumes(
        self,
        references=None,  # type: List[models.ReferenceType]
        volume=None,  # type: models.VolumePost
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        names=None,  # type: List[str]
        overwrite=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.VolumeResponse
        """
        Create one or more virtual storage volumes of the specified size. If
        `provisioned` is not specified, the size of the new volume defaults to 1 MB in
        size. The `names` query parameter is required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            volume (VolumePost, required):
            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            overwrite (bool, optional):
                If set to `true`, overwrites an existing volume during a volume copy operation.
                If set to `false` or not set at all and the target name is an existing volume,
                the volume copy operation fails. Required if the `source: id` or `source: name`
                body parameter is set and the source overwrites an existing volume during the
                volume copy operation.
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
            volume=volume,
            authorization=authorization,
            x_request_id=x_request_id,
            names=names,
            overwrite=overwrite,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._volumes_api.api20_volumes_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_volumes_space(
        self,
        references=None,  # type: List[models.ReferenceType]
        authorization=None,  # type: str
        x_request_id=None,  # type: str
        destroyed=None,  # type: bool
        filter=None,  # type: str
        end_time=None,  # type: int
        resolution=None,  # type: int
        start_time=None,  # type: int
        ids=None,  # type: List[str]
        limit=None,  # type: int
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_item_count=None,  # type: bool
        total_only=None,  # type: bool
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ResourceSpaceGetResponse
        """
        Return provisioned (virtual) size and physical storage consumption data for each
        volume.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            x_request_id (str, optional):
                A header to provide to track the API call. Generated by the server if not
                provided.
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in milliseconds.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            end_time (int, optional):
                Displays historical performance data for the specified time window, where
                `start_time` is the beginning of the time window, and `end_time` is the end of
                the time window. The `start_time` and `end_time` parameters are specified in
                milliseconds since the UNIX epoch. If `start_time` is not specified, the start
                time will default to one resolution before the end time, meaning that the most
                recent sample of performance data will be displayed. If `end_time`is not
                specified, the end time will default to the current time. Include the
                `resolution` parameter to display the performance data at the specified
                resolution. If not specified, `resolution` defaults to the lowest valid
                resolution.
            resolution (int, optional):
                The number of milliseconds between samples of historical data. For array-wide
                performance metrics (`/arrays/performance` endpoint), valid values are `1000` (1
                second), `30000` (30 seconds), `300000` (5 minutes), `1800000` (30 minutes),
                `7200000` (2 hours), `28800000` (8 hours), and `86400000` (24 hours). For
                performance metrics on storage objects (`<object name>/performance` endpoint),
                such as volumes, valid values are `30000` (30 seconds), `300000` (5 minutes),
                `1800000` (30 minutes), `7200000` (2 hours), `28800000` (8 hours), and
                `86400000` (24 hours). For space metrics, (`<object name>/space` endpoint),
                valid values are `300000` (5 minutes), `1800000` (30 minutes), `7200000` (2
                hours), `28800000` (8 hours), and `86400000` (24 hours). Include the
                `start_time` parameter to display the performance data starting at the specified
                start time. If `start_time` is not specified, the start time will default to one
                resolution before the end time, meaning that the most recent sample of
                performance data will be displayed. Include the `end_time` parameter to display
                the performance data until the specified end time. If `end_time`is not
                specified, the end time will default to the current time. If the `resolution`
                parameter is not specified but either the `start_time` or `end_time` parameter
                is, then `resolution` will default to the lowest valid resolution.
            start_time (int, optional):
                Displays historical performance data for the specified time window, where
                `start_time` is the beginning of the time window, and `end_time` is the end of
                the time window. The `start_time` and `end_time` parameters are specified in
                milliseconds since the UNIX epoch. If `start_time` is not specified, the start
                time will default to one resolution before the end time, meaning that the most
                recent sample of performance data will be displayed. If `end_time`is not
                specified, the end time will default to the current time. Include the
                `resolution` parameter to display the performance data at the specified
                resolution. If not specified, `resolution` defaults to the lowest valid
                resolution.
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                is calculated and returned in the response. If set to `false`, the
                `total_item_count` is `null` in the response. This may speed up queries where
                the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
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
            destroyed=destroyed,
            filter=filter,
            end_time=end_time,
            resolution=resolution,
            start_time=start_time,
            ids=ids,
            limit=limit,
            offset=offset,
            sort=sort,
            total_item_count=total_item_count,
            total_only=total_only,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._volumes_api.api20_volumes_space_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def _get_base_url(self, target):
        return 'https://{}'.format(target)

    def _get_api_token_endpoint(self, target):
        return self._get_base_url(target) + '/api/2.0/login'

    def _set_agent_header(self):
        """
        Set the user-agent header of the internal client.
        """
        self._api_client.set_default_header('User-Agent', self._api_client.user_agent)

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

    def _create_valid_response(self, response, endpoint, kwargs):
        """
        Create a ValidResponse from a Swagger response.

        Args:
            response (tuple):
                Body, status, header tuple as returned from Swagger client.
            endpoint (function):
                The function of the Swagger client that was called.
            kwargs (dict):
                The processed kwargs that were passed to the endpoint function.

        Returns:
            ValidResponse
        """
        body, status, headers = response
        continuation_token = getattr(body, "continuation_token", None)
        total_item_count = getattr(body, "total_item_count", None)
        total = getattr(body, "total", None)
        more_items_remaining = getattr(body, "more_items_remaining", None)
        items = None
        if body is not None:
            items = iter(ItemIterator(self, endpoint, kwargs,
                                      continuation_token, total_item_count,
                                      body.items,
                                      headers.get(Headers.x_request_id, None),
                                      more_items_remaining or False, None))
        return ValidResponse(status, continuation_token, total_item_count,
                             items, headers, total, more_items_remaining)

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
            errors = [ApiError(None, body.get(Responses.message, None))]
        else:
            errors = [ApiError(err.get(Responses.context, None),
                               err.get(Responses.message, None))
                      for err in body.get(Responses.errors, {})]
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
