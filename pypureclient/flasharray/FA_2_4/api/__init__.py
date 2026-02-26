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
    'APIClientsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.api_clients_api_v_1', 'APIClientsApi', '2.4'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flasharray.common.apis.active_directory_api_v_3', 'ActiveDirectoryApi', '2.4'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.administrators_api_v_2', 'AdministratorsApi', '2.4'),
    'AlertWatchersApi': __LazyApiLoader('pypureclient.flasharray.common.apis.alert_watchers_api_v_4', 'AlertWatchersApi', '2.4'),
    'AlertsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.alerts_api_v_2', 'AlertsApi', '2.4'),
    'AppsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.apps_api_v_2', 'AppsApi', '2.4'),
    'ArrayConnectionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.array_connections_api_v_4', 'ArrayConnectionsApi', '2.4'),
    'ArraysApi': __LazyApiLoader('pypureclient.flasharray.common.apis.arrays_api_v_4', 'ArraysApi', '2.4'),
    'AuditsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.audits_api_v_2', 'AuditsApi', '2.4'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flasharray.common.apis.authorization_api_v_0', 'AuthorizationApi', '2.4'),
    'CertificatesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.certificates_api_v_4', 'CertificatesApi', '2.4'),
    'ConnectionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.connections_api_v_1', 'ConnectionsApi', '2.4'),
    'ControllersApi': __LazyApiLoader('pypureclient.flasharray.common.apis.controllers_api_v_2', 'ControllersApi', '2.4'),
    'DNSApi': __LazyApiLoader('pypureclient.flasharray.common.apis.dns_api_v_2', 'DNSApi', '2.4'),
    'DirectoriesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directories_api_v_3', 'DirectoriesApi', '2.4'),
    'DirectoryExportsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_exports_api_v_3', 'DirectoryExportsApi', '2.4'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_services_api_v_2', 'DirectoryServicesApi', '2.4'),
    'DirectorySnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_snapshots_api_v_3', 'DirectorySnapshotsApi', '2.4'),
    'DrivesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.drives_api_v_4', 'DrivesApi', '2.4'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.file_systems_api_v_3', 'FileSystemsApi', '2.4'),
    'HardwareApi': __LazyApiLoader('pypureclient.flasharray.common.apis.hardware_api_v_2', 'HardwareApi', '2.4'),
    'HostGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.host_groups_api_v_1', 'HostGroupsApi', '2.4'),
    'HostsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.hosts_api_v_4', 'HostsApi', '2.4'),
    'KMIPApi': __LazyApiLoader('pypureclient.flasharray.common.apis.kmip_api_v_2', 'KMIPApi', '2.4'),
    'MaintenanceWindowsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.maintenance_windows_api_v_2', 'MaintenanceWindowsApi', '2.4'),
    'NetworkInterfacesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.network_interfaces_api_v_4', 'NetworkInterfacesApi', '2.4'),
    'OffloadsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.offloads_api_v_1', 'OffloadsApi', '2.4'),
    'PodReplicaLinksApi': __LazyApiLoader('pypureclient.flasharray.common.apis.pod_replica_links_api_v_4', 'PodReplicaLinksApi', '2.4'),
    'PodsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.pods_api_v_4', 'PodsApi', '2.4'),
    'PoliciesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.policies_api_v_4', 'PoliciesApi', '2.4'),
    'PortsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.ports_api_v_2', 'PortsApi', '2.4'),
    'ProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.protection_group_snapshots_api_v_4', 'ProtectionGroupSnapshotsApi', '2.4'),
    'ProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.protection_groups_api_v_1', 'ProtectionGroupsApi', '2.4'),
    'RemotePodsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_pods_api_v_1', 'RemotePodsApi', '2.4'),
    'RemoteProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_protection_group_snapshots_api_v_4', 'RemoteProtectionGroupSnapshotsApi', '2.4'),
    'RemoteProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_protection_groups_api_v_1', 'RemoteProtectionGroupsApi', '2.4'),
    'RemoteVolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_volume_snapshots_api_v_4', 'RemoteVolumeSnapshotsApi', '2.4'),
    'SMISApi': __LazyApiLoader('pypureclient.flasharray.common.apis.smis_api_v_2', 'SMISApi', '2.4'),
    'SMTPApi': __LazyApiLoader('pypureclient.flasharray.common.apis.smtp_api_v_4', 'SMTPApi', '2.4'),
    'SNMPAgentsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.snmp_agents_api_v_4', 'SNMPAgentsApi', '2.4'),
    'SNMPManagersApi': __LazyApiLoader('pypureclient.flasharray.common.apis.snmp_managers_api_v_4', 'SNMPManagersApi', '2.4'),
    'SessionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.sessions_api_v_4', 'SessionsApi', '2.4'),
    'SoftwareApi': __LazyApiLoader('pypureclient.flasharray.common.apis.software_api_v_4', 'SoftwareApi', '2.4'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.subnets_api_v_2', 'SubnetsApi', '2.4'),
    'SupportApi': __LazyApiLoader('pypureclient.flasharray.common.apis.support_api_v_2', 'SupportApi', '2.4'),
    'SyslogApi': __LazyApiLoader('pypureclient.flasharray.common.apis.syslog_api_v_4', 'SyslogApi', '2.4'),
    'VolumeGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.volume_groups_api_v_3', 'VolumeGroupsApi', '2.4'),
    'VolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.volume_snapshots_api_v_4', 'VolumeSnapshotsApi', '2.4'),
    'VolumesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.volumes_api_v_3', 'VolumesApi', '2.4'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
