"""
    FlashArray REST API
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
    'APIClientsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.api_clients_api_v_2_36', 'APIClientsApi', '2.55'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flasharray._common.apis.active_directory_api_v_2_55', 'ActiveDirectoryApi', '2.55'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.administrators_api_v_2_54', 'AdministratorsApi', '2.55'),
    'AlertWatchersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.alert_watchers_api_v_2_49', 'AlertWatchersApi', '2.55'),
    'AlertsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.alerts_api_v_2_49', 'AlertsApi', '2.55'),
    'AppsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.apps_api_v_2_36', 'AppsApi', '2.55'),
    'ArrayConnectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.array_connections_api_v_2_55', 'ArrayConnectionsApi', '2.55'),
    'ArraysApi': __LazyApiLoader('pypureclient.flasharray._common.apis.arrays_api_v_2_51', 'ArraysApi', '2.55'),
    'AuditsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.audits_api_v_2_49', 'AuditsApi', '2.55'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flasharray._common.apis.authorization_api_v_2_47', 'AuthorizationApi', '2.55'),
    'BucketsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.buckets_api_v_2_52', 'BucketsApi', '2.55'),
    'CertificateGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.certificate_groups_api_v_2_41', 'CertificateGroupsApi', '2.55'),
    'CertificatesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.certificates_api_v_2_41', 'CertificatesApi', '2.55'),
    'ConnectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.connections_api_v_2_49', 'ConnectionsApi', '2.55'),
    'ContainerDefaultProtectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.container_default_protections_api_v_2_49', 'ContainerDefaultProtectionsApi', '2.55'),
    'ControllersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.controllers_api_v_2_36', 'ControllersApi', '2.55'),
    'DNSApi': __LazyApiLoader('pypureclient.flasharray._common.apis.dns_api_v_2_49', 'DNSApi', '2.55'),
    'DataSealingKeysApi': __LazyApiLoader('pypureclient.flasharray._common.apis.data_sealing_keys_api_v_2_55', 'DataSealingKeysApi', '2.55'),
    'DirectoriesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directories_api_v_2_55', 'DirectoriesApi', '2.55'),
    'DirectoryExportsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_exports_api_v_2_51', 'DirectoryExportsApi', '2.55'),
    'DirectoryQuotasApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_quotas_api_v_2_49', 'DirectoryQuotasApi', '2.55'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_services_api_v_2_55', 'DirectoryServicesApi', '2.55'),
    'DirectorySnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_snapshots_api_v_2_49', 'DirectorySnapshotsApi', '2.55'),
    'DrivesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.drives_api_v_2_36', 'DrivesApi', '2.55'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.file_systems_api_v_2_51', 'FileSystemsApi', '2.55'),
    'FilesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.files_api_v_2_36', 'FilesApi', '2.55'),
    'FleetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.fleets_api_v_2_39', 'FleetsApi', '2.55'),
    'HardwareApi': __LazyApiLoader('pypureclient.flasharray._common.apis.hardware_api_v_2_36', 'HardwareApi', '2.55'),
    'HostGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.host_groups_api_v_2_50', 'HostGroupsApi', '2.55'),
    'HostsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.hosts_api_v_2_50', 'HostsApi', '2.55'),
    'KMIPApi': __LazyApiLoader('pypureclient.flasharray._common.apis.kmip_api_v_2_36', 'KMIPApi', '2.55'),
    'LifecycleRulesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.lifecycle_rules_api_v_2_51', 'LifecycleRulesApi', '2.55'),
    'LogTargetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.log_targets_api_v_2_49', 'LogTargetsApi', '2.55'),
    'MaintenanceWindowsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.maintenance_windows_api_v_2_36', 'MaintenanceWindowsApi', '2.55'),
    'NetworkInterfacesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.network_interfaces_api_v_2_55', 'NetworkInterfacesApi', '2.55'),
    'ObjectStoreAccessKeysApi': __LazyApiLoader('pypureclient.flasharray._common.apis.object_store_access_keys_api_v_2_51', 'ObjectStoreAccessKeysApi', '2.55'),
    'ObjectStoreAccountsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.object_store_accounts_api_v_2_52', 'ObjectStoreAccountsApi', '2.55'),
    'ObjectStoreUsersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.object_store_users_api_v_2_51', 'ObjectStoreUsersApi', '2.55'),
    'ObjectStoreVirtualHostsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.object_store_virtual_hosts_api_v_2_51', 'ObjectStoreVirtualHostsApi', '2.55'),
    'OffloadsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.offloads_api_v_2_50', 'OffloadsApi', '2.55'),
    'PodReplicaLinksApi': __LazyApiLoader('pypureclient.flasharray._common.apis.pod_replica_links_api_v_2_52', 'PodReplicaLinksApi', '2.55'),
    'PodsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.pods_api_v_2_55', 'PodsApi', '2.55'),
    'PoliciesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.policies_api_v_2_54', 'PoliciesApi', '2.55'),
    'PortsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.ports_api_v_2_49', 'PortsApi', '2.55'),
    'PresetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.presets_api_v_2_51', 'PresetsApi', '2.55'),
    'ProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.protection_group_snapshots_api_v_2_49', 'ProtectionGroupSnapshotsApi', '2.55'),
    'ProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.protection_groups_api_v_2_49', 'ProtectionGroupsApi', '2.55'),
    'RealmConnectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.realm_connections_api_v_2_55', 'RealmConnectionsApi', '2.55'),
    'RealmsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.realms_api_v_2_55', 'RealmsApi', '2.55'),
    'RemoteArraysApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_arrays_api_v_2_54', 'RemoteArraysApi', '2.55'),
    'RemotePodsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_pods_api_v_2_50', 'RemotePodsApi', '2.55'),
    'RemoteProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_protection_group_snapshots_api_v_2_49', 'RemoteProtectionGroupSnapshotsApi', '2.55'),
    'RemoteProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_protection_groups_api_v_2_49', 'RemoteProtectionGroupsApi', '2.55'),
    'RemoteRealmsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_realms_api_v_2_50', 'RemoteRealmsApi', '2.55'),
    'RemoteVolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_volume_snapshots_api_v_2_49', 'RemoteVolumeSnapshotsApi', '2.55'),
    'ResourceAccessesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.resource_accesses_api_v_2_40', 'ResourceAccessesApi', '2.55'),
    'SAML2SSOApi': __LazyApiLoader('pypureclient.flasharray._common.apis.saml2_sso_api_v_2_38', 'SAML2SSOApi', '2.55'),
    'SMISApi': __LazyApiLoader('pypureclient.flasharray._common.apis.smis_api_v_2_36', 'SMISApi', '2.55'),
    'SMTPApi': __LazyApiLoader('pypureclient.flasharray._common.apis.smtp_api_v_2_36', 'SMTPApi', '2.55'),
    'SNMPAgentsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.snmp_agents_api_v_2_36', 'SNMPAgentsApi', '2.55'),
    'SNMPManagersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.snmp_managers_api_v_2_49', 'SNMPManagersApi', '2.55'),
    'ServersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.servers_api_v_2_55', 'ServersApi', '2.55'),
    'SessionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.sessions_api_v_2_36', 'SessionsApi', '2.55'),
    'SoftwareApi': __LazyApiLoader('pypureclient.flasharray._common.apis.software_api_v_2_36', 'SoftwareApi', '2.55'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.subnets_api_v_2_55', 'SubnetsApi', '2.55'),
    'SubscriptionAssetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.subscription_assets_api_v_2_36', 'SubscriptionAssetsApi', '2.55'),
    'SubscriptionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.subscriptions_api_v_2_36', 'SubscriptionsApi', '2.55'),
    'SupportApi': __LazyApiLoader('pypureclient.flasharray._common.apis.support_api_v_2_51', 'SupportApi', '2.55'),
    'SyslogApi': __LazyApiLoader('pypureclient.flasharray._common.apis.syslog_api_v_2_49', 'SyslogApi', '2.55'),
    'TopologyGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.topology_groups_api_v_2_54', 'TopologyGroupsApi', '2.55'),
    'UserGroupQuotasApi': __LazyApiLoader('pypureclient.flasharray._common.apis.user_group_quotas_api_v_2_49', 'UserGroupQuotasApi', '2.55'),
    'VchostConnectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.vchost_connections_api_v_2_36', 'VchostConnectionsApi', '2.55'),
    'VchostsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.vchosts_api_v_2_36', 'VchostsApi', '2.55'),
    'VirtualMachinesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.virtual_machines_api_v_2_36', 'VirtualMachinesApi', '2.55'),
    'VolumeGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.volume_groups_api_v_2_49', 'VolumeGroupsApi', '2.55'),
    'VolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.volume_snapshots_api_v_2_50', 'VolumeSnapshotsApi', '2.55'),
    'VolumesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.volumes_api_v_2_49', 'VolumesApi', '2.55'),
    'WorkloadsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.workloads_api_v_2_55', 'WorkloadsApi', '2.55'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
