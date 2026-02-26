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
    'APIClientsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.api_clients_api_v_1', 'APIClientsApi', '2.49'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flasharray.common.apis.active_directory_api_v_44', 'ActiveDirectoryApi', '2.49'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.administrators_api_v_49', 'AdministratorsApi', '2.49'),
    'AlertWatchersApi': __LazyApiLoader('pypureclient.flasharray.common.apis.alert_watchers_api_v_49', 'AlertWatchersApi', '2.49'),
    'AlertsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.alerts_api_v_49', 'AlertsApi', '2.49'),
    'AppsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.apps_api_v_2', 'AppsApi', '2.49'),
    'ArrayConnectionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.array_connections_api_v_49', 'ArrayConnectionsApi', '2.49'),
    'ArraysApi': __LazyApiLoader('pypureclient.flasharray.common.apis.arrays_api_v_49', 'ArraysApi', '2.49'),
    'AuditsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.audits_api_v_49', 'AuditsApi', '2.49'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flasharray.common.apis.authorization_api_v_47', 'AuthorizationApi', '2.49'),
    'CertificateGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.certificate_groups_api_v_41', 'CertificateGroupsApi', '2.49'),
    'CertificatesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.certificates_api_v_41', 'CertificatesApi', '2.49'),
    'ConnectionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.connections_api_v_49', 'ConnectionsApi', '2.49'),
    'ContainerDefaultProtectionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.container_default_protections_api_v_49', 'ContainerDefaultProtectionsApi', '2.49'),
    'ControllersApi': __LazyApiLoader('pypureclient.flasharray.common.apis.controllers_api_v_2', 'ControllersApi', '2.49'),
    'DNSApi': __LazyApiLoader('pypureclient.flasharray.common.apis.dns_api_v_49', 'DNSApi', '2.49'),
    'DirectoriesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directories_api_v_49', 'DirectoriesApi', '2.49'),
    'DirectoryExportsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_exports_api_v_49', 'DirectoryExportsApi', '2.49'),
    'DirectoryQuotasApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_quotas_api_v_49', 'DirectoryQuotasApi', '2.49'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_services_api_v_49', 'DirectoryServicesApi', '2.49'),
    'DirectorySnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_snapshots_api_v_49', 'DirectorySnapshotsApi', '2.49'),
    'DrivesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.drives_api_v_4', 'DrivesApi', '2.49'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.file_systems_api_v_49', 'FileSystemsApi', '2.49'),
    'FilesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.files_api_v_26', 'FilesApi', '2.49'),
    'FleetsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.fleets_api_v_39', 'FleetsApi', '2.49'),
    'HardwareApi': __LazyApiLoader('pypureclient.flasharray.common.apis.hardware_api_v_2', 'HardwareApi', '2.49'),
    'HostGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.host_groups_api_v_49', 'HostGroupsApi', '2.49'),
    'HostsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.hosts_api_v_49', 'HostsApi', '2.49'),
    'KMIPApi': __LazyApiLoader('pypureclient.flasharray.common.apis.kmip_api_v_2', 'KMIPApi', '2.49'),
    'LogTargetsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.log_targets_api_v_49', 'LogTargetsApi', '2.49'),
    'MaintenanceWindowsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.maintenance_windows_api_v_2', 'MaintenanceWindowsApi', '2.49'),
    'NetworkInterfacesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.network_interfaces_api_v_49', 'NetworkInterfacesApi', '2.49'),
    'OffloadsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.offloads_api_v_49', 'OffloadsApi', '2.49'),
    'PodReplicaLinksApi': __LazyApiLoader('pypureclient.flasharray.common.apis.pod_replica_links_api_v_49', 'PodReplicaLinksApi', '2.49'),
    'PodsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.pods_api_v_49', 'PodsApi', '2.49'),
    'PoliciesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.policies_api_v_49', 'PoliciesApi', '2.49'),
    'PortsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.ports_api_v_49', 'PortsApi', '2.49'),
    'PresetsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.presets_api_v_40', 'PresetsApi', '2.49'),
    'ProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.protection_group_snapshots_api_v_49', 'ProtectionGroupSnapshotsApi', '2.49'),
    'ProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.protection_groups_api_v_49', 'ProtectionGroupsApi', '2.49'),
    'RealmsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.realms_api_v_49', 'RealmsApi', '2.49'),
    'RemoteArraysApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_arrays_api_v_36', 'RemoteArraysApi', '2.49'),
    'RemotePodsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_pods_api_v_49', 'RemotePodsApi', '2.49'),
    'RemoteProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_protection_group_snapshots_api_v_49', 'RemoteProtectionGroupSnapshotsApi', '2.49'),
    'RemoteProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_protection_groups_api_v_49', 'RemoteProtectionGroupsApi', '2.49'),
    'RemoteVolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_volume_snapshots_api_v_49', 'RemoteVolumeSnapshotsApi', '2.49'),
    'ResourceAccessesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.resource_accesses_api_v_40', 'ResourceAccessesApi', '2.49'),
    'SAML2SSOApi': __LazyApiLoader('pypureclient.flasharray.common.apis.saml2_sso_api_v_38', 'SAML2SSOApi', '2.49'),
    'SMISApi': __LazyApiLoader('pypureclient.flasharray.common.apis.smis_api_v_2', 'SMISApi', '2.49'),
    'SMTPApi': __LazyApiLoader('pypureclient.flasharray.common.apis.smtp_api_v_4', 'SMTPApi', '2.49'),
    'SNMPAgentsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.snmp_agents_api_v_4', 'SNMPAgentsApi', '2.49'),
    'SNMPManagersApi': __LazyApiLoader('pypureclient.flasharray.common.apis.snmp_managers_api_v_49', 'SNMPManagersApi', '2.49'),
    'ServersApi': __LazyApiLoader('pypureclient.flasharray.common.apis.servers_api_v_44', 'ServersApi', '2.49'),
    'SessionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.sessions_api_v_4', 'SessionsApi', '2.49'),
    'SoftwareApi': __LazyApiLoader('pypureclient.flasharray.common.apis.software_api_v_29', 'SoftwareApi', '2.49'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.subnets_api_v_2', 'SubnetsApi', '2.49'),
    'SubscriptionAssetsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.subscription_assets_api_v_26', 'SubscriptionAssetsApi', '2.49'),
    'SubscriptionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.subscriptions_api_v_26', 'SubscriptionsApi', '2.49'),
    'SupportApi': __LazyApiLoader('pypureclient.flasharray.common.apis.support_api_v_41', 'SupportApi', '2.49'),
    'SyslogApi': __LazyApiLoader('pypureclient.flasharray.common.apis.syslog_api_v_49', 'SyslogApi', '2.49'),
    'UserGroupQuotasApi': __LazyApiLoader('pypureclient.flasharray.common.apis.user_group_quotas_api_v_49', 'UserGroupQuotasApi', '2.49'),
    'VchostConnectionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.vchost_connections_api_v_33', 'VchostConnectionsApi', '2.49'),
    'VchostsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.vchosts_api_v_26', 'VchostsApi', '2.49'),
    'VirtualMachinesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.virtual_machines_api_v_36', 'VirtualMachinesApi', '2.49'),
    'VolumeGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.volume_groups_api_v_49', 'VolumeGroupsApi', '2.49'),
    'VolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.volume_snapshots_api_v_49', 'VolumeSnapshotsApi', '2.49'),
    'VolumesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.volumes_api_v_49', 'VolumesApi', '2.49'),
    'WorkloadsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.workloads_api_v_49', 'WorkloadsApi', '2.49'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
