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
    'APIClientsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.api_clients_api_v_1', 'APIClientsApi', '2.21'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flasharray.common.apis.active_directory_api_v_15', 'ActiveDirectoryApi', '2.21'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.administrators_api_v_2', 'AdministratorsApi', '2.21'),
    'AlertWatchersApi': __LazyApiLoader('pypureclient.flasharray.common.apis.alert_watchers_api_v_4', 'AlertWatchersApi', '2.21'),
    'AlertsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.alerts_api_v_2', 'AlertsApi', '2.21'),
    'AppsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.apps_api_v_2', 'AppsApi', '2.21'),
    'ArrayConnectionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.array_connections_api_v_4', 'ArrayConnectionsApi', '2.21'),
    'ArraysApi': __LazyApiLoader('pypureclient.flasharray.common.apis.arrays_api_v_19', 'ArraysApi', '2.21'),
    'AuditsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.audits_api_v_2', 'AuditsApi', '2.21'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flasharray.common.apis.authorization_api_v_0', 'AuthorizationApi', '2.21'),
    'CertificatesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.certificates_api_v_4', 'CertificatesApi', '2.21'),
    'ConnectionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.connections_api_v_9', 'ConnectionsApi', '2.21'),
    'ContainerDefaultProtectionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.container_default_protections_api_v_16', 'ContainerDefaultProtectionsApi', '2.21'),
    'ControllersApi': __LazyApiLoader('pypureclient.flasharray.common.apis.controllers_api_v_2', 'ControllersApi', '2.21'),
    'DNSApi': __LazyApiLoader('pypureclient.flasharray.common.apis.dns_api_v_15', 'DNSApi', '2.21'),
    'DirectoriesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directories_api_v_21', 'DirectoriesApi', '2.21'),
    'DirectoryExportsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_exports_api_v_3', 'DirectoryExportsApi', '2.21'),
    'DirectoryQuotasApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_quotas_api_v_7', 'DirectoryQuotasApi', '2.21'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_services_api_v_21', 'DirectoryServicesApi', '2.21'),
    'DirectorySnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_snapshots_api_v_3', 'DirectorySnapshotsApi', '2.21'),
    'DrivesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.drives_api_v_4', 'DrivesApi', '2.21'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.file_systems_api_v_3', 'FileSystemsApi', '2.21'),
    'HardwareApi': __LazyApiLoader('pypureclient.flasharray.common.apis.hardware_api_v_2', 'HardwareApi', '2.21'),
    'HostGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.host_groups_api_v_16', 'HostGroupsApi', '2.21'),
    'HostsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.hosts_api_v_16', 'HostsApi', '2.21'),
    'KMIPApi': __LazyApiLoader('pypureclient.flasharray.common.apis.kmip_api_v_2', 'KMIPApi', '2.21'),
    'MaintenanceWindowsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.maintenance_windows_api_v_2', 'MaintenanceWindowsApi', '2.21'),
    'NetworkInterfacesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.network_interfaces_api_v_16', 'NetworkInterfacesApi', '2.21'),
    'OffloadsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.offloads_api_v_1', 'OffloadsApi', '2.21'),
    'PodReplicaLinksApi': __LazyApiLoader('pypureclient.flasharray.common.apis.pod_replica_links_api_v_4', 'PodReplicaLinksApi', '2.21'),
    'PodsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.pods_api_v_13', 'PodsApi', '2.21'),
    'PoliciesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.policies_api_v_21', 'PoliciesApi', '2.21'),
    'PortsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.ports_api_v_2', 'PortsApi', '2.21'),
    'ProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.protection_group_snapshots_api_v_4', 'ProtectionGroupSnapshotsApi', '2.21'),
    'ProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.protection_groups_api_v_9', 'ProtectionGroupsApi', '2.21'),
    'RemotePodsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_pods_api_v_1', 'RemotePodsApi', '2.21'),
    'RemoteProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_protection_group_snapshots_api_v_4', 'RemoteProtectionGroupSnapshotsApi', '2.21'),
    'RemoteProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_protection_groups_api_v_1', 'RemoteProtectionGroupsApi', '2.21'),
    'RemoteVolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_volume_snapshots_api_v_4', 'RemoteVolumeSnapshotsApi', '2.21'),
    'SAML2SSOApi': __LazyApiLoader('pypureclient.flasharray.common.apis.saml2_sso_api_v_11', 'SAML2SSOApi', '2.21'),
    'SMISApi': __LazyApiLoader('pypureclient.flasharray.common.apis.smis_api_v_2', 'SMISApi', '2.21'),
    'SMTPApi': __LazyApiLoader('pypureclient.flasharray.common.apis.smtp_api_v_4', 'SMTPApi', '2.21'),
    'SNMPAgentsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.snmp_agents_api_v_4', 'SNMPAgentsApi', '2.21'),
    'SNMPManagersApi': __LazyApiLoader('pypureclient.flasharray.common.apis.snmp_managers_api_v_4', 'SNMPManagersApi', '2.21'),
    'SessionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.sessions_api_v_4', 'SessionsApi', '2.21'),
    'SoftwareApi': __LazyApiLoader('pypureclient.flasharray.common.apis.software_api_v_17', 'SoftwareApi', '2.21'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.subnets_api_v_2', 'SubnetsApi', '2.21'),
    'SupportApi': __LazyApiLoader('pypureclient.flasharray.common.apis.support_api_v_2', 'SupportApi', '2.21'),
    'SyslogApi': __LazyApiLoader('pypureclient.flasharray.common.apis.syslog_api_v_4', 'SyslogApi', '2.21'),
    'VirtualMachinesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.virtual_machines_api_v_14', 'VirtualMachinesApi', '2.21'),
    'VolumeGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.volume_groups_api_v_20', 'VolumeGroupsApi', '2.21'),
    'VolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.volume_snapshots_api_v_9', 'VolumeSnapshotsApi', '2.21'),
    'VolumesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.volumes_api_v_16', 'VolumesApi', '2.21'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
