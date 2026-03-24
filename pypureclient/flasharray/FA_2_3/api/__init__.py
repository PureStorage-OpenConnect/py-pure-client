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
    'APIClientsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.api_clients_api_v_2_1', 'APIClientsApi', '2.3'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flasharray._common.apis.active_directory_api_v_2_3', 'ActiveDirectoryApi', '2.3'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.administrators_api_v_2_2', 'AdministratorsApi', '2.3'),
    'AlertsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.alerts_api_v_2_2', 'AlertsApi', '2.3'),
    'AppsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.apps_api_v_2_2', 'AppsApi', '2.3'),
    'ArraysApi': __LazyApiLoader('pypureclient.flasharray._common.apis.arrays_api_v_2_2', 'ArraysApi', '2.3'),
    'AuditsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.audits_api_v_2_2', 'AuditsApi', '2.3'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flasharray._common.apis.authorization_api_v_2_0', 'AuthorizationApi', '2.3'),
    'ConnectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.connections_api_v_2_1', 'ConnectionsApi', '2.3'),
    'ControllersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.controllers_api_v_2_2', 'ControllersApi', '2.3'),
    'DNSApi': __LazyApiLoader('pypureclient.flasharray._common.apis.dns_api_v_2_2', 'DNSApi', '2.3'),
    'DirectoriesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directories_api_v_2_3', 'DirectoriesApi', '2.3'),
    'DirectoryExportsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_exports_api_v_2_3', 'DirectoryExportsApi', '2.3'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_services_api_v_2_2', 'DirectoryServicesApi', '2.3'),
    'DirectorySnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_snapshots_api_v_2_3', 'DirectorySnapshotsApi', '2.3'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.file_systems_api_v_2_3', 'FileSystemsApi', '2.3'),
    'HardwareApi': __LazyApiLoader('pypureclient.flasharray._common.apis.hardware_api_v_2_2', 'HardwareApi', '2.3'),
    'HostGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.host_groups_api_v_2_1', 'HostGroupsApi', '2.3'),
    'HostsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.hosts_api_v_2_1', 'HostsApi', '2.3'),
    'KMIPApi': __LazyApiLoader('pypureclient.flasharray._common.apis.kmip_api_v_2_2', 'KMIPApi', '2.3'),
    'MaintenanceWindowsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.maintenance_windows_api_v_2_2', 'MaintenanceWindowsApi', '2.3'),
    'OffloadsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.offloads_api_v_2_1', 'OffloadsApi', '2.3'),
    'PodReplicaLinksApi': __LazyApiLoader('pypureclient.flasharray._common.apis.pod_replica_links_api_v_2_2', 'PodReplicaLinksApi', '2.3'),
    'PodsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.pods_api_v_2_3', 'PodsApi', '2.3'),
    'PoliciesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.policies_api_v_2_3', 'PoliciesApi', '2.3'),
    'PortsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.ports_api_v_2_2', 'PortsApi', '2.3'),
    'ProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.protection_group_snapshots_api_v_2_1', 'ProtectionGroupSnapshotsApi', '2.3'),
    'ProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.protection_groups_api_v_2_1', 'ProtectionGroupsApi', '2.3'),
    'RemotePodsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_pods_api_v_2_1', 'RemotePodsApi', '2.3'),
    'RemoteProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_protection_group_snapshots_api_v_2_1', 'RemoteProtectionGroupSnapshotsApi', '2.3'),
    'RemoteProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_protection_groups_api_v_2_1', 'RemoteProtectionGroupsApi', '2.3'),
    'RemoteVolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_volume_snapshots_api_v_2_1', 'RemoteVolumeSnapshotsApi', '2.3'),
    'SMISApi': __LazyApiLoader('pypureclient.flasharray._common.apis.smis_api_v_2_2', 'SMISApi', '2.3'),
    'SoftwareApi': __LazyApiLoader('pypureclient.flasharray._common.apis.software_api_v_2_2', 'SoftwareApi', '2.3'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.subnets_api_v_2_2', 'SubnetsApi', '2.3'),
    'SupportApi': __LazyApiLoader('pypureclient.flasharray._common.apis.support_api_v_2_2', 'SupportApi', '2.3'),
    'VolumeGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.volume_groups_api_v_2_3', 'VolumeGroupsApi', '2.3'),
    'VolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.volume_snapshots_api_v_2_3', 'VolumeSnapshotsApi', '2.3'),
    'VolumesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.volumes_api_v_2_3', 'VolumesApi', '2.3'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
