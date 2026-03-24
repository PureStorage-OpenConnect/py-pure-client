"""
    FlashBlade REST API
"""

from functools import partial

class __LazyApiLoader:
    def __init__(self, modname, attr, version=None):
        self._modname  = modname
        self._attr     = attr
        self._version  = version
        self._mod      = None

    def load(self):
        import importlib
        if self._mod is None:
            self._mod = importlib.import_module(self._modname, package=__package__)
        cls = getattr(self._mod, self._attr)
        if self._version:
            return partial(cls, version=self._version)
        return cls

__class_apis_dict = {
    'APIClientsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.api_clients_api_v_2_14', 'APIClientsApi', '2.18'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flashblade._common.apis.active_directory_api_v_2_14', 'ActiveDirectoryApi', '2.18'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.administrators_api_v_2_15', 'AdministratorsApi', '2.18'),
    'AlertWatchersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.alert_watchers_api_v_2_14', 'AlertWatchersApi', '2.18'),
    'AlertsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.alerts_api_v_2_14', 'AlertsApi', '2.18'),
    'ArrayConnectionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.array_connections_api_v_2_17', 'ArrayConnectionsApi', '2.18'),
    'ArraysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.arrays_api_v_2_18', 'ArraysApi', '2.18'),
    'AuditsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.audits_api_v_2_14', 'AuditsApi', '2.18'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flashblade._common.apis.authorization_api_v_2_14', 'AuthorizationApi', '2.18'),
    'BladesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.blades_api_v_2_14', 'BladesApi', '2.18'),
    'BucketReplicaLinksApi': __LazyApiLoader('pypureclient.flashblade._common.apis.bucket_replica_links_api_v_2_17', 'BucketReplicaLinksApi', '2.18'),
    'BucketsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.buckets_api_v_2_17', 'BucketsApi', '2.18'),
    'CertificateGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.certificate_groups_api_v_2_14', 'CertificateGroupsApi', '2.18'),
    'CertificatesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.certificates_api_v_2_14', 'CertificatesApi', '2.18'),
    'ClientsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.clients_api_v_2_18', 'ClientsApi', '2.18'),
    'DNSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.dns_api_v_2_16', 'DNSApi', '2.18'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.directory_services_api_v_2_14', 'DirectoryServicesApi', '2.18'),
    'DrivesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.drives_api_v_2_14', 'DrivesApi', '2.18'),
    'FileSystemExportsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_exports_api_v_2_17', 'FileSystemExportsApi', '2.18'),
    'FileSystemReplicaLinksApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_replica_links_api_v_2_17', 'FileSystemReplicaLinksApi', '2.18'),
    'FileSystemSnapshotsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_snapshots_api_v_2_17', 'FileSystemSnapshotsApi', '2.18'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_systems_api_v_2_18', 'FileSystemsApi', '2.18'),
    'FleetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.fleets_api_v_2_17', 'FleetsApi', '2.18'),
    'HardwareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.hardware_api_v_2_16', 'HardwareApi', '2.18'),
    'HardwareConnectorsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.hardware_connectors_api_v_2_14', 'HardwareConnectorsApi', '2.18'),
    'KMIPApi': __LazyApiLoader('pypureclient.flashblade._common.apis.kmip_api_v_2_14', 'KMIPApi', '2.18'),
    'KeytabsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.keytabs_api_v_2_14', 'KeytabsApi', '2.18'),
    'LegalHoldsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.legal_holds_api_v_2_17', 'LegalHoldsApi', '2.18'),
    'LifecycleRulesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.lifecycle_rules_api_v_2_17', 'LifecycleRulesApi', '2.18'),
    'LinkAggregationGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.link_aggregation_groups_api_v_2_14', 'LinkAggregationGroupsApi', '2.18'),
    'LogsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.logs_api_v_2_14', 'LogsApi', '2.18'),
    'MaintenanceWindowsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.maintenance_windows_api_v_2_16', 'MaintenanceWindowsApi', '2.18'),
    'NetworkInterfacesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.network_interfaces_api_v_2_18', 'NetworkInterfacesApi', '2.18'),
    'NodeGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.node_groups_api_v_2_18', 'NodeGroupsApi', '2.18'),
    'NodesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.nodes_api_v_2_18', 'NodesApi', '2.18'),
    'OIDCSSOApi': __LazyApiLoader('pypureclient.flashblade._common.apis.oidcsso_api_v_2_17', 'OIDCSSOApi', '2.18'),
    'ObjectStoreAccessKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_access_keys_api_v_2_17', 'ObjectStoreAccessKeysApi', '2.18'),
    'ObjectStoreAccountsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_accounts_api_v_2_17', 'ObjectStoreAccountsApi', '2.18'),
    'ObjectStoreRemoteCredentialsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_remote_credentials_api_v_2_17', 'ObjectStoreRemoteCredentialsApi', '2.18'),
    'ObjectStoreRolesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_roles_api_v_2_17', 'ObjectStoreRolesApi', '2.18'),
    'ObjectStoreUsersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_users_api_v_2_17', 'ObjectStoreUsersApi', '2.18'),
    'ObjectStoreVirtualHostsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_virtual_hosts_api_v_2_17', 'ObjectStoreVirtualHostsApi', '2.18'),
    'PoliciesAllApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_all_api_v_2_17', 'PoliciesAllApi', '2.18'),
    'PoliciesAuditForFileSystemsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_audit_for_file_systems_api_v_2_18', 'PoliciesAuditForFileSystemsApi', '2.18'),
    'PoliciesNFSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_nfs_api_v_2_17', 'PoliciesNFSApi', '2.18'),
    'PoliciesNetworkAccessApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_network_access_api_v_2_14', 'PoliciesNetworkAccessApi', '2.18'),
    'PoliciesObjectStoreAccessApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_object_store_access_api_v_2_17', 'PoliciesObjectStoreAccessApi', '2.18'),
    'PoliciesPasswordApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_password_api_v_2_16', 'PoliciesPasswordApi', '2.18'),
    'PoliciesQoSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_qo_s_api_v_2_17', 'PoliciesQoSApi', '2.18'),
    'PoliciesSMBClientApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_smb_client_api_v_2_17', 'PoliciesSMBClientApi', '2.18'),
    'PoliciesSMBShareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_smb_share_api_v_2_17', 'PoliciesSMBShareApi', '2.18'),
    'PoliciesSSHCertificateAuthorityApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_ssh_certificate_authority_api_v_2_14', 'PoliciesSSHCertificateAuthorityApi', '2.18'),
    'PoliciesSnapshotApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_snapshot_api_v_2_17', 'PoliciesSnapshotApi', '2.18'),
    'PoliciesStorageClassTieringApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_storage_class_tiering_api_v_2_18', 'PoliciesStorageClassTieringApi', '2.18'),
    'PoliciesTLSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_tls_api_v_2_17', 'PoliciesTLSApi', '2.18'),
    'PoliciesWORMDataApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_worm_data_api_v_2_17', 'PoliciesWORMDataApi', '2.18'),
    'PublicKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.public_keys_api_v_2_14', 'PublicKeysApi', '2.18'),
    'QuotasApi': __LazyApiLoader('pypureclient.flashblade._common.apis.quotas_api_v_2_17', 'QuotasApi', '2.18'),
    'RDLApi': __LazyApiLoader('pypureclient.flashblade._common.apis.rdl_api_v_2_14', 'RDLApi', '2.18'),
    'RemoteArraysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.remote_arrays_api_v_2_17', 'RemoteArraysApi', '2.18'),
    'RolesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.roles_api_v_2_14', 'RolesApi', '2.18'),
    'SAML2SSOApi': __LazyApiLoader('pypureclient.flashblade._common.apis.saml2_sso_api_v_2_16', 'SAML2SSOApi', '2.18'),
    'SMTPApi': __LazyApiLoader('pypureclient.flashblade._common.apis.smtp_api_v_2_14', 'SMTPApi', '2.18'),
    'SNMPAgentsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.snmp_agents_api_v_2_14', 'SNMPAgentsApi', '2.18'),
    'SNMPManagersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.snmp_managers_api_v_2_14', 'SNMPManagersApi', '2.18'),
    'ServersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.servers_api_v_2_17', 'ServersApi', '2.18'),
    'SessionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.sessions_api_v_2_14', 'SessionsApi', '2.18'),
    'SoftwareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.software_api_v_2_16', 'SoftwareApi', '2.18'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.subnets_api_v_2_14', 'SubnetsApi', '2.18'),
    'SupportApi': __LazyApiLoader('pypureclient.flashblade._common.apis.support_api_v_2_14', 'SupportApi', '2.18'),
    'SupportDiagnosticsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.support_diagnostics_api_v_2_16', 'SupportDiagnosticsApi', '2.18'),
    'SyslogApi': __LazyApiLoader('pypureclient.flashblade._common.apis.syslog_api_v_2_17', 'SyslogApi', '2.18'),
    'TargetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.targets_api_v_2_17', 'TargetsApi', '2.18'),
    'UsageApi': __LazyApiLoader('pypureclient.flashblade._common.apis.usage_api_v_2_17', 'UsageApi', '2.18'),
    'VerificationKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.verification_keys_api_v_2_14', 'VerificationKeysApi', '2.18'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
