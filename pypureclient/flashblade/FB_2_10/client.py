import json
import platform
import ssl
import time
import urllib3
import six
from typing import List, Optional

from ...exceptions import PureError
from ...keywords import Headers, Responses
from ...responses import ValidResponse, ErrorResponse, ApiError, ItemIterator
from ...token_manager import TokenManager
from ...api_token_manager import APITokenManager
from ...client_settings import USER_AGENT_TEMPLATE, resolve_ssl_validation
from .api_client import ApiClient
from .rest import ApiException
from .configuration import Configuration
from . import api
from . import models

class _FBApiClient(ApiClient):
    """ Flashblade version of API client that strips attributes with
    value None while sanitizing object arguments."""
    def extract_object_dict_from_object(self, obj):
        """Convert model obj to dict, using `swagger_types`
        and use `attribute_map` to determine json keys.
        Attributes that are unset or with value 'None' are filtered out."""
        obj_dict = {obj.attribute_map[attr]: getattr(obj, attr)
                     for attr, _ in six.iteritems(obj.swagger_types)
                     if getattr(obj, attr) is not None}
        return obj_dict


class Client(object):
    DEFAULT_TIMEOUT = 15.0
    DEFAULT_RETRIES = 5
    # Format: client/client_version/endpoint/endpoint_version/system/release
    USER_AGENT = USER_AGENT_TEMPLATE.format(prod='FB', rest_version='2.10', sys=platform.system(), rel=platform.release())

    def __init__(self, target, id_token=None, private_key_file=None, private_key_password=None,
                 username=None, client_id=None, key_id=None, issuer=None, api_token=None,
                 retries=DEFAULT_RETRIES, timeout=DEFAULT_TIMEOUT, ssl_cert=None, user_agent=None,
                 verify_ssl=None):
        """
        Initialize a FlashBlade Client. id_token is generated based on app ID and private
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

        self._api_client = _FBApiClient(configuration=config)
        self._api_client.user_agent = effective_user_agent
        self._set_agent_header()
        self._set_auth_header()
        self.models = models

        # Read timeout and retries
        self._retries = retries
        self._timeout = timeout

        # Instantiate APIs
        self._active_directory_api = api.ActiveDirectoryApi(self._api_client)
        self._administrators_api = api.AdministratorsApi(self._api_client)
        self._alert_watchers_api = api.AlertWatchersApi(self._api_client)
        self._alerts_api = api.AlertsApi(self._api_client)
        self._api_clients_api = api.APIClientsApi(self._api_client)
        self._array_connections_api = api.ArrayConnectionsApi(self._api_client)
        self._arrays_api = api.ArraysApi(self._api_client)
        self._audits_api = api.AuditsApi(self._api_client)
        self._blades_api = api.BladesApi(self._api_client)
        self._bucket_replica_links_api = api.BucketReplicaLinksApi(self._api_client)
        self._buckets_api = api.BucketsApi(self._api_client)
        self._certificate_groups_api = api.CertificateGroupsApi(self._api_client)
        self._certificates_api = api.CertificatesApi(self._api_client)
        self._clients_api = api.ClientsApi(self._api_client)
        self._directory_services_api = api.DirectoryServicesApi(self._api_client)
        self._dns_api = api.DNSApi(self._api_client)
        self._drives_api = api.DrivesApi(self._api_client)
        self._file_system_replica_links_api = api.FileSystemReplicaLinksApi(self._api_client)
        self._file_system_snapshots_api = api.FileSystemSnapshotsApi(self._api_client)
        self._file_systems_api = api.FileSystemsApi(self._api_client)
        self._hardware_api = api.HardwareApi(self._api_client)
        self._hardware_connectors_api = api.HardwareConnectorsApi(self._api_client)
        self._keytabs_api = api.KeytabsApi(self._api_client)
        self._kmip_api = api.KMIPApi(self._api_client)
        self._lifecycle_rules_api = api.LifecycleRulesApi(self._api_client)
        self._link_aggregation_groups_api = api.LinkAggregationGroupsApi(self._api_client)
        self._logs_api = api.LogsApi(self._api_client)
        self._network_interfaces_api = api.NetworkInterfacesApi(self._api_client)
        self._object_store_access_keys_api = api.ObjectStoreAccessKeysApi(self._api_client)
        self._object_store_accounts_api = api.ObjectStoreAccountsApi(self._api_client)
        self._object_store_remote_credentials_api = api.ObjectStoreRemoteCredentialsApi(self._api_client)
        self._object_store_users_api = api.ObjectStoreUsersApi(self._api_client)
        self._object_store_virtual_hosts_api = api.ObjectStoreVirtualHostsApi(self._api_client)
        self._policies___nfs_api = api.PoliciesNFSApi(self._api_client)
        self._policies___object_store_access_api = api.PoliciesObjectStoreAccessApi(self._api_client)
        self._policies___smb_client_api = api.PoliciesSMBClientApi(self._api_client)
        self._policies___smb_share_api = api.PoliciesSMBShareApi(self._api_client)
        self._policies___snapshot_api = api.PoliciesSnapshotApi(self._api_client)
        self._policies__all_api = api.PoliciesAllApi(self._api_client)
        self._quotas_api = api.QuotasApi(self._api_client)
        self._rdl_api = api.RDLApi(self._api_client)
        self._roles_api = api.RolesApi(self._api_client)
        self._sessions_api = api.SessionsApi(self._api_client)
        self._smtp_api = api.SMTPApi(self._api_client)
        self._snmp_agents_api = api.SNMPAgentsApi(self._api_client)
        self._snmp_managers_api = api.SNMPManagersApi(self._api_client)
        self._subnets_api = api.SubnetsApi(self._api_client)
        self._support_api = api.SupportApi(self._api_client)
        self._syslog_api = api.SyslogApi(self._api_client)
        self._targets_api = api.TargetsApi(self._api_client)
        self._usage_api = api.UsageApi(self._api_client)
        self._verification_keys_api = api.VerificationKeysApi(self._api_client)
        self._authorization_api = api.AuthorizationApi(self._api_client)

    def __del__(self):
        # Cleanup this REST API client resources
        if self._api_client:
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

    def disable_verify_ssl(self):
        """ Change our certificate requirements so that a certificate is not validated. """
        self._api_client.rest_client.pool_manager.connection_pool_kw['cert_reqs'] = ssl.CERT_NONE

    def enable_verify_ssl(self, ca_certs_file_path=None):
        """ Change our certificate requirements so that a certificate is required and validated.
        Optionally, if a CA certificate(s) file path is provided, configure the client to use
        that CA certificate file.
        """
        if ca_certs_file_path:
            self.configure_ca_certificate_file(ca_certs_file_path)
        self._api_client.rest_client.pool_manager.connection_pool_kw['cert_reqs'] = ssl.CERT_REQUIRED

    def configure_ca_certificate_file(self, ca_certs_file_path):
        """"
        :param ca_certs_file_path: The path to the CA certificate(s) file to use.
        :return:
        """
        self._api_client.rest_client.pool_manager.connection_pool_kw['ca_certs'] = ca_certs_file_path

    def delete_active_directory(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        local_only=None,  # type: bool
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete an Active Directory account.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            local_only (bool, optional):
                If specified as `true`, only delete the Active Directory configuration on the
                local array, without deleting the computer account created in the Active
                Directory domain. If not specified, defaults to `false`.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            local_only=local_only,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._active_directory_api.api210_active_directory_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_active_directory(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.ActiveDirectoryGetResponse
        """
        List an Active Directory account and its configuration.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._active_directory_api.api210_active_directory_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_active_directory(
        self,
        references=None,  # type: List[models.ReferenceType]
        active_directory=None,  # type: models.ActiveDirectoryPatch
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ActiveDirectoryResponse
        """
        Modify the configuration of an Active Directory account.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            active_directory (ActiveDirectoryPatch, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            active_directory=active_directory,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._active_directory_api.api210_active_directory_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_active_directory(
        self,
        references=None,  # type: List[models.ReferenceType]
        active_directory=None,  # type: models.ActiveDirectoryPost
        names=None,  # type: List[str]
        join_existing_account=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ActiveDirectoryResponse
        """
        Join an Active Directory domain and generate keytabs for the registered SPNs and
        supported encryption types.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            active_directory (ActiveDirectoryPost, required):
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            join_existing_account (bool, optional):
                If specified as `true`, the domain is searched for a pre-existing computer
                account to join to, and no new account will be created within the domain. The
                `user` specified when joining to a pre-existing account must have permissions to
                'read attributes from' and 'reset the password of' the pre-existing account.
                `service_principal_names`, `encryption_types`, and `join_ou` will be read from
                the pre-existing account and cannot be specified when joining to an existing
                account. If not specified, defaults to `false`.
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
            active_directory=active_directory,
            names=names,
            join_existing_account=join_existing_account,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._active_directory_api.api210_active_directory_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_active_directory_test(
        self,
        references=None,  # type: List[models.ReferenceType]
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.TestResultGetResponse
        """
        Testing if the configuration of an Active Directory account is valid.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._active_directory_api.api210_active_directory_test_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_admins_api_tokens(
        self,
        admins=None,  # type: List[models.ReferenceType]
        admin_ids=None,  # type: List[str]
        admin_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Deletes the API tokens of the specified administrators.

        Args:
            admins (list[FixedReference], optional):
                A list of admins to query for. Overrides admin_ids and admin_names keyword arguments.

            admin_ids (list[str], optional):
                A list of admin IDs. If after filtering, there is not at least one admin
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `admin_names` query parameter.
            admin_names (list[str], optional):
                A list of admin names. If there is not at least one admin resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `admin_ids` query parameter.
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
            admin_ids=admin_ids,
            admin_names=admin_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._administrators_api.api210_admins_api_tokens_delete_with_http_info
        _process_references(admins, ['admin_ids', 'admin_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_admins_api_tokens(
        self,
        admins=None,  # type: List[models.ReferenceType]
        admin_ids=None,  # type: List[str]
        admin_names=None,  # type: List[str]
        continuation_token=None,  # type: str
        expose_api_token=None,  # type: bool
        filter=None,  # type: str
        limit=None,  # type: int
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.AdminApiTokenGetResponse
        """
        Displays API tokens for the specified administrators.

        Args:
            admins (list[FixedReference], optional):
                A list of admins to query for. Overrides admin_ids and admin_names keyword arguments.

            admin_ids (list[str], optional):
                A list of admin IDs. If after filtering, there is not at least one admin
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `admin_names` query parameter.
            admin_names (list[str], optional):
                A list of admin names. If there is not at least one admin resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `admin_ids` query parameter.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            expose_api_token (bool, optional):
                If `true`, exposes the API token of the current user.
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
            admin_ids=admin_ids,
            admin_names=admin_names,
            continuation_token=continuation_token,
            expose_api_token=expose_api_token,
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
        endpoint = self._administrators_api.api210_admins_api_tokens_get_with_http_info
        _process_references(admins, ['admin_ids', 'admin_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_admins_api_tokens(
        self,
        admins=None,  # type: List[models.ReferenceType]
        admin_ids=None,  # type: List[str]
        admin_names=None,  # type: List[str]
        timeout=None,  # type: int
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.AdminApiTokenResponse
        """
        Creates API tokens for the specified administrators.

        Args:
            admins (list[FixedReference], optional):
                A list of admins to query for. Overrides admin_ids and admin_names keyword arguments.

            admin_ids (list[str], optional):
                A list of admin IDs. If after filtering, there is not at least one admin
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `admin_names` query parameter.
            admin_names (list[str], optional):
                A list of admin names. If there is not at least one admin resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `admin_ids` query parameter.
            timeout (int, optional):
                The duration of API token validity, in milliseconds.
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
            admin_ids=admin_ids,
            admin_names=admin_names,
            timeout=timeout,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._administrators_api.api210_admins_api_tokens_post_with_http_info
        _process_references(admins, ['admin_ids', 'admin_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_admins_cache(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete cached administrator role information by name or ID.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._administrators_api.api210_admins_cache_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_admins_cache(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        refresh=None,  # type: bool
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.AdminCacheGetResponse
        """
        List cached administrator information used to determine role based access
        control privileges.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            refresh (bool, optional):
                Whether to refresh the user info from directory service. If not specified,
                defaults to `false`.
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
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            refresh=refresh,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._administrators_api.api210_admins_cache_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_admins(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        expose_api_token=None,  # type: bool
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
        # type: (...) -> models.AdminGetResponse
        """
        List the administrator's attributes, including the API token and public key.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            expose_api_token (bool, optional):
                If `true`, exposes the API token of the current user.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            continuation_token=continuation_token,
            expose_api_token=expose_api_token,
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
        endpoint = self._administrators_api.api210_admins_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_admins(
        self,
        references=None,  # type: List[models.ReferenceType]
        admin=None,  # type: models.AdminPatch
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.AdminResponse
        """
        Modify the attributes of the administrator.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            admin (AdminPatch, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            admin=admin,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._administrators_api.api210_admins_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_admins_settings(
        self,
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
        # type: (...) -> models.AdminSettingsGetResponse
        """
        Return global admin settings.

        Args:

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
        endpoint = self._administrators_api.api210_admins_settings_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def patch_admins_settings(
        self,
        admin_setting=None,  # type: models.AdminSetting
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.AdminSettingsResponse
        """
        Update properties for global admin settings.

        Args:

            admin_setting (AdminSetting, required):
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
            admin_setting=admin_setting,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._administrators_api.api210_admins_settings_patch_with_http_info
        return self._call_api(endpoint, kwargs)

    def delete_alert_watchers(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete an alert watcher.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._alert_watchers_api.api210_alert_watchers_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_alert_watchers(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.AlertWatcherGetResponse
        """
        List alert watchers that are configured to receive alert messages.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._alert_watchers_api.api210_alert_watchers_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_alert_watchers(
        self,
        references=None,  # type: List[models.ReferenceType]
        alert_watcher=None,  # type: models.AlertWatcher
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.AlertWatcherResponse
        """
        Modify an alert watcher’s configuration. Enable or disable an alert watcher
        privilege and select the level of alert notification of an alert watcher. Alert
        notification levels are `info`, `warning`, or `critical`.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            alert_watcher (AlertWatcher, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            alert_watcher=alert_watcher,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._alert_watchers_api.api210_alert_watchers_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_alert_watchers(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        alert_watcher=None,  # type: models.AlertWatcherPost
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.AlertWatcherResponse
        """
        Create an alert watcher to receive array alert messages.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], required):
                A list of resource names.
            alert_watcher (AlertWatcherPost, optional):
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
            names=names,
            alert_watcher=alert_watcher,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._alert_watchers_api.api210_alert_watchers_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_alert_watchers_test(
        self,
        references=None,  # type: List[models.ReferenceType]
        filter=None,  # type: str
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.TestResultResponse
        """
        Test an alert watcher's contact information to verify alerts can be sent and
        received.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            filter=filter,
            ids=ids,
            names=names,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._alert_watchers_api.api210_alert_watchers_test_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_alerts(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.AlertGetResponse
        """
        Returns a list of alerts which have been generated by the array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._alerts_api.api210_alerts_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_alerts(
        self,
        references=None,  # type: List[models.ReferenceType]
        alerts_settings=None,  # type: models.Alert
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.AlertResponse
        """
        Make changes to an alert. This is currently limited to the alert's `flagged`
        property.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            alerts_settings (Alert, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            alerts_settings=alerts_settings,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._alerts_api.api210_alerts_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_api_clients(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete the API client.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._api_clients_api.api210_api_clients_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_api_clients(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.ApiClientsResponse
        """
        List an API client and its configuration attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._api_clients_api.api210_api_clients_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_api_clients(
        self,
        references=None,  # type: List[models.ReferenceType]
        api_clients=None,  # type: models.ApiClient
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ApiClientsResponse
        """
        Modify an API client. Newly created API clients can be enabled by setting the
        `enabled` parameter to `true`.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            api_clients (ApiClient, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            api_clients=api_clients,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._api_clients_api.api210_api_clients_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_api_clients(
        self,
        references=None,  # type: List[models.ReferenceType]
        api_client=None,  # type: models.ApiClientsPost
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ApiClientsResponse
        """
        Create an API client to authorize Access Token or Bearer Tokens for use on the
        array. Required fields include `issuer`, `public_key`, and
        `access_token_ttl_in_ms`. After creating an API client, it can only be enabled
        by an authorized user.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            api_client (ApiClientsPost, required):
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            api_client=api_client,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._api_clients_api.api210_api_clients_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_array_connections_connection_key(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.ArrayConnectionKeyGetResponse
        """
        List connection keys used to authenticate the connection from one array to
        another.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._array_connections_api.api210_array_connections_connection_key_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_array_connections_connection_key(
        self,
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ArrayConnectionKeyResponse
        """
        Create an array connection key allowing one array to connect to another for
        replication.

        Args:

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
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._array_connections_api.api210_array_connections_connection_key_post_with_http_info
        return self._call_api(endpoint, kwargs)

    def delete_array_connections(
        self,
        references=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete a connection to an array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
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
            ids=ids,
            remote_ids=remote_ids,
            remote_names=remote_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._array_connections_api.api210_array_connections_delete_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_array_connections(
        self,
        references=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        offset=None,  # type: int
        remote_ids=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ArrayConnectionGetResponse
        """
        List connected arrays for replication.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
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
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            offset=offset,
            remote_ids=remote_ids,
            remote_names=remote_names,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._array_connections_api.api210_array_connections_get_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_array_connections(
        self,
        references=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        array_connection=None,  # type: models.ArrayConnection
        ids=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ArrayConnectionResponse
        """
        Modify the configuration of a connected array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.

            array_connection (ArrayConnection, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
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
            array_connection=array_connection,
            ids=ids,
            remote_ids=remote_ids,
            remote_names=remote_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._array_connections_api.api210_array_connections_patch_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_array_connections_path(
        self,
        references=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        offset=None,  # type: int
        remote_ids=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ArrayConnectionPathGetResponse
        """
        List network path details of connected arrays.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
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
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            offset=offset,
            remote_ids=remote_ids,
            remote_names=remote_names,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._array_connections_api.api210_array_connections_path_get_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_array_connections_performance_replication(
        self,
        references=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        end_time=None,  # type: int
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        offset=None,  # type: int
        remote_ids=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        resolution=None,  # type: int
        sort=None,  # type: List[str]
        start_time=None,  # type: int
        total_only=None,  # type: bool
        type=None,  # type: str
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ConnectionRelationshipPerformanceReplicationGetResp
        """
        List performance metrics of file systems or objects being replicated from one
        array to another.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            end_time (int, optional):
                When the time window ends (in milliseconds since epoch).
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
            resolution (int, optional):
                The desired ms between samples. Available resolutions may depend on data type,
                `start_time` and `end_time`. In general `1000`, `30000`, `300000`, `1800000`,
                `7200000`, and `86400000` are possible values.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            start_time (int, optional):
                When the time window starts (in milliseconds since epoch).
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
            type (str, optional):
                Display the metric of a specified object type. Valid values are `all`, `file-
                system`, and `object-store`. If not specified, defaults to `all`.
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
            continuation_token=continuation_token,
            end_time=end_time,
            filter=filter,
            ids=ids,
            limit=limit,
            offset=offset,
            remote_ids=remote_ids,
            remote_names=remote_names,
            resolution=resolution,
            sort=sort,
            start_time=start_time,
            total_only=total_only,
            type=type,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._array_connections_api.api210_array_connections_performance_replication_get_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_array_connections(
        self,
        array_connection=None,  # type: models.ArrayConnectionPost
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ArrayConnectionResponse
        """
        Create a connection to an array for replication and configure network settings.

        Args:

            array_connection (ArrayConnectionPost, required):
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
            array_connection=array_connection,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._array_connections_api.api210_array_connections_post_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_arrays_eula(
        self,
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
        # type: (...) -> models.EulaGetResponse
        """
        List the End User Agreement and signature.

        Args:

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
        endpoint = self._arrays_api.api210_arrays_eula_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def patch_arrays_eula(
        self,
        eula=None,  # type: models.Eula
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.EulaResponse
        """
        Modifies the signature on the End User Agreement.

        Args:

            eula (Eula, required):
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
            eula=eula,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._arrays_api.api210_arrays_eula_patch_with_http_info
        return self._call_api(endpoint, kwargs)

    def delete_arrays_factory_reset_token(
        self,
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Deletes any existing token that could be used to perform a factory reset on the
        array.

        Args:

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
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._arrays_api.api210_arrays_factory_reset_token_delete_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_arrays_factory_reset_token(
        self,
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
        # type: (...) -> models.ArrayFactoryResetTokenGetResponse
        """
        Displays a list of tokens used to perform a factory reset on the array.

        Args:

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
        endpoint = self._arrays_api.api210_arrays_factory_reset_token_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def post_arrays_factory_reset_token(
        self,
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ArrayFactoryResetTokenResponse
        """
        Creates a token that can be used to perform a factory reset on the array.
        Factory reset tokens can only be created after the array has been prepared for
        reset (e.g., all file systems, buckets, and snapshots must first be eradicated).
        After a token has been created, operations that would take the array out of the
        prepared state (e.g., creating file systems) are disabled until all tokens have
        been deleted.

        Args:

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
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._arrays_api.api210_arrays_factory_reset_token_post_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_arrays(
        self,
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
        # type: (...) -> models.ArrayGetResponse
        """
        List array attributes such as the array name, ID, version, and NTP servers.

        Args:

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
        endpoint = self._arrays_api.api210_arrays_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_arrays_http_specific_performance(
        self,
        end_time=None,  # type: int
        resolution=None,  # type: int
        start_time=None,  # type: int
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ArrayHttpSpecificPerformanceGet
        """
        List the HTTP performance metrics of the array.

        Args:

            end_time (int, optional):
                When the time window ends (in milliseconds since epoch).
            resolution (int, optional):
                The desired ms between samples. Available resolutions may depend on data type,
                `start_time` and `end_time`. In general `1000`, `30000`, `300000`, `1800000`,
                `7200000`, and `86400000` are possible values.
            start_time (int, optional):
                When the time window starts (in milliseconds since epoch).
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
            end_time=end_time,
            resolution=resolution,
            start_time=start_time,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._arrays_api.api210_arrays_http_specific_performance_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_arrays_nfs_specific_performance(
        self,
        end_time=None,  # type: int
        resolution=None,  # type: int
        start_time=None,  # type: int
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ArrayNfsSpecificPerformanceGet
        """
        List the NFS performance metrics of the array.

        Args:

            end_time (int, optional):
                When the time window ends (in milliseconds since epoch).
            resolution (int, optional):
                The desired ms between samples. Available resolutions may depend on data type,
                `start_time` and `end_time`. In general `1000`, `30000`, `300000`, `1800000`,
                `7200000`, and `86400000` are possible values.
            start_time (int, optional):
                When the time window starts (in milliseconds since epoch).
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
            end_time=end_time,
            resolution=resolution,
            start_time=start_time,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._arrays_api.api210_arrays_nfs_specific_performance_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def patch_arrays(
        self,
        array=None,  # type: list
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ArrayResponse
        """
        Modify the general configuration of the array including banner text, array name,
        NTP servers, and time zone.

        Args:

            array (Array, required):
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
            array=array,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._arrays_api.api210_arrays_patch_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_arrays_performance(
        self,
        end_time=None,  # type: int
        protocol=None,  # type: str
        resolution=None,  # type: int
        start_time=None,  # type: int
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ArrayPerformanceGetResponse
        """
        Lists the overall performance metrics of the array.

        Args:

            end_time (int, optional):
                When the time window ends (in milliseconds since epoch).
            protocol (str, optional):
                Display the performance of a specified protocol. Valid values are `all`, `HTTP`,
                `SMB`, `NFS`, and `S3`. If not specified, defaults to `all`, which will provide
                the combined performance of all available protocols.
            resolution (int, optional):
                The desired ms between samples. Available resolutions may depend on data type,
                `start_time` and `end_time`. In general `1000`, `30000`, `300000`, `1800000`,
                `7200000`, and `86400000` are possible values.
            start_time (int, optional):
                When the time window starts (in milliseconds since epoch).
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
            end_time=end_time,
            protocol=protocol,
            resolution=resolution,
            start_time=start_time,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._arrays_api.api210_arrays_performance_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_arrays_performance_replication(
        self,
        end_time=None,  # type: int
        resolution=None,  # type: int
        start_time=None,  # type: int
        type=None,  # type: str
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ArrayPerformanceReplicationGetResp
        """
        List replication performance metrics.

        Args:

            end_time (int, optional):
                When the time window ends (in milliseconds since epoch).
            resolution (int, optional):
                The desired ms between samples. Available resolutions may depend on data type,
                `start_time` and `end_time`. In general `1000`, `30000`, `300000`, `1800000`,
                `7200000`, and `86400000` are possible values.
            start_time (int, optional):
                When the time window starts (in milliseconds since epoch).
            type (str, optional):
                Display the metric of a specified object type. Valid values are `all`, `file-
                system`, and `object-store`. If not specified, defaults to `all`.
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
            end_time=end_time,
            resolution=resolution,
            start_time=start_time,
            type=type,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._arrays_api.api210_arrays_performance_replication_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_arrays_s3_specific_performance(
        self,
        end_time=None,  # type: int
        resolution=None,  # type: int
        start_time=None,  # type: int
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ArrayS3SpecificPerformanceGetResp
        """
        List the S3 performance metrics of the array.

        Args:

            end_time (int, optional):
                When the time window ends (in milliseconds since epoch).
            resolution (int, optional):
                The desired ms between samples. Available resolutions may depend on data type,
                `start_time` and `end_time`. In general `1000`, `30000`, `300000`, `1800000`,
                `7200000`, and `86400000` are possible values.
            start_time (int, optional):
                When the time window starts (in milliseconds since epoch).
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
            end_time=end_time,
            resolution=resolution,
            start_time=start_time,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._arrays_api.api210_arrays_s3_specific_performance_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_arrays_space(
        self,
        end_time=None,  # type: int
        resolution=None,  # type: int
        start_time=None,  # type: int
        type=None,  # type: str
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ArraySpaceGetResponse
        """
        List available and used storage space on the array.

        Args:

            end_time (int, optional):
                When the time window ends (in milliseconds since epoch).
            resolution (int, optional):
                The desired ms between samples. Available resolutions may depend on data type,
                `start_time` and `end_time`. In general `1000`, `30000`, `300000`, `1800000`,
                `7200000`, and `86400000` are possible values.
            start_time (int, optional):
                When the time window starts (in milliseconds since epoch).
            type (str, optional):
                Display the metric of a specified object type. Valid values are `array`, `file-
                system`, and `object-store`. If not specified, defaults to `array`.
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
            end_time=end_time,
            resolution=resolution,
            start_time=start_time,
            type=type,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._arrays_api.api210_arrays_space_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_arrays_supported_time_zones(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ArraysSupportedTimeZonesGetResponse
        """
        List supported time zones for the array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            continuation_token=continuation_token,
            filter=filter,
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
        endpoint = self._arrays_api.api210_arrays_supported_time_zones_get_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_audits(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.AuditGetResponse
        """
        List the array audit trail to view activities that were performed on the array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._audits_api.api210_audits_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_blades(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.BladeGetResponse
        """
        List array blade information.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
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
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._blades_api.api210_blades_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_bucket_replica_links(
        self,
        references=None,  # type: List[models.ReferenceType]
        local_buckets=None,  # type: List[models.ReferenceType]
        remote_buckets=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        local_bucket_ids=None,  # type: List[str]
        local_bucket_names=None,  # type: List[str]
        remote_bucket_names=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete a bucket replica link.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            local_buckets (list[FixedReference], optional):
                A list of local_buckets to query for. Overrides local_bucket_ids and local_bucket_names keyword arguments.
            remote_buckets (list[FixedReference], optional):
                A list of remote_buckets to query for. Overrides remote_bucket_names keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            local_bucket_ids (list[str], optional):
                A list of local bucket IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `local_bucket_names` query parameter.
            local_bucket_names (list[str], optional):
                A list of local bucket names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `local_bucket_ids` query parameter.
            remote_bucket_names (list[str], optional):
                A list of remote bucket names. If there is not at least one resource that
                matches each of the elements, then an error is returned.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
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
            ids=ids,
            local_bucket_ids=local_bucket_ids,
            local_bucket_names=local_bucket_names,
            remote_bucket_names=remote_bucket_names,
            remote_ids=remote_ids,
            remote_names=remote_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._bucket_replica_links_api.api210_bucket_replica_links_delete_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(local_buckets, ['local_bucket_ids', 'local_bucket_names'], kwargs)
        _process_references(remote_buckets, ['remote_bucket_names'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_bucket_replica_links(
        self,
        references=None,  # type: List[models.ReferenceType]
        local_buckets=None,  # type: List[models.ReferenceType]
        remote_buckets=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        local_bucket_ids=None,  # type: List[str]
        local_bucket_names=None,  # type: List[str]
        offset=None,  # type: int
        remote_bucket_names=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.BucketReplicaLinkGetResponse
        """
        List bucket replica links for object replication.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            local_buckets (list[FixedReference], optional):
                A list of local_buckets to query for. Overrides local_bucket_ids and local_bucket_names keyword arguments.
            remote_buckets (list[FixedReference], optional):
                A list of remote_buckets to query for. Overrides remote_bucket_names keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            local_bucket_ids (list[str], optional):
                A list of local bucket IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `local_bucket_names` query parameter.
            local_bucket_names (list[str], optional):
                A list of local bucket names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `local_bucket_ids` query parameter.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            remote_bucket_names (list[str], optional):
                A list of remote bucket names. If there is not at least one resource that
                matches each of the elements, then an error is returned.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
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
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            local_bucket_ids=local_bucket_ids,
            local_bucket_names=local_bucket_names,
            offset=offset,
            remote_bucket_names=remote_bucket_names,
            remote_ids=remote_ids,
            remote_names=remote_names,
            sort=sort,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._bucket_replica_links_api.api210_bucket_replica_links_get_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(local_buckets, ['local_bucket_ids', 'local_bucket_names'], kwargs)
        _process_references(remote_buckets, ['remote_bucket_names'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_bucket_replica_links(
        self,
        references=None,  # type: List[models.ReferenceType]
        local_buckets=None,  # type: List[models.ReferenceType]
        remote_buckets=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        bucket_replica_link=None,  # type: models.BucketReplicaLink
        ids=None,  # type: List[str]
        local_bucket_ids=None,  # type: List[str]
        local_bucket_names=None,  # type: List[str]
        remote_bucket_names=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.BucketReplicaLinkResponse
        """
        Modify the configuration of a bucket replica link including whether the link is
        paused and the object store remote credentials used.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            local_buckets (list[FixedReference], optional):
                A list of local_buckets to query for. Overrides local_bucket_ids and local_bucket_names keyword arguments.
            remote_buckets (list[FixedReference], optional):
                A list of remote_buckets to query for. Overrides remote_bucket_names keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.

            bucket_replica_link (BucketReplicaLink, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            local_bucket_ids (list[str], optional):
                A list of local bucket IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `local_bucket_names` query parameter.
            local_bucket_names (list[str], optional):
                A list of local bucket names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `local_bucket_ids` query parameter.
            remote_bucket_names (list[str], optional):
                A list of remote bucket names. If there is not at least one resource that
                matches each of the elements, then an error is returned.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
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
            bucket_replica_link=bucket_replica_link,
            ids=ids,
            local_bucket_ids=local_bucket_ids,
            local_bucket_names=local_bucket_names,
            remote_bucket_names=remote_bucket_names,
            remote_ids=remote_ids,
            remote_names=remote_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._bucket_replica_links_api.api210_bucket_replica_links_patch_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(local_buckets, ['local_bucket_ids', 'local_bucket_names'], kwargs)
        _process_references(remote_buckets, ['remote_bucket_names'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_bucket_replica_links(
        self,
        local_buckets=None,  # type: List[models.ReferenceType]
        remote_buckets=None,  # type: List[models.ReferenceType]
        remote_credential=None,  # type: List[models.ReferenceType]
        bucket_replica_link=None,  # type: models.BucketReplicaLinkPost
        local_bucket_names=None,  # type: List[str]
        local_bucket_ids=None,  # type: List[str]
        remote_bucket_names=None,  # type: List[str]
        remote_credentials_names=None,  # type: List[str]
        remote_credentials_ids=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.BucketReplicaLinkResponse
        """
        Create a bucket replica link for object replication.

        Args:
            local_buckets (list[FixedReference], optional):
                A list of local_buckets to query for. Overrides local_bucket_names and local_bucket_ids keyword arguments.
            remote_buckets (list[FixedReference], optional):
                A list of remote_buckets to query for. Overrides remote_bucket_names keyword arguments.
            remote_credential (list[FixedReference], optional):
                A list of remote_credential to query for. Overrides remote_credentials_names and remote_credentials_ids keyword arguments.

            bucket_replica_link (BucketReplicaLinkPost, required):
            local_bucket_names (list[str], optional):
                A list of local bucket names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `local_bucket_ids` query parameter.
            local_bucket_ids (list[str], optional):
                A list of local bucket IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `local_bucket_names` query parameter.
            remote_bucket_names (list[str], optional):
                A list of remote bucket names. If there is not at least one resource that
                matches each of the elements, then an error is returned.
            remote_credentials_names (list[str], optional):
                A list of remote credentials names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with the `remote_credentials_ids` query parameter.
            remote_credentials_ids (list[str], optional):
                A list of remote credentials IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_credentials_names` query parameter.
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
            bucket_replica_link=bucket_replica_link,
            local_bucket_names=local_bucket_names,
            local_bucket_ids=local_bucket_ids,
            remote_bucket_names=remote_bucket_names,
            remote_credentials_names=remote_credentials_names,
            remote_credentials_ids=remote_credentials_ids,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._bucket_replica_links_api.api210_bucket_replica_links_post_with_http_info
        _process_references(local_buckets, ['local_bucket_names', 'local_bucket_ids'], kwargs)
        _process_references(remote_buckets, ['remote_bucket_names'], kwargs)
        _process_references(remote_credential, ['remote_credentials_names', 'remote_credentials_ids'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_buckets(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete object store buckets.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._buckets_api.api210_buckets_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_buckets(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        destroyed=None,  # type: bool
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.BucketGetResponse
        """
        List object store bucket attributes such as creation time and space usage.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. If
                not set, lists both objects that are destroyed and those that are not destroyed.
                If object name(s) are specified in the `names` parameter, then each object
                referenced must exist. If `destroyed` is set to `true`, then each object
                referenced must also be destroyed. If `destroyed` is set to `false`, then each
                object referenced must also not be destroyed. An error is returned if any of
                these conditions are not met.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
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
            continuation_token=continuation_token,
            destroyed=destroyed,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._buckets_api.api210_buckets_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_buckets(
        self,
        references=None,  # type: List[models.ReferenceType]
        bucket=None,  # type: models.BucketPatch
        ids=None,  # type: List[str]
        ignore_usage=None,  # type: bool
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.BucketResponse
        """
        Modify object store bucket attributes such as destroyed and versioning.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            bucket (BucketPatch, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            ignore_usage (bool, optional):
                Allow update operations that lead to a `hard_limit_enabled` object store
                account, bucket, or file system with usage over its limiting value. For object
                store accounts and buckets, the limiting value is that of `quota_limit`, and for
                file systems it is that of `provisioned`. The operation can be either setting
                `hard_limit_enabled` when usage is higher than the limiting value, or modifying
                the limiting value to a value under usage when `hard_limit_enabled` is `true`.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            bucket=bucket,
            ids=ids,
            ignore_usage=ignore_usage,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._buckets_api.api210_buckets_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_buckets_performance(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        end_time=None,  # type: int
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        resolution=None,  # type: int
        sort=None,  # type: List[str]
        start_time=None,  # type: int
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.BucketPerformanceGetResponse
        """
        List performance metrics for a bucket.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            end_time (int, optional):
                When the time window ends (in milliseconds since epoch).
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            resolution (int, optional):
                The desired ms between samples. Available resolutions may depend on data type,
                `start_time` and `end_time`. In general `1000`, `30000`, `300000`, `1800000`,
                `7200000`, and `86400000` are possible values.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            start_time (int, optional):
                When the time window starts (in milliseconds since epoch).
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
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
            continuation_token=continuation_token,
            end_time=end_time,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            resolution=resolution,
            sort=sort,
            start_time=start_time,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._buckets_api.api210_buckets_performance_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_buckets(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        bucket=None,  # type: models.BucketPost
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.BucketResponse
        """
        Create a new object store bucket.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], required):
                A list of resource names.
            bucket (BucketPost, required):
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
            names=names,
            bucket=bucket,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._buckets_api.api210_buckets_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_buckets_s3_specific_performance(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        end_time=None,  # type: int
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        resolution=None,  # type: int
        sort=None,  # type: List[str]
        start_time=None,  # type: int
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.BucketS3SpecificPerformanceGetResp
        """
        List performance metrics specific to S3 operations for a bucket.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            end_time (int, optional):
                When the time window ends (in milliseconds since epoch).
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            resolution (int, optional):
                The desired ms between samples. Available resolutions may depend on data type,
                `start_time` and `end_time`. In general `1000`, `30000`, `300000`, `1800000`,
                `7200000`, and `86400000` are possible values.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            start_time (int, optional):
                When the time window starts (in milliseconds since epoch).
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
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
            continuation_token=continuation_token,
            end_time=end_time,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            resolution=resolution,
            sort=sort,
            start_time=start_time,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._buckets_api.api210_buckets_s3_specific_performance_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_certificate_groups_certificates(
        self,
        certificates=None,  # type: List[models.ReferenceType]
        certificate_groups=None,  # type: List[models.ReferenceType]
        certificate_ids=None,  # type: List[str]
        certificate_group_ids=None,  # type: List[str]
        certificate_group_names=None,  # type: List[str]
        certificate_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete one or more certificate groups.

        Args:
            certificates (list[FixedReference], optional):
                A list of certificates to query for. Overrides certificate_ids and certificate_names keyword arguments.
            certificate_groups (list[FixedReference], optional):
                A list of certificate_groups to query for. Overrides certificate_group_ids and certificate_group_names keyword arguments.

            certificate_ids (list[str], optional):
                A list of certificate ids. If there is not at least one resource that matches
                each of the elements of `certificate_ids`, then an error is returned. This
                cannot be provided in conjunction with the `certificate_names` parameter.
            certificate_group_ids (list[str], optional):
                A list of certificate group ids. If there is not at least one resource that
                matches each of the elements of `certificate_group_ids`, then an error is
                returned. This cannot be provided in conjunction with the
                `certificate_group_names` parameter.
            certificate_group_names (list[str], optional):
                A list of certificate group names. If there is not at least one resource that
                matches each of the elements of `certificate_group_names`, then an error is
                returned. This cannot be provided in conjunction with the
                `certificate_group_ids` parameter.
            certificate_names (list[str], optional):
                A list of certificate names. If there is not at least one resource that matches
                each of the elements of `certificate_names`, then an error is returned. This
                cannot be provided in conjunction with the `certificate_ids` parameter.
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
            certificate_ids=certificate_ids,
            certificate_group_ids=certificate_group_ids,
            certificate_group_names=certificate_group_names,
            certificate_names=certificate_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._certificate_groups_api.api210_certificate_groups_certificates_delete_with_http_info
        _process_references(certificates, ['certificate_ids', 'certificate_names'], kwargs)
        _process_references(certificate_groups, ['certificate_group_ids', 'certificate_group_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_certificate_groups_certificates(
        self,
        certificates=None,  # type: List[models.ReferenceType]
        certificate_groups=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        certificate_ids=None,  # type: List[str]
        certificate_group_ids=None,  # type: List[str]
        certificate_group_names=None,  # type: List[str]
        certificate_names=None,  # type: List[str]
        filter=None,  # type: str
        limit=None,  # type: int
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.CertificateGroupCertificateGetResp
        """
        List membership associations between groups and certificates on the array.

        Args:
            certificates (list[FixedReference], optional):
                A list of certificates to query for. Overrides certificate_ids and certificate_names keyword arguments.
            certificate_groups (list[FixedReference], optional):
                A list of certificate_groups to query for. Overrides certificate_group_ids and certificate_group_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            certificate_ids (list[str], optional):
                A list of certificate ids. If there is not at least one resource that matches
                each of the elements of `certificate_ids`, then an error is returned. This
                cannot be provided in conjunction with the `certificate_names` parameter.
            certificate_group_ids (list[str], optional):
                A list of certificate group ids. If there is not at least one resource that
                matches each of the elements of `certificate_group_ids`, then an error is
                returned. This cannot be provided in conjunction with the
                `certificate_group_names` parameter.
            certificate_group_names (list[str], optional):
                A list of certificate group names. If there is not at least one resource that
                matches each of the elements of `certificate_group_names`, then an error is
                returned. This cannot be provided in conjunction with the
                `certificate_group_ids` parameter.
            certificate_names (list[str], optional):
                A list of certificate names. If there is not at least one resource that matches
                each of the elements of `certificate_names`, then an error is returned. This
                cannot be provided in conjunction with the `certificate_ids` parameter.
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
            continuation_token=continuation_token,
            certificate_ids=certificate_ids,
            certificate_group_ids=certificate_group_ids,
            certificate_group_names=certificate_group_names,
            certificate_names=certificate_names,
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
        endpoint = self._certificate_groups_api.api210_certificate_groups_certificates_get_with_http_info
        _process_references(certificates, ['certificate_ids', 'certificate_names'], kwargs)
        _process_references(certificate_groups, ['certificate_group_ids', 'certificate_group_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_certificate_groups_certificates(
        self,
        certificates=None,  # type: List[models.ReferenceType]
        certificate_groups=None,  # type: List[models.ReferenceType]
        certificate_ids=None,  # type: List[str]
        certificate_group_ids=None,  # type: List[str]
        certificate_group_names=None,  # type: List[str]
        certificate_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.CertificateGroupCertificateResponse
        """
        Add one or more certificates to one or more certificate groups on the array.

        Args:
            certificates (list[FixedReference], optional):
                A list of certificates to query for. Overrides certificate_ids and certificate_names keyword arguments.
            certificate_groups (list[FixedReference], optional):
                A list of certificate_groups to query for. Overrides certificate_group_ids and certificate_group_names keyword arguments.

            certificate_ids (list[str], optional):
                A list of certificate ids. If there is not at least one resource that matches
                each of the elements of `certificate_ids`, then an error is returned. This
                cannot be provided in conjunction with the `certificate_names` parameter.
            certificate_group_ids (list[str], optional):
                A list of certificate group ids. If there is not at least one resource that
                matches each of the elements of `certificate_group_ids`, then an error is
                returned. This cannot be provided in conjunction with the
                `certificate_group_names` parameter.
            certificate_group_names (list[str], optional):
                A list of certificate group names. If there is not at least one resource that
                matches each of the elements of `certificate_group_names`, then an error is
                returned. This cannot be provided in conjunction with the
                `certificate_group_ids` parameter.
            certificate_names (list[str], optional):
                A list of certificate names. If there is not at least one resource that matches
                each of the elements of `certificate_names`, then an error is returned. This
                cannot be provided in conjunction with the `certificate_ids` parameter.
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
            certificate_ids=certificate_ids,
            certificate_group_ids=certificate_group_ids,
            certificate_group_names=certificate_group_names,
            certificate_names=certificate_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._certificate_groups_api.api210_certificate_groups_certificates_post_with_http_info
        _process_references(certificates, ['certificate_ids', 'certificate_names'], kwargs)
        _process_references(certificate_groups, ['certificate_group_ids', 'certificate_group_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_certificate_groups(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete one or more certificate groups from the array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._certificate_groups_api.api210_certificate_groups_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_certificate_groups(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.CertificateGroupGetResponse
        """
        Display all array certificate groups.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._certificate_groups_api.api210_certificate_groups_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_certificate_groups(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.CertificateGroupResponse
        """
        Create one or more certificate groups on the array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._certificate_groups_api.api210_certificate_groups_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_certificate_groups_uses(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.CertificateGroupUseGetResponse
        """
        List how certificate groups are being used and by what.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._certificate_groups_api.api210_certificate_groups_uses_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_certificates_certificate_groups(
        self,
        certificates=None,  # type: List[models.ReferenceType]
        certificate_groups=None,  # type: List[models.ReferenceType]
        certificate_ids=None,  # type: List[str]
        certificate_group_ids=None,  # type: List[str]
        certificate_group_names=None,  # type: List[str]
        certificate_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Remove one or more certificates from one or more certificate groups.

        Args:
            certificates (list[FixedReference], optional):
                A list of certificates to query for. Overrides certificate_ids and certificate_names keyword arguments.
            certificate_groups (list[FixedReference], optional):
                A list of certificate_groups to query for. Overrides certificate_group_ids and certificate_group_names keyword arguments.

            certificate_ids (list[str], optional):
                A list of certificate ids. If there is not at least one resource that matches
                each of the elements of `certificate_ids`, then an error is returned. This
                cannot be provided in conjunction with the `certificate_names` parameter.
            certificate_group_ids (list[str], optional):
                A list of certificate group ids. If there is not at least one resource that
                matches each of the elements of `certificate_group_ids`, then an error is
                returned. This cannot be provided in conjunction with the
                `certificate_group_names` parameter.
            certificate_group_names (list[str], optional):
                A list of certificate group names. If there is not at least one resource that
                matches each of the elements of `certificate_group_names`, then an error is
                returned. This cannot be provided in conjunction with the
                `certificate_group_ids` parameter.
            certificate_names (list[str], optional):
                A list of certificate names. If there is not at least one resource that matches
                each of the elements of `certificate_names`, then an error is returned. This
                cannot be provided in conjunction with the `certificate_ids` parameter.
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
            certificate_ids=certificate_ids,
            certificate_group_ids=certificate_group_ids,
            certificate_group_names=certificate_group_names,
            certificate_names=certificate_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._certificates_api.api210_certificates_certificate_groups_delete_with_http_info
        _process_references(certificates, ['certificate_ids', 'certificate_names'], kwargs)
        _process_references(certificate_groups, ['certificate_group_ids', 'certificate_group_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_certificates_certificate_groups(
        self,
        certificates=None,  # type: List[models.ReferenceType]
        certificate_groups=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        certificate_ids=None,  # type: List[str]
        certificate_group_ids=None,  # type: List[str]
        certificate_group_names=None,  # type: List[str]
        certificate_names=None,  # type: List[str]
        filter=None,  # type: str
        limit=None,  # type: int
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.CertificateCertificateGroupGetResp
        """
        List membership associations between groups and certificates.

        Args:
            certificates (list[FixedReference], optional):
                A list of certificates to query for. Overrides certificate_ids and certificate_names keyword arguments.
            certificate_groups (list[FixedReference], optional):
                A list of certificate_groups to query for. Overrides certificate_group_ids and certificate_group_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            certificate_ids (list[str], optional):
                A list of certificate ids. If there is not at least one resource that matches
                each of the elements of `certificate_ids`, then an error is returned. This
                cannot be provided in conjunction with the `certificate_names` parameter.
            certificate_group_ids (list[str], optional):
                A list of certificate group ids. If there is not at least one resource that
                matches each of the elements of `certificate_group_ids`, then an error is
                returned. This cannot be provided in conjunction with the
                `certificate_group_names` parameter.
            certificate_group_names (list[str], optional):
                A list of certificate group names. If there is not at least one resource that
                matches each of the elements of `certificate_group_names`, then an error is
                returned. This cannot be provided in conjunction with the
                `certificate_group_ids` parameter.
            certificate_names (list[str], optional):
                A list of certificate names. If there is not at least one resource that matches
                each of the elements of `certificate_names`, then an error is returned. This
                cannot be provided in conjunction with the `certificate_ids` parameter.
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
            continuation_token=continuation_token,
            certificate_ids=certificate_ids,
            certificate_group_ids=certificate_group_ids,
            certificate_group_names=certificate_group_names,
            certificate_names=certificate_names,
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
        endpoint = self._certificates_api.api210_certificates_certificate_groups_get_with_http_info
        _process_references(certificates, ['certificate_ids', 'certificate_names'], kwargs)
        _process_references(certificate_groups, ['certificate_group_ids', 'certificate_group_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_certificates_certificate_groups(
        self,
        certificates=None,  # type: List[models.ReferenceType]
        certificate_groups=None,  # type: List[models.ReferenceType]
        certificate_ids=None,  # type: List[str]
        certificate_group_ids=None,  # type: List[str]
        certificate_group_names=None,  # type: List[str]
        certificate_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.CertificateCertificateGroupResponse
        """
        Add one or more certificates to one or more certificate groups.

        Args:
            certificates (list[FixedReference], optional):
                A list of certificates to query for. Overrides certificate_ids and certificate_names keyword arguments.
            certificate_groups (list[FixedReference], optional):
                A list of certificate_groups to query for. Overrides certificate_group_ids and certificate_group_names keyword arguments.

            certificate_ids (list[str], optional):
                A list of certificate ids. If there is not at least one resource that matches
                each of the elements of `certificate_ids`, then an error is returned. This
                cannot be provided in conjunction with the `certificate_names` parameter.
            certificate_group_ids (list[str], optional):
                A list of certificate group ids. If there is not at least one resource that
                matches each of the elements of `certificate_group_ids`, then an error is
                returned. This cannot be provided in conjunction with the
                `certificate_group_names` parameter.
            certificate_group_names (list[str], optional):
                A list of certificate group names. If there is not at least one resource that
                matches each of the elements of `certificate_group_names`, then an error is
                returned. This cannot be provided in conjunction with the
                `certificate_group_ids` parameter.
            certificate_names (list[str], optional):
                A list of certificate names. If there is not at least one resource that matches
                each of the elements of `certificate_names`, then an error is returned. This
                cannot be provided in conjunction with the `certificate_ids` parameter.
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
            certificate_ids=certificate_ids,
            certificate_group_ids=certificate_group_ids,
            certificate_group_names=certificate_group_names,
            certificate_names=certificate_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._certificates_api.api210_certificates_certificate_groups_post_with_http_info
        _process_references(certificates, ['certificate_ids', 'certificate_names'], kwargs)
        _process_references(certificate_groups, ['certificate_group_ids', 'certificate_group_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_certificates(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete a CA certificate from the array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._certificates_api.api210_certificates_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_certificates(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.CertificateGetResponse
        """
        List array certificates and their attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._certificates_api.api210_certificates_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_certificates(
        self,
        references=None,  # type: List[models.ReferenceType]
        certificate=None,  # type: models.CertificatePatch
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.CertificateResponse
        """
        Modify SSL certificate attributes such as passphrases and intermediate
        certificates.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            certificate (CertificatePatch, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            certificate=certificate,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._certificates_api.api210_certificates_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_certificates(
        self,
        references=None,  # type: List[models.ReferenceType]
        certificate=None,  # type: models.CertificatePost
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.CertificateResponse
        """
        Upload a CA certificate to the array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            certificate (CertificatePost, required):
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            certificate=certificate,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._certificates_api.api210_certificates_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_certificates_uses(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.CertificateUseGetResponse
        """
        List how certificates are being used and by what.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._certificates_api.api210_certificates_uses_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_arrays_clients_performance(
        self,
        references=None,  # type: List[models.ReferenceType]
        filter=None,  # type: str
        limit=None,  # type: int
        names=None,  # type: List[str]
        sort=None,  # type: List[str]
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ClientPerformanceGetResponse
        """
        List NFS client I/O performance metrics.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
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
            filter=filter,
            limit=limit,
            names=names,
            sort=sort,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._clients_api.api210_arrays_clients_performance_get_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_directory_services(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.DirectoryServiceGetResponse
        """
        List directory service configuration information for the array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._directory_services_api.api210_directory_services_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_directory_services(
        self,
        references=None,  # type: List[models.ReferenceType]
        directory_service=None,  # type: models.DirectoryService
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.DirectoryServiceResponse
        """
        Modifies and tests the directory service configuration.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            directory_service (DirectoryService, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            directory_service=directory_service,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._directory_services_api.api210_directory_services_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_directory_services_roles(
        self,
        references=None,  # type: List[models.ReferenceType]
        roles=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        ids=None,  # type: List[str]
        filter=None,  # type: str
        limit=None,  # type: int
        offset=None,  # type: int
        role_ids=None,  # type: List[str]
        role_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.DirectoryServiceRolesGetResponse
        """
        Return array's RBAC group configuration settings for manageability.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            roles (list[FixedReference], optional):
                A list of roles to query for. Overrides role_ids and role_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `role_names` or `role_ids` query
                parameters.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            role_ids (list[str], optional):
                A list of role_ids. If after filtering, there is not at least one resource that
                matches each of the elements of `role_ids`, then an error is returned. This
                cannot be provided together with the `ids` or `role_names` query parameters.
            role_names (list[str], optional):
                A list of role_names. If there is not at least one resource that matches each of
                the elements of `role_names`, then an error is returned. This cannot be provided
                together with the `ids` or `role_ids` query parameters.
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
            continuation_token=continuation_token,
            ids=ids,
            filter=filter,
            limit=limit,
            offset=offset,
            role_ids=role_ids,
            role_names=role_names,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._directory_services_api.api210_directory_services_roles_get_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(roles, ['role_ids', 'role_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_directory_services_roles(
        self,
        references=None,  # type: List[models.ReferenceType]
        roles=None,  # type: List[models.ReferenceType]
        directory_service_roles=None,  # type: models.DirectoryServiceRole
        ids=None,  # type: List[str]
        role_ids=None,  # type: List[str]
        role_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.DirectoryServiceRolesResponse
        """
        Update an RBAC group configuration setting for manageability.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            roles (list[FixedReference], optional):
                A list of roles to query for. Overrides role_ids and role_names keyword arguments.

            directory_service_roles (DirectoryServiceRole, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `role_names` or `role_ids` query
                parameters.
            role_ids (list[str], optional):
                A list of role_ids. If after filtering, there is not at least one resource that
                matches each of the elements of `role_ids`, then an error is returned. This
                cannot be provided together with the `ids` or `role_names` query parameters.
            role_names (list[str], optional):
                A list of role_names. If there is not at least one resource that matches each of
                the elements of `role_names`, then an error is returned. This cannot be provided
                together with the `ids` or `role_ids` query parameters.
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
            directory_service_roles=directory_service_roles,
            ids=ids,
            role_ids=role_ids,
            role_names=role_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._directory_services_api.api210_directory_services_roles_patch_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(roles, ['role_ids', 'role_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_directory_services_test(
        self,
        references=None,  # type: List[models.ReferenceType]
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.TestResultGetResponse
        """
        Test the configured directory services on the array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._directory_services_api.api210_directory_services_test_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_directory_services_test(
        self,
        references=None,  # type: List[models.ReferenceType]
        filter=None,  # type: str
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        sort=None,  # type: List[str]
        directory_service=None,  # type: models.DirectoryService
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.TestResultResponse
        """
        Test the configured directory services on the array. Optionally, provide
        modifications which will be used to perform the tests, but will not be applied
        to the current configuration.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            directory_service (DirectoryService, optional):
                An optional directory service configuration that, if provided, will be used to
                overwrite aspects of the existing directory service objects when performing
                tests.
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
            filter=filter,
            ids=ids,
            names=names,
            sort=sort,
            directory_service=directory_service,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._directory_services_api.api210_directory_services_test_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_dns(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.DnsGetResponse
        """
        List DNS attributes for the array's administrative network.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._dns_api.api210_dns_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_dns(
        self,
        references=None,  # type: List[models.ReferenceType]
        dns=None,  # type: models.Dns
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.DnsResponse
        """
        Modify DNS attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            dns (Dns, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            dns=dns,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._dns_api.api210_dns_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_drives(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.DriveGetResponse
        """
        List array drive information.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
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
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._drives_api.api210_drives_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_file_system_replica_links(
        self,
        references=None,  # type: List[models.ReferenceType]
        local_file_systems=None,  # type: List[models.ReferenceType]
        remote_file_systems=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        local_file_system_ids=None,  # type: List[str]
        local_file_system_names=None,  # type: List[str]
        remote_file_system_ids=None,  # type: List[str]
        remote_file_system_names=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        cancel_in_progress_transfers=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete a file system replication link.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            local_file_systems (list[FixedReference], optional):
                A list of local_file_systems to query for. Overrides local_file_system_ids and local_file_system_names keyword arguments.
            remote_file_systems (list[FixedReference], optional):
                A list of remote_file_systems to query for. Overrides remote_file_system_ids and remote_file_system_names keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            local_file_system_ids (list[str], optional):
                A list of local file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `local_file_system_names` query parameter.
            local_file_system_names (list[str], optional):
                A list of local file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with `local_file_system_ids` query parameter.
            remote_file_system_ids (list[str], optional):
                A list of remote file system IDs. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with the `remote_file_system_names` query parameter.
            remote_file_system_names (list[str], optional):
                A list of remote file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with the `remote_file_system_ids` query parameter.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
            cancel_in_progress_transfers (bool, optional):
                This parameter must be set to `true` in order to delete a file system
                replication link (which can cancel any in-progress replication transfers).
                Setting this parameter to `true` is acknowledgement that any in-progress
                replication transfers on the specified links will be cancelled when this request
                is fulfilled.
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
            ids=ids,
            local_file_system_ids=local_file_system_ids,
            local_file_system_names=local_file_system_names,
            remote_file_system_ids=remote_file_system_ids,
            remote_file_system_names=remote_file_system_names,
            remote_ids=remote_ids,
            remote_names=remote_names,
            cancel_in_progress_transfers=cancel_in_progress_transfers,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_replica_links_api.api210_file_system_replica_links_delete_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(local_file_systems, ['local_file_system_ids', 'local_file_system_names'], kwargs)
        _process_references(remote_file_systems, ['remote_file_system_ids', 'remote_file_system_names'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_system_replica_links(
        self,
        references=None,  # type: List[models.ReferenceType]
        local_file_systems=None,  # type: List[models.ReferenceType]
        remote_file_systems=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        local_file_system_ids=None,  # type: List[str]
        local_file_system_names=None,  # type: List[str]
        offset=None,  # type: int
        remote_file_system_ids=None,  # type: List[str]
        remote_file_system_names=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemReplicaLinkGetResponse
        """
        List file system replication link.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            local_file_systems (list[FixedReference], optional):
                A list of local_file_systems to query for. Overrides local_file_system_ids and local_file_system_names keyword arguments.
            remote_file_systems (list[FixedReference], optional):
                A list of remote_file_systems to query for. Overrides remote_file_system_ids and remote_file_system_names keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            local_file_system_ids (list[str], optional):
                A list of local file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `local_file_system_names` query parameter.
            local_file_system_names (list[str], optional):
                A list of local file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with `local_file_system_ids` query parameter.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            remote_file_system_ids (list[str], optional):
                A list of remote file system IDs. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with the `remote_file_system_names` query parameter.
            remote_file_system_names (list[str], optional):
                A list of remote file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with the `remote_file_system_ids` query parameter.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
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
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            local_file_system_ids=local_file_system_ids,
            local_file_system_names=local_file_system_names,
            offset=offset,
            remote_file_system_ids=remote_file_system_ids,
            remote_file_system_names=remote_file_system_names,
            remote_ids=remote_ids,
            remote_names=remote_names,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_replica_links_api.api210_file_system_replica_links_get_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(local_file_systems, ['local_file_system_ids', 'local_file_system_names'], kwargs)
        _process_references(remote_file_systems, ['remote_file_system_ids', 'remote_file_system_names'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_file_system_replica_links_policies(
        self,
        local_file_systems=None,  # type: List[models.ReferenceType]
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        local_file_system_ids=None,  # type: List[str]
        local_file_system_names=None,  # type: List[str]
        member_ids=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Remove a policy from a file system replication link.

        Args:
            local_file_systems (list[FixedReference], optional):
                A list of local_file_systems to query for. Overrides local_file_system_ids and local_file_system_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.

            local_file_system_ids (list[str], optional):
                A list of local file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `local_file_system_names` query parameter.
            local_file_system_names (list[str], optional):
                A list of local file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with `local_file_system_ids` query parameter.
            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
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
            local_file_system_ids=local_file_system_ids,
            local_file_system_names=local_file_system_names,
            member_ids=member_ids,
            policy_ids=policy_ids,
            policy_names=policy_names,
            remote_ids=remote_ids,
            remote_names=remote_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_replica_links_api.api210_file_system_replica_links_policies_delete_with_http_info
        _process_references(local_file_systems, ['local_file_system_ids', 'local_file_system_names'], kwargs)
        _process_references(members, ['member_ids'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_system_replica_links_policies(
        self,
        local_file_systems=None,  # type: List[models.ReferenceType]
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        remote_file_systems=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        local_file_system_ids=None,  # type: List[str]
        local_file_system_names=None,  # type: List[str]
        member_ids=None,  # type: List[str]
        offset=None,  # type: int
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        remote_file_system_ids=None,  # type: List[str]
        remote_file_system_names=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMemberWithRemoteGetResponse
        """
        List file system replication link policies.

        Args:
            local_file_systems (list[FixedReference], optional):
                A list of local_file_systems to query for. Overrides local_file_system_ids and local_file_system_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.
            remote_file_systems (list[FixedReference], optional):
                A list of remote_file_systems to query for. Overrides remote_file_system_ids and remote_file_system_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            local_file_system_ids (list[str], optional):
                A list of local file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `local_file_system_names` query parameter.
            local_file_system_names (list[str], optional):
                A list of local file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with `local_file_system_ids` query parameter.
            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_file_system_ids (list[str], optional):
                A list of remote file system IDs. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with the `remote_file_system_names` query parameter.
            remote_file_system_names (list[str], optional):
                A list of remote file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with the `remote_file_system_ids` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
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
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            local_file_system_ids=local_file_system_ids,
            local_file_system_names=local_file_system_names,
            member_ids=member_ids,
            offset=offset,
            policy_ids=policy_ids,
            policy_names=policy_names,
            remote_ids=remote_ids,
            remote_file_system_ids=remote_file_system_ids,
            remote_file_system_names=remote_file_system_names,
            remote_names=remote_names,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_replica_links_api.api210_file_system_replica_links_policies_get_with_http_info
        _process_references(local_file_systems, ['local_file_system_ids', 'local_file_system_names'], kwargs)
        _process_references(members, ['member_ids'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        _process_references(remote_file_systems, ['remote_file_system_ids', 'remote_file_system_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_file_system_replica_links_policies(
        self,
        local_file_systems=None,  # type: List[models.ReferenceType]
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        local_file_system_ids=None,  # type: List[str]
        local_file_system_names=None,  # type: List[str]
        member_ids=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMemberWithRemoteResponse
        """
        Add a policy to a file system replication link.

        Args:
            local_file_systems (list[FixedReference], optional):
                A list of local_file_systems to query for. Overrides local_file_system_ids and local_file_system_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.

            local_file_system_ids (list[str], optional):
                A list of local file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `local_file_system_names` query parameter.
            local_file_system_names (list[str], optional):
                A list of local file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with `local_file_system_ids` query parameter.
            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
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
            local_file_system_ids=local_file_system_ids,
            local_file_system_names=local_file_system_names,
            member_ids=member_ids,
            policy_ids=policy_ids,
            policy_names=policy_names,
            remote_ids=remote_ids,
            remote_names=remote_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_replica_links_api.api210_file_system_replica_links_policies_post_with_http_info
        _process_references(local_file_systems, ['local_file_system_ids', 'local_file_system_names'], kwargs)
        _process_references(members, ['member_ids'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_file_system_replica_links(
        self,
        references=None,  # type: List[models.ReferenceType]
        local_file_systems=None,  # type: List[models.ReferenceType]
        remote_file_systems=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        file_system_replica_link=None,  # type: models.FileSystemReplicaLink
        ids=None,  # type: List[str]
        local_file_system_ids=None,  # type: List[str]
        local_file_system_names=None,  # type: List[str]
        remote_file_system_names=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemReplicaLinkResponse
        """
        Create a file system replication link.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            local_file_systems (list[FixedReference], optional):
                A list of local_file_systems to query for. Overrides local_file_system_ids and local_file_system_names keyword arguments.
            remote_file_systems (list[FixedReference], optional):
                A list of remote_file_systems to query for. Overrides remote_file_system_names keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.

            file_system_replica_link (FileSystemReplicaLink, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            local_file_system_ids (list[str], optional):
                A list of local file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `local_file_system_names` query parameter.
            local_file_system_names (list[str], optional):
                A list of local file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with `local_file_system_ids` query parameter.
            remote_file_system_names (list[str], optional):
                A list of remote file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with the `remote_file_system_ids` query parameter.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
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
            file_system_replica_link=file_system_replica_link,
            ids=ids,
            local_file_system_ids=local_file_system_ids,
            local_file_system_names=local_file_system_names,
            remote_file_system_names=remote_file_system_names,
            remote_ids=remote_ids,
            remote_names=remote_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_replica_links_api.api210_file_system_replica_links_post_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(local_file_systems, ['local_file_system_ids', 'local_file_system_names'], kwargs)
        _process_references(remote_file_systems, ['remote_file_system_names'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_system_replica_links_transfer(
        self,
        references=None,  # type: List[models.ReferenceType]
        names_or_owners=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names_or_owner_names=None,  # type: List[str]
        offset=None,  # type: int
        remote_ids=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemSnapshotGetTransferResponse
        """
        List the transfer status details for file system replication.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            names_or_owners (list[FixedReference], optional):
                A list of names_or_owners to query for. Overrides names_or_owner_names keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names_or_owner_names (list[str], optional):
                A list of resource names. Either the names of the snapshots or the owning file
                systems.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
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
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names_or_owner_names=names_or_owner_names,
            offset=offset,
            remote_ids=remote_ids,
            remote_names=remote_names,
            sort=sort,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_replica_links_api.api210_file_system_replica_links_transfer_get_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(names_or_owners, ['names_or_owner_names'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_file_system_snapshots(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete a file system snapshot.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_snapshots_api.api210_file_system_snapshots_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_system_snapshots(
        self,
        references=None,  # type: List[models.ReferenceType]
        names_or_owners=None,  # type: List[models.ReferenceType]
        owners=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        destroyed=None,  # type: bool
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names_or_owner_names=None,  # type: List[str]
        offset=None,  # type: int
        owner_ids=None,  # type: List[str]
        sort=None,  # type: List[str]
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemSnapshotGetResponse
        """
        List file system snapshots.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            names_or_owners (list[FixedReference], optional):
                A list of names_or_owners to query for. Overrides names_or_owner_names keyword arguments.
            owners (list[FixedReference], optional):
                A list of owners to query for. Overrides owner_ids keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. If
                not set, lists both objects that are destroyed and those that are not destroyed.
                If object name(s) are specified in the `names` parameter, then each object
                referenced must exist. If `destroyed` is set to `true`, then each object
                referenced must also be destroyed. If `destroyed` is set to `false`, then each
                object referenced must also not be destroyed. An error is returned if any of
                these conditions are not met.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names_or_owner_names (list[str], optional):
                A list of resource names. Either the names of the snapshots or the owning file
                systems.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            owner_ids (list[str], optional):
                A list of owning file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements of owner IDs, then an error is
                returned. This cannot be provided together with the `ids`,
                `names_or_owner_names`, or `names_or_sources` query parameters.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
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
            continuation_token=continuation_token,
            destroyed=destroyed,
            filter=filter,
            ids=ids,
            limit=limit,
            names_or_owner_names=names_or_owner_names,
            offset=offset,
            owner_ids=owner_ids,
            sort=sort,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_snapshots_api.api210_file_system_snapshots_get_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(names_or_owners, ['names_or_owner_names'], kwargs)
        _process_references(owners, ['owner_ids'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_file_system_snapshots(
        self,
        references=None,  # type: List[models.ReferenceType]
        file_system_snapshot=None,  # type: models.FileSystemSnapshot
        ids=None,  # type: List[str]
        latest_replica=None,  # type: bool
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemSnapshotResponse
        """
        Modify file system snapshot attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            file_system_snapshot (FileSystemSnapshot, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            latest_replica (bool, optional):
                Used when destroying a snapshot. If not present or `false`, and the snapshot is
                the latest replicated snapshot, then destroy will fail. If `true` or the
                snapshot is not the latest replicated snapshot, then destroy will be successful.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            file_system_snapshot=file_system_snapshot,
            ids=ids,
            latest_replica=latest_replica,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_snapshots_api.api210_file_system_snapshots_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_file_system_snapshots_policies(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Remove snapshot scheduling policies from a file system.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_snapshots_api.api210_file_system_snapshots_policies_delete_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_system_snapshots_policies(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        offset=None,  # type: int
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyFileSystemSnapshotGetResponse
        """
        List file system snapshots mapped to snapshot scheduling policies.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_snapshots_api.api210_file_system_snapshots_policies_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_file_system_snapshots(
        self,
        sources=None,  # type: List[models.ReferenceType]
        source_ids=None,  # type: List[str]
        source_names=None,  # type: List[str]
        send=None,  # type: bool
        targets=None,  # type: List[str]
        file_system_snapshot=None,  # type: models.FileSystemSnapshotPost
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemSnapshotResponse
        """
        Create a snapshot for a specified source file system. If a source file system is
        not specified, creates snapshots for all file systems on the array.

        Args:
            sources (list[FixedReference], optional):
                A list of sources to query for. Overrides source_ids and source_names keyword arguments.

            source_ids (list[str], optional):
                A list of source file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements of `source_ids`, then an error is
                returned. This cannot be provided together with the `names_or_sources` or
                `sources` query parameters.
            source_names (list[str], optional):
                A list of names for the source of the object. If there is not at least one
                resource that matches each of the elements of `source_names`, an error is
                returned.
            send (bool, optional):
                Whether to replicate created snapshots immediately to other arrays. If it's
                `false`, created snapshots may still be replicated to other arrays according to
                policy.
            targets (list[str], optional):
                The target arrays to replicate created snapshots to. Only valid when `send` is
                `true`.
            file_system_snapshot (FileSystemSnapshotPost, optional):
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
            source_ids=source_ids,
            source_names=source_names,
            send=send,
            targets=targets,
            file_system_snapshot=file_system_snapshot,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_snapshots_api.api210_file_system_snapshots_post_with_http_info
        _process_references(sources, ['source_ids', 'source_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_file_system_snapshots_transfer(
        self,
        references=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete file system snapshot transfers from the source array to the target array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_names and remote_ids keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
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
            ids=ids,
            names=names,
            remote_names=remote_names,
            remote_ids=remote_ids,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_snapshots_api.api210_file_system_snapshots_transfer_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(remotes, ['remote_names', 'remote_ids'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_system_snapshots_transfer(
        self,
        references=None,  # type: List[models.ReferenceType]
        names_or_owners=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names_or_owner_names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemSnapshotGetTransferResponse
        """
        List file system snapshot transfers from the source array to the target array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids keyword arguments.
            names_or_owners (list[FixedReference], optional):
                A list of names_or_owners to query for. Overrides names_or_owner_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names_or_owner_names (list[str], optional):
                A list of resource names. Either the names of the snapshots or the owning file
                systems.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
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
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names_or_owner_names=names_or_owner_names,
            offset=offset,
            sort=sort,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_system_snapshots_api.api210_file_system_snapshots_transfer_get_with_http_info
        _process_references(references, ['ids'], kwargs)
        _process_references(names_or_owners, ['names_or_owner_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_file_systems(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Deletes a file system. Deleting a file system is equivalent to eradication. A
        file system's `destroyed` parameter must be set to `true` before a file system
        can be deleted.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_systems(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        destroyed=None,  # type: bool
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemGetResponse
        """
        List one or more file systems on the array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            destroyed (bool, optional):
                If set to `true`, lists only destroyed objects that are in the eradication
                pending state. If set to `false`, lists only objects that are not destroyed. If
                not set, lists both objects that are destroyed and those that are not destroyed.
                If object name(s) are specified in the `names` parameter, then each object
                referenced must exist. If `destroyed` is set to `true`, then each object
                referenced must also be destroyed. If `destroyed` is set to `false`, then each
                object referenced must also not be destroyed. An error is returned if any of
                these conditions are not met.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
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
            continuation_token=continuation_token,
            destroyed=destroyed,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_systems_groups_performance(
        self,
        file_systems=None,  # type: List[models.ReferenceType]
        groups=None,  # type: List[models.ReferenceType]
        references=None,  # type: List[models.ReferenceType]
        file_system_ids=None,  # type: List[str]
        file_system_names=None,  # type: List[str]
        filter=None,  # type: str
        gids=None,  # type: List[str]
        group_names=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        sort=None,  # type: List[str]
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemGroupsPerformanceGetResponse
        """
        List a group’s I/O performance metrics on a file system.

        Args:
            file_systems (list[FixedReference], optional):
                A list of file_systems to query for. Overrides file_system_ids and file_system_names keyword arguments.
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            file_system_ids (list[str], optional):
                A list of file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements of `file_system_ids`, then an error
                is returned. This cannot be provided together with the `file_system_names` query
                parameter.
            file_system_names (list[str], optional):
                A list of file system names. If there is not at least one resource that matches
                each of the elements of `file_system_names`, then an error is returned.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            gids (list[str], optional):
                A list of group IDs. This cannot be provided together with `group_names` query
                parameter.
            group_names (list[str], optional):
                A list of group names. This cannot be provided together with `gids` query
                parameter.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
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
            file_system_ids=file_system_ids,
            file_system_names=file_system_names,
            filter=filter,
            gids=gids,
            group_names=group_names,
            limit=limit,
            names=names,
            sort=sort,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_groups_performance_get_with_http_info
        _process_references(file_systems, ['file_system_ids', 'file_system_names'], kwargs)
        _process_references(groups, ['group_names'], kwargs)
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_systems_locks_clients(
        self,
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemClientsGetResponse
        """
        Lists all clients that hold active file locks.

        Args:

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
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
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_locks_clients_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def delete_file_systems_locks(
        self,
        clients=None,  # type: List[models.ReferenceType]
        file_systems=None,  # type: List[models.ReferenceType]
        references=None,  # type: List[models.ReferenceType]
        client_names=None,  # type: List[str]
        file_system_ids=None,  # type: List[str]
        file_system_names=None,  # type: List[str]
        inodes=None,  # type: List[float]
        names=None,  # type: List[str]
        paths=None,  # type: List[str]
        recursive=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Invalidates file locks. It can be used to either delete an individual lock by
        name or multiple locks filtered by parameters. E.g. to delete locks held by a
        client on specific file, parameters `client_names`, `file_system_ids` or
        `file_system_names` and `path` must be specified. When `names` is specified, no
        other query parameter can be specified.

        Args:
            clients (list[FixedReference], optional):
                A list of clients to query for. Overrides client_names keyword arguments.
            file_systems (list[FixedReference], optional):
                A list of file_systems to query for. Overrides file_system_ids and file_system_names keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            client_names (list[str], optional):
                A list of ip addresses of clients. For IPv6 both the extended format
                (x:x:x:x:x:x:x:x) and the shortened format are supported.
            file_system_ids (list[str], optional):
                A list of file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements of `file_system_ids`, then an error
                is returned. This cannot be provided together with the `file_system_names` query
                parameter.
            file_system_names (list[str], optional):
                A list of file system names. If there is not at least one resource that matches
                each of the elements of `file_system_names`, then an error is returned.
            inodes (list[float], optional):
                A list of inodes used for filtering file locks query by inodes. This may only be
                specified if `file_system_ids` or `file_system_names` is also specified. This
                cannot be provided together with the `paths` query parameter.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            paths (list[str], optional):
                A list of paths used for filtering file locks query by paths. This may only be
                specified if `file_system_ids` or `file_system_names` is also specified. This
                cannot be provided together with the `inodes` query parameter.
            recursive (bool, optional):
                Flag used to indicate that the action should be done recursively. If set to
                `true` and used e.g. with `path` pointing to a directory, the operation will
                delete all locks in given directory and subdirectories recursively. For more
                fine grained control over deleted locks, use delete by name. If not specified,
                defaults to `false`.
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
            client_names=client_names,
            file_system_ids=file_system_ids,
            file_system_names=file_system_names,
            inodes=inodes,
            names=names,
            paths=paths,
            recursive=recursive,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_locks_delete_with_http_info
        _process_references(clients, ['client_names'], kwargs)
        _process_references(file_systems, ['file_system_ids', 'file_system_names'], kwargs)
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_systems_locks(
        self,
        clients=None,  # type: List[models.ReferenceType]
        file_systems=None,  # type: List[models.ReferenceType]
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        client_names=None,  # type: List[str]
        file_system_ids=None,  # type: List[str]
        file_system_names=None,  # type: List[str]
        filter=None,  # type: str
        inodes=None,  # type: List[float]
        limit=None,  # type: int
        names=None,  # type: List[str]
        paths=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileLockGetResponse
        """
        Lists all active file locks that satisfy the conditions specified by the
        parameters.

        Args:
            clients (list[FixedReference], optional):
                A list of clients to query for. Overrides client_names keyword arguments.
            file_systems (list[FixedReference], optional):
                A list of file_systems to query for. Overrides file_system_ids and file_system_names keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            client_names (list[str], optional):
                A list of ip addresses of clients. For IPv6 both the extended format
                (x:x:x:x:x:x:x:x) and the shortened format are supported.
            file_system_ids (list[str], optional):
                A list of file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements of `file_system_ids`, then an error
                is returned. This cannot be provided together with the `file_system_names` query
                parameter.
            file_system_names (list[str], optional):
                A list of file system names. If there is not at least one resource that matches
                each of the elements of `file_system_names`, then an error is returned.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            inodes (list[float], optional):
                A list of inodes used for filtering file locks query by inodes. This may only be
                specified if `file_system_ids` or `file_system_names` is also specified. This
                cannot be provided together with the `paths` query parameter.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            paths (list[str], optional):
                A list of paths used for filtering file locks query by paths. This may only be
                specified if `file_system_ids` or `file_system_names` is also specified. This
                cannot be provided together with the `inodes` query parameter.
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
            continuation_token=continuation_token,
            client_names=client_names,
            file_system_ids=file_system_ids,
            file_system_names=file_system_names,
            filter=filter,
            inodes=inodes,
            limit=limit,
            names=names,
            paths=paths,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_locks_get_with_http_info
        _process_references(clients, ['client_names'], kwargs)
        _process_references(file_systems, ['file_system_ids', 'file_system_names'], kwargs)
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_file_systems_locks_nlm_reclamations(
        self,
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileLockNlmReclamationResponse
        """
        NLM reclamation is a system-wide operation, affecting all clients, and so only
        one may be in progress at a time. Attempting to initiate reclamation while one
        is in progress will result in an error. When NLM reclamation is initiated, all
        NLM locks are deleted and client applications are notified that they can
        reacquire their locks within a grace period.

        Args:

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
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_locks_nlm_reclamations_post_with_http_info
        return self._call_api(endpoint, kwargs)

    def patch_file_systems(
        self,
        references=None,  # type: List[models.ReferenceType]
        file_system=None,  # type: models.FileSystemPatch
        delete_link_on_eradication=None,  # type: bool
        discard_detailed_permissions=None,  # type: bool
        discard_non_snapshotted_data=None,  # type: bool
        ids=None,  # type: List[str]
        ignore_usage=None,  # type: bool
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemResponse
        """
        Modify a file system’s attributes including its export protocols and limits.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            file_system (FileSystemPatch, required):
            delete_link_on_eradication (bool, optional):
                If set to `true`, the file system can be destroyed, even if it has a replica
                link. If set to `false`, the file system cannot be destroyed if it has a replica
                link. Defaults to `false`.
            discard_detailed_permissions (bool, optional):
                This parameter must be set to `true` in order to change a file system's
                `access_control_style` from a style that supports more detailed access control
                lists to a style that only supports less detailed mode bits as a form of
                permission control. This parameter may not be set to `true` any other time.
                Setting this parameter to `true` is acknowledgement that any more detailed
                access control lists currently set within the file system will be lost, and NFS
                permission controls will only be enforced at the granularity level of NFS mode
                bits.
            discard_non_snapshotted_data (bool, optional):
                This parameter must be set to `true` in order to restore a file system from a
                snapshot or to demote a file system (which restores the file system from the
                common baseline snapshot). Setting this parameter to `true` is acknowledgement
                that any non-snapshotted data currently in the file system will be irretrievably
                lost.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            ignore_usage (bool, optional):
                Allow update operations that lead to a `hard_limit_enabled` object store
                account, bucket, or file system with usage over its limiting value. For object
                store accounts and buckets, the limiting value is that of `quota_limit`, and for
                file systems it is that of `provisioned`. The operation can be either setting
                `hard_limit_enabled` when usage is higher than the limiting value, or modifying
                the limiting value to a value under usage when `hard_limit_enabled` is `true`.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            file_system=file_system,
            delete_link_on_eradication=delete_link_on_eradication,
            discard_detailed_permissions=discard_detailed_permissions,
            discard_non_snapshotted_data=discard_non_snapshotted_data,
            ids=ids,
            ignore_usage=ignore_usage,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_systems_performance(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        end_time=None,  # type: int
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        protocol=None,  # type: str
        resolution=None,  # type: int
        sort=None,  # type: List[str]
        start_time=None,  # type: int
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemPerformanceGetResponse
        """
        Displays the performance metrics for a file system.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            end_time (int, optional):
                When the time window ends (in milliseconds since epoch).
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            protocol (str, optional):
                Display the performance of a specified protocol. Valid values are `all`, `HTTP`,
                `SMB`, `NFS`, and `S3`. If not specified, defaults to `all`, which will provide
                the combined performance of all available protocols.
            resolution (int, optional):
                The desired ms between samples. Available resolutions may depend on data type,
                `start_time` and `end_time`. In general `1000`, `30000`, `300000`, `1800000`,
                `7200000`, and `86400000` are possible values.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            start_time (int, optional):
                When the time window starts (in milliseconds since epoch).
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
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
            continuation_token=continuation_token,
            end_time=end_time,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            protocol=protocol,
            resolution=resolution,
            sort=sort,
            start_time=start_time,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_performance_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_systems_policies_all(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        offset=None,  # type: int
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMemberGetResponse
        """
        List file system policies.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_policies_all_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_file_systems_policies(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Remove a snapshot scheduling policy from a file system.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_policies_delete_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_systems_policies(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        offset=None,  # type: int
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMemberGetResponse
        """
        List file system snapshot scheduling policies.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_policies_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_file_systems_policies(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMemberResponse
        """
        Apply a snapshot scheduling policy to a file system. Only one file system can be
        mapped to a policy at a time.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_policies_post_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_file_systems(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        file_system=None,  # type: models.FileSystemPost
        discard_non_snapshotted_data=None,  # type: bool
        overwrite=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemResponse
        """
        Create a file system on the current array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], required):
                A list of resource names.
            file_system (FileSystemPost, required):
            discard_non_snapshotted_data (bool, optional):
                This parameter must be set to `true` in order to restore a file system from a
                snapshot or to demote a file system (which restores the file system from the
                common baseline snapshot). Setting this parameter to `true` is acknowledgement
                that any non-snapshotted data currently in the file system will be irretrievably
                lost.
            overwrite (bool, optional):
                When used for snapshot restore, overwrites (`true`) an existing file system.
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
            names=names,
            file_system=file_system,
            discard_non_snapshotted_data=discard_non_snapshotted_data,
            overwrite=overwrite,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_file_systems_sessions(
        self,
        clients=None,  # type: List[models.ReferenceType]
        references=None,  # type: List[models.ReferenceType]
        users=None,  # type: List[models.ReferenceType]
        client_names=None,  # type: List[str]
        disruptive=None,  # type: bool
        names=None,  # type: List[str]
        protocols=None,  # type: List[str]
        user_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete sessions. It can be used to either delete an individual session by name
        or multiple sessions filtered by parameters. E.g. to delete SMBv3 sessions held
        by specific client, `protocols` and `client_names` must be specified. To prevent
        accidental deletes, setting flag `disruptive` to `true` is required when only a
        single query parameter is part of the query. E.g. to delete all SMBv3 sessions,
        query parameters `protocols` and `disruptive` must be set. When `names` is
        specified, no other query parameter can be specified.

        Args:
            clients (list[FixedReference], optional):
                A list of clients to query for. Overrides client_names keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.
            users (list[FixedReference], optional):
                A list of users to query for. Overrides user_names keyword arguments.

            client_names (list[str], optional):
                A list of ip addresses of clients. For IPv6 both the extended format
                (x:x:x:x:x:x:x:x) and the shortened format are supported.
            disruptive (bool, optional):
                If set to `true`, a wide scope of sessions may be deleted in a single action
                using a single query parameter from `user_names`, `client_names`, or
                `protocols`. Otherwise, multiple query parameters must be specified to narrow
                the impact of deletion and avoid potential for accidental disruption of clients.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            protocols (list[str], optional):
                A list of file protocols. Valid values include `nfs` and `smb`.
            user_names (list[str], optional):
                A list of user names.
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
            client_names=client_names,
            disruptive=disruptive,
            names=names,
            protocols=protocols,
            user_names=user_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_sessions_delete_with_http_info
        _process_references(clients, ['client_names'], kwargs)
        _process_references(references, ['names'], kwargs)
        _process_references(users, ['user_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_systems_sessions(
        self,
        clients=None,  # type: List[models.ReferenceType]
        references=None,  # type: List[models.ReferenceType]
        users=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        client_names=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        protocols=None,  # type: List[str]
        user_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSessionGetResponse
        """
        Lists all active sessions that satisfy the conditions specified by the
        parameters.

        Args:
            clients (list[FixedReference], optional):
                A list of clients to query for. Overrides client_names keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.
            users (list[FixedReference], optional):
                A list of users to query for. Overrides user_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            client_names (list[str], optional):
                A list of ip addresses of clients. For IPv6 both the extended format
                (x:x:x:x:x:x:x:x) and the shortened format are supported.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            protocols (list[str], optional):
                A list of file protocols. Valid values include `nfs` and `smb`.
            user_names (list[str], optional):
                A list of user names.
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
            continuation_token=continuation_token,
            client_names=client_names,
            limit=limit,
            names=names,
            protocols=protocols,
            user_names=user_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_sessions_get_with_http_info
        _process_references(clients, ['client_names'], kwargs)
        _process_references(references, ['names'], kwargs)
        _process_references(users, ['user_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_file_systems_users_performance(
        self,
        file_systems=None,  # type: List[models.ReferenceType]
        references=None,  # type: List[models.ReferenceType]
        users=None,  # type: List[models.ReferenceType]
        file_system_ids=None,  # type: List[str]
        file_system_names=None,  # type: List[str]
        filter=None,  # type: str
        limit=None,  # type: int
        names=None,  # type: List[str]
        sort=None,  # type: List[str]
        total_only=None,  # type: bool
        uids=None,  # type: List[int]
        user_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.FileSystemUsersPerformanceGetResponse
        """
        List a user’s I/O performance metrics on a file system.

        Args:
            file_systems (list[FixedReference], optional):
                A list of file_systems to query for. Overrides file_system_ids and file_system_names keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.
            users (list[FixedReference], optional):
                A list of users to query for. Overrides user_names keyword arguments.

            file_system_ids (list[str], optional):
                A list of file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements of `file_system_ids`, then an error
                is returned. This cannot be provided together with the `file_system_names` query
                parameter.
            file_system_names (list[str], optional):
                A list of file system names. If there is not at least one resource that matches
                each of the elements of `file_system_names`, then an error is returned.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
            uids (list[int], optional):
                A list of user IDs. This cannot be provided together with `user_names` query
                parameter.
            user_names (list[str], optional):
                A list of user names. This cannot be provided together with `uids` query
                parameter.
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
            file_system_ids=file_system_ids,
            file_system_names=file_system_names,
            filter=filter,
            limit=limit,
            names=names,
            sort=sort,
            total_only=total_only,
            uids=uids,
            user_names=user_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._file_systems_api.api210_file_systems_users_performance_get_with_http_info
        _process_references(file_systems, ['file_system_ids', 'file_system_names'], kwargs)
        _process_references(references, ['names'], kwargs)
        _process_references(users, ['user_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_hardware(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        offset=None,  # type: int
        sort=None,  # type: List[str]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.HardwareGetResponse
        """
        List hardware slots and bays and the status of installed components.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

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
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._hardware_api.api210_hardware_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_hardware(
        self,
        references=None,  # type: List[models.ReferenceType]
        hardware=None,  # type: models.Hardware
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.HardwareResponse
        """
        Controls the visual identification light of the specified hardware component.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            hardware (Hardware, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            hardware=hardware,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._hardware_api.api210_hardware_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_hardware_connectors(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        offset=None,  # type: int
        sort=None,  # type: List[str]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.HardwareConnectorGetResponse
        """
        List array connection information.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

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
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._hardware_connectors_api.api210_hardware_connectors_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_hardware_connectors(
        self,
        references=None,  # type: List[models.ReferenceType]
        hardware_connector=None,  # type: models.HardwareConnector
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.HardwareConnectorResponse
        """
        Modify array connection information.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            hardware_connector (HardwareConnector, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            hardware_connector=hardware_connector,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._hardware_connectors_api.api210_hardware_connectors_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_hardware_connectors_performance(
        self,
        references=None,  # type: List[models.ReferenceType]
        end_time=None,  # type: int
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        resolution=None,  # type: int
        sort=None,  # type: List[str]
        start_time=None,  # type: int
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.HardwareConnectorPerformanceGetResponse
        """
        Displays network statistics, historical bandwidth, and error reporting for all
        specified hardware connectors.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            end_time (int, optional):
                When the time window ends (in milliseconds since epoch).
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            resolution (int, optional):
                The desired ms between samples. Available resolutions may depend on data type,
                `start_time` and `end_time`. In general `1000`, `30000`, `300000`, `1800000`,
                `7200000`, and `86400000` are possible values.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            start_time (int, optional):
                When the time window starts (in milliseconds since epoch).
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
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
            end_time=end_time,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            resolution=resolution,
            sort=sort,
            start_time=start_time,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._hardware_connectors_api.api210_hardware_connectors_performance_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_keytabs(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete a Kerberos keytab file.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._keytabs_api.api210_keytabs_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_keytabs_download(
        self,
        keytabs=None,  # type: List[models.ReferenceType]
        keytab_ids=None,  # type: List[str]
        keytab_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.KeytabFileResponse
        """
        Download a Kerberos keytab file. The file can be downloaded in the native binary
        format or a base64 encoded format. If not specified, defaults to binary.

        Args:
            keytabs (list[FixedReference], optional):
                A list of keytabs to query for. Overrides keytab_ids and keytab_names keyword arguments.

            keytab_ids (list[str], optional):
                A list of keytab IDs. If after filtering, there is not at least one resource
                that matches each of the elements, then an error is returned. This cannot be
                provided together with the `keytab_names` query parameter.
            keytab_names (list[str], optional):
                A list of keytab names. If there is not at least one resource that matches each
                of the elements, then an error is returned. This cannot be provided together
                with `keytab_ids` query parameter.
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
            keytab_ids=keytab_ids,
            keytab_names=keytab_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._keytabs_api.api210_keytabs_download_get_with_http_info
        _process_references(keytabs, ['keytab_ids', 'keytab_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_keytabs(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.KeytabGetResponse
        """
        List a Kerberos keytab file and its configuration information.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._keytabs_api.api210_keytabs_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_keytabs(
        self,
        keytab=None,  # type: models.KeytabPost
        name_prefixes=None,  # type: str
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.KeytabResponse
        """
        Import a Kerberos keytab file from a Key Distribution Center.

        Args:

            keytab (KeytabPost, required):
            name_prefixes (str, optional):
                The prefix to use for the names of all Kerberos keytab objects that are being
                created.
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
            keytab=keytab,
            name_prefixes=name_prefixes,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._keytabs_api.api210_keytabs_post_with_http_info
        return self._call_api(endpoint, kwargs)

    def post_keytabs_upload(
        self,
        keytab_file=None,  # type: models.ERRORUNKNOWN
        name_prefixes=None,  # type: str
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.KeytabFileResponse
        """
        Upload a Kerberos keytab file to the array. The file can be uploaded in the
        native binary format or a base64 encoded format. If not specified, defaults to
        binary. The procedure to upload a file may vary depending on the type of REST
        client.

        Args:

            keytab_file (ERRORUNKNOWN, required):
                The keytab file to upload.
            name_prefixes (str, optional):
                The prefix to use for the names of all Kerberos keytab objects that are being
                created.
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
            keytab_file=keytab_file,
            name_prefixes=name_prefixes,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._keytabs_api.api210_keytabs_upload_post_with_http_info
        return self._call_api(endpoint, kwargs)

    def delete_kmip(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        ids=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Deletes a KMIP server configuration. A server can only be deleted when not in
        use by the array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names and ids keyword arguments.

            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
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
            names=names,
            ids=ids,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._kmip_api.api210_kmip_delete_with_http_info
        _process_references(references, ['names', 'ids'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_kmip(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        ids=None,  # type: List[str]
        filter=None,  # type: str
        limit=None,  # type: int
        offset=None,  # type: int
        sort=None,  # type: List[str]
        continuation_token=None,  # type: str
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.KmipServerResponse
        """
        Displays a list of KMIP server configurations.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names and ids keyword arguments.

            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
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
            names=names,
            ids=ids,
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            continuation_token=continuation_token,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._kmip_api.api210_kmip_get_with_http_info
        _process_references(references, ['names', 'ids'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_kmip(
        self,
        references=None,  # type: List[models.ReferenceType]
        kmip_server=None,  # type: models.KmipServer
        names=None,  # type: List[str]
        ids=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.KmipServerResponse
        """
        Modifies KMIP server properties - URI, certificate, certificate group.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names and ids keyword arguments.

            kmip_server (KmipServer, required):
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
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
            kmip_server=kmip_server,
            names=names,
            ids=ids,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._kmip_api.api210_kmip_patch_with_http_info
        _process_references(references, ['names', 'ids'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_kmip(
        self,
        references=None,  # type: List[models.ReferenceType]
        kmip_server=None,  # type: models.KmipServer
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.KmipServerResponse
        """
        Creates a KMIP server configuration.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            kmip_server (KmipServer, required):
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            kmip_server=kmip_server,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._kmip_api.api210_kmip_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_kmip_test(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        ids=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.TestResultResponse
        """
        Displays a detailed result of of KMIP server test.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names and ids keyword arguments.

            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
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
            names=names,
            ids=ids,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._kmip_api.api210_kmip_test_get_with_http_info
        _process_references(references, ['names', 'ids'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_lifecycle_rules(
        self,
        buckets=None,  # type: List[models.ReferenceType]
        references=None,  # type: List[models.ReferenceType]
        bucket_ids=None,  # type: List[str]
        bucket_names=None,  # type: List[str]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Deletes individual lifecycle rules by name or id, or deletes all rules for a
        bucket. If `ids` is specified, `bucket_names` or `bucket_ids` is also required.
        If `bucket_names` or `bucket_ids` are specified without `ids`, delete all the
        rules for the bucket.

        Args:
            buckets (list[FixedReference], optional):
                A list of buckets to query for. Overrides bucket_ids and bucket_names keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            bucket_ids (list[str], optional):
                A list of bucket IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `bucket_ids`, then an error is returned.
                This cannot be provided together with the `bucket_names` query parameter. This
                can be provided with the `ids` query parameter but not with `names`.
            bucket_names (list[str], optional):
                A list of bucket names. If there is not at least one resource that matches each
                of the elements of `bucket_names`, then an error is returned. This cannot be
                provided together with the `bucket_ids` query parameter. This can be provided
                with the `ids` query parameter but not with `names`.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            bucket_ids=bucket_ids,
            bucket_names=bucket_names,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._lifecycle_rules_api.api210_lifecycle_rules_delete_with_http_info
        _process_references(buckets, ['bucket_ids', 'bucket_names'], kwargs)
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_lifecycle_rules(
        self,
        buckets=None,  # type: List[models.ReferenceType]
        references=None,  # type: List[models.ReferenceType]
        bucket_ids=None,  # type: List[str]
        bucket_names=None,  # type: List[str]
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
        # type: (...) -> models.LifecycleRuleGetResponse
        """
        Returns a list of lifecycle rules. If `names` is specified, list the individual
        rules. If `ids` is specified, `bucket_names` or `bucket_ids` is also required.
        If `bucket_names` or `bucket_ids` are specified without `ids`, list all the
        rules for the bucket.

        Args:
            buckets (list[FixedReference], optional):
                A list of buckets to query for. Overrides bucket_ids and bucket_names keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            bucket_ids (list[str], optional):
                A list of bucket IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `bucket_ids`, then an error is returned.
                This cannot be provided together with the `bucket_names` query parameter. This
                can be provided with the `ids` query parameter but not with `names`.
            bucket_names (list[str], optional):
                A list of bucket names. If there is not at least one resource that matches each
                of the elements of `bucket_names`, then an error is returned. This cannot be
                provided together with the `bucket_ids` query parameter. This can be provided
                with the `ids` query parameter but not with `names`.
            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            bucket_ids=bucket_ids,
            bucket_names=bucket_names,
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
        endpoint = self._lifecycle_rules_api.api210_lifecycle_rules_get_with_http_info
        _process_references(buckets, ['bucket_ids', 'bucket_names'], kwargs)
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_lifecycle_rules(
        self,
        buckets=None,  # type: List[models.ReferenceType]
        references=None,  # type: List[models.ReferenceType]
        lifecycle=None,  # type: models.LifecycleRulePatch
        bucket_ids=None,  # type: List[str]
        bucket_names=None,  # type: List[str]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        confirm_date=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.LifecycleRuleResponse
        """
        Modify an existing lifecycle rule by name or id. If `ids` is specified,
        `bucket_names` or `bucket_ids` is also required.

        Args:
            buckets (list[FixedReference], optional):
                A list of buckets to query for. Overrides bucket_ids and bucket_names keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            lifecycle (LifecycleRulePatch, required):
            bucket_ids (list[str], optional):
                A list of bucket IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `bucket_ids`, then an error is returned.
                This cannot be provided together with the `bucket_names` query parameter. This
                can be provided with the `ids` query parameter but not with `names`.
            bucket_names (list[str], optional):
                A list of bucket names. If there is not at least one resource that matches each
                of the elements of `bucket_names`, then an error is returned. This cannot be
                provided together with the `bucket_ids` query parameter. This can be provided
                with the `ids` query parameter but not with `names`.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            confirm_date (bool, optional):
                If set to `true`, then confirm the date of `keep_current_version_until` is
                correct.
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
            lifecycle=lifecycle,
            bucket_ids=bucket_ids,
            bucket_names=bucket_names,
            ids=ids,
            names=names,
            confirm_date=confirm_date,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._lifecycle_rules_api.api210_lifecycle_rules_patch_with_http_info
        _process_references(buckets, ['bucket_ids', 'bucket_names'], kwargs)
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_lifecycle_rules(
        self,
        rule=None,  # type: models.LifecycleRulePost
        confirm_date=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.LifecycleRuleResponse
        """
        Creates a lifecycle rule. `bucket` and `keep_previous_version_for` are required.
        If `rule_id` is not specified, it will be automatically generated in the format
        \"fbRuleIdX\".

        Args:

            rule (LifecycleRulePost, required):
            confirm_date (bool, optional):
                If set to `true`, then confirm the date of `keep_current_version_until` is
                correct.
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
            rule=rule,
            confirm_date=confirm_date,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._lifecycle_rules_api.api210_lifecycle_rules_post_with_http_info
        return self._call_api(endpoint, kwargs)

    def delete_link_aggregation_groups(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Remove a link aggregation group to unbind the ports.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._link_aggregation_groups_api.api210_link_aggregation_groups_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_link_aggregation_groups(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.LinkAggregationGroupGetResponse
        """
        List the status and attributes of the Ethernet ports in the configured link
        aggregation groups.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._link_aggregation_groups_api.api210_link_aggregation_groups_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_link_aggregation_groups(
        self,
        references=None,  # type: List[models.ReferenceType]
        link_aggregation_group=None,  # type: models.Linkaggregationgroup
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.LinkAggregationGroupResponse
        """
        Modify link aggregation groups by adding and removing Ethernet ports.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            link_aggregation_group (Linkaggregationgroup, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            link_aggregation_group=link_aggregation_group,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._link_aggregation_groups_api.api210_link_aggregation_groups_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_link_aggregation_groups(
        self,
        references=None,  # type: List[models.ReferenceType]
        link_aggregation_group=None,  # type: models.LinkAggregationGroup
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.LinkAggregationGroupResponse
        """
        Create a link aggregation group of Ethernet ports on the array.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            link_aggregation_group (LinkAggregationGroup, required):
            names (list[str], required):
                A list of resource names.
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
            link_aggregation_group=link_aggregation_group,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._link_aggregation_groups_api.api210_link_aggregation_groups_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_logs_async_download(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.file
        """
        Download the files which contain a history of log events from the array to
        provide to Pure Technical Services for analysis.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._logs_api.api210_logs_async_download_get_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_logs_async(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.LogsAsyncGetResponse
        """
        List the attributes and status of preparation for a history of log events from
        the array to provide to Pure Technical Services for analysis.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._logs_api.api210_logs_async_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_logs_async(
        self,
        logs_async=None,  # type: models.LogsAsync
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.LogsAsyncResponse
        """
        Start the preparation for a history of log events from the array to provide to
        Pure Technical Services for analysis.

        Args:

            logs_async (LogsAsync, required):
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
            logs_async=logs_async,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._logs_api.api210_logs_async_patch_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_logs(
        self,
        end_time=None,  # type: int
        start_time=None,  # type: int
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.file
        """
        Download a history of log events from the array to provide to Pure Technical
        Services for analysis.

        Args:

            end_time (int, optional):
                When the time window ends (in milliseconds since epoch).
            start_time (int, optional):
                When the time window starts (in milliseconds since epoch).
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
            end_time=end_time,
            start_time=start_time,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._logs_api.api210_logs_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def delete_network_interfaces(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Remove a data VIP. Once removed, any clients connected through the data VIP will
        lose their connection to the file system.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._network_interfaces_api.api210_network_interfaces_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_network_interfaces(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        List network interfaces and their attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._network_interfaces_api.api210_network_interfaces_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_network_interfaces(
        self,
        references=None,  # type: List[models.ReferenceType]
        network_interface=None,  # type: models.NetworkInterfacePatch
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.NetworkInterfaceResponse
        """
        Modify the attributes of a data VIP.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            network_interface (NetworkInterfacePatch, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            network_interface=network_interface,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._network_interfaces_api.api210_network_interfaces_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_network_interfaces_ping(
        self,
        destination=None,  # type: str
        packet_size=None,  # type: int
        count=None,  # type: int
        component_name=None,  # type: str
        source=None,  # type: str
        print_latency=None,  # type: bool
        resolve_hostname=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.NetworkInterfacePingGetResponse
        """
        Display network interface ping result.

        Args:

            destination (str, required):
                A destination specified by user to run the network diagnosis against. Can be a
                hostname or an IP.
            packet_size (int, optional):
                Used by ping to specify the number of data bytes to be sent per packet. If not
                specified, defaults to 56.
            count (int, optional):
                Used by ping to specify the number of packets to send. If not specified,
                defaults to 1.
            component_name (str, optional):
                Used by ping and trace to specify where to run the operation. Valid values are
                controllers and blades from hardware list. If not specified, defaults to all
                available controllers and selected blades.
            source (str, optional):
                Used by ping and trace to specify the property where to start to run the
                specified operation. The property can be subnet or IP.
            print_latency (bool, optional):
                Used by ping to specify whether or not to print the full user-to-user latency.
                If not specified, defaults to false.
            resolve_hostname (bool, optional):
                Used by ping and trace to specify whether or not to map IP addresses to host
                names. If not specified, defaults to true.
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
            destination=destination,
            packet_size=packet_size,
            count=count,
            component_name=component_name,
            source=source,
            print_latency=print_latency,
            resolve_hostname=resolve_hostname,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._network_interfaces_api.api210_network_interfaces_ping_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def post_network_interfaces(
        self,
        references=None,  # type: List[models.ReferenceType]
        network_interface=None,  # type: models.NetworkInterface
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.NetworkInterfaceResponse
        """
        Create a data VIP to export a file system.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            network_interface (NetworkInterface, required):
            names (list[str], required):
                A list of resource names.
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
            network_interface=network_interface,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._network_interfaces_api.api210_network_interfaces_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_network_interfaces_trace(
        self,
        destination=None,  # type: str
        fragment_packet=None,  # type: bool
        method=None,  # type: str
        discover_mtu=None,  # type: bool
        component_name=None,  # type: str
        source=None,  # type: str
        port=None,  # type: str
        resolve_hostname=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.NetworkInterfaceTraceGetResponse
        """
        Display network interface trace result.

        Args:

            destination (str, required):
                A destination specified by user to run the network diagnosis against. Can be a
                hostname or an IP.
            fragment_packet (bool, optional):
                Used by trace to specify whether or not to fragment packets. If not specified,
                defaults to true.
            method (str, optional):
                Used by trace to specify which method to use for trace operations. Valid values
                are `icmp`, `tcp`, and `udp`. If not specified, defaults to 'udp'.
            discover_mtu (bool, optional):
                Used by trace to specify whether or not to discover the MTU along the path being
                traced. If not specified, defaults to false.
            component_name (str, optional):
                Used by ping and trace to specify where to run the operation. Valid values are
                controllers and blades from hardware list. If not specified, defaults to all
                available controllers and selected blades.
            source (str, optional):
                Used by ping and trace to specify the property where to start to run the
                specified operation. The property can be subnet or IP.
            port (str, optional):
                Used by trace to specify a destination port.
            resolve_hostname (bool, optional):
                Used by ping and trace to specify whether or not to map IP addresses to host
                names. If not specified, defaults to true.
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
            destination=destination,
            fragment_packet=fragment_packet,
            method=method,
            discover_mtu=discover_mtu,
            component_name=component_name,
            source=source,
            port=port,
            resolve_hostname=resolve_hostname,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._network_interfaces_api.api210_network_interfaces_trace_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def delete_object_store_access_keys(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete an object store access key. Once an access key has been deleted, it
        cannot be recovered.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], required):
                A list of resource names.
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
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_access_keys_api.api210_object_store_access_keys_delete_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_object_store_access_keys(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreAccessKeyGetResponse
        """
        List object store access keys.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            continuation_token=continuation_token,
            filter=filter,
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
        endpoint = self._object_store_access_keys_api.api210_object_store_access_keys_get_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_object_store_access_keys(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        object_store_access_key=None,  # type: models.ObjectStoreAccessKey
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreAccessKeyResponse
        """
        Enable or disable object store access keys.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], required):
                A list of resource names.
            object_store_access_key (ObjectStoreAccessKey, required):
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
            names=names,
            object_store_access_key=object_store_access_key,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_access_keys_api.api210_object_store_access_keys_patch_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_object_store_access_keys(
        self,
        references=None,  # type: List[models.ReferenceType]
        object_store_access_key=None,  # type: models.ObjectStoreAccessKeyPost
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreAccessKeyResponse
        """
        Create or import object store access keys.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            object_store_access_key (ObjectStoreAccessKeyPost, required):
            names (list[str], optional):
                A list of resource names to import. To import a set of credentials, this field
                must be specified with the `secret_access_key` body parameter. If both of these
                are not specified, the system will generate a new set of credentials.
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
            object_store_access_key=object_store_access_key,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_access_keys_api.api210_object_store_access_keys_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_object_store_accounts(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete an object store account.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_accounts_api.api210_object_store_accounts_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_object_store_accounts(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreAccountGetResponse
        """
        List object store accounts and their attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
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
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_accounts_api.api210_object_store_accounts_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_object_store_accounts(
        self,
        references=None,  # type: List[models.ReferenceType]
        object_store_account=None,  # type: models.ObjectStoreAccountPatch
        ids=None,  # type: List[str]
        ignore_usage=None,  # type: bool
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreAccountResponse
        """
        Modify object store account attributes such as quota limit and bucket defaults.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            object_store_account (ObjectStoreAccountPatch, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            ignore_usage (bool, optional):
                Allow update operations that lead to a `hard_limit_enabled` object store
                account, bucket, or file system with usage over its limiting value. For object
                store accounts and buckets, the limiting value is that of `quota_limit`, and for
                file systems it is that of `provisioned`. The operation can be either setting
                `hard_limit_enabled` when usage is higher than the limiting value, or modifying
                the limiting value to a value under usage when `hard_limit_enabled` is `true`.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            object_store_account=object_store_account,
            ids=ids,
            ignore_usage=ignore_usage,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_accounts_api.api210_object_store_accounts_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_object_store_accounts(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        object_store_account=None,  # type: models.ObjectStoreAccountPost
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreAccountResponse
        """
        Create an object store account.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], required):
                A list of resource names.
            object_store_account (ObjectStoreAccountPost, optional):
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
            names=names,
            object_store_account=object_store_account,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_accounts_api.api210_object_store_accounts_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_object_store_remote_credentials(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete object store remote credentials.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_remote_credentials_api.api210_object_store_remote_credentials_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_object_store_remote_credentials(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.ObjectStoreRemoteCredentialGetResp
        """
        List object store remote credentials used by bucket replica links to access
        buckets on remote arrays or targets.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._object_store_remote_credentials_api.api210_object_store_remote_credentials_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_object_store_remote_credentials(
        self,
        references=None,  # type: List[models.ReferenceType]
        remote_credentials=None,  # type: models.ObjectStoreRemoteCredentials
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreRemoteCredentialsResp
        """
        Rename and/or change the access key/secret key pair for object store remote
        credentials.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            remote_credentials (ObjectStoreRemoteCredentials, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            remote_credentials=remote_credentials,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_remote_credentials_api.api210_object_store_remote_credentials_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_object_store_remote_credentials(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        remote_credentials=None,  # type: models.ObjectStoreRemoteCredentialsPost
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreRemoteCredentialsResp
        """
        Create object store remote credentials to set up bucket replicat links to a
        remote array or target.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], required):
                A list of resource names.
            remote_credentials (ObjectStoreRemoteCredentialsPost, required):
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
            names=names,
            remote_credentials=remote_credentials,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_remote_credentials_api.api210_object_store_remote_credentials_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_object_store_users(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete an object store user.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_users_api.api210_object_store_users_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_object_store_users(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.ObjectStoreUserGetResponse
        """
        List object store users and their attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._object_store_users_api.api210_object_store_users_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_object_store_users_object_store_access_policies(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Revoke an object store user’s access policy.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_users_api.api210_object_store_users_object_store_access_policies_delete_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_object_store_users_object_store_access_policies(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        offset=None,  # type: int
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMemberGetResponse
        """
        List object store users and their access policies.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_users_api.api210_object_store_users_object_store_access_policies_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_object_store_users_object_store_access_policies(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMemberResponse
        """
        Grant access policies to an object store user.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_users_api.api210_object_store_users_object_store_access_policies_post_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_object_store_users(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        full_access=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreUserResponse
        """
        Create object store users to administer object storage for an object store
        account.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], required):
                A list of resource names.
            full_access (bool, optional):
                If set to `true`, creates an object store user with full permissions. If set to
                `false`, creates an object store user with no permission. If not specified,
                defaults to `false`.
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
            names=names,
            full_access=full_access,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_users_api.api210_object_store_users_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_object_store_virtual_hosts(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete an object store virtual host.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_virtual_hosts_api.api210_object_store_virtual_hosts_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_object_store_virtual_hosts(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.ObjectStoreVirtualHostGetResponse
        """
        List object store virtual hosts.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._object_store_virtual_hosts_api.api210_object_store_virtual_hosts_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_object_store_virtual_hosts(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreVirtualHostResponse
        """
        Create an object store virtual host. An example of a hostname is
        buckethost.example.com. A hostname cannot exceed 255 characters in length, it
        cannot be an IP address, only 10 hostnames are supported, supersets or subsets
        of existing hostnames with the same root are not allowed. The default hostname
        is s3.amazonaws.com and it cannot be deleted.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], required):
                A list of resource names.
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
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._object_store_virtual_hosts_api.api210_object_store_virtual_hosts_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_nfs_export_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        versions=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete one or more NFS export policies.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            versions (list[str], optional):
                A list of versions. This is an optional query param used for concurrency
                control. The ordering should match the names or ids query param. This will fail
                with a 412 Precondition failed if the resource was changed and the current
                version of the resource doesn't match the value in the query param.
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
            ids=ids,
            names=names,
            versions=versions,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___nfs_api.api210_nfs_export_policies_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_nfs_export_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.NfsExportPolicyGetResponse
        """
        Displays a list of NFS export policies.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._policies___nfs_api.api210_nfs_export_policies_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_nfs_export_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        policy=None,  # type: models.NfsExportPolicy
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        versions=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.NfsExportPolicyResponse
        """
        Modify an existing NFS export policy's attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            policy (NfsExportPolicy, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            versions (list[str], optional):
                A list of versions. This is an optional query param used for concurrency
                control. The ordering should match the names or ids query param. This will fail
                with a 412 Precondition failed if the resource was changed and the current
                version of the resource doesn't match the value in the query param.
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
            policy=policy,
            ids=ids,
            names=names,
            versions=versions,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___nfs_api.api210_nfs_export_policies_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_nfs_export_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        policy=None,  # type: models.NfsExportPolicyPost
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.NfsExportPolicyResponse
        """
        Create a new NFS export policy.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], required):
                A list of resource names.
            policy (NfsExportPolicyPost, optional):
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
            names=names,
            policy=policy,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___nfs_api.api210_nfs_export_policies_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_nfs_export_policies_rules(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        versions=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete one or more NFS export policy rules. One of the following is required:
        `ids` or `names`.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            versions (list[str], optional):
                A list of versions. This is an optional query param used for concurrency
                control. The ordering should match the names or ids query param. This will fail
                with a 412 Precondition failed if the resource was changed and the current
                version of the resource doesn't match the value in the query param.
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
            ids=ids,
            names=names,
            versions=versions,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___nfs_api.api210_nfs_export_policies_rules_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_nfs_export_policies_rules(
        self,
        references=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.NfsExportPolicyRuleGetResponse
        """
        Displays a list of NFS export policy rules. The default sort is by policy name,
        then index.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            policy_ids=policy_ids,
            policy_names=policy_names,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___nfs_api.api210_nfs_export_policies_rules_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_nfs_export_policies_rules(
        self,
        references=None,  # type: List[models.ReferenceType]
        rule=None,  # type: models.NfsExportPolicyRule
        before_rule_id=None,  # type: str
        before_rule_name=None,  # type: str
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        versions=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.NfsExportPolicyRuleResponse
        """
        Modify an existing NFS export policy rule. If `before_rule_id` or
        `before_rule_name` are specified, the rule will be moved before that rule. Rules
        are ordered in three groups; ip addresses, other and `*` and can only be moved
        within the appropriate group. One of the following is required: `ids` or
        `names`.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            rule (NfsExportPolicyRule, required):
            before_rule_id (str, optional):
                The id of the rule to insert or move a rule before. This cannot be provided
                together with the `before_rule_name` query parameter.
            before_rule_name (str, optional):
                The name of the rule to insert or move a rule before. This cannot be provided
                together with the `before_rule_id` query parameter.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            versions (list[str], optional):
                A list of versions. This is an optional query param used for concurrency
                control. The ordering should match the names or ids query param. This will fail
                with a 412 Precondition failed if the resource was changed and the current
                version of the resource doesn't match the value in the query param.
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
            rule=rule,
            before_rule_id=before_rule_id,
            before_rule_name=before_rule_name,
            ids=ids,
            names=names,
            versions=versions,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___nfs_api.api210_nfs_export_policies_rules_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_nfs_export_policies_rules(
        self,
        policies=None,  # type: List[models.ReferenceType]
        rule=None,  # type: models.NfsExportPolicyRule
        before_rule_id=None,  # type: str
        before_rule_name=None,  # type: str
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        versions=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.NfsExportPolicyRuleResponse
        """
        Add a NFS export policy rule. Rules are ordered in three groups; ip addresses,
        other and `*`. The new rule will be added at the end of the appropriate group if
        neither `before_rule_id` and `before_rule_name` are specified. Rules can only be
        inserted into the appropriate group. Either `policy_ids` or `policy_names`
        parameter is required.

        Args:
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            rule (NfsExportPolicyRule, required):
            before_rule_id (str, optional):
                The id of the rule to insert or move a rule before. This cannot be provided
                together with the `before_rule_name` query parameter.
            before_rule_name (str, optional):
                The name of the rule to insert or move a rule before. This cannot be provided
                together with the `before_rule_id` query parameter.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
            versions (list[str], optional):
                A list of versions. This is an optional query param used for concurrency
                control. The ordering should match the names or ids query param. This will fail
                with a 412 Precondition failed if the resource was changed and the current
                version of the resource doesn't match the value in the query param.
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
            rule=rule,
            before_rule_id=before_rule_id,
            before_rule_name=before_rule_name,
            policy_ids=policy_ids,
            policy_names=policy_names,
            versions=versions,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___nfs_api.api210_nfs_export_policies_rules_post_with_http_info
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_object_store_access_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete one or more access policies.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___object_store_access_api.api210_object_store_access_policies_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_object_store_access_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        exclude_rules=None,  # type: bool
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
        # type: (...) -> models.ObjectStoreAccessPolicyGetResponse
        """
        List access policies and their attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            exclude_rules (bool, optional):
                If true, the rules field in each policy will be null. If false, each returned
                policy will include its list of rules in the response. If not specified,
                defaults to `false`.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            continuation_token=continuation_token,
            exclude_rules=exclude_rules,
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
        endpoint = self._policies___object_store_access_api.api210_object_store_access_policies_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_object_store_access_policies_object_store_users(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Revokes an object store user's access policy.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___object_store_access_api.api210_object_store_access_policies_object_store_users_delete_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_object_store_access_policies_object_store_users(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        offset=None,  # type: int
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMemberGetResponse
        """
        List object store users and their access policies.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___object_store_access_api.api210_object_store_access_policies_object_store_users_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_object_store_access_policies_object_store_users(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMemberResponse
        """
        Grant access policies to an object store user.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___object_store_access_api.api210_object_store_access_policies_object_store_users_post_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_object_store_access_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        enforce_action_restrictions=None,  # type: bool
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        policy=None,  # type: models.ObjectStoreAccessPolicyPatch
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreAccessPolicyResponse
        """
        Modify the rules of an object store access policy.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            enforce_action_restrictions (bool, optional):
                Certain combinations of actions and other rule elements are inherently ignored
                if specified together in a rule. If set to `true`, operations which attempt to
                set these combinations will fail. If set to `false`, such operations will
                instead be allowed. Defaults to `true`.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            policy (ObjectStoreAccessPolicyPatch, optional):
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
            enforce_action_restrictions=enforce_action_restrictions,
            ids=ids,
            names=names,
            policy=policy,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___object_store_access_api.api210_object_store_access_policies_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_object_store_access_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        enforce_action_restrictions=None,  # type: bool
        policy=None,  # type: models.ObjectStoreAccessPolicyPost
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreAccessPolicyResponse
        """
        Create a new access policy.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], required):
                A list of resource names.
            enforce_action_restrictions (bool, optional):
                Certain combinations of actions and other rule elements are inherently ignored
                if specified together in a rule. If set to `true`, operations which attempt to
                set these combinations will fail. If set to `false`, such operations will
                instead be allowed. Defaults to `true`.
            policy (ObjectStoreAccessPolicyPost, optional):
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
            names=names,
            enforce_action_restrictions=enforce_action_restrictions,
            policy=policy,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___object_store_access_api.api210_object_store_access_policies_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_object_store_access_policies_rules(
        self,
        references=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete one or more access policy rules.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            names=names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___object_store_access_api.api210_object_store_access_policies_rules_delete_with_http_info
        _process_references(references, ['names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_object_store_access_policies_rules(
        self,
        references=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreAccessPolicyRuleGetResponse
        """
        List access policy rules and their attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            names=names,
            offset=offset,
            policy_ids=policy_ids,
            policy_names=policy_names,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___object_store_access_api.api210_object_store_access_policies_rules_get_with_http_info
        _process_references(references, ['names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_object_store_access_policies_rules(
        self,
        references=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        rule=None,  # type: models.PolicyRuleObjectAccess
        enforce_action_restrictions=None,  # type: bool
        names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreAccessPolicyRuleResponse
        """
        Modify an access policy rule's attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            rule (PolicyRuleObjectAccess, required):
            enforce_action_restrictions (bool, optional):
                Certain combinations of actions and other rule elements are inherently ignored
                if specified together in a rule. If set to `true`, operations which attempt to
                set these combinations will fail. If set to `false`, such operations will
                instead be allowed. Defaults to `true`.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            rule=rule,
            enforce_action_restrictions=enforce_action_restrictions,
            names=names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___object_store_access_api.api210_object_store_access_policies_rules_patch_with_http_info
        _process_references(references, ['names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_object_store_access_policies_rules(
        self,
        references=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        rule=None,  # type: models.PolicyRuleObjectAccessPost
        enforce_action_restrictions=None,  # type: bool
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreAccessPolicyRuleResponse
        """
        Create a new access policy rule.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            names (list[str], required):
                A list of resource names.
            rule (PolicyRuleObjectAccessPost, required):
            enforce_action_restrictions (bool, optional):
                Certain combinations of actions and other rule elements are inherently ignored
                if specified together in a rule. If set to `true`, operations which attempt to
                set these combinations will fail. If set to `false`, such operations will
                instead be allowed. Defaults to `true`.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            names=names,
            rule=rule,
            enforce_action_restrictions=enforce_action_restrictions,
            policy_ids=policy_ids,
            policy_names=policy_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___object_store_access_api.api210_object_store_access_policies_rules_post_with_http_info
        _process_references(references, ['names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_object_store_access_policy_actions(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ObjectStoreAccessPolicyActionGetResponse
        """
        List valid actions for access policy rules. Each action is either a valid AWS S3
        action (prefixed by `s3:`) or our special wildcard action (`s3:*`). Each action,
        when included in a rule, may restrict which other properties may be set for that
        rule.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            continuation_token=continuation_token,
            filter=filter,
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
        endpoint = self._policies___object_store_access_api.api210_object_store_access_policy_actions_get_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_smb_client_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete one or more SMB Client policies.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___smb_client_api.api210_smb_client_policies_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_smb_client_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.SmbClientPolicyGetResponse
        """
        Display SMB Client policies and their attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._policies___smb_client_api.api210_smb_client_policies_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_smb_client_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        policy=None,  # type: models.SmbClientPolicy
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SmbClientPolicyResponse
        """
        Modify an existing SMB Client policy's attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            policy (SmbClientPolicy, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            policy=policy,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___smb_client_api.api210_smb_client_policies_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_smb_client_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        policy=None,  # type: models.SmbClientPolicyPost
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SmbClientPolicyResponse
        """
        Create a new SMB Client policy.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], required):
                A list of resource names.
            policy (SmbClientPolicyPost, optional):
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
            names=names,
            policy=policy,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___smb_client_api.api210_smb_client_policies_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_smb_client_policies_rules(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        versions=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete one or more SMB Client policy rules. One of the following is required:
        `ids` or `names`.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            versions (list[str], optional):
                A list of versions. This is an optional query param used for concurrency
                control. The ordering should match the names or ids query param. This will fail
                with a 412 Precondition failed if the resource was changed and the current
                version of the resource doesn't match the value in the query param.
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
            ids=ids,
            names=names,
            versions=versions,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___smb_client_api.api210_smb_client_policies_rules_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_smb_client_policies_rules(
        self,
        references=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SmbClientPolicyRuleGetResponse
        """
        Displays a list of SMB Client policy rules. The default sort is by policy name,
        then index.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            policy_ids=policy_ids,
            policy_names=policy_names,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___smb_client_api.api210_smb_client_policies_rules_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_smb_client_policies_rules(
        self,
        references=None,  # type: List[models.ReferenceType]
        rule=None,  # type: models.SmbClientPolicyRule
        before_rule_id=None,  # type: str
        before_rule_name=None,  # type: str
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        versions=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SmbClientPolicyRuleResponse
        """
        Modify an existing SMB Client policy rule. If `before_rule_id` or
        `before_rule_name` are specified, the rule will be moved before that rule. Rules
        are ordered in three groups; ip addresses, other and `*` and can only be moved
        within the appropriate group. One of the following is required: `ids` or
        `names`.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            rule (SmbClientPolicyRule, required):
            before_rule_id (str, optional):
                The id of the rule to insert or move a rule before. This cannot be provided
                together with the `before_rule_name` query parameter.
            before_rule_name (str, optional):
                The name of the rule to insert or move a rule before. This cannot be provided
                together with the `before_rule_id` query parameter.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            versions (list[str], optional):
                A list of versions. This is an optional query param used for concurrency
                control. The ordering should match the names or ids query param. This will fail
                with a 412 Precondition failed if the resource was changed and the current
                version of the resource doesn't match the value in the query param.
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
            rule=rule,
            before_rule_id=before_rule_id,
            before_rule_name=before_rule_name,
            ids=ids,
            names=names,
            versions=versions,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___smb_client_api.api210_smb_client_policies_rules_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_smb_client_policies_rules(
        self,
        policies=None,  # type: List[models.ReferenceType]
        rule=None,  # type: models.SmbClientPolicyRulePost
        before_rule_id=None,  # type: str
        before_rule_name=None,  # type: str
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        versions=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SmbClientPolicyRuleResponse
        """
        Add an SMB Client policy rule. Rules are ordered in three groups; ip addresses,
        other and `*`. The new rule will be added at the end of the appropriate group if
        neither `before_rule_id` nor `before_rule_name` are specified. Rules can only be
        inserted into the appropriate group. The `policy_ids` or `policy_names`
        parameter is required, but they cannot be set together.

        Args:
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            rule (SmbClientPolicyRulePost, required):
            before_rule_id (str, optional):
                The id of the rule to insert or move a rule before. This cannot be provided
                together with the `before_rule_name` query parameter.
            before_rule_name (str, optional):
                The name of the rule to insert or move a rule before. This cannot be provided
                together with the `before_rule_id` query parameter.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
            versions (list[str], optional):
                A list of versions. This is an optional query param used for concurrency
                control. The ordering should match the names or ids query param. This will fail
                with a 412 Precondition failed if the resource was changed and the current
                version of the resource doesn't match the value in the query param.
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
            rule=rule,
            before_rule_id=before_rule_id,
            before_rule_name=before_rule_name,
            policy_ids=policy_ids,
            policy_names=policy_names,
            versions=versions,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___smb_client_api.api210_smb_client_policies_rules_post_with_http_info
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_smb_share_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete one or more SMB Share policies.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___smb_share_api.api210_smb_share_policies_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_smb_share_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.SmbSharePolicyGetResponse
        """
        Display SMB Share policies and their attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._policies___smb_share_api.api210_smb_share_policies_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_smb_share_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        policy=None,  # type: models.SmbSharePolicy
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SmbSharePolicyResponse
        """
        Modify an existing SMB Share policy's attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            policy (SmbSharePolicy, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            policy=policy,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___smb_share_api.api210_smb_share_policies_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_smb_share_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        policy=None,  # type: models.SmbSharePolicyPost
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SmbSharePolicyResponse
        """
        Create a new SMB Share policy.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], required):
                A list of resource names.
            policy (SmbSharePolicyPost, optional):
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
            names=names,
            policy=policy,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___smb_share_api.api210_smb_share_policies_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_smb_share_policies_rules(
        self,
        references=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete one or more SMB Share policy rules. One of the following is required:
        `ids` or `names`. If `names` is provided, the `policy_ids` or `policy_names`
        parameter is also required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            ids=ids,
            names=names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___smb_share_api.api210_smb_share_policies_rules_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_smb_share_policies_rules(
        self,
        references=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SmbSharePolicyRuleGetResponse
        """
        Displays a list of SMB Share policy rules.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            continuation_token=continuation_token,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            policy_ids=policy_ids,
            policy_names=policy_names,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___smb_share_api.api210_smb_share_policies_rules_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_smb_share_policies_rules(
        self,
        references=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        rule=None,  # type: models.SmbSharePolicyRule
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SmbSharePolicyRuleResponse
        """
        Modify an existing SMB Share policy rule. One of the following is required:
        `ids` or `names`. If `names` is provided, the `policy_ids` or `policy_names`
        parameter is also required.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            rule (SmbSharePolicyRule, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            rule=rule,
            ids=ids,
            names=names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___smb_share_api.api210_smb_share_policies_rules_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_smb_share_policies_rules(
        self,
        policies=None,  # type: List[models.ReferenceType]
        rule=None,  # type: models.SmbSharePolicyRulePost
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SmbSharePolicyRuleResponse
        """
        Add an SMB Share policy rule. The `policy_ids` or `policy_names` parameter is
        required, but they cannot be set together.

        Args:
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            rule (SmbSharePolicyRulePost, required):
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            rule=rule,
            policy_ids=policy_ids,
            policy_names=policy_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___smb_share_api.api210_smb_share_policies_rules_post_with_http_info
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete one or more snapshot scheduling policies.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___snapshot_api.api210_policies_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_policies_file_system_replica_links(
        self,
        local_file_systems=None,  # type: List[models.ReferenceType]
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        local_file_system_ids=None,  # type: List[str]
        local_file_system_names=None,  # type: List[str]
        member_ids=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Remove a snapshot scheduling policy mapped to a file system replica link.

        Args:
            local_file_systems (list[FixedReference], optional):
                A list of local_file_systems to query for. Overrides local_file_system_ids and local_file_system_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.

            local_file_system_ids (list[str], optional):
                A list of local file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `local_file_system_names` query parameter.
            local_file_system_names (list[str], optional):
                A list of local file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with `local_file_system_ids` query parameter.
            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
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
            local_file_system_ids=local_file_system_ids,
            local_file_system_names=local_file_system_names,
            member_ids=member_ids,
            policy_ids=policy_ids,
            policy_names=policy_names,
            remote_ids=remote_ids,
            remote_names=remote_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___snapshot_api.api210_policies_file_system_replica_links_delete_with_http_info
        _process_references(local_file_systems, ['local_file_system_ids', 'local_file_system_names'], kwargs)
        _process_references(members, ['member_ids'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_policies_file_system_replica_links(
        self,
        local_file_systems=None,  # type: List[models.ReferenceType]
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        remote_file_systems=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        local_file_system_ids=None,  # type: List[str]
        local_file_system_names=None,  # type: List[str]
        member_ids=None,  # type: List[str]
        offset=None,  # type: int
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        remote_file_system_ids=None,  # type: List[str]
        remote_file_system_names=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMemberWithRemoteGetResponse
        """
        List snapshot scheduling policies for file system replica links.

        Args:
            local_file_systems (list[FixedReference], optional):
                A list of local_file_systems to query for. Overrides local_file_system_ids and local_file_system_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.
            remote_file_systems (list[FixedReference], optional):
                A list of remote_file_systems to query for. Overrides remote_file_system_ids and remote_file_system_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            local_file_system_ids (list[str], optional):
                A list of local file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `local_file_system_names` query parameter.
            local_file_system_names (list[str], optional):
                A list of local file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with `local_file_system_ids` query parameter.
            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_file_system_ids (list[str], optional):
                A list of remote file system IDs. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with the `remote_file_system_names` query parameter.
            remote_file_system_names (list[str], optional):
                A list of remote file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with the `remote_file_system_ids` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
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
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            local_file_system_ids=local_file_system_ids,
            local_file_system_names=local_file_system_names,
            member_ids=member_ids,
            offset=offset,
            policy_ids=policy_ids,
            policy_names=policy_names,
            remote_ids=remote_ids,
            remote_file_system_ids=remote_file_system_ids,
            remote_file_system_names=remote_file_system_names,
            remote_names=remote_names,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___snapshot_api.api210_policies_file_system_replica_links_get_with_http_info
        _process_references(local_file_systems, ['local_file_system_ids', 'local_file_system_names'], kwargs)
        _process_references(members, ['member_ids'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        _process_references(remote_file_systems, ['remote_file_system_ids', 'remote_file_system_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_policies_file_system_replica_links(
        self,
        local_file_systems=None,  # type: List[models.ReferenceType]
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        local_file_system_ids=None,  # type: List[str]
        local_file_system_names=None,  # type: List[str]
        member_ids=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMemberWithRemoteResponse
        """
        Add a snapshot scheduling policy to a file system replica link.

        Args:
            local_file_systems (list[FixedReference], optional):
                A list of local_file_systems to query for. Overrides local_file_system_ids and local_file_system_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.

            local_file_system_ids (list[str], optional):
                A list of local file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `local_file_system_names` query parameter.
            local_file_system_names (list[str], optional):
                A list of local file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with `local_file_system_ids` query parameter.
            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
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
            local_file_system_ids=local_file_system_ids,
            local_file_system_names=local_file_system_names,
            member_ids=member_ids,
            policy_ids=policy_ids,
            policy_names=policy_names,
            remote_ids=remote_ids,
            remote_names=remote_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___snapshot_api.api210_policies_file_system_replica_links_post_with_http_info
        _process_references(local_file_systems, ['local_file_system_ids', 'local_file_system_names'], kwargs)
        _process_references(members, ['member_ids'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_policies_file_system_snapshots(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Remove the snapshot scheduling policy mapped to a file system.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___snapshot_api.api210_policies_file_system_snapshots_delete_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_policies_file_system_snapshots(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        offset=None,  # type: int
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyFileSystemSnapshotGetResponse
        """
        List file system snapshots mapped to a snapshot scheduling policy.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___snapshot_api.api210_policies_file_system_snapshots_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_policies_file_systems(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Remove the snapshot scheduling policy mapped to a file system.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___snapshot_api.api210_policies_file_systems_delete_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_policies_file_systems(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        offset=None,  # type: int
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMemberGetResponse
        """
        List file systems mapped to a snapshot scheduling policy.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___snapshot_api.api210_policies_file_systems_get_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_policies_file_systems(
        self,
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMemberResponse
        """
        Map a file system to a snapshot scheduling policy.

        Args:
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.

            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
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
            member_ids=member_ids,
            member_names=member_names,
            policy_ids=policy_ids,
            policy_names=policy_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___snapshot_api.api210_policies_file_systems_post_with_http_info
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        Display snapshot scheduling policies and their attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._policies___snapshot_api.api210_policies_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_policies_members(
        self,
        local_file_systems=None,  # type: List[models.ReferenceType]
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        remote_file_systems=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        local_file_system_ids=None,  # type: List[str]
        local_file_system_names=None,  # type: List[str]
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        member_types=None,  # type: List[models.ModelsFB210ResourceTypeYaml]
        offset=None,  # type: int
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        remote_file_system_ids=None,  # type: List[str]
        remote_file_system_names=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMemberWithRemoteGetResponse
        """
        List snapshot scheduling policies mapped to file systems, snapshots, and file
        system replica links.

        Args:
            local_file_systems (list[FixedReference], optional):
                A list of local_file_systems to query for. Overrides local_file_system_ids and local_file_system_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.
            remote_file_systems (list[FixedReference], optional):
                A list of remote_file_systems to query for. Overrides remote_file_system_ids and remote_file_system_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            local_file_system_ids (list[str], optional):
                A list of local file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `local_file_system_names` query parameter.
            local_file_system_names (list[str], optional):
                A list of local file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with `local_file_system_ids` query parameter.
            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            member_types (list[ModelsFB210ResourceTypeYaml], optional):
                A list of member types. Valid values are `file-systems`, `file-system-
                snapshots`, `file-system-replica-links`, and `object-store-users`. Different
                endpoints may accept different subsets of these values.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_file_system_ids (list[str], optional):
                A list of remote file system IDs. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with the `remote_file_system_names` query parameter.
            remote_file_system_names (list[str], optional):
                A list of remote file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with the `remote_file_system_ids` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
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
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            local_file_system_ids=local_file_system_ids,
            local_file_system_names=local_file_system_names,
            member_ids=member_ids,
            member_names=member_names,
            member_types=member_types,
            offset=offset,
            policy_ids=policy_ids,
            policy_names=policy_names,
            remote_ids=remote_ids,
            remote_file_system_ids=remote_file_system_ids,
            remote_file_system_names=remote_file_system_names,
            remote_names=remote_names,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___snapshot_api.api210_policies_members_get_with_http_info
        _process_references(local_file_systems, ['local_file_system_ids', 'local_file_system_names'], kwargs)
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        _process_references(remote_file_systems, ['remote_file_system_ids', 'remote_file_system_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        policy=None,  # type: models.PolicyPatch
        ids=None,  # type: List[str]
        destroy_snapshots=None,  # type: bool
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyResponse
        """
        Modify a snapshot scheduling policy’s attributes for when and how often
        snapshots are created and how long they are retained.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            policy (PolicyPatch, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            destroy_snapshots (bool, optional):
                This parameter must be set to `true` in order to modify a policy such that local
                or remote snapshots would be destroyed.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            policy=policy,
            ids=ids,
            destroy_snapshots=destroy_snapshots,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___snapshot_api.api210_policies_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_policies(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        policy=None,  # type: models.Policy
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyResponse
        """
        Create a new snapshot scheduling policy with rule attributes to capture file
        system snapshots for a set period of time and frequency, as well as how long
        snapshots are retained before being destroyed and eradicated.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], required):
                A list of resource names.
            policy (Policy, optional):
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
            names=names,
            policy=policy,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies___snapshot_api.api210_policies_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_policies_all(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.PolicyBaseGetResponse
        """
        List all policies of all types.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._policies__all_api.api210_policies_all_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_policies_all_members(
        self,
        local_file_systems=None,  # type: List[models.ReferenceType]
        members=None,  # type: List[models.ReferenceType]
        policies=None,  # type: List[models.ReferenceType]
        remotes=None,  # type: List[models.ReferenceType]
        remote_file_systems=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        filter=None,  # type: str
        limit=None,  # type: int
        local_file_system_ids=None,  # type: List[str]
        local_file_system_names=None,  # type: List[str]
        member_ids=None,  # type: List[str]
        member_names=None,  # type: List[str]
        member_types=None,  # type: List[models.ModelsFB210ResourceTypeYaml]
        offset=None,  # type: int
        policy_ids=None,  # type: List[str]
        policy_names=None,  # type: List[str]
        remote_ids=None,  # type: List[str]
        remote_file_system_ids=None,  # type: List[str]
        remote_file_system_names=None,  # type: List[str]
        remote_names=None,  # type: List[str]
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.PolicyMemberWithRemoteGetResponse
        """
        List policies (of all types) mapped to other entities (file systems, snapshots,
        file system replica links, and object store users).

        Args:
            local_file_systems (list[FixedReference], optional):
                A list of local_file_systems to query for. Overrides local_file_system_ids and local_file_system_names keyword arguments.
            members (list[FixedReference], optional):
                A list of members to query for. Overrides member_ids and member_names keyword arguments.
            policies (list[FixedReference], optional):
                A list of policies to query for. Overrides policy_ids and policy_names keyword arguments.
            remotes (list[FixedReference], optional):
                A list of remotes to query for. Overrides remote_ids and remote_names keyword arguments.
            remote_file_systems (list[FixedReference], optional):
                A list of remote_file_systems to query for. Overrides remote_file_system_ids and remote_file_system_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            local_file_system_ids (list[str], optional):
                A list of local file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `local_file_system_names` query parameter.
            local_file_system_names (list[str], optional):
                A list of local file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with `local_file_system_ids` query parameter.
            member_ids (list[str], optional):
                A list of member IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `member_ids`, then an error is returned.
                This cannot be provided together with the `member_names` query parameter.
            member_names (list[str], optional):
                A list of member names.
            member_types (list[ModelsFB210ResourceTypeYaml], optional):
                A list of member types. Valid values are `file-systems`, `file-system-
                snapshots`, `file-system-replica-links`, and `object-store-users`. Different
                endpoints may accept different subsets of these values.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            policy_ids (list[str], optional):
                A list of policy IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `policy_ids`, then an error is returned.
                This cannot be provided together with the `policy_names` query parameter.
            policy_names (list[str], optional):
                A list of policy names.
            remote_ids (list[str], optional):
                A list of remote array IDs. If after filtering, there is not at least one
                resource that matches each of the elements, then an error is returned. This
                cannot be provided together with the `remote_names` query parameter.
            remote_file_system_ids (list[str], optional):
                A list of remote file system IDs. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with the `remote_file_system_names` query parameter.
            remote_file_system_names (list[str], optional):
                A list of remote file system names. If there is not at least one resource that
                matches each of the elements, then an error is returned. This cannot be provided
                together with the `remote_file_system_ids` query parameter.
            remote_names (list[str], optional):
                A list of remote array names. If there is not at least one resource that matches
                each of the elements, then an error is returned. This cannot be provided
                together with `remote_ids` query parameter.
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
            continuation_token=continuation_token,
            filter=filter,
            limit=limit,
            local_file_system_ids=local_file_system_ids,
            local_file_system_names=local_file_system_names,
            member_ids=member_ids,
            member_names=member_names,
            member_types=member_types,
            offset=offset,
            policy_ids=policy_ids,
            policy_names=policy_names,
            remote_ids=remote_ids,
            remote_file_system_ids=remote_file_system_ids,
            remote_file_system_names=remote_file_system_names,
            remote_names=remote_names,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._policies__all_api.api210_policies_all_members_get_with_http_info
        _process_references(local_file_systems, ['local_file_system_ids', 'local_file_system_names'], kwargs)
        _process_references(members, ['member_ids', 'member_names'], kwargs)
        _process_references(policies, ['policy_ids', 'policy_names'], kwargs)
        _process_references(remotes, ['remote_ids', 'remote_names'], kwargs)
        _process_references(remote_file_systems, ['remote_file_system_ids', 'remote_file_system_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_quotas_groups(
        self,
        file_systems=None,  # type: List[models.ReferenceType]
        groups=None,  # type: List[models.ReferenceType]
        references=None,  # type: List[models.ReferenceType]
        file_system_names=None,  # type: List[str]
        file_system_ids=None,  # type: List[str]
        gids=None,  # type: List[int]
        group_names=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete a hard limit quota for a group.

        Args:
            file_systems (list[FixedReference], optional):
                A list of file_systems to query for. Overrides file_system_names and file_system_ids keyword arguments.
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            file_system_names (list[str], optional):
                A list of file system names. If there is not at least one resource that matches
                each of the elements of `file_system_names`, then an error is returned.
            file_system_ids (list[str], optional):
                A list of file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements of `file_system_ids`, then an error
                is returned. This cannot be provided together with the `file_system_names` query
                parameter.
            gids (list[int], optional):
                A list of group IDs. If there is not at least one resource that matches each of
                the elements of `gids`, then an error is returned. This cannot be provided
                together with `group_names` query parameter.
            group_names (list[str], optional):
                A list of group names. If there is not at least one resource that matches each
                of the elements of `group_names`, then an error is returned. This cannot be
                provided together with `gids` query parameter.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            file_system_names=file_system_names,
            file_system_ids=file_system_ids,
            gids=gids,
            group_names=group_names,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._quotas_api.api210_quotas_groups_delete_with_http_info
        _process_references(file_systems, ['file_system_names', 'file_system_ids'], kwargs)
        _process_references(groups, ['group_names'], kwargs)
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_quotas_groups(
        self,
        file_systems=None,  # type: List[models.ReferenceType]
        groups=None,  # type: List[models.ReferenceType]
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        file_system_ids=None,  # type: List[str]
        file_system_names=None,  # type: List[str]
        filter=None,  # type: str
        gids=None,  # type: List[int]
        group_names=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.GroupQuotaGetResponse
        """
        List groups with hard limit quotas.

        Args:
            file_systems (list[FixedReference], optional):
                A list of file_systems to query for. Overrides file_system_ids and file_system_names keyword arguments.
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            file_system_ids (list[str], optional):
                A list of file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements of `file_system_ids`, then an error
                is returned. This cannot be provided together with the `file_system_names` query
                parameter.
            file_system_names (list[str], optional):
                A list of file system names. If there is not at least one resource that matches
                each of the elements of `file_system_names`, then an error is returned.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            gids (list[int], optional):
                A list of group IDs. If there is not at least one resource that matches each of
                the elements of `gids`, then an error is returned. This cannot be provided
                together with `group_names` query parameter.
            group_names (list[str], optional):
                A list of group names. If there is not at least one resource that matches each
                of the elements of `group_names`, then an error is returned. This cannot be
                provided together with `gids` query parameter.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            continuation_token=continuation_token,
            file_system_ids=file_system_ids,
            file_system_names=file_system_names,
            filter=filter,
            gids=gids,
            group_names=group_names,
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
        endpoint = self._quotas_api.api210_quotas_groups_get_with_http_info
        _process_references(file_systems, ['file_system_ids', 'file_system_names'], kwargs)
        _process_references(groups, ['group_names'], kwargs)
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_quotas_groups(
        self,
        file_systems=None,  # type: List[models.ReferenceType]
        groups=None,  # type: List[models.ReferenceType]
        references=None,  # type: List[models.ReferenceType]
        file_system_names=None,  # type: List[str]
        file_system_ids=None,  # type: List[str]
        gids=None,  # type: List[int]
        group_names=None,  # type: List[str]
        names=None,  # type: List[str]
        quota=None,  # type: models.GroupQuotaPatch
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.GroupQuotaResponse
        """
        Modify a quota for a group. Note that if you modify a group's quota to a lower
        value and that group's usage has already exceeded the new value, writes will
        automatically halt until usage decreases below the new quota setting.

        Args:
            file_systems (list[FixedReference], optional):
                A list of file_systems to query for. Overrides file_system_names and file_system_ids keyword arguments.
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            file_system_names (list[str], optional):
                A list of file system names. If there is not at least one resource that matches
                each of the elements of `file_system_names`, then an error is returned.
            file_system_ids (list[str], optional):
                A list of file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements of `file_system_ids`, then an error
                is returned. This cannot be provided together with the `file_system_names` query
                parameter.
            gids (list[int], optional):
                A list of group IDs. If there is not at least one resource that matches each of
                the elements of `gids`, then an error is returned. This cannot be provided
                together with `group_names` query parameter.
            group_names (list[str], optional):
                A list of group names. If there is not at least one resource that matches each
                of the elements of `group_names`, then an error is returned. This cannot be
                provided together with `gids` query parameter.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            quota (GroupQuotaPatch, optional):
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
            file_system_names=file_system_names,
            file_system_ids=file_system_ids,
            gids=gids,
            group_names=group_names,
            names=names,
            quota=quota,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._quotas_api.api210_quotas_groups_patch_with_http_info
        _process_references(file_systems, ['file_system_names', 'file_system_ids'], kwargs)
        _process_references(groups, ['group_names'], kwargs)
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_quotas_groups(
        self,
        file_systems=None,  # type: List[models.ReferenceType]
        groups=None,  # type: List[models.ReferenceType]
        file_system_ids=None,  # type: List[str]
        file_system_names=None,  # type: List[str]
        gids=None,  # type: List[int]
        group_names=None,  # type: List[str]
        quota=None,  # type: models.GroupQuotaPost
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.GroupQuotaResponse
        """
        Create a hard limit quota for a group.

        Args:
            file_systems (list[FixedReference], optional):
                A list of file_systems to query for. Overrides file_system_ids and file_system_names keyword arguments.
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.

            file_system_ids (list[str], optional):
                A list of file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements of `file_system_ids`, then an error
                is returned. This cannot be provided together with the `file_system_names` query
                parameter.
            file_system_names (list[str], optional):
                A list of file system names. If there is not at least one resource that matches
                each of the elements of `file_system_names`, then an error is returned.
            gids (list[int], optional):
                A list of group IDs. If there is not at least one resource that matches each of
                the elements of `gids`, then an error is returned. This cannot be provided
                together with `group_names` query parameter.
            group_names (list[str], optional):
                A list of group names. If there is not at least one resource that matches each
                of the elements of `group_names`, then an error is returned. This cannot be
                provided together with `gids` query parameter.
            quota (GroupQuotaPost, optional):
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
            file_system_ids=file_system_ids,
            file_system_names=file_system_names,
            gids=gids,
            group_names=group_names,
            quota=quota,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._quotas_api.api210_quotas_groups_post_with_http_info
        _process_references(file_systems, ['file_system_ids', 'file_system_names'], kwargs)
        _process_references(groups, ['group_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_quotas_settings(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.QuotaSettingGetResponse
        """
        List notification attributes of a group or user quota.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._quotas_api.api210_quotas_settings_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_quotas_settings(
        self,
        quota_setting=None,  # type: models.QuotaSetting
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.QuotaSettingResponse
        """
        Modify the notification attributes of a group or user quota.

        Args:

            quota_setting (QuotaSetting, required):
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
            quota_setting=quota_setting,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._quotas_api.api210_quotas_settings_patch_with_http_info
        return self._call_api(endpoint, kwargs)

    def delete_quotas_users(
        self,
        file_systems=None,  # type: List[models.ReferenceType]
        references=None,  # type: List[models.ReferenceType]
        users=None,  # type: List[models.ReferenceType]
        file_system_names=None,  # type: List[str]
        file_system_ids=None,  # type: List[str]
        names=None,  # type: List[str]
        uids=None,  # type: List[int]
        user_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete a hard limit file system quota for a user.

        Args:
            file_systems (list[FixedReference], optional):
                A list of file_systems to query for. Overrides file_system_names and file_system_ids keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.
            users (list[FixedReference], optional):
                A list of users to query for. Overrides user_names keyword arguments.

            file_system_names (list[str], optional):
                A list of file system names. If there is not at least one resource that matches
                each of the elements of `file_system_names`, then an error is returned.
            file_system_ids (list[str], optional):
                A list of file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements of `file_system_ids`, then an error
                is returned. This cannot be provided together with the `file_system_names` query
                parameter.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            uids (list[int], optional):
                A list of user IDs. If there is not at least one resource that matches each of
                the elements of `uids`, then an error is returned. This cannot be provided
                together with `user_names` query parameter.
            user_names (list[str], optional):
                A list of user names. If there is not at least one resource that matches each of
                the elements of `user_names`, then an error is returned. This cannot be provided
                together with `uids` query parameter.
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
            file_system_names=file_system_names,
            file_system_ids=file_system_ids,
            names=names,
            uids=uids,
            user_names=user_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._quotas_api.api210_quotas_users_delete_with_http_info
        _process_references(file_systems, ['file_system_names', 'file_system_ids'], kwargs)
        _process_references(references, ['names'], kwargs)
        _process_references(users, ['user_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_quotas_users(
        self,
        file_systems=None,  # type: List[models.ReferenceType]
        references=None,  # type: List[models.ReferenceType]
        users=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        file_system_ids=None,  # type: List[str]
        file_system_names=None,  # type: List[str]
        filter=None,  # type: str
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        uids=None,  # type: List[int]
        user_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.UserQuotaGetResponse
        """
        List users with hard limit file system quotas.

        Args:
            file_systems (list[FixedReference], optional):
                A list of file_systems to query for. Overrides file_system_ids and file_system_names keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.
            users (list[FixedReference], optional):
                A list of users to query for. Overrides user_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            file_system_ids (list[str], optional):
                A list of file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements of `file_system_ids`, then an error
                is returned. This cannot be provided together with the `file_system_names` query
                parameter.
            file_system_names (list[str], optional):
                A list of file system names. If there is not at least one resource that matches
                each of the elements of `file_system_names`, then an error is returned.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            uids (list[int], optional):
                A list of user IDs. If there is not at least one resource that matches each of
                the elements of `uids`, then an error is returned. This cannot be provided
                together with `user_names` query parameter.
            user_names (list[str], optional):
                A list of user names. If there is not at least one resource that matches each of
                the elements of `user_names`, then an error is returned. This cannot be provided
                together with `uids` query parameter.
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
            continuation_token=continuation_token,
            file_system_ids=file_system_ids,
            file_system_names=file_system_names,
            filter=filter,
            limit=limit,
            names=names,
            offset=offset,
            sort=sort,
            uids=uids,
            user_names=user_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._quotas_api.api210_quotas_users_get_with_http_info
        _process_references(file_systems, ['file_system_ids', 'file_system_names'], kwargs)
        _process_references(references, ['names'], kwargs)
        _process_references(users, ['user_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_quotas_users(
        self,
        file_systems=None,  # type: List[models.ReferenceType]
        references=None,  # type: List[models.ReferenceType]
        users=None,  # type: List[models.ReferenceType]
        file_system_names=None,  # type: List[str]
        file_system_ids=None,  # type: List[str]
        names=None,  # type: List[str]
        uids=None,  # type: List[int]
        user_names=None,  # type: List[str]
        quota=None,  # type: models.UserQuotaPatch
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.UserQuotaResponse
        """
        Modify the attributes of a hard limit file system quota. Note that if you modify
        a user's quota to a lower value and that user’s usage has already exceeded the
        new value, writes will automatically halt until usage decreases below the new
        quota setting.

        Args:
            file_systems (list[FixedReference], optional):
                A list of file_systems to query for. Overrides file_system_names and file_system_ids keyword arguments.
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.
            users (list[FixedReference], optional):
                A list of users to query for. Overrides user_names keyword arguments.

            file_system_names (list[str], optional):
                A list of file system names. If there is not at least one resource that matches
                each of the elements of `file_system_names`, then an error is returned.
            file_system_ids (list[str], optional):
                A list of file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements of `file_system_ids`, then an error
                is returned. This cannot be provided together with the `file_system_names` query
                parameter.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            uids (list[int], optional):
                A list of user IDs. If there is not at least one resource that matches each of
                the elements of `uids`, then an error is returned. This cannot be provided
                together with `user_names` query parameter.
            user_names (list[str], optional):
                A list of user names. If there is not at least one resource that matches each of
                the elements of `user_names`, then an error is returned. This cannot be provided
                together with `uids` query parameter.
            quota (UserQuotaPatch, optional):
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
            file_system_names=file_system_names,
            file_system_ids=file_system_ids,
            names=names,
            uids=uids,
            user_names=user_names,
            quota=quota,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._quotas_api.api210_quotas_users_patch_with_http_info
        _process_references(file_systems, ['file_system_names', 'file_system_ids'], kwargs)
        _process_references(references, ['names'], kwargs)
        _process_references(users, ['user_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_quotas_users(
        self,
        file_systems=None,  # type: List[models.ReferenceType]
        users=None,  # type: List[models.ReferenceType]
        file_system_ids=None,  # type: List[str]
        file_system_names=None,  # type: List[str]
        uids=None,  # type: List[int]
        user_names=None,  # type: List[str]
        quota=None,  # type: models.UserQuotaPost
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.UserQuotaResponse
        """
        Create a hard limit file system quota for a user.

        Args:
            file_systems (list[FixedReference], optional):
                A list of file_systems to query for. Overrides file_system_ids and file_system_names keyword arguments.
            users (list[FixedReference], optional):
                A list of users to query for. Overrides user_names keyword arguments.

            file_system_ids (list[str], optional):
                A list of file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements of `file_system_ids`, then an error
                is returned. This cannot be provided together with the `file_system_names` query
                parameter.
            file_system_names (list[str], optional):
                A list of file system names. If there is not at least one resource that matches
                each of the elements of `file_system_names`, then an error is returned.
            uids (list[int], optional):
                A list of user IDs. If there is not at least one resource that matches each of
                the elements of `uids`, then an error is returned. This cannot be provided
                together with `user_names` query parameter.
            user_names (list[str], optional):
                A list of user names. If there is not at least one resource that matches each of
                the elements of `user_names`, then an error is returned. This cannot be provided
                together with `uids` query parameter.
            quota (UserQuotaPost, optional):
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
            file_system_ids=file_system_ids,
            file_system_names=file_system_names,
            uids=uids,
            user_names=user_names,
            quota=quota,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._quotas_api.api210_quotas_users_post_with_http_info
        _process_references(file_systems, ['file_system_ids', 'file_system_names'], kwargs)
        _process_references(users, ['user_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_rapid_data_locking(
        self,
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.RapidDataLockingResponse
        """
        Displays the status of the Rapid Data Locking feature.

        Args:

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
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._rdl_api.api210_rapid_data_locking_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def patch_rapid_data_locking(
        self,
        rapid_data_locking=None,  # type: models.RapidDataLocking
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.RapidDataLockingResponse
        """
        Modifies the Rapid Data Locking feature. Note that the feature can only be
        enabled if there are no file systems nor buckets created on the array. Once
        enabled, the feature cannot be modified.

        Args:

            rapid_data_locking (RapidDataLocking, required):
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
            rapid_data_locking=rapid_data_locking,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._rdl_api.api210_rapid_data_locking_patch_with_http_info
        return self._call_api(endpoint, kwargs)

    def post_rapid_data_locking_rotate(
        self,
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Rotates the external keys on the associated EKM appliance.

        Args:

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
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._rdl_api.api210_rapid_data_locking_rotate_post_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_rapid_data_locking_test(
        self,
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.TestResultResponse
        """
        Displays a detailed result of a Rapid Data Locking test.

        Args:

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
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._rdl_api.api210_rapid_data_locking_test_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_roles(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        ids=None,  # type: List[str]
        filter=None,  # type: str
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.RoleGetResponse
        """
        List roles and permission attributes for role-based access control (RBAC).

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            continuation_token=continuation_token,
            ids=ids,
            filter=filter,
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
        endpoint = self._roles_api.api210_roles_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_sessions(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.SessionGetResponse
        """
        Displays session data for user login events performed in the Purity//FB GUI,
        CLI, and REST API.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._sessions_api.api210_sessions_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_smtp_servers(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.SmtpServerGetResponse
        """
        List SMTP server attributes for the array network.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._smtp_api.api210_smtp_servers_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_smtp_servers(
        self,
        smtp=None,  # type: models.SmtpServer
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SmtpServerResponse
        """
        Modify SMTP server attributes such as the relay host and sender domain.

        Args:

            smtp (SmtpServer, required):
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
            smtp=smtp,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._smtp_api.api210_smtp_servers_patch_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_snmp_agents(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.SnmpAgentGetResponse
        """
        List SNMP agent attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._snmp_agents_api.api210_snmp_agents_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_snmp_agents_mib(
        self,
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SnmpAgentMibResponse
        """
        List the SNMP MIB text.

        Args:

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
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._snmp_agents_api.api210_snmp_agents_mib_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def patch_snmp_agents(
        self,
        snmp_agent=None,  # type: models.SnmpAgent
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SnmpAgentResponse
        """
        Modify SNMP agent attributes.

        Args:

            snmp_agent (SnmpAgent, required):
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
            snmp_agent=snmp_agent,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._snmp_agents_api.api210_snmp_agents_patch_with_http_info
        return self._call_api(endpoint, kwargs)

    def delete_snmp_managers(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Remove an SNMP manager.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._snmp_managers_api.api210_snmp_managers_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_snmp_managers(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        ids=None,  # type: List[str]
        filter=None,  # type: str
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SnmpManagerGetResponse
        """
        List SNMP managers and their attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            continuation_token=continuation_token,
            ids=ids,
            filter=filter,
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
        endpoint = self._snmp_managers_api.api210_snmp_managers_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_snmp_managers(
        self,
        references=None,  # type: List[models.ReferenceType]
        snmp_manager=None,  # type: models.SnmpManager
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SnmpManagerResponse
        """
        Modify SNMP manager attributes such as versions.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            snmp_manager (SnmpManager, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            snmp_manager=snmp_manager,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._snmp_managers_api.api210_snmp_managers_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_snmp_managers(
        self,
        references=None,  # type: List[models.ReferenceType]
        snmp_manager=None,  # type: models.SnmpManagerPost
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SnmpManagerResponse
        """
        Create an SNMP manager.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            snmp_manager (SnmpManagerPost, required):
            names (list[str], required):
                A list of resource names.
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
            snmp_manager=snmp_manager,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._snmp_managers_api.api210_snmp_managers_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_snmp_managers_test(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        ids=None,  # type: List[str]
        filter=None,  # type: str
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.TestResultGetResponse
        """
        Test if the configuration of an SNMP manager is valid.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            continuation_token=continuation_token,
            ids=ids,
            filter=filter,
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
        endpoint = self._snmp_managers_api.api210_snmp_managers_test_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def delete_subnets(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Remove an array subnet.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._subnets_api.api210_subnets_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_subnets(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.SubnetGetResponse
        """
        List the array’s subnets.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._subnets_api.api210_subnets_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_subnets(
        self,
        references=None,  # type: List[models.ReferenceType]
        subnet=None,  # type: models.Subnet
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SubnetResponse
        """
        Modify array subnet attributes.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            subnet (Subnet, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            subnet=subnet,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._subnets_api.api210_subnets_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_subnets(
        self,
        references=None,  # type: List[models.ReferenceType]
        subnet=None,  # type: models.Subnet
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SubnetResponse
        """
        Create an array subnet.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            subnet (Subnet, required):
            names (list[str], required):
                A list of resource names.
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
            subnet=subnet,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._subnets_api.api210_subnets_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_support(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SupportGetResponse
        """
        List Phone Home and Remote Assistance settings.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._support_api.api210_support_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_support(
        self,
        support=None,  # type: models.Support
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SupportResponse
        """
        Modify Phone Home and Remote Assistance settings.

        Args:

            support (Support, required):
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
            support=support,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._support_api.api210_support_patch_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_support_test(
        self,
        filter=None,  # type: str
        sort=None,  # type: List[str]
        test_type=None,  # type: str
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.TestResultGetResponse
        """
        Test if the Phone Home and Remote Assistance settings are functioning properly.

        Args:

            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            test_type (str, optional):
                Specify the type of test. Valid values are `all`, `phonehome` and `remote-
                assist`. If not specified, defaults to `all`.
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
            filter=filter,
            sort=sort,
            test_type=test_type,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._support_api.api210_support_test_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def delete_syslog_servers(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete a configured syslog server and stop forwarding syslog messages.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._syslog_api.api210_syslog_servers_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_syslog_servers(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.SyslogServerGetResponse
        """
        Return a list of configured syslog servers.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                Performs the operation on the unique name specified. Enter multiple names in
                comma-separated format. For example, `name01,name02`.
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
        endpoint = self._syslog_api.api210_syslog_servers_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_syslog_servers(
        self,
        references=None,  # type: List[models.ReferenceType]
        syslog_server=None,  # type: models.SyslogServerPostOrPatch
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SyslogServerResponse
        """
        Modify the URI of a configured syslog server.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            syslog_server (SyslogServerPostOrPatch, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
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
            syslog_server=syslog_server,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._syslog_api.api210_syslog_servers_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_syslog_servers(
        self,
        references=None,  # type: List[models.ReferenceType]
        syslog_server=None,  # type: models.SyslogServerPostOrPatch
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SyslogServerResponse
        """
        Configure a new syslog server. Transmission of syslog messages is enabled
        immediately.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            syslog_server (SyslogServerPostOrPatch, required):
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
            syslog_server=syslog_server,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._syslog_api.api210_syslog_servers_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_syslog_servers_settings(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        # type: (...) -> models.SyslogServerSettingsGetResponse
        """
        List the certificate or certificate group associated with the syslog servers.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._syslog_api.api210_syslog_servers_settings_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_syslog_servers_settings(
        self,
        references=None,  # type: List[models.ReferenceType]
        syslog_server_settings=None,  # type: models.SyslogServerSettings
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.SyslogServerSettingsResponse
        """
        Modify the certificate or certificate group associated with the syslog servers.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            syslog_server_settings (SyslogServerSettings, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            syslog_server_settings=syslog_server_settings,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._syslog_api.api210_syslog_servers_settings_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_syslog_servers_test(
        self,
        continuation_token=None,  # type: str
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.TestResultGetResponse
        """
        Send test messages to conifgured remote syslog servers.

        Args:

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
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
            continuation_token=continuation_token,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._syslog_api.api210_syslog_servers_test_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def delete_targets(
        self,
        references=None,  # type: List[models.ReferenceType]
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Delete the connection to the target for replication.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._targets_api.api210_targets_delete_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_targets(
        self,
        references=None,  # type: List[models.ReferenceType]
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
        List targets used for replication.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
        endpoint = self._targets_api.api210_targets_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def patch_targets(
        self,
        references=None,  # type: List[models.ReferenceType]
        target=None,  # type: models.Target
        ids=None,  # type: List[str]
        names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.TargetResponse
        """
        Modify the target attributes for replication.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            target (Target, required):
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
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
            target=target,
            ids=ids,
            names=names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._targets_api.api210_targets_patch_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_targets_performance_replication(
        self,
        references=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        end_time=None,  # type: int
        filter=None,  # type: str
        ids=None,  # type: List[str]
        limit=None,  # type: int
        names=None,  # type: List[str]
        offset=None,  # type: int
        resolution=None,  # type: int
        sort=None,  # type: List[str]
        start_time=None,  # type: int
        total_only=None,  # type: bool
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.ResourcePerformanceReplicationGetResponse
        """
        List replication performance metrics for targets.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides ids and names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            end_time (int, optional):
                When the time window ends (in milliseconds since epoch).
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            ids (list[str], optional):
                A list of resource IDs. If after filtering, there is not at least one resource
                that matches each of the elements of `ids`, then an error is returned. This
                cannot be provided together with the `name` or `names` query parameters.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            names (list[str], optional):
                A list of resource names. If there is not at least one resource that matches
                each of the elements of `names`, then an error is returned.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            resolution (int, optional):
                The desired ms between samples. Available resolutions may depend on data type,
                `start_time` and `end_time`. In general `1000`, `30000`, `300000`, `1800000`,
                `7200000`, and `86400000` are possible values.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            start_time (int, optional):
                When the time window starts (in milliseconds since epoch).
            total_only (bool, optional):
                Only return the total record for the specified items. The total record will be
                the total of all items after filtering. The `items` list will be empty.
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
            continuation_token=continuation_token,
            end_time=end_time,
            filter=filter,
            ids=ids,
            limit=limit,
            names=names,
            offset=offset,
            resolution=resolution,
            sort=sort,
            start_time=start_time,
            total_only=total_only,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._targets_api.api210_targets_performance_replication_get_with_http_info
        _process_references(references, ['ids', 'names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def post_targets(
        self,
        references=None,  # type: List[models.ReferenceType]
        names=None,  # type: List[str]
        target=None,  # type: models.TargetPost
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.TargetResponse
        """
        Add a target for replication.

        Args:
            references (list[FixedReference], optional):
                A list of references to query for. Overrides names keyword arguments.

            names (list[str], required):
                A list of resource names.
            target (TargetPost, required):
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
            names=names,
            target=target,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._targets_api.api210_targets_post_with_http_info
        _process_references(references, ['names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_usage_groups(
        self,
        file_systems=None,  # type: List[models.ReferenceType]
        groups=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        file_system_ids=None,  # type: List[str]
        file_system_names=None,  # type: List[str]
        filter=None,  # type: str
        gids=None,  # type: List[int]
        group_names=None,  # type: List[str]
        limit=None,  # type: int
        offset=None,  # type: int
        sort=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.GroupQuotaGetResponse
        """
        List groups with hard limit quotas and their file system usage.

        Args:
            file_systems (list[FixedReference], optional):
                A list of file_systems to query for. Overrides file_system_ids and file_system_names keyword arguments.
            groups (list[FixedReference], optional):
                A list of groups to query for. Overrides group_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            file_system_ids (list[str], optional):
                A list of file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements of `file_system_ids`, then an error
                is returned. This cannot be provided together with the `file_system_names` query
                parameter.
            file_system_names (list[str], optional):
                A list of file system names. If there is not at least one resource that matches
                each of the elements of `file_system_names`, then an error is returned.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            gids (list[int], optional):
                A list of group IDs. If there is not at least one resource that matches each of
                the elements of `gids`, then an error is returned. This cannot be provided
                together with `group_names` query parameter.
            group_names (list[str], optional):
                A list of group names. If there is not at least one resource that matches each
                of the elements of `group_names`, then an error is returned. This cannot be
                provided together with `gids` query parameter.
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
            continuation_token=continuation_token,
            file_system_ids=file_system_ids,
            file_system_names=file_system_names,
            filter=filter,
            gids=gids,
            group_names=group_names,
            limit=limit,
            offset=offset,
            sort=sort,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._usage_api.api210_usage_groups_get_with_http_info
        _process_references(file_systems, ['file_system_ids', 'file_system_names'], kwargs)
        _process_references(groups, ['group_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_usage_users(
        self,
        file_systems=None,  # type: List[models.ReferenceType]
        users=None,  # type: List[models.ReferenceType]
        continuation_token=None,  # type: str
        file_system_ids=None,  # type: List[str]
        file_system_names=None,  # type: List[str]
        filter=None,  # type: str
        limit=None,  # type: int
        offset=None,  # type: int
        sort=None,  # type: List[str]
        uids=None,  # type: List[int]
        user_names=None,  # type: List[str]
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.UserQuotaGetResponse
        """
        List users with hard limit quotas and their file system usage.

        Args:
            file_systems (list[FixedReference], optional):
                A list of file_systems to query for. Overrides file_system_ids and file_system_names keyword arguments.
            users (list[FixedReference], optional):
                A list of users to query for. Overrides user_names keyword arguments.

            continuation_token (str, optional):
                An opaque token to iterate over a collection of resources.
            file_system_ids (list[str], optional):
                A list of file system IDs. If after filtering, there is not at least one
                resource that matches each of the elements of `file_system_ids`, then an error
                is returned. This cannot be provided together with the `file_system_names` query
                parameter.
            file_system_names (list[str], optional):
                A list of file system names. If there is not at least one resource that matches
                each of the elements of `file_system_names`, then an error is returned.
            filter (Filter, optional):
                A filter to include only resources that match the specified criteria.
            limit (int, optional):
                Limit the number of resources in the response. If not specified, defaults to
                1000.
            offset (int, optional):
                The offset of the first resource to return from a collection.
            sort (list[Property], optional):
                Sort the response by the specified Properties. Can also be a single element.
            uids (list[int], optional):
                A list of user IDs. If there is not at least one resource that matches each of
                the elements of `uids`, then an error is returned. This cannot be provided
                together with `user_names` query parameter.
            user_names (list[str], optional):
                A list of user names. If there is not at least one resource that matches each of
                the elements of `user_names`, then an error is returned. This cannot be provided
                together with `uids` query parameter.
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
            continuation_token=continuation_token,
            file_system_ids=file_system_ids,
            file_system_names=file_system_names,
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            uids=uids,
            user_names=user_names,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._usage_api.api210_usage_users_get_with_http_info
        _process_references(file_systems, ['file_system_ids', 'file_system_names'], kwargs)
        _process_references(users, ['user_names'], kwargs)
        return self._call_api(endpoint, kwargs)

    def get_support_verification_keys(
        self,
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
        # type: (...) -> models.VerificationKeyGetResponse
        """
        List the key used to verify the signed challenges that are used by Pure Support
        to access the FlashBlade.

        Args:

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
        endpoint = self._verification_keys_api.api210_support_verification_keys_get_with_http_info
        return self._call_api(endpoint, kwargs)

    def patch_support_verification_keys(
        self,
        key=None,  # type: models.VerificationKeyPatch
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> models.VerificationKeyResponse
        """
        Update the key used to verify the signed challenges that are used by Pure
        Support to access the FlashBlade.

        Args:

            key (VerificationKeyPatch, required):
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
            key=key,
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._verification_keys_api.api210_support_verification_keys_patch_with_http_info
        return self._call_api(endpoint, kwargs)

    def get_versions(
        self,
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> dict
        """
        Get available API versions. No authentication is required to access this
        endpoint.  The response will be a ValidResponse with version ids listed as items.

        Args:

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
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._authorization_api.api_api_version_get_with_http_info
        return self._call_api(endpoint, kwargs, response_creator=self._create_api_versions_response)

    def logout(
        self,
        async_req=False,  # type: bool
        _return_http_data_only=False,  # type: bool
        _preload_content=True,  # type: bool
        _request_timeout=None,  # type: Optional[int]
    ):
        # type: (...) -> None
        """
        Invalidate a REST session token.

        Args:

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
            async_req=async_req,
            _return_http_data_only=_return_http_data_only,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        endpoint = self._authorization_api.api_logout_post_with_http_info
        res = self._call_api(endpoint, kwargs, response_creator=self._create_logout_response)
        # Note: The normal behavior when a call returns a 401 or 403 authentication error status
        # is to reset the authentication token and retry. This effectively logs the client in again.
        # Setting _retries to 0 prevents this behavior for any future calls with this client.
        self._retries = 0
        return res


    def _get_base_url(self, target):
        return 'https://{}'.format(target)

    def _get_api_token_endpoint(self, target):
        return self._get_base_url(target) + '/api/login'

    def _get_api_token_dispose_endpoint(self, target):
        return self._get_base_url(target) + '/api/logout'

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

    def _call_api(self, api_function, kwargs, response_creator=None):
        """
        Call the API function and process the response. May call the API
        repeatedly if the request failed for a reason that may not persist in
        the next call.

        Args:
            api_function (function): Swagger-generated function to call.
            kwargs (dict): kwargs to pass to the function.
            response_creator: optional method to generate a ValidResponse from a non-standard endpoint.
                              If None, use the standard _create_valid_response method.

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
                if response_creator:
                    return response_creator(response, api_function, kwargs)
                else:
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
            # if body is a file then should be a singleton list
            body_items = [body] if type(body) == str else body.items
            items = iter(ItemIterator(self, endpoint, kwargs,
                                      continuation_token, total_item_count,
                                      body_items,
                                      headers.get(Headers.x_request_id, None),
                                      more_items_remaining or False, None))
        return ValidResponse(status, continuation_token, total_item_count,
                             items, headers, total, more_items_remaining)


    def _create_api_versions_response(self, response, endpoint, kwargs):
        """
        Create a ValidResponse from an ApiVersion Swagger response.

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
        continuation_token = None
        total_item_count = None
        total = None
        more_items_remaining = None
        items = None

        if body is not None:
            # if body is a file then should be a singleton list
            body_items = [body] if type(body) == str else body.versions
            items = iter(ItemIterator(self, endpoint, kwargs,
                                      continuation_token, total_item_count,
                                      body_items,
                                      headers.get(Headers.x_request_id, None),
                                      more_items_remaining or False, None))
        response = ValidResponse(status, continuation_token, total_item_count,
                                 items, headers, total, more_items_remaining)
        return response


    def _create_logout_response(self, response, endpoint, kwargs):
        """
           A logout response only contains the status field.
        """
        body, status, headers = response
        continuation_token = None
        total_item_count = None
        total = None
        more_items_remaining = None
        items = None
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
