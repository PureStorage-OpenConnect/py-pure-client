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
    'APIClientsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.api_clients_api_v_1', 'APIClientsApi', '2.26'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flasharray.common.apis.active_directory_api_v_15', 'ActiveDirectoryApi', '2.26'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.administrators_api_v_2', 'AdministratorsApi', '2.26'),
    'AlertWatchersApi': __LazyApiLoader('pypureclient.flasharray.common.apis.alert_watchers_api_v_4', 'AlertWatchersApi', '2.26'),
    'AlertsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.alerts_api_v_23', 'AlertsApi', '2.26'),
    'AppsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.apps_api_v_2', 'AppsApi', '2.26'),
    'ArrayConnectionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.array_connections_api_v_4', 'ArrayConnectionsApi', '2.26'),
    'ArraysApi': __LazyApiLoader('pypureclient.flasharray.common.apis.arrays_api_v_19', 'ArraysApi', '2.26'),
    'AuditsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.audits_api_v_2', 'AuditsApi', '2.26'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flasharray.common.apis.authorization_api_v_0', 'AuthorizationApi', '2.26'),
    'CertificatesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.certificates_api_v_4', 'CertificatesApi', '2.26'),
    'ConnectionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.connections_api_v_9', 'ConnectionsApi', '2.26'),
    'ContainerDefaultProtectionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.container_default_protections_api_v_16', 'ContainerDefaultProtectionsApi', '2.26'),
    'ControllersApi': __LazyApiLoader('pypureclient.flasharray.common.apis.controllers_api_v_2', 'ControllersApi', '2.26'),
    'DNSApi': __LazyApiLoader('pypureclient.flasharray.common.apis.dns_api_v_15', 'DNSApi', '2.26'),
    'DirectoriesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directories_api_v_24', 'DirectoriesApi', '2.26'),
    'DirectoryExportsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_exports_api_v_3', 'DirectoryExportsApi', '2.26'),
    'DirectoryQuotasApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_quotas_api_v_7', 'DirectoryQuotasApi', '2.26'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_services_api_v_21', 'DirectoryServicesApi', '2.26'),
    'DirectorySnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_snapshots_api_v_3', 'DirectorySnapshotsApi', '2.26'),
    'DrivesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.drives_api_v_4', 'DrivesApi', '2.26'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.file_systems_api_v_3', 'FileSystemsApi', '2.26'),
    'FilesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.files_api_v_26', 'FilesApi', '2.26'),
    'HardwareApi': __LazyApiLoader('pypureclient.flasharray.common.apis.hardware_api_v_2', 'HardwareApi', '2.26'),
    'HostGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.host_groups_api_v_26', 'HostGroupsApi', '2.26'),
    'HostsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.hosts_api_v_26', 'HostsApi', '2.26'),
    'KMIPApi': __LazyApiLoader('pypureclient.flasharray.common.apis.kmip_api_v_2', 'KMIPApi', '2.26'),
    'MaintenanceWindowsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.maintenance_windows_api_v_2', 'MaintenanceWindowsApi', '2.26'),
    'NetworkInterfacesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.network_interfaces_api_v_22', 'NetworkInterfacesApi', '2.26'),
    'OffloadsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.offloads_api_v_1', 'OffloadsApi', '2.26'),
    'PodReplicaLinksApi': __LazyApiLoader('pypureclient.flasharray.common.apis.pod_replica_links_api_v_4', 'PodReplicaLinksApi', '2.26'),
    'PodsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.pods_api_v_13', 'PodsApi', '2.26'),
    'PoliciesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.policies_api_v_24', 'PoliciesApi', '2.26'),
    'PortsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.ports_api_v_2', 'PortsApi', '2.26'),
    'ProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.protection_group_snapshots_api_v_26', 'ProtectionGroupSnapshotsApi', '2.26'),
    'ProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.protection_groups_api_v_26', 'ProtectionGroupsApi', '2.26'),
    'RemotePodsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_pods_api_v_1', 'RemotePodsApi', '2.26'),
    'RemoteProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_protection_group_snapshots_api_v_26', 'RemoteProtectionGroupSnapshotsApi', '2.26'),
    'RemoteProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_protection_groups_api_v_1', 'RemoteProtectionGroupsApi', '2.26'),
    'RemoteVolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_volume_snapshots_api_v_4', 'RemoteVolumeSnapshotsApi', '2.26'),
    'SAML2SSOApi': __LazyApiLoader('pypureclient.flasharray.common.apis.saml2_sso_api_v_11', 'SAML2SSOApi', '2.26'),
    'SMISApi': __LazyApiLoader('pypureclient.flasharray.common.apis.smis_api_v_2', 'SMISApi', '2.26'),
    'SMTPApi': __LazyApiLoader('pypureclient.flasharray.common.apis.smtp_api_v_4', 'SMTPApi', '2.26'),
    'SNMPAgentsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.snmp_agents_api_v_4', 'SNMPAgentsApi', '2.26'),
    'SNMPManagersApi': __LazyApiLoader('pypureclient.flasharray.common.apis.snmp_managers_api_v_4', 'SNMPManagersApi', '2.26'),
    'SessionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.sessions_api_v_4', 'SessionsApi', '2.26'),
    'SoftwareApi': __LazyApiLoader('pypureclient.flasharray.common.apis.software_api_v_17', 'SoftwareApi', '2.26'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.subnets_api_v_2', 'SubnetsApi', '2.26'),
    'SubscriptionAssetsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.subscription_assets_api_v_26', 'SubscriptionAssetsApi', '2.26'),
    'SubscriptionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.subscriptions_api_v_26', 'SubscriptionsApi', '2.26'),
    'SupportApi': __LazyApiLoader('pypureclient.flasharray.common.apis.support_api_v_2', 'SupportApi', '2.26'),
    'SyslogApi': __LazyApiLoader('pypureclient.flasharray.common.apis.syslog_api_v_4', 'SyslogApi', '2.26'),
    'VchostsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.vchosts_api_v_26', 'VchostsApi', '2.26'),
    'VirtualMachinesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.virtual_machines_api_v_14', 'VirtualMachinesApi', '2.26'),
    'VolumeGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.volume_groups_api_v_20', 'VolumeGroupsApi', '2.26'),
    'VolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.volume_snapshots_api_v_25', 'VolumeSnapshotsApi', '2.26'),
    'VolumesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.volumes_api_v_26', 'VolumesApi', '2.26'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
