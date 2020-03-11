import json
import platform
import time
import urllib3

from ...exceptions import PureError
from ...keywords import Parameters, Headers, Responses
from ...responses import ValidResponse, ErrorResponse, ApiError, ItemIterator
from ...token_manager import TokenManager
from .api_client import ApiClient
from .rest import ApiException
from .configuration import Configuration
from . import api
from . import models


class Client(object):
    DEFAULT_TIMEOUT = 15.0
    DEFAULT_RETRIES = 5
    # Format: client/client_version/endpoint/endpoint_version/system/release
    USER_AGENT = ('pypureclient/1.3.0/FA/2.1/{sys}/{rel}'
                  .format(sys=platform.system(), rel=platform.release()))

    def __init__(self, target, id_token=None, private_key_file=None, private_key_password=None,
                 username=None, client_id=None, key_id=None, issuer=None,
                 retries=DEFAULT_RETRIES, timeout=DEFAULT_TIMEOUT, ssl_cert=None):
        """
        Initialize a FlashArray Client.

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
            retries (int, optional):
                The number of times to retry an API call if it fails for a
                non-blocking reason. Defaults to 5.
            timeout (float or (float, float), optional):
                The timeout duration in seconds, either in total time or
                (connect and read) times. Defaults to 15.0 total.
            ssl_cert (str, optional):
                SSL certificate to use. Defaults to None.

        Raises:
            PureError: If it could not create an ID or access token
        """
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        config = Configuration()
        config.verify_ssl = ssl_cert is not None
        config.ssl_ca_cert = ssl_cert
        config.host = 'https://{}'.format(target)

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
        self._set_auth_header()
        self._api_client.user_agent = self.USER_AGENT

        # Read timeout and retries
        self._retries = retries
        self._timeout = timeout

        # Instantiate APIs
        self._api_clients_api = api.APIClientsApi(self._api_client)
        self._connections_api = api.ConnectionsApi(self._api_client)
        self._host_groups_api = api.HostGroupsApi(self._api_client)
        self._hosts_api = api.HostsApi(self._api_client)
        self._offloads_api = api.OffloadsApi(self._api_client)
        self._pods_api = api.PodsApi(self._api_client)
        self._protection_group_snapshots_api = api.ProtectionGroupSnapshotsApi(self._api_client)
        self._protection_groups_api = api.ProtectionGroupsApi(self._api_client)
        self._remote_pods_api = api.RemotePodsApi(self._api_client)
        self._remote_protection_group_snapshots_api = api.RemoteProtectionGroupSnapshotsApi(self._api_client)
        self._remote_protection_groups_api = api.RemoteProtectionGroupsApi(self._api_client)
        self._remote_volume_snapshots_api = api.RemoteVolumeSnapshotsApi(self._api_client)
        self._volume_groups_api = api.VolumeGroupsApi(self._api_client)
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

    def delete_api_clients(self, references=None, **kwargs):
        """
        Deletes an API client. The `ids` or `names` parameter is required, but cannot be
        set together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._api_clients_api.api21_api_clients_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_api_clients(self, references=None, **kwargs):
        """
        Returns a list of API clients.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._api_clients_api.api21_api_clients_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def patch_api_clients(self, references=None, **kwargs):
        """
        Enables or disables an API client. The `ids` or `names` parameter is required,
        but cannot be set together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            api_clients (ApiClientPatch, required):
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._api_clients_api.api21_api_clients_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_api_clients(self, references=None, **kwargs):
        """
        Creates an API client. Newly created API clients are disabled by default. Enable
        an API client through the `PATCH` method. The `names`, `max_role`, `issuer`, and
        `public_key` parameters are required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            api_clients (ApiClientPost, required):
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._api_clients_api.api21_api_clients_post_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_connections(self, host_groups=None, hosts=None, volumes=None, **kwargs):
        """
        Breaks the connection between a volume and its associated host or host group.
        The `volume_names` and `host_names` or `host_group_names` query parameters are
        required.

        Args:
            host_groups (list[FixedReference], optional):
                A list of host_groups to query for. Overrides host_group_names keyword arguments.
            hosts (list[FixedReference], optional):
                A list of hosts to query for. Overrides host_names keyword arguments.
            volumes (list[FixedReference], optional):
                A list of volumes to query for. Overrides volume_names keyword arguments.

        Keyword args:
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

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._connections_api.api21_connections_delete_with_http_info
        _process_references(host_groups, ['host_group_names'], kwargs)
        _process_references(hosts, ['host_names'], kwargs)
        _process_references(volumes, ['volume_names'], kwargs)
        list_params = ['host_group_names', 'host_names', 'volume_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_connections(self, host_groups=None, hosts=None, protocol_endpoints=None, volumes=None, **kwargs):
        """
        Returns a list of connections between a volume and its hosts and host groups,
        and the LUNs used by the associated hosts to address these volumes.

        Args:
            host_groups (list[FixedReference], optional):
                A list of host_groups to query for. Overrides host_group_names keyword arguments.
            hosts (list[FixedReference], optional):
                A list of hosts to query for. Overrides host_names keyword arguments.
            protocol_endpoints (list[FixedReference], optional):
                A list of protocol_endpoints to query for. Overrides protocol_endpoint_names keyword arguments.
            volumes (list[FixedReference], optional):
                A list of volumes to query for. Overrides volume_names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            volume_names (list[str], optional):
                Performs the operation on the volume specified. Enter multiple names in comma-
                separated format. For example, `vol01,vol02`. A request cannot include a mix of
                multiple objects with multiple names. For example, a request cannot include a
                mix of multiple volume names and host names; instead, at least one of the
                objects (e.g., `volume_names`) must be set to only one name (e.g., `vol01`).

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._connections_api.api21_connections_get_with_http_info
        _process_references(host_groups, ['host_group_names'], kwargs)
        _process_references(hosts, ['host_names'], kwargs)
        _process_references(protocol_endpoints, ['protocol_endpoint_names'], kwargs)
        _process_references(volumes, ['volume_names'], kwargs)
        list_params = ['host_group_names', 'host_names', 'protocol_endpoint_names', 'sort', 'volume_names']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_connections(self, host_groups=None, hosts=None, volumes=None, **kwargs):
        """
        Creates a connection between a volume and a host or host group. The
        `volume_names` and `host_names` or `host_group_names` query parameters are
        required.

        Args:
            host_groups (list[FixedReference], optional):
                A list of host_groups to query for. Overrides host_group_names keyword arguments.
            hosts (list[FixedReference], optional):
                A list of hosts to query for. Overrides host_names keyword arguments.
            volumes (list[FixedReference], optional):
                A list of volumes to query for. Overrides volume_names keyword arguments.

        Keyword args:
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

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._connections_api.api21_connections_post_with_http_info
        _process_references(host_groups, ['host_group_names'], kwargs)
        _process_references(hosts, ['host_names'], kwargs)
        _process_references(volumes, ['volume_names'], kwargs)
        list_params = ['host_group_names', 'host_names', 'volume_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_host_groups(self, references=None, **kwargs):
        """
        Deletes a host group. The `names` query parameter is required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._host_groups_api.api21_host_groups_delete_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_host_groups(self, references=None, **kwargs):
        """
        Returns a list of host groups.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._host_groups_api.api21_host_groups_get_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names', 'sort']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_host_groups_hosts(self, groups=None, members=None, **kwargs):
        """
        Removes a host from a host group. Removing a host from a host group
        automatically disconnects the host from all volumes associated with the group.
        Hosts can be removed from host groups at any time. The `group_names` and
        `member_names` parameters are required and must be set together, and only one
        host group can be specified at a time.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._host_groups_api.api21_host_groups_hosts_delete_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_host_groups_hosts(self, groups=None, members=None, **kwargs):
        """
        Returns a list of host groups that are associated with hosts.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
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
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._host_groups_api.api21_host_groups_hosts_get_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names', 'sort']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_host_groups_hosts(self, groups=None, members=None, **kwargs):
        """
        Adds a host to a host group. Adding a host to a host group automatically
        connects the host to all volumes associated with the group. Multiple hosts can
        be belong to a host group, but a host can only belong to one host group. Hosts
        can be added to host groups at any time. The `group_names` and `member_names`
        parameters are required and must be set together, and only one host group can be
        specified at a time.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._host_groups_api.api21_host_groups_hosts_post_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def patch_host_groups(self, references=None, **kwargs):
        """
        Manages a host group. The `names` query parameter is required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            host_group (HostGroupPatch, required):
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._host_groups_api.api21_host_groups_patch_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_host_groups_performance_by_array(self, references=None, **kwargs):
        """
        Returns real-time and historical performance data, real-time latency data, and
        average I/O size data. The data returned is for each volume that is connected to
        a host group on the current array and for each volume that is connected to a
        host group on any remote arrays that are visible to the current array. The data
        is displayed as a total across all host groups on each array and by individual
        host group.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._host_groups_api.api21_host_groups_performance_by_array_get_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_host_groups_performance(self, references=None, **kwargs):
        """
        Returns real-time and historical performance data, real-time latency data, and
        average I/O sizes across all volumes, displayed both by host group and as a
        total across all host groups.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._host_groups_api.api21_host_groups_performance_get_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_host_groups(self, references=None, **kwargs):
        """
        Creates a host group. The `names` query parameter is required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._host_groups_api.api21_host_groups_post_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_host_groups_protection_groups(self, groups=None, members=None, **kwargs):
        """
        Removes a host group member from a protection group. After the member has been
        removed, it is no longer protected by the group. Any protection group snapshots
        that were taken before the member was removed will not be affected. Removing a
        member from a protection group does not delete the member from the array, and
        the member can be added back to the protection group at any time. The
        `group_names` parameter represents the name of the protection group, and the
        `member_names` parameter represents the name of the host group. The
        `group_names` and `member_names` parameters are required and must be set
        together.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._host_groups_api.api21_host_groups_protection_groups_delete_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_host_groups_protection_groups(self, groups=None, members=None, **kwargs):
        """
        Returns a list of host group members that belong to one or more protection
        groups.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
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
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._host_groups_api.api21_host_groups_protection_groups_get_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names', 'sort']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_host_groups_protection_groups(self, groups=None, members=None, **kwargs):
        """
        Adds a host group member to a protection group. Members that are already in the
        protection group are not affected. For asynchronous replication, only members of
        the same type can belong to a protection group. The `group_names` parameter
        represents the name of the protection group, and the `member_names` parameter
        represents the name of the host group. The `group_names` and `member_names`
        parameters are required and must be set together.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._host_groups_api.api21_host_groups_protection_groups_post_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_host_groups_space(self, references=None, **kwargs):
        """
        Returns provisioned (virtual) size and physical storage consumption data for
        each host group.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._host_groups_api.api21_host_groups_space_get_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_hosts(self, references=None, **kwargs):
        """
        Deletes an existing host. All volumes that are connected to the host, either
        through private or shared connections, must be disconnected from the host before
        the host can be deleted. The `names` query parameter is required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._hosts_api.api21_hosts_delete_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_hosts(self, references=None, **kwargs):
        """
        Returns a list of hosts.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._hosts_api.api21_hosts_get_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names', 'sort']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_hosts_host_groups(self, groups=None, members=None, **kwargs):
        """
        Removes a host from a host group. Removing a host from a host group
        automatically disconnects the host from all volumes associated with the group.
        Hosts can be removed from host groups at any time. The `group_names` and
        `member_names` parameters are required and must be set together, and only one
        host group can be specified at a time.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._hosts_api.api21_hosts_host_groups_delete_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_hosts_host_groups(self, groups=None, members=None, **kwargs):
        """
        Returns a list of hosts that are associated with host groups.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
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
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._hosts_api.api21_hosts_host_groups_get_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names', 'sort']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_hosts_host_groups(self, groups=None, members=None, **kwargs):
        """
        Adds a host to a host group. Adding a host to a host group automatically
        connects the host to all volumes associated with the group. Multiple hosts can
        be belong to a host group, but a host can only belong to one host group. Hosts
        can be added to host groups at any time. The `group_names` and `member_names`
        parameters are required and must be set together, and only one host group can be
        specified at a time.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._hosts_api.api21_hosts_host_groups_post_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def patch_hosts(self, references=None, **kwargs):
        """
        Manages an existing host, including its storage network addresses, CHAP, host
        personality, and preferred arrays, or associate a host to a host group. The
        `names` query parameter is required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            host (HostPatch, required):
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._hosts_api.api21_hosts_patch_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_hosts_performance_by_array(self, references=None, **kwargs):
        """
        Returns real-time and historical performance data, real-time latency data, and
        average I/O size data. The data returned is for each volume that is connected to
        a host on the current array and for each volume that is connected to a host on
        any remote arrays that are visible to the current array. The data is displayed
        as a total across all hosts on each array and by individual host.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._hosts_api.api21_hosts_performance_by_array_get_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_hosts_performance(self, references=None, **kwargs):
        """
        Returns real-time and historical performance data, real-time latency data, and
        average I/O sizes across all volumes, displayed both by host and as a total
        across all hosts.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._hosts_api.api21_hosts_performance_get_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_hosts(self, references=None, **kwargs):
        """
        Creates a host. The `names` query parameter is required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            host (HostPost, required):
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._hosts_api.api21_hosts_post_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_hosts_protection_groups(self, groups=None, members=None, **kwargs):
        """
        Removes a host member from a protection group. After the member has been
        removed, it is no longer protected by the group. Any protection group snapshots
        that were taken before the member was removed will not be affected. Removing a
        member from a protection group does not delete the member from the array, and
        the member can be added back to the protection group at any time. The
        `group_names` parameter represents the name of the protection group, and the
        `member_names` parameter represents the name of the host. The `group_names` and
        `member_names` parameters are required and must be set together.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._hosts_api.api21_hosts_protection_groups_delete_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_hosts_protection_groups(self, groups=None, members=None, **kwargs):
        """
        Returns a list of host members that belong to one or more protection groups.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
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
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._hosts_api.api21_hosts_protection_groups_get_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names', 'sort']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_hosts_protection_groups(self, groups=None, members=None, **kwargs):
        """
        Adds a host member to a protection group. Members that are already in the
        protection group are not affected. For asynchronous replication, only members of
        the same type can belong to a protection group. The `group_names` parameter
        represents the name of the protection group, and the `member_names` parameter
        represents the name of the host. The `group_names` and `member_names` parameters
        are required and must be set together.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._hosts_api.api21_hosts_protection_groups_post_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_hosts_space(self, references=None, **kwargs):
        """
        Returns provisioned (virtual) size and physical storage consumption data for
        each host.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._hosts_api.api21_hosts_space_get_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_offloads(self, references=None, **kwargs):
        """
        Disconnects the array from an offload target.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._offloads_api.api21_offloads_delete_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_offloads(self, references=None, **kwargs):
        """
        Returns a list of offload targets that are connected to the array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
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
            protocol (str, optional):
                Protocol type. Valid values are `nfs`, `s3`, and `azure`.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._offloads_api.api21_offloads_get_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_offloads(self, references=None, **kwargs):
        """
        Connects the array to an offload target. Before you can connect to, manage, and
        replicate to an offload target, the respective Purity//FA app must be installed.
        For more information about Purity//FA apps, refer to the Apps section of this
        guide.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            offload (OffloadPost, required):
            initialize (bool, optional):
                If set to `true`, initializes the Amazon S3 or Azure Blob container in
                preparation for offloading. The parameter must be set to `true` if this is the
                first time the array is connecting to the offload target.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._offloads_api.api21_offloads_post_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_pods_arrays(self, groups=None, members=None, **kwargs):
        """
        Unstretches a pod from an array, collapsing the pod to a single array. Unstretch
        a pod from an array when the volumes within the stretched pod no longer need to
        be synchronously replicated between the two arrays. After a pod has been
        unstretched, synchronous replication stops. A destroyed version of the pod with
        \"restretch\" appended to the pod name is created on the array that no longer
        has the pod. The restretch pod represents a point-in-time snapshot of the pod,
        just before it was unstretched. The restretch pod enters an eradication pending
        period starting from the time that the pod was unstretched. A restretch can pod
        can be cloned or destroyed, but it cannot be explicitly recovered. The
        `group_names` parameter represents the name of the pod to be unstretched. The
        `member_names` parameter represents the name of the array from which the pod is
        to be unstretched. The `group_names` and `member_names` parameters are required
        and must be set together.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names and group_ids keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names and member_ids keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            group_ids (list[str], optional):
                A list of group IDs.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.
            member_ids (list[str], optional):
                A list of member IDs.
            with_unknown (bool, optional):
                If set to `true`, unstretches the specified pod from the specified array by
                force. Use the `with_unknown` parameter in the following rare event&#58; the
                local array goes offline while the pod is still stretched across two arrays, the
                status of the remote array becomes unknown, and there is no guarantee that the
                pod is online elsewhere.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._pods_api.api21_pods_arrays_delete_with_http_info
        _process_references(groups, ['group_names', 'group_ids'], kwargs)
        _process_references(members, ['member_names', 'member_ids'], kwargs)
        list_params = ['group_names', 'group_ids', 'member_names', 'member_ids']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_pods_arrays(self, groups=None, members=None, **kwargs):
        """
        Returns a list of pods and the local and remote arrays over which the pods are
        stretched. The optional `group_names` parameter represents the name of the pod.
        The optional `member_names` parameter represents the name of the array over
        which the pod is stretched.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names and group_ids keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names and member_ids keyword arguments.

        Keyword args:
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            group_ids (list[str], optional):
                A list of group IDs.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.
            member_ids (list[str], optional):
                A list of member IDs.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._pods_api.api21_pods_arrays_get_with_http_info
        _process_references(groups, ['group_names', 'group_ids'], kwargs)
        _process_references(members, ['member_names', 'member_ids'], kwargs)
        list_params = ['group_names', 'group_ids', 'member_names', 'member_ids', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_pods_arrays(self, groups=None, members=None, **kwargs):
        """
        Stretches a pod to an array. When a pod is stretched to an array, the data in
        the arrays over which the pod is stretched is synchronously replicated. The
        `group_names` parameter represents the name of the pod to be stretched. The
        `member_names` parameter represents the name of the array over which the pod is
        to be stretched. The `group_names` and `member_names` parameters are required
        and must be set together.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names and group_ids keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names and member_ids keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            group_ids (list[str], optional):
                A list of group IDs.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.
            member_ids (list[str], optional):
                A list of member IDs.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._pods_api.api21_pods_arrays_post_with_http_info
        _process_references(groups, ['group_names', 'group_ids'], kwargs)
        _process_references(members, ['member_names', 'member_ids'], kwargs)
        list_params = ['group_names', 'group_ids', 'member_names', 'member_ids']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_pods(self, references=None, **kwargs):
        """
        Eradicates a pod that has been destroyed and is pending eradication. Eradicated
        pods cannot be recovered. Pods are destroyed through the PATCH method. The `ids`
        or `names` parameter is required, but cannot be set together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._pods_api.api21_pods_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_pods(self, references=None, **kwargs):
        """
        Returns a list of pods that are stretched to this array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._pods_api.api21_pods_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def patch_pods(self, references=None, **kwargs):
        """
        Manages the details of a pod.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            pod (PodPatch, required):
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._pods_api.api21_pods_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_pods_performance_by_array(self, references=None, **kwargs):
        """
        Returns real-time and historical performance data, real-time latency data, and
        average I/O size data. The data is displayed as a total across all pods on the
        local array and by individual pod.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._pods_api.api21_pods_performance_by_array_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_pods_performance(self, references=None, **kwargs):
        """
        Returns real-time and historical performance data, real-time latency data, and
        average I/O sizes across all pods, displayed both by pod and as a total across
        all pods.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._pods_api.api21_pods_performance_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_pods(self, references=None, **kwargs):
        """
        Creates a pod on the local array. Each pod must be given a name that is unique
        across the arrays to which they are stretched, so a pod cannot be stretched to
        an array that already contains a pod with the same name. After a pod has been
        created, add volumes and protection groups to the pod, and then stretch the pod
        to another (connected) array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            pod (PodPost, required):
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._pods_api.api21_pods_post_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_pods_space(self, references=None, **kwargs):
        """
        Returns provisioned (virtual) size and physical storage consumption data for
        each pod on the local array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._pods_api.api21_pods_space_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'sort', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_protection_group_snapshots(self, references=None, **kwargs):
        """
        Eradicates a protection group snapshot that has been destroyed and is pending
        eradication. Eradicating a protection group snapshot eradicates all of its
        protection group snapshots. Eradicated protection group snapshots cannot be
        recovered. Protection group snapshots are destroyed through the `PATCH` method.
        The `ids` or `names` parameter is required, but cannot be set together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_group_snapshots_api.api21_protection_group_snapshots_delete_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_protection_group_snapshots(self, references=None, sources=None, **kwargs):
        """
        Returns a list of protection group snapshots, including those pending
        eradication.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
            source_names (list[str], optional):
                Performs the operation on the source name specified. Enter multiple source names
                in comma-separated format. For example, `name01,name02`.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_group_snapshots_api.api21_protection_group_snapshots_get_with_http_info
        _process_references(references, ['names'], kwargs)
        _process_references(sources, ['source_names'], kwargs)
        list_params = ['names', 'sort', 'source_names']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def patch_protection_group_snapshots(self, references=None, **kwargs):
        """
        Destroys a protection group snapshot. To destroy a volume, set `destroyed=true`.
        To recover a volume that has been destroyed and is pending eradication, set
        `destroyed=false`. The `names` parameter is required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            protection_group_snapshot (ProtectionGroupSnapshotPatch, required):
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_group_snapshots_api.api21_protection_group_snapshots_patch_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_protection_group_snapshots(self, sources=None, **kwargs):
        """
        Creates a point-in-time snapshot of the contents of a protection group. The
        `source_ids` or `source_names` parameter is required, but cannot be set
        together.

        Args:
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_names keyword arguments.

        Keyword args:
            apply_retention (bool, optional):
                If `true`, applies the local and remote retention policy to the snapshots.
            source_names (list[str], optional):
                Performs the operation on the source name specified. Enter multiple source names
                in comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_group_snapshots_api.api21_protection_group_snapshots_post_with_http_info
        _process_references(sources, ['source_names'], kwargs)
        list_params = ['source_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_protection_group_snapshots_transfer(self, references=None, sources=None, **kwargs):
        """
        Returns a list of protection group snapshots and their transfer statistics.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
            source_names (list[str], optional):
                Performs the operation on the source name specified. Enter multiple source names
                in comma-separated format. For example, `name01,name02`.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_group_snapshots_api.api21_protection_group_snapshots_transfer_get_with_http_info
        _process_references(references, ['names'], kwargs)
        _process_references(sources, ['source_names'], kwargs)
        list_params = ['names', 'sort', 'source_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_protection_groups(self, references=None, **kwargs):
        """
        Eradicates a protection group that has been destroyed and is pending
        eradication. Eradicated protection groups cannot be recovered. Protection groups
        are destroyed through the PATCH method. The`ids` or `names` parameter is
        required, but cannot be set together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_delete_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_protection_groups(self, references=None, **kwargs):
        """
        Returns a list of protection groups, including their associated source arrays,
        replication targets, hosts, host groups, and volumes. The list includes
        protection groups that were created on the local array to replicate snapshot
        data to other arrays or offload targets, created on a remote array and
        replicated asynchronously to this array, or created inside a pod on a remote
        array and stretched to the local array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_get_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names', 'sort']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_protection_groups_host_groups(self, groups=None, members=None, **kwargs):
        """
        Removes a host group member from a protection group. After the member has been
        removed, it is no longer protected by the group. Any protection group snapshots
        that were taken before the member was removed will not be affected. Removing a
        member from a protection group does not delete the member from the array, and
        the member can be added back to the protection group at any time. The
        `group_names` parameter represents the name of the protection group, and the
        `member_names` parameter represents the name of the host group. The
        `group_names` and `member_names` parameters are required and must be set
        together.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_host_groups_delete_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_protection_groups_host_groups(self, groups=None, members=None, **kwargs):
        """
        Returns a list of protection groups that have host group members.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
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
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_host_groups_get_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names', 'sort']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_protection_groups_host_groups(self, groups=None, members=None, **kwargs):
        """
        Adds a host group member to a protection group. Members that are already in the
        protection group are not affected. For asynchronous replication, only members of
        the same type can belong to a protection group. The `group_names` parameter
        represents the name of the protection group, and the `member_names` parameter
        represents the name of the host group. The `group_names` and `member_names`
        parameters are required and must be set together.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_host_groups_post_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_protection_groups_hosts(self, groups=None, members=None, **kwargs):
        """
        Removes a host member from a protection group. After the member has been
        removed, it is no longer protected by the group. Any protection group snapshots
        that were taken before the member was removed will not be affected. Removing a
        member from a protection group does not delete the member from the array, and
        the member can be added back to the protection group at any time. The
        `group_names` parameter represents the name of the protection group, and the
        `member_names` parameter represents the name of the host. The `group_names` and
        `member_names` parameters are required and must be set together.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_hosts_delete_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_protection_groups_hosts(self, groups=None, members=None, **kwargs):
        """
        Returns a list of protection groups that have host members.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
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
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_hosts_get_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names', 'sort']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_protection_groups_hosts(self, groups=None, members=None, **kwargs):
        """
        Adds a host member to a protection group. Members that are already in the
        protection group are not affected. For asynchronous replication, only members of
        the same type can belong to a protection group. The `group_names` parameter
        represents the name of the protection group, and the `member_names` parameter
        represents the name of the host. The `group_names` and `member_names` parameters
        are required and must be set together.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_hosts_post_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def patch_protection_groups(self, references=None, **kwargs):
        """
        Configures the protection group schedules to generate and replicate snapshots to
        another array or to an external storage system. Also renames or destroys a
        protection group.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            protection_group (ProtectionGroup, required):
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_patch_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_protection_groups_performance_replication_by_array(self, references=None, **kwargs):
        """
        Returns the total number of bytes of replication data transmitted and received
        per second. The data is grouped by protection group and includes the names of
        the source array and targets for each protection group.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_performance_replication_by_array_get_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['sort', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_protection_groups_performance_replication(self, references=None, **kwargs):
        """
        Returns the total number of bytes of replication data transmitted and received
        per second. The data is grouped by protection group.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_performance_replication_get_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['sort', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_protection_groups(self, references=None, sources=None, **kwargs):
        """
        Creates a protection group on the local array for asynchronous replication.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_names keyword arguments.

        Keyword args:
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            source_names (list[str], optional):
                The name of the protection group or protection group snapshot to be copied into
                a new or existing protection group. If the destination protection group and all
                of its volumes already exist, include the `overwrite` parameter to overwrite all
                of the existing volumes with the snapshot contents. If including the `overwrite`
                parameter, the names of the volumes that are being overwritten must match the
                names of the volumes that are being restored. If the source is a protection
                group, the latest snapshot of the protection group will be used as the source
                during the copy operation.
            overwrite (bool, optional):
                If set to `true`, overwrites an existing volume during a volume copy operation.
                If set to `false` or not set at all and the target name is an existing volume,
                the volume copy operation fails. Required if the `source: id` or `source: name`
                body parameter is set and the source overwrites an existing volume during the
                volume copy operation.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_post_with_http_info
        _process_references(references, ['names'], kwargs)
        _process_references(sources, ['source_names'], kwargs)
        list_params = ['names', 'source_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_protection_groups_space(self, references=None, **kwargs):
        """
        Returns provisioned (virtual) size and physical storage consumption data for
        each protection group.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_space_get_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_protection_groups_targets(self, groups=None, members=None, **kwargs):
        """
        Removes an array or offload target from a protection group. The `group_names`
        parameter represents the name of the protection group. The `member_names`
        parameter represents the name of the array or offload target that is being
        removed from the protection group. The `group_names` and `member_names`
        parameters are required and must be set together.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_targets_delete_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_protection_groups_targets(self, groups=None, members=None, **kwargs):
        """
        Returns a list of protection groups that have target arrays or offload targets.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
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
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_targets_get_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names', 'sort']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def patch_protection_groups_targets(self, groups=None, members=None, **kwargs):
        """
        Allows the source array to replicate protection group data to the target array,
        or disallows the source array from replicating protection group data to the
        target array. The `allowed` parameter must be set from the target array. The
        `group_names` parameter represents the name of the protection group. The
        `allowed` and `group_names` parameters are required and must be set together.
        Offload targets do not support the `allowed` parameter.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            target (TargetProtectionGroupPostPatch, required):
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_targets_patch_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_protection_groups_targets(self, groups=None, members=None, **kwargs):
        """
        Adds an array or offload target to a protection group. The `group_names`
        parameter represents the name of the protection group. The `member_names`
        parameter represents the name of the array or offload target that is being added
        to the protection group. The `group_names` and `member_names` parameters are
        required and must be set together.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_targets_post_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_protection_groups_volumes(self, groups=None, members=None, **kwargs):
        """
        Removes a volume member from a protection group. After the member has been
        removed, it is no longer protected by the group. Any protection group snapshots
        that were taken before the member was removed will not be affected. Removing a
        member from a protection group does not delete the member from the array, and
        the member can be added back to the protection group at any time. The
        `group_names` parameter represents the name of the protection group, and the
        `member_names` parameter represents the name of the volume. The `group_names`
        and `member_names` parameters are required and must be set together.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_volumes_delete_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_protection_groups_volumes(self, groups=None, members=None, **kwargs):
        """
        Returns a list of protection groups that have volume members.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
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
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_volumes_get_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names', 'sort']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_protection_groups_volumes(self, groups=None, members=None, **kwargs):
        """
        Adds a volume member to a protection group. Members that are already in the
        protection group are not affected. For asynchronous replication, only members of
        the same type can belong to a protection group. The `group_names` parameter
        represents the name of the protection group, and the `member_names` parameter
        represents the name of the volume. The `group_names` and `member_names`
        parameters are required and must be set together.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._protection_groups_api.api21_protection_groups_volumes_post_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_remote_pods(self, references=None, **kwargs):
        """
        Returns a list of pods that that are on connected arrays but not stretched to
        this array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
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
            on (list[str], optional):
                Performs the operation on the target name specified. Enter multiple target names
                in comma-separated format. For example, `targetName01,targetName02`.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._remote_pods_api.api21_remote_pods_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'on', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_remote_protection_group_snapshots(self, references=None, **kwargs):
        """
        Eradicates a remote protection group snapshot that has been destroyed and is
        pending eradication. Eradicated remote protection group snapshots cannot be
        recovered. Remote protection group snapshots are destroyed through the `PATCH`
        method. The `names` parameter represents the name of the protection group
        snapshot. The `on` parameter represents the name of the offload target. The
        `names` and `on` parameters are required and must be used together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            on (str, optional):
                Performs the operation on the target name specified. For example,
                `targetName01`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._remote_protection_group_snapshots_api.api21_remote_protection_group_snapshots_delete_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_remote_protection_group_snapshots(self, references=None, sources=None, **kwargs):
        """
        Returns a list of remote protection group snapshots.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
            on (list[str], optional):
                Performs the operation on the target name specified. Enter multiple target names
                in comma-separated format. For example, `targetName01,targetName02`.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            source_names (list[str], optional):
                Performs the operation on the source name specified. Enter multiple source names
                in comma-separated format. For example, `name01,name02`.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._remote_protection_group_snapshots_api.api21_remote_protection_group_snapshots_get_with_http_info
        _process_references(references, ['names'], kwargs)
        _process_references(sources, ['source_names'], kwargs)
        list_params = ['names', 'on', 'sort', 'source_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def patch_remote_protection_group_snapshots(self, references=None, **kwargs):
        """
        Destroys a remote protection group snapshot from the offload target. The `on`
        parameter represents the name of the offload target. The `ids` or `names`
        parameter and the `on` parameter are required and must be used together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            remote_protection_group_snapshot (DestroyedPatchPost, required):
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            on (str, optional):
                Performs the operation on the target name specified. For example,
                `targetName01`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._remote_protection_group_snapshots_api.api21_remote_protection_group_snapshots_patch_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_remote_protection_group_snapshots_transfer(self, sources=None, references=None, **kwargs):
        """
        Returns a list of remote protection groups and their transfer statistics.

        Args:
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_names keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            on (list[str], optional):
                Performs the operation on the target name specified. Enter multiple target names
                in comma-separated format. For example, `targetName01,targetName02`.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            source_names (list[str], optional):
                Performs the operation on the source name specified. Enter multiple source names
                in comma-separated format. For example, `name01,name02`.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._remote_protection_group_snapshots_api.api21_remote_protection_group_snapshots_transfer_get_with_http_info
        _process_references(sources, ['source_names'], kwargs)
        _process_references(references, ['names'], kwargs)
        list_params = ['on', 'sort', 'source_names', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_remote_protection_groups(self, references=None, **kwargs):
        """
        Eradicates a remote protection group that has been destroyed and is pending
        eradication. Eradicated remote protection groups cannot be recovered. Remote
        protection groups are destroyed through the `PATCH` method. The `on` parameter
        represents the name of the offload target. The `ids` or `names` parameter and
        the `on` parameter are required and must be used together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            on (str, optional):
                Performs the operation on the target name specified. For example,
                `targetName01`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._remote_protection_groups_api.api21_remote_protection_groups_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_remote_protection_groups(self, references=None, **kwargs):
        """
        Returns a list of remote protection groups.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
            on (list[str], optional):
                Performs the operation on the target name specified. Enter multiple target names
                in comma-separated format. For example, `targetName01,targetName02`.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._remote_protection_groups_api.api21_remote_protection_groups_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'on', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def patch_remote_protection_groups(self, references=None, **kwargs):
        """
        Configures the snapshot retention schedule of a remote protection group. Also
        destroys a remote protection group from the offload target. Before the remote
        protection group can be destroyed, the offload target must first be removed from
        the protection group via the source array. The `on` parameter represents the
        name of the offload target. The `ids` or `names` parameter and the `on`
        parameter are required and must be used together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            remote_protection_group (RemoteProtectionGroup, required):
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            on (str, optional):
                Performs the operation on the target name specified. For example,
                `targetName01`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._remote_protection_groups_api.api21_remote_protection_groups_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_remote_volume_snapshots(self, references=None, sources=None, **kwargs):
        """
        Returns a list of remote volume snapshots.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_ids and source_names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
            on (list[str], optional):
                Performs the operation on the target name specified. Enter multiple target names
                in comma-separated format. For example, `targetName01,targetName02`.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._remote_volume_snapshots_api.api21_remote_volume_snapshots_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        list_params = ['ids', 'names', 'on', 'sort', 'source_ids', 'source_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_remote_volume_snapshots_transfer(self, references=None, sources=None, **kwargs):
        """
        Returns a list of remote volume snapshots and their transfer statistics.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_ids and source_names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
            on (list[str], optional):
                Performs the operation on the target name specified. Enter multiple target names
                in comma-separated format. For example, `targetName01,targetName02`.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._remote_volume_snapshots_api.api21_remote_volume_snapshots_transfer_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        list_params = ['ids', 'on', 'sort', 'source_ids', 'source_names', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_volume_groups(self, references=None, **kwargs):
        """
        Eradicates a volume group that has been destroyed and is pending eradication.
        Eradicated volume groups cannot be recovered. Volume groups are destroyed
        through the `PATCH` method. The `ids` or `names` parameter is required, but
        cannot be set together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volume_groups_api.api21_volume_groups_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_volume_groups(self, references=None, **kwargs):
        """
        Returns a list of volume groups, including those pending eradication.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volume_groups_api.api21_volume_groups_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def patch_volume_groups(self, references=None, **kwargs):
        """
        Renames, destroys, or sets the QoS limits for the To rename a volume group, set
        `name` to the new name. To destroy a volume group, set `destroyed=true`. To
        recover a volume group that has been destroyed and is pending eradication, set
        `destroyed=false`. Sets the bandwidth and IOPs limits of a volume group through
        the respective `bandwidth_limit` and `iops_limit` parameter. The `ids` or
        `names` parameter is required, but cannot be set together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            volume_group (VolumeGroup, required):
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volume_groups_api.api21_volume_groups_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_volume_groups_performance(self, references=None, **kwargs):
        """
        Returns real-time and historical performance data, real-time latency data, and
        average I/O sizes for each volume group and and as a total of all volume groups
        across the entire array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volume_groups_api.api21_volume_groups_performance_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_volume_groups(self, references=None, **kwargs):
        """
        Creates a volume group. The volume group itself does not contain any meaningful
        content; instead, it acts as a container that is used to organize volumes. Once
        a volume group has been created, volumes can be created inside the volume group
        or moved into and out of the volume group.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            volume_group (VolumeGroupPost, required):
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volume_groups_api.api21_volume_groups_post_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_volume_groups_space(self, references=None, **kwargs):
        """
        Returns the provisioned (virtual) size and physical storage consumption data for
        each volume group.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volume_groups_api.api21_volume_groups_space_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'sort', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_volume_groups_volumes(self, groups=None, members=None, **kwargs):
        """
        Returns a list of volume groups that contain volumes.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_ids and group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            group_ids (list[str], optional):
                A list of group IDs.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volume_groups_api.api21_volume_groups_volumes_get_with_http_info
        _process_references(groups, ['group_ids', 'group_names'], kwargs)
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        list_params = ['group_ids', 'member_ids', 'sort', 'group_names', 'member_names']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_volume_snapshots(self, references=None, **kwargs):
        """
        Eradicate a volume snapshot that has been destroyed and is pending eradication.
        Eradicated volumes snapshots cannot be recovered. Volume snapshots are destroyed
        through the `PATCH` method. The `ids` or `names` parameter is required, but
        cannot be set together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volume_snapshots_api.api21_volume_snapshots_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_volume_snapshots(self, references=None, sources=None, **kwargs):
        """
        Return a list of volume snapshots, including those pending eradication.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_ids and source_names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volume_snapshots_api.api21_volume_snapshots_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        list_params = ['ids', 'names', 'sort', 'source_ids', 'source_names']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def patch_volume_snapshots(self, references=None, **kwargs):
        """
        Rename, destroy, or recover a volume snapshot. To rename the suffix of a volume
        snapshot, set `name` to the new suffix name. To recover a volume snapshot that
        has been destroyed and is pending eradication, set `destroyed=true`. The `ids`
        or `names` parameter is required, but cannot be set together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            volume_snapshot (VolumeSnapshotPatch, required):
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volume_snapshots_api.api21_volume_snapshots_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_volume_snapshots(self, sources=None, **kwargs):
        """
        Create a point-in-time snapshot of the contents of a volume. The `source_ids` or
        `source_names` parameter is required, but cannot be set together.

        Args:
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_ids and source_names keyword arguments.

        Keyword args:
            volume_snapshot (VolumeSnapshotPost, required):
            on (str, optional):
                Performs the operation on the target name specified. For example,
                `targetName01`.
            source_ids (list[str], optional):
                Performs the operation on the source ID specified. Enter multiple source IDs in
                comma-separated format.
            source_names (list[str], optional):
                Performs the operation on the source name specified. Enter multiple source names
                in comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volume_snapshots_api.api21_volume_snapshots_post_with_http_info
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        list_params = ['source_ids', 'source_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_volume_snapshots_transfer(self, references=None, sources=None, **kwargs):
        """
        Returns a list of volume snapshots and their transfer statistics.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_ids and source_names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volume_snapshots_api.api21_volume_snapshots_transfer_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        list_params = ['ids', 'sort', 'source_ids', 'source_names', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_volumes(self, references=None, **kwargs):
        """
        Eradicates a volume that has been destroyed and is pending eradication.
        Eradicated volumes cannot be recovered. Volumes are destroyed through the
        `PATCH` method. The `ids` or `names` parameter is required, but cannot be set
        together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            ids (list[str], optional):
                Performs the operation on the unique resource IDs specified. Enter multiple
                resource IDs in comma-separated format. The `ids` and `names` parameters cannot
                be provided together.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volumes_api.api21_volumes_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_volumes(self, references=None, **kwargs):
        """
        Returns a list of volumes, including those pending eradication.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volumes_api.api21_volumes_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def patch_volumes(self, references=None, **kwargs):
        """
        Renames, destroys, or resizes a volume. To rename a volume, set `name` to the
        new name. To destroy a volume, set `destroyed=true`. To recover a volume that
        has been destroyed and is pending eradication, set `destroyed=false`. Sets the
        bandwidth and IOPs limits of a volume through the respective `bandwidth_limit`
        and `iops_limit` parameter. Moves the volume into a pod or volume group through
        the respective `pod` or `volume_group` parameter. The `ids` or `names` parameter
        is required, but cannot be set together.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            volume (VolumePatch, required):
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

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volumes_api.api21_volumes_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_volumes_performance_by_array(self, references=None, **kwargs):
        """
        Return real-time and historical performance data, real-time latency data, and
        average I/O size data. The data returned is for each volume on the current array
        and for each volume on any remote arrays that are visible to the current array.
        The data is grouped by individual volumes and as a total across all volumes on
        each array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volumes_api.api21_volumes_performance_by_array_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_volumes_performance(self, references=None, **kwargs):
        """
        Returns real-time and historical performance data, real-time latency data, and
        average I/O sizes for each volume and and as a total of all volumes across the
        entire array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volumes_api.api21_volumes_performance_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'names', 'sort']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_volumes(self, references=None, **kwargs):
        """
        Creates one or more virtual storage volumes of the specified size. If
        `provisioned` is not specified, the size of the new volume defaults to 1 MB in
        size. The `names` query parameter is required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

        Keyword args:
            volume (VolumePost, required):
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
            overwrite (bool, optional):
                If set to `true`, overwrites an existing volume during a volume copy operation.
                If set to `false` or not set at all and the target name is an existing volume,
                the volume copy operation fails. Required if the `source: id` or `source: name`
                body parameter is set and the source overwrites an existing volume during the
                volume copy operation.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volumes_api.api21_volumes_post_with_http_info
        _process_references(references, ['names'], kwargs)
        list_params = ['names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def delete_volumes_protection_groups(self, groups=None, members=None, **kwargs):
        """
        Removes a volume member from a protection group. After the member has been
        removed, it is no longer protected by the group. Any protection group snapshots
        that were taken before the member was removed will not be affected. Removing a
        member from a protection group does not delete the member from the array, and
        the member can be added back to the protection group at any time. The
        `group_names` parameter represents the name of the protection group, and the
        `member_names` parameter represents the name of the volume. The `group_names`
        and `member_names` parameters are required and must be set together.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volumes_api.api21_volumes_protection_groups_delete_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_volumes_protection_groups(self, groups=None, members=None, **kwargs):
        """
        Returns a list of volume members that belong to one or more protection groups.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
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
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volumes_api.api21_volumes_protection_groups_get_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names', 'sort']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def post_volumes_protection_groups(self, groups=None, members=None, **kwargs):
        """
        Adds a volume member to a protection group. Members that are already in the
        protection group are not affected. For asynchronous replication, only members of
        the same type can belong to a protection group. The `group_names` parameter
        represents the name of the protection group, and the `member_names` parameter
        represents the name of the volume. The `group_names` and `member_names`
        parameters are required and must be set together.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_names keyword arguments.

        Keyword args:
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volumes_api.api21_volumes_protection_groups_post_with_http_info
        _process_references(groups, ['group_names'], kwargs)
        _process_references(members, ['member_names'], kwargs)
        list_params = ['group_names', 'member_names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_volumes_space(self, references=None, **kwargs):
        """
        Returns the provisioned (virtual) size and physical storage consumption data for
        each volume.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

        Keyword args:
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. For
                destroyed objects, the time remaining is displayed in seconds.
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
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            total_only (bool, optional):
                If set to `true`, returns the aggregate value of all items after filtering.
                Where it makes more sense, the average value is displayed instead. The values
                are displayed for each name where meaningful. If `total_only=true`, the `items`
                list will be empty.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volumes_api.api21_volumes_space_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        list_params = ['ids', 'sort', 'names']
        quoted_params = []
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

    def get_volumes_volume_groups(self, groups=None, members=None, **kwargs):
        """
        Returns a list of volumes that are in a volume group.

        Args:
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_ids and group_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.

        Keyword args:
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            group_ids (list[str], optional):
                A list of group IDs.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs.
            offset (int, optional):
                The starting position based on the results of the query in relation to the full
                set of response objects returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_item_count (bool, optional):
                If set to `true`, the `total_item_count` matching the specified query parameters
                will be calculated and returned in the response. If set to `false`, the
                `total_item_count` will be `null` in the response. This may speed up queries
                where the `total_item_count` is large. If not specified, defaults to `false`.
            group_names (list[str], optional):
                Performs the operation on the unique group name specified. Examples of groups
                include host groups, pods, protection groups, and volume groups. Enter multiple
                names in comma-separated format. For example, `hgroup01,hgroup02`.
            member_names (list[str], optional):
                Performs the operation on the unique member name specified. Examples of members
                include volumes, hosts, and host groups. Enter multiple names in comma-separated
                format. For example, `vol01,vol02`.

        Returns:
            ValidResponse: If the call was successful.
            ErrorResponse: If the call was not successful.

        Raises:
            PureError: If calling the API fails.
            ValueError: If a parameter is of an invalid type.
            TypeError: If invalid or missing parameters are used.
        """
        endpoint = self._volumes_api.api21_volumes_volume_groups_get_with_http_info
        _process_references(groups, ['group_ids', 'group_names'], kwargs)
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        list_params = ['group_ids', 'member_ids', 'sort', 'group_names', 'member_names']
        quoted_params = ['continuation_token']
        _process_kwargs(kwargs, list_params, quoted_params)
        return self._call_api(endpoint, kwargs)

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
