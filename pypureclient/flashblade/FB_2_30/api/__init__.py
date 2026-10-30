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
    'APIClientsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.api_clients_api_v_2_30', 'APIClientsApi', '2.30'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flashblade._common.apis.active_directory_api_v_2_30', 'ActiveDirectoryApi', '2.30'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.administrators_api_v_2_30', 'AdministratorsApi', '2.30'),
    'AlertWatchersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.alert_watchers_api_v_2_30', 'AlertWatchersApi', '2.30'),
    'AlertsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.alerts_api_v_2_27', 'AlertsApi', '2.30'),
    'ArrayConnectionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.array_connections_api_v_2_30', 'ArrayConnectionsApi', '2.30'),
    'ArraysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.arrays_api_v_2_30', 'ArraysApi', '2.30'),
    'AuditLogTargetForFileSystemsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.audit_log_target_for_file_systems_api_v_2_30', 'AuditLogTargetForFileSystemsApi', '2.30'),
    'AuditLogTargetForObjectStoreApi': __LazyApiLoader('pypureclient.flashblade._common.apis.audit_log_target_for_object_store_api_v_2_30', 'AuditLogTargetForObjectStoreApi', '2.30'),
    'AuditsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.audits_api_v_2_28', 'AuditsApi', '2.30'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flashblade._common.apis.authorization_api_v_2_26', 'AuthorizationApi', '2.30'),
    'BladesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.blades_api_v_2_27', 'BladesApi', '2.30'),
    'BucketReplicaLinksApi': __LazyApiLoader('pypureclient.flashblade._common.apis.bucket_replica_links_api_v_2_30', 'BucketReplicaLinksApi', '2.30'),
    'BucketsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.buckets_api_v_2_30', 'BucketsApi', '2.30'),
    'CertificateGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.certificate_groups_api_v_2_30', 'CertificateGroupsApi', '2.30'),
    'CertificatesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.certificates_api_v_2_30', 'CertificatesApi', '2.30'),
    'ClientsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.clients_api_v_2_27', 'ClientsApi', '2.30'),
    'DNSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.dns_api_v_2_30', 'DNSApi', '2.30'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.directory_services_api_v_2_30', 'DirectoryServicesApi', '2.30'),
    'DrivesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.drives_api_v_2_27', 'DrivesApi', '2.30'),
    'FileSystemExportsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_exports_api_v_2_30', 'FileSystemExportsApi', '2.30'),
    'FileSystemJunctionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_junctions_api_v_2_30', 'FileSystemJunctionsApi', '2.30'),
    'FileSystemReplicaLinksApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_replica_links_api_v_2_30', 'FileSystemReplicaLinksApi', '2.30'),
    'FileSystemSnapshotsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_snapshots_api_v_2_30', 'FileSystemSnapshotsApi', '2.30'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_systems_api_v_2_30', 'FileSystemsApi', '2.30'),
    'FleetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.fleets_api_v_2_27', 'FleetsApi', '2.30'),
    'HardwareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.hardware_api_v_2_27', 'HardwareApi', '2.30'),
    'HardwareConnectorsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.hardware_connectors_api_v_2_27', 'HardwareConnectorsApi', '2.30'),
    'KMIPApi': __LazyApiLoader('pypureclient.flashblade._common.apis.kmip_api_v_2_30', 'KMIPApi', '2.30'),
    'KeytabsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.keytabs_api_v_2_30', 'KeytabsApi', '2.30'),
    'LegalHoldsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.legal_holds_api_v_2_30', 'LegalHoldsApi', '2.30'),
    'LifecycleRulesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.lifecycle_rules_api_v_2_30', 'LifecycleRulesApi', '2.30'),
    'LinkAggregationGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.link_aggregation_groups_api_v_2_30', 'LinkAggregationGroupsApi', '2.30'),
    'LogsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.logs_api_v_2_27', 'LogsApi', '2.30'),
    'MaintenanceWindowsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.maintenance_windows_api_v_2_30', 'MaintenanceWindowsApi', '2.30'),
    'NetworkInterfacesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.network_interfaces_api_v_2_30', 'NetworkInterfacesApi', '2.30'),
    'NodeGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.node_groups_api_v_2_30', 'NodeGroupsApi', '2.30'),
    'NodesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.nodes_api_v_2_30', 'NodesApi', '2.30'),
    'OIDCSSOApi': __LazyApiLoader('pypureclient.flashblade._common.apis.oidcsso_api_v_2_30', 'OIDCSSOApi', '2.30'),
    'ObjectStoreAccessKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_access_keys_api_v_2_27', 'ObjectStoreAccessKeysApi', '2.30'),
    'ObjectStoreAccountExportsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_account_exports_api_v_2_30', 'ObjectStoreAccountExportsApi', '2.30'),
    'ObjectStoreAccountsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_accounts_api_v_2_30', 'ObjectStoreAccountsApi', '2.30'),
    'ObjectStoreRemoteCredentialsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_remote_credentials_api_v_2_30', 'ObjectStoreRemoteCredentialsApi', '2.30'),
    'ObjectStoreRolesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_roles_api_v_2_30', 'ObjectStoreRolesApi', '2.30'),
    'ObjectStoreUsersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_users_api_v_2_30', 'ObjectStoreUsersApi', '2.30'),
    'ObjectStoreVirtualHostsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_virtual_hosts_api_v_2_30', 'ObjectStoreVirtualHostsApi', '2.30'),
    'PoliciesAllApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_all_api_v_2_27', 'PoliciesAllApi', '2.30'),
    'PoliciesAuditForFileSystemsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_audit_for_file_systems_api_v_2_30', 'PoliciesAuditForFileSystemsApi', '2.30'),
    'PoliciesAuditForObjectStoreApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_audit_for_object_store_api_v_2_30', 'PoliciesAuditForObjectStoreApi', '2.30'),
    'PoliciesDataEvictionApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_data_eviction_api_v_2_30', 'PoliciesDataEvictionApi', '2.30'),
    'PoliciesManagementAccessApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_management_access_api_v_2_30', 'PoliciesManagementAccessApi', '2.30'),
    'PoliciesManagementAuthenticationApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_management_authentication_api_v_2_30', 'PoliciesManagementAuthenticationApi', '2.30'),
    'PoliciesNFSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_nfs_api_v_2_30', 'PoliciesNFSApi', '2.30'),
    'PoliciesNetworkAccessApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_network_access_api_v_2_30', 'PoliciesNetworkAccessApi', '2.30'),
    'PoliciesObjectStoreAccessApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_object_store_access_api_v_2_30', 'PoliciesObjectStoreAccessApi', '2.30'),
    'PoliciesPasswordApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_password_api_v_2_27', 'PoliciesPasswordApi', '2.30'),
    'PoliciesQoSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_qo_s_api_v_2_30', 'PoliciesQoSApi', '2.30'),
    'PoliciesS3ExportApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_s3_export_api_v_2_30', 'PoliciesS3ExportApi', '2.30'),
    'PoliciesSMBClientApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_smb_client_api_v_2_30', 'PoliciesSMBClientApi', '2.30'),
    'PoliciesSMBShareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_smb_share_api_v_2_30', 'PoliciesSMBShareApi', '2.30'),
    'PoliciesSSHCertificateAuthorityApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_ssh_certificate_authority_api_v_2_30', 'PoliciesSSHCertificateAuthorityApi', '2.30'),
    'PoliciesSnapshotApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_snapshot_api_v_2_30', 'PoliciesSnapshotApi', '2.30'),
    'PoliciesStorageClassTieringApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_storage_class_tiering_api_v_2_30', 'PoliciesStorageClassTieringApi', '2.30'),
    'PoliciesTLSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_tls_api_v_2_30', 'PoliciesTLSApi', '2.30'),
    'PoliciesUserAndGroupQuotaPolicyApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_user_and_group_quota_policy_api_v_2_30', 'PoliciesUserAndGroupQuotaPolicyApi', '2.30'),
    'PoliciesWORMDataApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_worm_data_api_v_2_30', 'PoliciesWORMDataApi', '2.30'),
    'PresetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.presets_api_v_2_27', 'PresetsApi', '2.30'),
    'PublicKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.public_keys_api_v_2_30', 'PublicKeysApi', '2.30'),
    'QuotasApi': __LazyApiLoader('pypureclient.flashblade._common.apis.quotas_api_v_2_30', 'QuotasApi', '2.30'),
    'RDLApi': __LazyApiLoader('pypureclient.flashblade._common.apis.rdl_api_v_2_27', 'RDLApi', '2.30'),
    'RealmConnectionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.realm_connections_api_v_2_30', 'RealmConnectionsApi', '2.30'),
    'RealmsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.realms_api_v_2_30', 'RealmsApi', '2.30'),
    'RemoteArraysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.remote_arrays_api_v_2_27', 'RemoteArraysApi', '2.30'),
    'RemoteRealmsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.remote_realms_api_v_2_27', 'RemoteRealmsApi', '2.30'),
    'ResiliencyGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.resiliency_groups_api_v_2_27', 'ResiliencyGroupsApi', '2.30'),
    'ResourceAccessesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.resource_accesses_api_v_2_30', 'ResourceAccessesApi', '2.30'),
    'RolesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.roles_api_v_2_17', 'RolesApi', '2.30'),
    'SAML2SSOApi': __LazyApiLoader('pypureclient.flashblade._common.apis.saml2_sso_api_v_2_30', 'SAML2SSOApi', '2.30'),
    'SMTPApi': __LazyApiLoader('pypureclient.flashblade._common.apis.smtp_api_v_2_27', 'SMTPApi', '2.30'),
    'SNMPAgentsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.snmp_agents_api_v_2_27', 'SNMPAgentsApi', '2.30'),
    'SNMPManagersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.snmp_managers_api_v_2_30', 'SNMPManagersApi', '2.30'),
    'ServersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.servers_api_v_2_30', 'ServersApi', '2.30'),
    'SessionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.sessions_api_v_2_27', 'SessionsApi', '2.30'),
    'SoftwareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.software_api_v_2_30', 'SoftwareApi', '2.30'),
    'StorageClassesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.storage_classes_api_v_2_27', 'StorageClassesApi', '2.30'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.subnets_api_v_2_30', 'SubnetsApi', '2.30'),
    'SupportApi': __LazyApiLoader('pypureclient.flashblade._common.apis.support_api_v_2_27', 'SupportApi', '2.30'),
    'SupportDiagnosticsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.support_diagnostics_api_v_2_27', 'SupportDiagnosticsApi', '2.30'),
    'SyslogApi': __LazyApiLoader('pypureclient.flashblade._common.apis.syslog_api_v_2_30', 'SyslogApi', '2.30'),
    'TargetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.targets_api_v_2_30', 'TargetsApi', '2.30'),
    'TelemetryMetricsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.telemetry_metrics_api_v_2_29', 'TelemetryMetricsApi', '2.30'),
    'TelemetryMetricsCollectionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.telemetry_metrics_collections_api_v_2_29', 'TelemetryMetricsCollectionsApi', '2.30'),
    'TelemetryMetricsPoliciesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.telemetry_metrics_policies_api_v_2_30', 'TelemetryMetricsPoliciesApi', '2.30'),
    'TelemetryTargetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.telemetry_targets_api_v_2_30', 'TelemetryTargetsApi', '2.30'),
    'TopologyGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.topology_groups_api_v_2_27', 'TopologyGroupsApi', '2.30'),
    'UsageApi': __LazyApiLoader('pypureclient.flashblade._common.apis.usage_api_v_2_27', 'UsageApi', '2.30'),
    'UserGroupQuotasApi': __LazyApiLoader('pypureclient.flashblade._common.apis.user_group_quotas_api_v_2_27', 'UserGroupQuotasApi', '2.30'),
    'VerificationKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.verification_keys_api_v_2_27', 'VerificationKeysApi', '2.30'),
    'WorkloadsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.workloads_api_v_2_30', 'WorkloadsApi', '2.30'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
