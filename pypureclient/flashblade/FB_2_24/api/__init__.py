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
    'APIClientsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.api_clients_api_v_2_24', 'APIClientsApi', '2.24'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flashblade._common.apis.active_directory_api_v_2_24', 'ActiveDirectoryApi', '2.24'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.administrators_api_v_2_24', 'AdministratorsApi', '2.24'),
    'AlertWatchersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.alert_watchers_api_v_2_14', 'AlertWatchersApi', '2.24'),
    'AlertsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.alerts_api_v_2_14', 'AlertsApi', '2.24'),
    'ArrayConnectionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.array_connections_api_v_2_24', 'ArrayConnectionsApi', '2.24'),
    'ArraysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.arrays_api_v_2_24', 'ArraysApi', '2.24'),
    'AuditLogTargetForFileSystemsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.audit_log_target_for_file_systems_api_v_2_20', 'AuditLogTargetForFileSystemsApi', '2.24'),
    'AuditLogTargetForObjectStoreApi': __LazyApiLoader('pypureclient.flashblade._common.apis.audit_log_target_for_object_store_api_v_2_24', 'AuditLogTargetForObjectStoreApi', '2.24'),
    'AuditsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.audits_api_v_2_14', 'AuditsApi', '2.24'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flashblade._common.apis.authorization_api_v_2_24', 'AuthorizationApi', '2.24'),
    'BladesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.blades_api_v_2_14', 'BladesApi', '2.24'),
    'BucketReplicaLinksApi': __LazyApiLoader('pypureclient.flashblade._common.apis.bucket_replica_links_api_v_2_24', 'BucketReplicaLinksApi', '2.24'),
    'BucketsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.buckets_api_v_2_24', 'BucketsApi', '2.24'),
    'CertificateGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.certificate_groups_api_v_2_14', 'CertificateGroupsApi', '2.24'),
    'CertificatesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.certificates_api_v_2_20', 'CertificatesApi', '2.24'),
    'ClientsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.clients_api_v_2_24', 'ClientsApi', '2.24'),
    'DNSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.dns_api_v_2_16', 'DNSApi', '2.24'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.directory_services_api_v_2_24', 'DirectoryServicesApi', '2.24'),
    'DrivesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.drives_api_v_2_14', 'DrivesApi', '2.24'),
    'FileSystemExportsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_exports_api_v_2_24', 'FileSystemExportsApi', '2.24'),
    'FileSystemReplicaLinksApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_replica_links_api_v_2_24', 'FileSystemReplicaLinksApi', '2.24'),
    'FileSystemSnapshotsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_snapshots_api_v_2_24', 'FileSystemSnapshotsApi', '2.24'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_systems_api_v_2_24', 'FileSystemsApi', '2.24'),
    'FleetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.fleets_api_v_2_24', 'FleetsApi', '2.24'),
    'HardwareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.hardware_api_v_2_16', 'HardwareApi', '2.24'),
    'HardwareConnectorsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.hardware_connectors_api_v_2_14', 'HardwareConnectorsApi', '2.24'),
    'KMIPApi': __LazyApiLoader('pypureclient.flashblade._common.apis.kmip_api_v_2_14', 'KMIPApi', '2.24'),
    'KeytabsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.keytabs_api_v_2_14', 'KeytabsApi', '2.24'),
    'LegalHoldsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.legal_holds_api_v_2_17', 'LegalHoldsApi', '2.24'),
    'LifecycleRulesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.lifecycle_rules_api_v_2_24', 'LifecycleRulesApi', '2.24'),
    'LinkAggregationGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.link_aggregation_groups_api_v_2_19', 'LinkAggregationGroupsApi', '2.24'),
    'LogsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.logs_api_v_2_14', 'LogsApi', '2.24'),
    'MaintenanceWindowsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.maintenance_windows_api_v_2_16', 'MaintenanceWindowsApi', '2.24'),
    'NetworkInterfacesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.network_interfaces_api_v_2_20', 'NetworkInterfacesApi', '2.24'),
    'NodeGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.node_groups_api_v_2_18', 'NodeGroupsApi', '2.24'),
    'NodesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.nodes_api_v_2_23', 'NodesApi', '2.24'),
    'OIDCSSOApi': __LazyApiLoader('pypureclient.flashblade._common.apis.oidcsso_api_v_2_17', 'OIDCSSOApi', '2.24'),
    'ObjectStoreAccessKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_access_keys_api_v_2_24', 'ObjectStoreAccessKeysApi', '2.24'),
    'ObjectStoreAccountExportsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_account_exports_api_v_2_24', 'ObjectStoreAccountExportsApi', '2.24'),
    'ObjectStoreAccountsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_accounts_api_v_2_24', 'ObjectStoreAccountsApi', '2.24'),
    'ObjectStoreRemoteCredentialsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_remote_credentials_api_v_2_24', 'ObjectStoreRemoteCredentialsApi', '2.24'),
    'ObjectStoreRolesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_roles_api_v_2_24', 'ObjectStoreRolesApi', '2.24'),
    'ObjectStoreUsersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_users_api_v_2_24', 'ObjectStoreUsersApi', '2.24'),
    'ObjectStoreVirtualHostsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_virtual_hosts_api_v_2_24', 'ObjectStoreVirtualHostsApi', '2.24'),
    'PoliciesAllApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_all_api_v_2_24', 'PoliciesAllApi', '2.24'),
    'PoliciesAuditForFileSystemsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_audit_for_file_systems_api_v_2_24', 'PoliciesAuditForFileSystemsApi', '2.24'),
    'PoliciesAuditForObjectStoreApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_audit_for_object_store_api_v_2_24', 'PoliciesAuditForObjectStoreApi', '2.24'),
    'PoliciesDataEvictionApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_data_eviction_api_v_2_24', 'PoliciesDataEvictionApi', '2.24'),
    'PoliciesManagementAccessApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_management_access_api_v_2_24', 'PoliciesManagementAccessApi', '2.24'),
    'PoliciesManagementAuthenticationApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_management_authentication_api_v_2_22', 'PoliciesManagementAuthenticationApi', '2.24'),
    'PoliciesNFSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_nfs_api_v_2_24', 'PoliciesNFSApi', '2.24'),
    'PoliciesNetworkAccessApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_network_access_api_v_2_14', 'PoliciesNetworkAccessApi', '2.24'),
    'PoliciesObjectStoreAccessApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_object_store_access_api_v_2_24', 'PoliciesObjectStoreAccessApi', '2.24'),
    'PoliciesPasswordApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_password_api_v_2_16', 'PoliciesPasswordApi', '2.24'),
    'PoliciesQoSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_qo_s_api_v_2_24', 'PoliciesQoSApi', '2.24'),
    'PoliciesS3ExportApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_s3_export_api_v_2_24', 'PoliciesS3ExportApi', '2.24'),
    'PoliciesSMBClientApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_smb_client_api_v_2_24', 'PoliciesSMBClientApi', '2.24'),
    'PoliciesSMBShareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_smb_share_api_v_2_24', 'PoliciesSMBShareApi', '2.24'),
    'PoliciesSSHCertificateAuthorityApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_ssh_certificate_authority_api_v_2_24', 'PoliciesSSHCertificateAuthorityApi', '2.24'),
    'PoliciesSnapshotApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_snapshot_api_v_2_24', 'PoliciesSnapshotApi', '2.24'),
    'PoliciesStorageClassTieringApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_storage_class_tiering_api_v_2_24', 'PoliciesStorageClassTieringApi', '2.24'),
    'PoliciesTLSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_tls_api_v_2_17', 'PoliciesTLSApi', '2.24'),
    'PoliciesWORMDataApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_worm_data_api_v_2_24', 'PoliciesWORMDataApi', '2.24'),
    'PresetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.presets_api_v_2_23', 'PresetsApi', '2.24'),
    'PublicKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.public_keys_api_v_2_14', 'PublicKeysApi', '2.24'),
    'QuotasApi': __LazyApiLoader('pypureclient.flashblade._common.apis.quotas_api_v_2_24', 'QuotasApi', '2.24'),
    'RDLApi': __LazyApiLoader('pypureclient.flashblade._common.apis.rdl_api_v_2_14', 'RDLApi', '2.24'),
    'RealmsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.realms_api_v_2_24', 'RealmsApi', '2.24'),
    'RemoteArraysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.remote_arrays_api_v_2_24', 'RemoteArraysApi', '2.24'),
    'ResiliencyGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.resiliency_groups_api_v_2_23', 'ResiliencyGroupsApi', '2.24'),
    'ResourceAccessesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.resource_accesses_api_v_2_19', 'ResourceAccessesApi', '2.24'),
    'RolesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.roles_api_v_2_14', 'RolesApi', '2.24'),
    'SAML2SSOApi': __LazyApiLoader('pypureclient.flashblade._common.apis.saml2_sso_api_v_2_16', 'SAML2SSOApi', '2.24'),
    'SMTPApi': __LazyApiLoader('pypureclient.flashblade._common.apis.smtp_api_v_2_14', 'SMTPApi', '2.24'),
    'SNMPAgentsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.snmp_agents_api_v_2_14', 'SNMPAgentsApi', '2.24'),
    'SNMPManagersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.snmp_managers_api_v_2_14', 'SNMPManagersApi', '2.24'),
    'ServersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.servers_api_v_2_24', 'ServersApi', '2.24'),
    'SessionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.sessions_api_v_2_14', 'SessionsApi', '2.24'),
    'SoftwareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.software_api_v_2_24', 'SoftwareApi', '2.24'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.subnets_api_v_2_14', 'SubnetsApi', '2.24'),
    'SupportApi': __LazyApiLoader('pypureclient.flashblade._common.apis.support_api_v_2_14', 'SupportApi', '2.24'),
    'SupportDiagnosticsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.support_diagnostics_api_v_2_24', 'SupportDiagnosticsApi', '2.24'),
    'SyslogApi': __LazyApiLoader('pypureclient.flashblade._common.apis.syslog_api_v_2_24', 'SyslogApi', '2.24'),
    'TargetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.targets_api_v_2_24', 'TargetsApi', '2.24'),
    'UsageApi': __LazyApiLoader('pypureclient.flashblade._common.apis.usage_api_v_2_24', 'UsageApi', '2.24'),
    'VerificationKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.verification_keys_api_v_2_14', 'VerificationKeysApi', '2.24'),
    'WorkloadsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.workloads_api_v_2_24', 'WorkloadsApi', '2.24'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
