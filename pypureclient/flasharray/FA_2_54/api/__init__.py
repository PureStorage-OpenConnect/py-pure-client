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
    'APIClientsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.api_clients_api_v_2_36', 'APIClientsApi', '2.54'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flasharray._common.apis.active_directory_api_v_2_52', 'ActiveDirectoryApi', '2.54'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.administrators_api_v_2_54', 'AdministratorsApi', '2.54'),
    'AlertWatchersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.alert_watchers_api_v_2_49', 'AlertWatchersApi', '2.54'),
    'AlertsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.alerts_api_v_2_49', 'AlertsApi', '2.54'),
    'AppsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.apps_api_v_2_36', 'AppsApi', '2.54'),
    'ArrayConnectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.array_connections_api_v_2_50', 'ArrayConnectionsApi', '2.54'),
    'ArraysApi': __LazyApiLoader('pypureclient.flasharray._common.apis.arrays_api_v_2_51', 'ArraysApi', '2.54'),
    'AuditsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.audits_api_v_2_49', 'AuditsApi', '2.54'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flasharray._common.apis.authorization_api_v_2_47', 'AuthorizationApi', '2.54'),
    'BucketsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.buckets_api_v_2_52', 'BucketsApi', '2.54'),
    'CertificateGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.certificate_groups_api_v_2_41', 'CertificateGroupsApi', '2.54'),
    'CertificatesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.certificates_api_v_2_41', 'CertificatesApi', '2.54'),
    'ConnectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.connections_api_v_2_49', 'ConnectionsApi', '2.54'),
    'ContainerDefaultProtectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.container_default_protections_api_v_2_49', 'ContainerDefaultProtectionsApi', '2.54'),
    'ControllersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.controllers_api_v_2_36', 'ControllersApi', '2.54'),
    'DNSApi': __LazyApiLoader('pypureclient.flasharray._common.apis.dns_api_v_2_49', 'DNSApi', '2.54'),
    'DirectoriesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directories_api_v_2_54', 'DirectoriesApi', '2.54'),
    'DirectoryExportsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_exports_api_v_2_51', 'DirectoryExportsApi', '2.54'),
    'DirectoryQuotasApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_quotas_api_v_2_49', 'DirectoryQuotasApi', '2.54'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_services_api_v_2_52', 'DirectoryServicesApi', '2.54'),
    'DirectorySnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_snapshots_api_v_2_49', 'DirectorySnapshotsApi', '2.54'),
    'DrivesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.drives_api_v_2_36', 'DrivesApi', '2.54'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.file_systems_api_v_2_51', 'FileSystemsApi', '2.54'),
    'FilesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.files_api_v_2_36', 'FilesApi', '2.54'),
    'FleetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.fleets_api_v_2_39', 'FleetsApi', '2.54'),
    'HardwareApi': __LazyApiLoader('pypureclient.flasharray._common.apis.hardware_api_v_2_36', 'HardwareApi', '2.54'),
    'HostGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.host_groups_api_v_2_50', 'HostGroupsApi', '2.54'),
    'HostsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.hosts_api_v_2_50', 'HostsApi', '2.54'),
    'KMIPApi': __LazyApiLoader('pypureclient.flasharray._common.apis.kmip_api_v_2_36', 'KMIPApi', '2.54'),
    'LifecycleRulesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.lifecycle_rules_api_v_2_51', 'LifecycleRulesApi', '2.54'),
    'LogTargetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.log_targets_api_v_2_49', 'LogTargetsApi', '2.54'),
    'MaintenanceWindowsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.maintenance_windows_api_v_2_36', 'MaintenanceWindowsApi', '2.54'),
    'NetworkInterfacesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.network_interfaces_api_v_2_49', 'NetworkInterfacesApi', '2.54'),
    'ObjectStoreAccessKeysApi': __LazyApiLoader('pypureclient.flasharray._common.apis.object_store_access_keys_api_v_2_51', 'ObjectStoreAccessKeysApi', '2.54'),
    'ObjectStoreAccountsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.object_store_accounts_api_v_2_52', 'ObjectStoreAccountsApi', '2.54'),
    'ObjectStoreUsersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.object_store_users_api_v_2_51', 'ObjectStoreUsersApi', '2.54'),
    'ObjectStoreVirtualHostsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.object_store_virtual_hosts_api_v_2_51', 'ObjectStoreVirtualHostsApi', '2.54'),
    'OffloadsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.offloads_api_v_2_50', 'OffloadsApi', '2.54'),
    'PodReplicaLinksApi': __LazyApiLoader('pypureclient.flasharray._common.apis.pod_replica_links_api_v_2_52', 'PodReplicaLinksApi', '2.54'),
    'PodsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.pods_api_v_2_49', 'PodsApi', '2.54'),
    'PoliciesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.policies_api_v_2_54', 'PoliciesApi', '2.54'),
    'PortsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.ports_api_v_2_49', 'PortsApi', '2.54'),
    'PresetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.presets_api_v_2_51', 'PresetsApi', '2.54'),
    'ProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.protection_group_snapshots_api_v_2_49', 'ProtectionGroupSnapshotsApi', '2.54'),
    'ProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.protection_groups_api_v_2_49', 'ProtectionGroupsApi', '2.54'),
    'RealmConnectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.realm_connections_api_v_2_50', 'RealmConnectionsApi', '2.54'),
    'RealmsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.realms_api_v_2_50', 'RealmsApi', '2.54'),
    'RemoteArraysApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_arrays_api_v_2_54', 'RemoteArraysApi', '2.54'),
    'RemotePodsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_pods_api_v_2_50', 'RemotePodsApi', '2.54'),
    'RemoteProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_protection_group_snapshots_api_v_2_49', 'RemoteProtectionGroupSnapshotsApi', '2.54'),
    'RemoteProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_protection_groups_api_v_2_49', 'RemoteProtectionGroupsApi', '2.54'),
    'RemoteRealmsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_realms_api_v_2_50', 'RemoteRealmsApi', '2.54'),
    'RemoteVolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_volume_snapshots_api_v_2_49', 'RemoteVolumeSnapshotsApi', '2.54'),
    'ResourceAccessesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.resource_accesses_api_v_2_40', 'ResourceAccessesApi', '2.54'),
    'SAML2SSOApi': __LazyApiLoader('pypureclient.flasharray._common.apis.saml2_sso_api_v_2_38', 'SAML2SSOApi', '2.54'),
    'SMISApi': __LazyApiLoader('pypureclient.flasharray._common.apis.smis_api_v_2_36', 'SMISApi', '2.54'),
    'SMTPApi': __LazyApiLoader('pypureclient.flasharray._common.apis.smtp_api_v_2_36', 'SMTPApi', '2.54'),
    'SNMPAgentsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.snmp_agents_api_v_2_36', 'SNMPAgentsApi', '2.54'),
    'SNMPManagersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.snmp_managers_api_v_2_49', 'SNMPManagersApi', '2.54'),
    'ServersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.servers_api_v_2_54', 'ServersApi', '2.54'),
    'SessionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.sessions_api_v_2_36', 'SessionsApi', '2.54'),
    'SoftwareApi': __LazyApiLoader('pypureclient.flasharray._common.apis.software_api_v_2_36', 'SoftwareApi', '2.54'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.subnets_api_v_2_36', 'SubnetsApi', '2.54'),
    'SubscriptionAssetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.subscription_assets_api_v_2_36', 'SubscriptionAssetsApi', '2.54'),
    'SubscriptionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.subscriptions_api_v_2_36', 'SubscriptionsApi', '2.54'),
    'SupportApi': __LazyApiLoader('pypureclient.flasharray._common.apis.support_api_v_2_51', 'SupportApi', '2.54'),
    'SyslogApi': __LazyApiLoader('pypureclient.flasharray._common.apis.syslog_api_v_2_49', 'SyslogApi', '2.54'),
    'TopologyGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.topology_groups_api_v_2_54', 'TopologyGroupsApi', '2.54'),
    'UserGroupQuotasApi': __LazyApiLoader('pypureclient.flasharray._common.apis.user_group_quotas_api_v_2_49', 'UserGroupQuotasApi', '2.54'),
    'VchostConnectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.vchost_connections_api_v_2_36', 'VchostConnectionsApi', '2.54'),
    'VchostsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.vchosts_api_v_2_36', 'VchostsApi', '2.54'),
    'VirtualMachinesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.virtual_machines_api_v_2_36', 'VirtualMachinesApi', '2.54'),
    'VolumeGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.volume_groups_api_v_2_49', 'VolumeGroupsApi', '2.54'),
    'VolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.volume_snapshots_api_v_2_50', 'VolumeSnapshotsApi', '2.54'),
    'VolumesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.volumes_api_v_2_49', 'VolumesApi', '2.54'),
    'WorkloadsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.workloads_api_v_2_51', 'WorkloadsApi', '2.54'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
