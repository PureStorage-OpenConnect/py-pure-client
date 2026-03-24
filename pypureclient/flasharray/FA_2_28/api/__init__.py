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
    'APIClientsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.api_clients_api_v_2_1', 'APIClientsApi', '2.28'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flasharray._common.apis.active_directory_api_v_2_15', 'ActiveDirectoryApi', '2.28'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.administrators_api_v_2_2', 'AdministratorsApi', '2.28'),
    'AlertWatchersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.alert_watchers_api_v_2_4', 'AlertWatchersApi', '2.28'),
    'AlertsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.alerts_api_v_2_23', 'AlertsApi', '2.28'),
    'AppsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.apps_api_v_2_2', 'AppsApi', '2.28'),
    'ArrayConnectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.array_connections_api_v_2_4', 'ArrayConnectionsApi', '2.28'),
    'ArraysApi': __LazyApiLoader('pypureclient.flasharray._common.apis.arrays_api_v_2_19', 'ArraysApi', '2.28'),
    'AuditsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.audits_api_v_2_2', 'AuditsApi', '2.28'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flasharray._common.apis.authorization_api_v_2_0', 'AuthorizationApi', '2.28'),
    'CertificatesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.certificates_api_v_2_4', 'CertificatesApi', '2.28'),
    'ConnectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.connections_api_v_2_9', 'ConnectionsApi', '2.28'),
    'ContainerDefaultProtectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.container_default_protections_api_v_2_16', 'ContainerDefaultProtectionsApi', '2.28'),
    'ControllersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.controllers_api_v_2_2', 'ControllersApi', '2.28'),
    'DNSApi': __LazyApiLoader('pypureclient.flasharray._common.apis.dns_api_v_2_15', 'DNSApi', '2.28'),
    'DirectoriesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directories_api_v_2_24', 'DirectoriesApi', '2.28'),
    'DirectoryExportsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_exports_api_v_2_3', 'DirectoryExportsApi', '2.28'),
    'DirectoryQuotasApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_quotas_api_v_2_7', 'DirectoryQuotasApi', '2.28'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_services_api_v_2_21', 'DirectoryServicesApi', '2.28'),
    'DirectorySnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_snapshots_api_v_2_3', 'DirectorySnapshotsApi', '2.28'),
    'DrivesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.drives_api_v_2_4', 'DrivesApi', '2.28'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.file_systems_api_v_2_3', 'FileSystemsApi', '2.28'),
    'FilesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.files_api_v_2_26', 'FilesApi', '2.28'),
    'HardwareApi': __LazyApiLoader('pypureclient.flasharray._common.apis.hardware_api_v_2_2', 'HardwareApi', '2.28'),
    'HostGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.host_groups_api_v_2_26', 'HostGroupsApi', '2.28'),
    'HostsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.hosts_api_v_2_26', 'HostsApi', '2.28'),
    'KMIPApi': __LazyApiLoader('pypureclient.flasharray._common.apis.kmip_api_v_2_2', 'KMIPApi', '2.28'),
    'MaintenanceWindowsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.maintenance_windows_api_v_2_2', 'MaintenanceWindowsApi', '2.28'),
    'NetworkInterfacesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.network_interfaces_api_v_2_22', 'NetworkInterfacesApi', '2.28'),
    'OffloadsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.offloads_api_v_2_1', 'OffloadsApi', '2.28'),
    'PodReplicaLinksApi': __LazyApiLoader('pypureclient.flasharray._common.apis.pod_replica_links_api_v_2_4', 'PodReplicaLinksApi', '2.28'),
    'PodsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.pods_api_v_2_13', 'PodsApi', '2.28'),
    'PoliciesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.policies_api_v_2_24', 'PoliciesApi', '2.28'),
    'PortsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.ports_api_v_2_2', 'PortsApi', '2.28'),
    'ProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.protection_group_snapshots_api_v_2_26', 'ProtectionGroupSnapshotsApi', '2.28'),
    'ProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.protection_groups_api_v_2_26', 'ProtectionGroupsApi', '2.28'),
    'RemotePodsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_pods_api_v_2_1', 'RemotePodsApi', '2.28'),
    'RemoteProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_protection_group_snapshots_api_v_2_26', 'RemoteProtectionGroupSnapshotsApi', '2.28'),
    'RemoteProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_protection_groups_api_v_2_1', 'RemoteProtectionGroupsApi', '2.28'),
    'RemoteVolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_volume_snapshots_api_v_2_28', 'RemoteVolumeSnapshotsApi', '2.28'),
    'SAML2SSOApi': __LazyApiLoader('pypureclient.flasharray._common.apis.saml2_sso_api_v_2_11', 'SAML2SSOApi', '2.28'),
    'SMISApi': __LazyApiLoader('pypureclient.flasharray._common.apis.smis_api_v_2_2', 'SMISApi', '2.28'),
    'SMTPApi': __LazyApiLoader('pypureclient.flasharray._common.apis.smtp_api_v_2_4', 'SMTPApi', '2.28'),
    'SNMPAgentsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.snmp_agents_api_v_2_4', 'SNMPAgentsApi', '2.28'),
    'SNMPManagersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.snmp_managers_api_v_2_4', 'SNMPManagersApi', '2.28'),
    'SessionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.sessions_api_v_2_4', 'SessionsApi', '2.28'),
    'SoftwareApi': __LazyApiLoader('pypureclient.flasharray._common.apis.software_api_v_2_17', 'SoftwareApi', '2.28'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.subnets_api_v_2_2', 'SubnetsApi', '2.28'),
    'SubscriptionAssetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.subscription_assets_api_v_2_26', 'SubscriptionAssetsApi', '2.28'),
    'SubscriptionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.subscriptions_api_v_2_26', 'SubscriptionsApi', '2.28'),
    'SupportApi': __LazyApiLoader('pypureclient.flasharray._common.apis.support_api_v_2_2', 'SupportApi', '2.28'),
    'SyslogApi': __LazyApiLoader('pypureclient.flasharray._common.apis.syslog_api_v_2_4', 'SyslogApi', '2.28'),
    'VchostsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.vchosts_api_v_2_26', 'VchostsApi', '2.28'),
    'VirtualMachinesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.virtual_machines_api_v_2_14', 'VirtualMachinesApi', '2.28'),
    'VolumeGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.volume_groups_api_v_2_20', 'VolumeGroupsApi', '2.28'),
    'VolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.volume_snapshots_api_v_2_25', 'VolumeSnapshotsApi', '2.28'),
    'VolumesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.volumes_api_v_2_26', 'VolumesApi', '2.28'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
