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
    'APIClientsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.api_clients_api_v_2_27', 'APIClientsApi', '2.27'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flashblade._common.apis.active_directory_api_v_2_27', 'ActiveDirectoryApi', '2.27'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.administrators_api_v_2_27', 'AdministratorsApi', '2.27'),
    'AlertWatchersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.alert_watchers_api_v_2_27', 'AlertWatchersApi', '2.27'),
    'AlertsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.alerts_api_v_2_27', 'AlertsApi', '2.27'),
    'ArrayConnectionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.array_connections_api_v_2_27', 'ArrayConnectionsApi', '2.27'),
    'ArraysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.arrays_api_v_2_27', 'ArraysApi', '2.27'),
    'AuditLogTargetForFileSystemsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.audit_log_target_for_file_systems_api_v_2_27', 'AuditLogTargetForFileSystemsApi', '2.27'),
    'AuditLogTargetForObjectStoreApi': __LazyApiLoader('pypureclient.flashblade._common.apis.audit_log_target_for_object_store_api_v_2_27', 'AuditLogTargetForObjectStoreApi', '2.27'),
    'AuditsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.audits_api_v_2_27', 'AuditsApi', '2.27'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flashblade._common.apis.authorization_api_v_2_26', 'AuthorizationApi', '2.27'),
    'BladesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.blades_api_v_2_27', 'BladesApi', '2.27'),
    'BucketReplicaLinksApi': __LazyApiLoader('pypureclient.flashblade._common.apis.bucket_replica_links_api_v_2_27', 'BucketReplicaLinksApi', '2.27'),
    'BucketsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.buckets_api_v_2_27', 'BucketsApi', '2.27'),
    'CertificateGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.certificate_groups_api_v_2_27', 'CertificateGroupsApi', '2.27'),
    'CertificatesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.certificates_api_v_2_27', 'CertificatesApi', '2.27'),
    'ClientsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.clients_api_v_2_27', 'ClientsApi', '2.27'),
    'DNSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.dns_api_v_2_27', 'DNSApi', '2.27'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.directory_services_api_v_2_27', 'DirectoryServicesApi', '2.27'),
    'DrivesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.drives_api_v_2_27', 'DrivesApi', '2.27'),
    'FileSystemExportsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_exports_api_v_2_27', 'FileSystemExportsApi', '2.27'),
    'FileSystemJunctionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_junctions_api_v_2_27', 'FileSystemJunctionsApi', '2.27'),
    'FileSystemReplicaLinksApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_replica_links_api_v_2_27', 'FileSystemReplicaLinksApi', '2.27'),
    'FileSystemSnapshotsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_snapshots_api_v_2_27', 'FileSystemSnapshotsApi', '2.27'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_systems_api_v_2_27', 'FileSystemsApi', '2.27'),
    'FleetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.fleets_api_v_2_27', 'FleetsApi', '2.27'),
    'HardwareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.hardware_api_v_2_27', 'HardwareApi', '2.27'),
    'HardwareConnectorsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.hardware_connectors_api_v_2_27', 'HardwareConnectorsApi', '2.27'),
    'KMIPApi': __LazyApiLoader('pypureclient.flashblade._common.apis.kmip_api_v_2_27', 'KMIPApi', '2.27'),
    'KeytabsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.keytabs_api_v_2_27', 'KeytabsApi', '2.27'),
    'LegalHoldsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.legal_holds_api_v_2_27', 'LegalHoldsApi', '2.27'),
    'LifecycleRulesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.lifecycle_rules_api_v_2_27', 'LifecycleRulesApi', '2.27'),
    'LinkAggregationGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.link_aggregation_groups_api_v_2_27', 'LinkAggregationGroupsApi', '2.27'),
    'LogsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.logs_api_v_2_27', 'LogsApi', '2.27'),
    'MaintenanceWindowsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.maintenance_windows_api_v_2_27', 'MaintenanceWindowsApi', '2.27'),
    'NetworkInterfacesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.network_interfaces_api_v_2_27', 'NetworkInterfacesApi', '2.27'),
    'NodeGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.node_groups_api_v_2_27', 'NodeGroupsApi', '2.27'),
    'NodesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.nodes_api_v_2_27', 'NodesApi', '2.27'),
    'OIDCSSOApi': __LazyApiLoader('pypureclient.flashblade._common.apis.oidcsso_api_v_2_27', 'OIDCSSOApi', '2.27'),
    'ObjectStoreAccessKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_access_keys_api_v_2_27', 'ObjectStoreAccessKeysApi', '2.27'),
    'ObjectStoreAccountExportsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_account_exports_api_v_2_27', 'ObjectStoreAccountExportsApi', '2.27'),
    'ObjectStoreAccountsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_accounts_api_v_2_27', 'ObjectStoreAccountsApi', '2.27'),
    'ObjectStoreRemoteCredentialsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_remote_credentials_api_v_2_27', 'ObjectStoreRemoteCredentialsApi', '2.27'),
    'ObjectStoreRolesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_roles_api_v_2_27', 'ObjectStoreRolesApi', '2.27'),
    'ObjectStoreUsersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_users_api_v_2_27', 'ObjectStoreUsersApi', '2.27'),
    'ObjectStoreVirtualHostsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_virtual_hosts_api_v_2_27', 'ObjectStoreVirtualHostsApi', '2.27'),
    'PoliciesAllApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_all_api_v_2_27', 'PoliciesAllApi', '2.27'),
    'PoliciesAuditForFileSystemsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_audit_for_file_systems_api_v_2_27', 'PoliciesAuditForFileSystemsApi', '2.27'),
    'PoliciesAuditForObjectStoreApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_audit_for_object_store_api_v_2_27', 'PoliciesAuditForObjectStoreApi', '2.27'),
    'PoliciesDataEvictionApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_data_eviction_api_v_2_27', 'PoliciesDataEvictionApi', '2.27'),
    'PoliciesManagementAccessApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_management_access_api_v_2_27', 'PoliciesManagementAccessApi', '2.27'),
    'PoliciesManagementAuthenticationApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_management_authentication_api_v_2_27', 'PoliciesManagementAuthenticationApi', '2.27'),
    'PoliciesNFSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_nfs_api_v_2_27', 'PoliciesNFSApi', '2.27'),
    'PoliciesNetworkAccessApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_network_access_api_v_2_27', 'PoliciesNetworkAccessApi', '2.27'),
    'PoliciesObjectStoreAccessApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_object_store_access_api_v_2_27', 'PoliciesObjectStoreAccessApi', '2.27'),
    'PoliciesPasswordApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_password_api_v_2_27', 'PoliciesPasswordApi', '2.27'),
    'PoliciesQoSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_qo_s_api_v_2_27', 'PoliciesQoSApi', '2.27'),
    'PoliciesS3ExportApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_s3_export_api_v_2_27', 'PoliciesS3ExportApi', '2.27'),
    'PoliciesSMBClientApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_smb_client_api_v_2_27', 'PoliciesSMBClientApi', '2.27'),
    'PoliciesSMBShareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_smb_share_api_v_2_27', 'PoliciesSMBShareApi', '2.27'),
    'PoliciesSSHCertificateAuthorityApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_ssh_certificate_authority_api_v_2_27', 'PoliciesSSHCertificateAuthorityApi', '2.27'),
    'PoliciesSnapshotApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_snapshot_api_v_2_27', 'PoliciesSnapshotApi', '2.27'),
    'PoliciesStorageClassTieringApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_storage_class_tiering_api_v_2_27', 'PoliciesStorageClassTieringApi', '2.27'),
    'PoliciesTLSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_tls_api_v_2_27', 'PoliciesTLSApi', '2.27'),
    'PoliciesUserAndGroupQuotaPolicyApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_user_and_group_quota_policy_api_v_2_27', 'PoliciesUserAndGroupQuotaPolicyApi', '2.27'),
    'PoliciesWORMDataApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_worm_data_api_v_2_27', 'PoliciesWORMDataApi', '2.27'),
    'PresetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.presets_api_v_2_27', 'PresetsApi', '2.27'),
    'PublicKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.public_keys_api_v_2_27', 'PublicKeysApi', '2.27'),
    'QuotasApi': __LazyApiLoader('pypureclient.flashblade._common.apis.quotas_api_v_2_27', 'QuotasApi', '2.27'),
    'RDLApi': __LazyApiLoader('pypureclient.flashblade._common.apis.rdl_api_v_2_27', 'RDLApi', '2.27'),
    'RealmConnectionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.realm_connections_api_v_2_27', 'RealmConnectionsApi', '2.27'),
    'RealmsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.realms_api_v_2_27', 'RealmsApi', '2.27'),
    'RemoteArraysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.remote_arrays_api_v_2_27', 'RemoteArraysApi', '2.27'),
    'RemoteRealmsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.remote_realms_api_v_2_27', 'RemoteRealmsApi', '2.27'),
    'ResiliencyGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.resiliency_groups_api_v_2_27', 'ResiliencyGroupsApi', '2.27'),
    'ResourceAccessesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.resource_accesses_api_v_2_27', 'ResourceAccessesApi', '2.27'),
    'RolesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.roles_api_v_2_17', 'RolesApi', '2.27'),
    'SAML2SSOApi': __LazyApiLoader('pypureclient.flashblade._common.apis.saml2_sso_api_v_2_27', 'SAML2SSOApi', '2.27'),
    'SMTPApi': __LazyApiLoader('pypureclient.flashblade._common.apis.smtp_api_v_2_27', 'SMTPApi', '2.27'),
    'SNMPAgentsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.snmp_agents_api_v_2_27', 'SNMPAgentsApi', '2.27'),
    'SNMPManagersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.snmp_managers_api_v_2_27', 'SNMPManagersApi', '2.27'),
    'ServersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.servers_api_v_2_27', 'ServersApi', '2.27'),
    'SessionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.sessions_api_v_2_27', 'SessionsApi', '2.27'),
    'SoftwareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.software_api_v_2_27', 'SoftwareApi', '2.27'),
    'StorageClassesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.storage_classes_api_v_2_27', 'StorageClassesApi', '2.27'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.subnets_api_v_2_27', 'SubnetsApi', '2.27'),
    'SupportApi': __LazyApiLoader('pypureclient.flashblade._common.apis.support_api_v_2_27', 'SupportApi', '2.27'),
    'SupportDiagnosticsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.support_diagnostics_api_v_2_27', 'SupportDiagnosticsApi', '2.27'),
    'SyslogApi': __LazyApiLoader('pypureclient.flashblade._common.apis.syslog_api_v_2_27', 'SyslogApi', '2.27'),
    'TargetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.targets_api_v_2_27', 'TargetsApi', '2.27'),
    'TopologyGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.topology_groups_api_v_2_27', 'TopologyGroupsApi', '2.27'),
    'UsageApi': __LazyApiLoader('pypureclient.flashblade._common.apis.usage_api_v_2_27', 'UsageApi', '2.27'),
    'UserGroupQuotasApi': __LazyApiLoader('pypureclient.flashblade._common.apis.user_group_quotas_api_v_2_27', 'UserGroupQuotasApi', '2.27'),
    'VerificationKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.verification_keys_api_v_2_27', 'VerificationKeysApi', '2.27'),
    'WorkloadsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.workloads_api_v_2_27', 'WorkloadsApi', '2.27'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
