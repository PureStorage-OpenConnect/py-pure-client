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
    'APIClientsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.api_clients_api_v_2_0', 'APIClientsApi', '2.11'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flashblade._common.apis.active_directory_api_v_2_0', 'ActiveDirectoryApi', '2.11'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.administrators_api_v_2_3', 'AdministratorsApi', '2.11'),
    'AlertWatchersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.alert_watchers_api_v_2_0', 'AlertWatchersApi', '2.11'),
    'AlertsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.alerts_api_v_2_0', 'AlertsApi', '2.11'),
    'ArrayConnectionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.array_connections_api_v_2_0', 'ArrayConnectionsApi', '2.11'),
    'ArraysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.arrays_api_v_2_11', 'ArraysApi', '2.11'),
    'AuditsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.audits_api_v_2_0', 'AuditsApi', '2.11'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flashblade._common.apis.authorization_api_v_2_0', 'AuthorizationApi', '2.11'),
    'BladesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.blades_api_v_2_0', 'BladesApi', '2.11'),
    'BucketReplicaLinksApi': __LazyApiLoader('pypureclient.flashblade._common.apis.bucket_replica_links_api_v_2_2', 'BucketReplicaLinksApi', '2.11'),
    'BucketsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.buckets_api_v_2_8', 'BucketsApi', '2.11'),
    'CertificateGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.certificate_groups_api_v_2_0', 'CertificateGroupsApi', '2.11'),
    'CertificatesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.certificates_api_v_2_0', 'CertificatesApi', '2.11'),
    'ClientsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.clients_api_v_2_0', 'ClientsApi', '2.11'),
    'DNSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.dns_api_v_2_0', 'DNSApi', '2.11'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.directory_services_api_v_2_0', 'DirectoryServicesApi', '2.11'),
    'DrivesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.drives_api_v_2_4', 'DrivesApi', '2.11'),
    'FileSystemReplicaLinksApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_replica_links_api_v_2_10', 'FileSystemReplicaLinksApi', '2.11'),
    'FileSystemSnapshotsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_snapshots_api_v_2_0', 'FileSystemSnapshotsApi', '2.11'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_systems_api_v_2_10', 'FileSystemsApi', '2.11'),
    'HardwareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.hardware_api_v_2_0', 'HardwareApi', '2.11'),
    'HardwareConnectorsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.hardware_connectors_api_v_2_3', 'HardwareConnectorsApi', '2.11'),
    'KMIPApi': __LazyApiLoader('pypureclient.flashblade._common.apis.kmip_api_v_2_1', 'KMIPApi', '2.11'),
    'KeytabsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.keytabs_api_v_2_0', 'KeytabsApi', '2.11'),
    'LifecycleRulesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.lifecycle_rules_api_v_2_1', 'LifecycleRulesApi', '2.11'),
    'LinkAggregationGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.link_aggregation_groups_api_v_2_0', 'LinkAggregationGroupsApi', '2.11'),
    'LogsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.logs_api_v_2_4', 'LogsApi', '2.11'),
    'NetworkInterfacesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.network_interfaces_api_v_2_6', 'NetworkInterfacesApi', '2.11'),
    'ObjectStoreAccessKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_access_keys_api_v_2_0', 'ObjectStoreAccessKeysApi', '2.11'),
    'ObjectStoreAccountsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_accounts_api_v_2_8', 'ObjectStoreAccountsApi', '2.11'),
    'ObjectStoreRemoteCredentialsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_remote_credentials_api_v_2_0', 'ObjectStoreRemoteCredentialsApi', '2.11'),
    'ObjectStoreUsersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_users_api_v_2_0', 'ObjectStoreUsersApi', '2.11'),
    'ObjectStoreVirtualHostsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_virtual_hosts_api_v_2_0', 'ObjectStoreVirtualHostsApi', '2.11'),
    'PoliciesAllApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_all_api_v_2_2', 'PoliciesAllApi', '2.11'),
    'PoliciesNFSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_nfs_api_v_2_4', 'PoliciesNFSApi', '2.11'),
    'PoliciesObjectStoreAccessApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_object_store_access_api_v_2_11', 'PoliciesObjectStoreAccessApi', '2.11'),
    'PoliciesSMBClientApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_smb_client_api_v_2_10', 'PoliciesSMBClientApi', '2.11'),
    'PoliciesSMBShareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_smb_share_api_v_2_10', 'PoliciesSMBShareApi', '2.11'),
    'PoliciesSnapshotApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_snapshot_api_v_2_2', 'PoliciesSnapshotApi', '2.11'),
    'QuotasApi': __LazyApiLoader('pypureclient.flashblade._common.apis.quotas_api_v_2_0', 'QuotasApi', '2.11'),
    'RDLApi': __LazyApiLoader('pypureclient.flashblade._common.apis.rdl_api_v_2_1', 'RDLApi', '2.11'),
    'RolesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.roles_api_v_2_0', 'RolesApi', '2.11'),
    'SMTPApi': __LazyApiLoader('pypureclient.flashblade._common.apis.smtp_api_v_2_0', 'SMTPApi', '2.11'),
    'SNMPAgentsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.snmp_agents_api_v_2_0', 'SNMPAgentsApi', '2.11'),
    'SNMPManagersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.snmp_managers_api_v_2_0', 'SNMPManagersApi', '2.11'),
    'SessionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.sessions_api_v_2_3', 'SessionsApi', '2.11'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.subnets_api_v_2_0', 'SubnetsApi', '2.11'),
    'SupportApi': __LazyApiLoader('pypureclient.flashblade._common.apis.support_api_v_2_0', 'SupportApi', '2.11'),
    'SyslogApi': __LazyApiLoader('pypureclient.flashblade._common.apis.syslog_api_v_2_0', 'SyslogApi', '2.11'),
    'TargetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.targets_api_v_2_0', 'TargetsApi', '2.11'),
    'UsageApi': __LazyApiLoader('pypureclient.flashblade._common.apis.usage_api_v_2_0', 'UsageApi', '2.11'),
    'VerificationKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.verification_keys_api_v_2_7', 'VerificationKeysApi', '2.11'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
