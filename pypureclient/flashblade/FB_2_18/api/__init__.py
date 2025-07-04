"""
    FlashBlade REST API

    A lightweight client for FlashBlade REST API 2.18, developed by Pure Storage, Inc. (http://www.purestorage.com/).

    The version of the OpenAPI document: 2.18
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


class __LazyApiLoader:
    def __init__(self, modname, attr):
        self._modname  = modname
        self._attr     = attr
        self._mod      = None

    def load(self):
        import importlib
        if self._mod is None:
            self._mod = importlib.__import__(self._modname, globals(), locals(), fromlist=[self._attr], level=1)
        return getattr(self._mod, self._attr)

__class_apis_dict = { 
    'APIClientsApi': __LazyApiLoader('api_clients_api', 'APIClientsApi'),
    'ActiveDirectoryApi': __LazyApiLoader('active_directory_api', 'ActiveDirectoryApi'),
    'AdministratorsApi': __LazyApiLoader('administrators_api', 'AdministratorsApi'),
    'AlertWatchersApi': __LazyApiLoader('alert_watchers_api', 'AlertWatchersApi'),
    'AlertsApi': __LazyApiLoader('alerts_api', 'AlertsApi'),
    'ArrayConnectionsApi': __LazyApiLoader('array_connections_api', 'ArrayConnectionsApi'),
    'ArraysApi': __LazyApiLoader('arrays_api', 'ArraysApi'),
    'AuditsApi': __LazyApiLoader('audits_api', 'AuditsApi'),
    'AuthorizationApi': __LazyApiLoader('authorization_api', 'AuthorizationApi'),
    'BladesApi': __LazyApiLoader('blades_api', 'BladesApi'),
    'BucketReplicaLinksApi': __LazyApiLoader('bucket_replica_links_api', 'BucketReplicaLinksApi'),
    'BucketsApi': __LazyApiLoader('buckets_api', 'BucketsApi'),
    'CertificateGroupsApi': __LazyApiLoader('certificate_groups_api', 'CertificateGroupsApi'),
    'CertificatesApi': __LazyApiLoader('certificates_api', 'CertificatesApi'),
    'ClientsApi': __LazyApiLoader('clients_api', 'ClientsApi'),
    'DNSApi': __LazyApiLoader('dns_api', 'DNSApi'),
    'DirectoryServicesApi': __LazyApiLoader('directory_services_api', 'DirectoryServicesApi'),
    'DrivesApi': __LazyApiLoader('drives_api', 'DrivesApi'),
    'FileSystemExportsApi': __LazyApiLoader('file_system_exports_api', 'FileSystemExportsApi'),
    'FileSystemReplicaLinksApi': __LazyApiLoader('file_system_replica_links_api', 'FileSystemReplicaLinksApi'),
    'FileSystemSnapshotsApi': __LazyApiLoader('file_system_snapshots_api', 'FileSystemSnapshotsApi'),
    'FileSystemsApi': __LazyApiLoader('file_systems_api', 'FileSystemsApi'),
    'FleetsApi': __LazyApiLoader('fleets_api', 'FleetsApi'),
    'HardwareApi': __LazyApiLoader('hardware_api', 'HardwareApi'),
    'HardwareConnectorsApi': __LazyApiLoader('hardware_connectors_api', 'HardwareConnectorsApi'),
    'KMIPApi': __LazyApiLoader('kmip_api', 'KMIPApi'),
    'KeytabsApi': __LazyApiLoader('keytabs_api', 'KeytabsApi'),
    'LegalHoldsApi': __LazyApiLoader('legal_holds_api', 'LegalHoldsApi'),
    'LifecycleRulesApi': __LazyApiLoader('lifecycle_rules_api', 'LifecycleRulesApi'),
    'LinkAggregationGroupsApi': __LazyApiLoader('link_aggregation_groups_api', 'LinkAggregationGroupsApi'),
    'LogsApi': __LazyApiLoader('logs_api', 'LogsApi'),
    'MaintenanceWindowsApi': __LazyApiLoader('maintenance_windows_api', 'MaintenanceWindowsApi'),
    'NetworkInterfacesApi': __LazyApiLoader('network_interfaces_api', 'NetworkInterfacesApi'),
    'NodeGroupsApi': __LazyApiLoader('node_groups_api', 'NodeGroupsApi'),
    'NodesApi': __LazyApiLoader('nodes_api', 'NodesApi'),
    'OIDCSSOApi': __LazyApiLoader('oidcsso_api', 'OIDCSSOApi'),
    'ObjectStoreAccessKeysApi': __LazyApiLoader('object_store_access_keys_api', 'ObjectStoreAccessKeysApi'),
    'ObjectStoreAccountsApi': __LazyApiLoader('object_store_accounts_api', 'ObjectStoreAccountsApi'),
    'ObjectStoreRemoteCredentialsApi': __LazyApiLoader('object_store_remote_credentials_api', 'ObjectStoreRemoteCredentialsApi'),
    'ObjectStoreRolesApi': __LazyApiLoader('object_store_roles_api', 'ObjectStoreRolesApi'),
    'ObjectStoreUsersApi': __LazyApiLoader('object_store_users_api', 'ObjectStoreUsersApi'),
    'ObjectStoreVirtualHostsApi': __LazyApiLoader('object_store_virtual_hosts_api', 'ObjectStoreVirtualHostsApi'),
    'PoliciesAllApi': __LazyApiLoader('policies_all_api', 'PoliciesAllApi'),
    'PoliciesAuditForFileSystemsApi': __LazyApiLoader('policies_audit_for_file_systems_api', 'PoliciesAuditForFileSystemsApi'),
    'PoliciesNFSApi': __LazyApiLoader('policies_nfs_api', 'PoliciesNFSApi'),
    'PoliciesNetworkAccessApi': __LazyApiLoader('policies_network_access_api', 'PoliciesNetworkAccessApi'),
    'PoliciesObjectStoreAccessApi': __LazyApiLoader('policies_object_store_access_api', 'PoliciesObjectStoreAccessApi'),
    'PoliciesPasswordApi': __LazyApiLoader('policies_password_api', 'PoliciesPasswordApi'),
    'PoliciesQoSApi': __LazyApiLoader('policies_qo_s_api', 'PoliciesQoSApi'),
    'PoliciesSMBClientApi': __LazyApiLoader('policies_smb_client_api', 'PoliciesSMBClientApi'),
    'PoliciesSMBShareApi': __LazyApiLoader('policies_smb_share_api', 'PoliciesSMBShareApi'),
    'PoliciesSSHCertificateAuthorityApi': __LazyApiLoader('policies_ssh_certificate_authority_api', 'PoliciesSSHCertificateAuthorityApi'),
    'PoliciesSnapshotApi': __LazyApiLoader('policies_snapshot_api', 'PoliciesSnapshotApi'),
    'PoliciesStorageClassTieringApi': __LazyApiLoader('policies_storage_class_tiering_api', 'PoliciesStorageClassTieringApi'),
    'PoliciesTLSApi': __LazyApiLoader('policies_tls_api', 'PoliciesTLSApi'),
    'PoliciesWORMDataApi': __LazyApiLoader('policies_worm_data_api', 'PoliciesWORMDataApi'),
    'PublicKeysApi': __LazyApiLoader('public_keys_api', 'PublicKeysApi'),
    'QuotasApi': __LazyApiLoader('quotas_api', 'QuotasApi'),
    'RDLApi': __LazyApiLoader('rdl_api', 'RDLApi'),
    'RemoteArraysApi': __LazyApiLoader('remote_arrays_api', 'RemoteArraysApi'),
    'RolesApi': __LazyApiLoader('roles_api', 'RolesApi'),
    'SAML2SSOApi': __LazyApiLoader('saml2_sso_api', 'SAML2SSOApi'),
    'SMTPApi': __LazyApiLoader('smtp_api', 'SMTPApi'),
    'SNMPAgentsApi': __LazyApiLoader('snmp_agents_api', 'SNMPAgentsApi'),
    'SNMPManagersApi': __LazyApiLoader('snmp_managers_api', 'SNMPManagersApi'),
    'ServersApi': __LazyApiLoader('servers_api', 'ServersApi'),
    'SessionsApi': __LazyApiLoader('sessions_api', 'SessionsApi'),
    'SoftwareApi': __LazyApiLoader('software_api', 'SoftwareApi'),
    'SubnetsApi': __LazyApiLoader('subnets_api', 'SubnetsApi'),
    'SupportApi': __LazyApiLoader('support_api', 'SupportApi'),
    'SupportDiagnosticsApi': __LazyApiLoader('support_diagnostics_api', 'SupportDiagnosticsApi'),
    'SyslogApi': __LazyApiLoader('syslog_api', 'SyslogApi'),
    'TargetsApi': __LazyApiLoader('targets_api', 'TargetsApi'),
    'UsageApi': __LazyApiLoader('usage_api', 'UsageApi'),
    'VerificationKeysApi': __LazyApiLoader('verification_keys_api', 'VerificationKeysApi'),
}

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
