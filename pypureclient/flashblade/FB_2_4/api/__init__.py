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
    'APIClientsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.api_clients_api_v_2_0', 'APIClientsApi', '2.4'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flashblade._common.apis.active_directory_api_v_2_0', 'ActiveDirectoryApi', '2.4'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.administrators_api_v_2_3', 'AdministratorsApi', '2.4'),
    'AlertWatchersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.alert_watchers_api_v_2_0', 'AlertWatchersApi', '2.4'),
    'AlertsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.alerts_api_v_2_0', 'AlertsApi', '2.4'),
    'ArrayConnectionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.array_connections_api_v_2_0', 'ArrayConnectionsApi', '2.4'),
    'ArraysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.arrays_api_v_2_1', 'ArraysApi', '2.4'),
    'AuditsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.audits_api_v_2_0', 'AuditsApi', '2.4'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flashblade._common.apis.authorization_api_v_2_0', 'AuthorizationApi', '2.4'),
    'BladesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.blades_api_v_2_0', 'BladesApi', '2.4'),
    'BucketReplicaLinksApi': __LazyApiLoader('pypureclient.flashblade._common.apis.bucket_replica_links_api_v_2_2', 'BucketReplicaLinksApi', '2.4'),
    'BucketsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.buckets_api_v_2_0', 'BucketsApi', '2.4'),
    'CertificateGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.certificate_groups_api_v_2_0', 'CertificateGroupsApi', '2.4'),
    'CertificatesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.certificates_api_v_2_0', 'CertificatesApi', '2.4'),
    'ClientsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.clients_api_v_2_0', 'ClientsApi', '2.4'),
    'DNSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.dns_api_v_2_0', 'DNSApi', '2.4'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.directory_services_api_v_2_0', 'DirectoryServicesApi', '2.4'),
    'DrivesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.drives_api_v_2_4', 'DrivesApi', '2.4'),
    'FileSystemReplicaLinksApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_replica_links_api_v_2_0', 'FileSystemReplicaLinksApi', '2.4'),
    'FileSystemSnapshotsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_system_snapshots_api_v_2_0', 'FileSystemSnapshotsApi', '2.4'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.file_systems_api_v_2_3', 'FileSystemsApi', '2.4'),
    'HardwareApi': __LazyApiLoader('pypureclient.flashblade._common.apis.hardware_api_v_2_0', 'HardwareApi', '2.4'),
    'HardwareConnectorsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.hardware_connectors_api_v_2_3', 'HardwareConnectorsApi', '2.4'),
    'KMIPApi': __LazyApiLoader('pypureclient.flashblade._common.apis.kmip_api_v_2_1', 'KMIPApi', '2.4'),
    'KeytabsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.keytabs_api_v_2_0', 'KeytabsApi', '2.4'),
    'LifecycleRulesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.lifecycle_rules_api_v_2_1', 'LifecycleRulesApi', '2.4'),
    'LinkAggregationGroupsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.link_aggregation_groups_api_v_2_0', 'LinkAggregationGroupsApi', '2.4'),
    'LogsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.logs_api_v_2_4', 'LogsApi', '2.4'),
    'NetworkInterfacesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.network_interfaces_api_v_2_0', 'NetworkInterfacesApi', '2.4'),
    'ObjectStoreAccessKeysApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_access_keys_api_v_2_0', 'ObjectStoreAccessKeysApi', '2.4'),
    'ObjectStoreAccountsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_accounts_api_v_2_0', 'ObjectStoreAccountsApi', '2.4'),
    'ObjectStoreRemoteCredentialsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_remote_credentials_api_v_2_0', 'ObjectStoreRemoteCredentialsApi', '2.4'),
    'ObjectStoreUsersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_users_api_v_2_0', 'ObjectStoreUsersApi', '2.4'),
    'ObjectStoreVirtualHostsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.object_store_virtual_hosts_api_v_2_0', 'ObjectStoreVirtualHostsApi', '2.4'),
    'PoliciesAllApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_all_api_v_2_2', 'PoliciesAllApi', '2.4'),
    'PoliciesNFSApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_nfs_api_v_2_4', 'PoliciesNFSApi', '2.4'),
    'PoliciesObjectStoreAccessApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_object_store_access_api_v_2_4', 'PoliciesObjectStoreAccessApi', '2.4'),
    'PoliciesSnapshotApi': __LazyApiLoader('pypureclient.flashblade._common.apis.policies_snapshot_api_v_2_2', 'PoliciesSnapshotApi', '2.4'),
    'QuotasApi': __LazyApiLoader('pypureclient.flashblade._common.apis.quotas_api_v_2_0', 'QuotasApi', '2.4'),
    'RDLApi': __LazyApiLoader('pypureclient.flashblade._common.apis.rdl_api_v_2_1', 'RDLApi', '2.4'),
    'RolesApi': __LazyApiLoader('pypureclient.flashblade._common.apis.roles_api_v_2_0', 'RolesApi', '2.4'),
    'SMTPApi': __LazyApiLoader('pypureclient.flashblade._common.apis.smtp_api_v_2_0', 'SMTPApi', '2.4'),
    'SNMPAgentsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.snmp_agents_api_v_2_0', 'SNMPAgentsApi', '2.4'),
    'SNMPManagersApi': __LazyApiLoader('pypureclient.flashblade._common.apis.snmp_managers_api_v_2_0', 'SNMPManagersApi', '2.4'),
    'SessionsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.sessions_api_v_2_3', 'SessionsApi', '2.4'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.subnets_api_v_2_0', 'SubnetsApi', '2.4'),
    'SupportApi': __LazyApiLoader('pypureclient.flashblade._common.apis.support_api_v_2_0', 'SupportApi', '2.4'),
    'SyslogApi': __LazyApiLoader('pypureclient.flashblade._common.apis.syslog_api_v_2_0', 'SyslogApi', '2.4'),
    'TargetsApi': __LazyApiLoader('pypureclient.flashblade._common.apis.targets_api_v_2_0', 'TargetsApi', '2.4'),
    'UsageApi': __LazyApiLoader('pypureclient.flashblade._common.apis.usage_api_v_2_0', 'UsageApi', '2.4'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
