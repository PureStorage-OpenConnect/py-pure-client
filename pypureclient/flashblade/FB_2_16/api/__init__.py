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
    'APIClientsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.api_clients_api_v_2_14', 'APIClientsApi', '2.16'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flashblade._common.apis.active_directory_api_v_2_14', 'ActiveDirectoryApi', '2.16'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.administrators_api_v_2_15', 'AdministratorsApi', '2.16'),
    'AlertWatchersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.alert_watchers_api_v_2_14', 'AlertWatchersApi', '2.16'),
    'AlertsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.alerts_api_v_2_14', 'AlertsApi', '2.16'),
    'ArrayConnectionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.array_connections_api_v_2_14', 'ArrayConnectionsApi', '2.16'),
    'ArraysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.arrays_api_v_2_16', 'ArraysApi', '2.16'),
    'AuditsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.audits_api_v_2_14', 'AuditsApi', '2.16'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flashblade._common.apis.authorization_api_v_2_14', 'AuthorizationApi', '2.16'),
    'BladesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.blades_api_v_2_14', 'BladesApi', '2.16'),
    'BucketReplicaLinksApi': __LazyApiLoader('pypureclient.flashblade._common.apis.bucket_replica_links_api_v_2_2', 'BucketReplicaLinksApi', '2.16'),
    'BucketsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.buckets_api_v_2_14', 'BucketsApi', '2.16'),
    'CertificateGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.certificate_groups_api_v_2_14', 'CertificateGroupsApi', '2.16'),
    'CertificatesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.certificates_api_v_2_14', 'CertificatesApi', '2.16'),
    'ClientsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.clients_api_v_2_14', 'ClientsApi', '2.16'),
    'DNSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.dns_api_v_2_16', 'DNSApi', '2.16'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.directory_services_api_v_2_14', 'DirectoryServicesApi', '2.16'),
    'DrivesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.drives_api_v_2_14', 'DrivesApi', '2.16'),
    'FileSystemExportsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_exports_api_v_2_16', 'FileSystemExportsApi', '2.16'),
    'FileSystemReplicaLinksApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_replica_links_api_v_2_14', 'FileSystemReplicaLinksApi', '2.16'),
    'FileSystemSnapshotsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_snapshots_api_v_2_14', 'FileSystemSnapshotsApi', '2.16'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_systems_api_v_2_16', 'FileSystemsApi', '2.16'),
    'HardwareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.hardware_api_v_2_16', 'HardwareApi', '2.16'),
    'HardwareConnectorsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.hardware_connectors_api_v_2_14', 'HardwareConnectorsApi', '2.16'),
    'KMIPApi': __LazyApiLoader('pypureclient.flashblade._common.apis.kmip_api_v_2_14', 'KMIPApi', '2.16'),
    'KeytabsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.keytabs_api_v_2_14', 'KeytabsApi', '2.16'),
    'LifecycleRulesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.lifecycle_rules_api_v_2_14', 'LifecycleRulesApi', '2.16'),
    'LinkAggregationGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.link_aggregation_groups_api_v_2_14', 'LinkAggregationGroupsApi', '2.16'),
    'LogsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.logs_api_v_2_14', 'LogsApi', '2.16'),
    'MaintenanceWindowsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.maintenance_windows_api_v_2_16', 'MaintenanceWindowsApi', '2.16'),
    'NetworkInterfacesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.network_interfaces_api_v_2_14', 'NetworkInterfacesApi', '2.16'),
    'ObjectStoreAccessKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_access_keys_api_v_2_14', 'ObjectStoreAccessKeysApi', '2.16'),
    'ObjectStoreAccountsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_accounts_api_v_2_14', 'ObjectStoreAccountsApi', '2.16'),
    'ObjectStoreRemoteCredentialsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_remote_credentials_api_v_2_14', 'ObjectStoreRemoteCredentialsApi', '2.16'),
    'ObjectStoreUsersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_users_api_v_2_14', 'ObjectStoreUsersApi', '2.16'),
    'ObjectStoreVirtualHostsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_virtual_hosts_api_v_2_14', 'ObjectStoreVirtualHostsApi', '2.16'),
    'PoliciesAllApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_all_api_v_2_14', 'PoliciesAllApi', '2.16'),
    'PoliciesAuditForFileSystemsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_audit_for_file_systems_api_v_2_14', 'PoliciesAuditForFileSystemsApi', '2.16'),
    'PoliciesNFSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_nfs_api_v_2_14', 'PoliciesNFSApi', '2.16'),
    'PoliciesNetworkAccessApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_network_access_api_v_2_14', 'PoliciesNetworkAccessApi', '2.16'),
    'PoliciesObjectStoreAccessApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_object_store_access_api_v_2_14', 'PoliciesObjectStoreAccessApi', '2.16'),
    'PoliciesPasswordApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_password_api_v_2_16', 'PoliciesPasswordApi', '2.16'),
    'PoliciesSMBClientApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_smb_client_api_v_2_14', 'PoliciesSMBClientApi', '2.16'),
    'PoliciesSMBShareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_smb_share_api_v_2_14', 'PoliciesSMBShareApi', '2.16'),
    'PoliciesSSHCertificateAuthorityApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_ssh_certificate_authority_api_v_2_14', 'PoliciesSSHCertificateAuthorityApi', '2.16'),
    'PoliciesSnapshotApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_snapshot_api_v_2_14', 'PoliciesSnapshotApi', '2.16'),
    'PoliciesWORMDataApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_worm_data_api_v_2_15', 'PoliciesWORMDataApi', '2.16'),
    'PublicKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.public_keys_api_v_2_14', 'PublicKeysApi', '2.16'),
    'QuotasApi': __LazyApiLoader('pypureclient.flashblade._common.apis.quotas_api_v_2_14', 'QuotasApi', '2.16'),
    'RDLApi': __LazyApiLoader('pypureclient.flashblade._common.apis.rdl_api_v_2_14', 'RDLApi', '2.16'),
    'RolesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.roles_api_v_2_14', 'RolesApi', '2.16'),
    'SAML2SSOApi': __LazyApiLoader('pypureclient.flashblade._common.apis.saml2_sso_api_v_2_16', 'SAML2SSOApi', '2.16'),
    'SMTPApi': __LazyApiLoader('pypureclient.flashblade._common.apis.smtp_api_v_2_14', 'SMTPApi', '2.16'),
    'SNMPAgentsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.snmp_agents_api_v_2_14', 'SNMPAgentsApi', '2.16'),
    'SNMPManagersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.snmp_managers_api_v_2_14', 'SNMPManagersApi', '2.16'),
    'ServersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.servers_api_v_2_16', 'ServersApi', '2.16'),
    'SessionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.sessions_api_v_2_14', 'SessionsApi', '2.16'),
    'SoftwareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.software_api_v_2_16', 'SoftwareApi', '2.16'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.subnets_api_v_2_14', 'SubnetsApi', '2.16'),
    'SupportApi': __LazyApiLoader('pypureclient.flashblade._common.apis.support_api_v_2_14', 'SupportApi', '2.16'),
    'SupportDiagnosticsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.support_diagnostics_api_v_2_16', 'SupportDiagnosticsApi', '2.16'),
    'SyslogApi': __LazyApiLoader('pypureclient.flashblade._common.apis.syslog_api_v_2_14', 'SyslogApi', '2.16'),
    'TargetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.targets_api_v_2_14', 'TargetsApi', '2.16'),
    'UsageApi': __LazyApiLoader('pypureclient.flashblade._common.apis.usage_api_v_2_14', 'UsageApi', '2.16'),
    'VerificationKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.verification_keys_api_v_2_14', 'VerificationKeysApi', '2.16'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
