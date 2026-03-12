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
    'APIClientsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.api_clients_api_v_2_1', 'APIClientsApi', '2.41'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flasharray._common.apis.active_directory_api_v_2_15', 'ActiveDirectoryApi', '2.41'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.administrators_api_v_2_38', 'AdministratorsApi', '2.41'),
    'AlertWatchersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.alert_watchers_api_v_2_38', 'AlertWatchersApi', '2.41'),
    'AlertsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.alerts_api_v_2_38', 'AlertsApi', '2.41'),
    'AppsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.apps_api_v_2_2', 'AppsApi', '2.41'),
    'ArrayConnectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.array_connections_api_v_2_40', 'ArrayConnectionsApi', '2.41'),
    'ArraysApi': __LazyApiLoader('pypureclient.flasharray._common.apis.arrays_api_v_2_40', 'ArraysApi', '2.41'),
    'AuditsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.audits_api_v_2_38', 'AuditsApi', '2.41'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flasharray._common.apis.authorization_api_v_2_0', 'AuthorizationApi', '2.41'),
    'CertificateGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.certificate_groups_api_v_2_41', 'CertificateGroupsApi', '2.41'),
    'CertificatesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.certificates_api_v_2_41', 'CertificatesApi', '2.41'),
    'ConnectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.connections_api_v_2_38', 'ConnectionsApi', '2.41'),
    'ContainerDefaultProtectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.container_default_protections_api_v_2_38', 'ContainerDefaultProtectionsApi', '2.41'),
    'ControllersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.controllers_api_v_2_2', 'ControllersApi', '2.41'),
    'DNSApi': __LazyApiLoader('pypureclient.flasharray._common.apis.dns_api_v_2_15', 'DNSApi', '2.41'),
    'DirectoriesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directories_api_v_2_38', 'DirectoriesApi', '2.41'),
    'DirectoryExportsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_exports_api_v_2_32', 'DirectoryExportsApi', '2.41'),
    'DirectoryQuotasApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_quotas_api_v_2_7', 'DirectoryQuotasApi', '2.41'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_services_api_v_2_38', 'DirectoryServicesApi', '2.41'),
    'DirectorySnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.directory_snapshots_api_v_2_3', 'DirectorySnapshotsApi', '2.41'),
    'DrivesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.drives_api_v_2_4', 'DrivesApi', '2.41'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.file_systems_api_v_2_38', 'FileSystemsApi', '2.41'),
    'FilesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.files_api_v_2_26', 'FilesApi', '2.41'),
    'FleetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.fleets_api_v_2_39', 'FleetsApi', '2.41'),
    'HardwareApi': __LazyApiLoader('pypureclient.flasharray._common.apis.hardware_api_v_2_2', 'HardwareApi', '2.41'),
    'HostGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.host_groups_api_v_2_40', 'HostGroupsApi', '2.41'),
    'HostsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.hosts_api_v_2_40', 'HostsApi', '2.41'),
    'KMIPApi': __LazyApiLoader('pypureclient.flasharray._common.apis.kmip_api_v_2_2', 'KMIPApi', '2.41'),
    'LogTargetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.log_targets_api_v_2_38', 'LogTargetsApi', '2.41'),
    'MaintenanceWindowsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.maintenance_windows_api_v_2_2', 'MaintenanceWindowsApi', '2.41'),
    'NetworkInterfacesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.network_interfaces_api_v_2_22', 'NetworkInterfacesApi', '2.41'),
    'OffloadsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.offloads_api_v_2_38', 'OffloadsApi', '2.41'),
    'PodReplicaLinksApi': __LazyApiLoader('pypureclient.flasharray._common.apis.pod_replica_links_api_v_2_38', 'PodReplicaLinksApi', '2.41'),
    'PodsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.pods_api_v_2_39', 'PodsApi', '2.41'),
    'PoliciesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.policies_api_v_2_38', 'PoliciesApi', '2.41'),
    'PortsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.ports_api_v_2_38', 'PortsApi', '2.41'),
    'PresetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.presets_api_v_2_40', 'PresetsApi', '2.41'),
    'ProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.protection_group_snapshots_api_v_2_38', 'ProtectionGroupSnapshotsApi', '2.41'),
    'ProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.protection_groups_api_v_2_41', 'ProtectionGroupsApi', '2.41'),
    'RealmsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.realms_api_v_2_41', 'RealmsApi', '2.41'),
    'RemoteArraysApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_arrays_api_v_2_36', 'RemoteArraysApi', '2.41'),
    'RemotePodsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_pods_api_v_2_38', 'RemotePodsApi', '2.41'),
    'RemoteProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_protection_group_snapshots_api_v_2_38', 'RemoteProtectionGroupSnapshotsApi', '2.41'),
    'RemoteProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_protection_groups_api_v_2_38', 'RemoteProtectionGroupsApi', '2.41'),
    'RemoteVolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.remote_volume_snapshots_api_v_2_38', 'RemoteVolumeSnapshotsApi', '2.41'),
    'ResourceAccessesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.resource_accesses_api_v_2_40', 'ResourceAccessesApi', '2.41'),
    'SAML2SSOApi': __LazyApiLoader('pypureclient.flasharray._common.apis.saml2_sso_api_v_2_38', 'SAML2SSOApi', '2.41'),
    'SMISApi': __LazyApiLoader('pypureclient.flasharray._common.apis.smis_api_v_2_2', 'SMISApi', '2.41'),
    'SMTPApi': __LazyApiLoader('pypureclient.flasharray._common.apis.smtp_api_v_2_4', 'SMTPApi', '2.41'),
    'SNMPAgentsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.snmp_agents_api_v_2_4', 'SNMPAgentsApi', '2.41'),
    'SNMPManagersApi': __LazyApiLoader('pypureclient.flasharray._common.apis.snmp_managers_api_v_2_38', 'SNMPManagersApi', '2.41'),
    'SessionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.sessions_api_v_2_4', 'SessionsApi', '2.41'),
    'SoftwareApi': __LazyApiLoader('pypureclient.flasharray._common.apis.software_api_v_2_29', 'SoftwareApi', '2.41'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.subnets_api_v_2_2', 'SubnetsApi', '2.41'),
    'SubscriptionAssetsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.subscription_assets_api_v_2_26', 'SubscriptionAssetsApi', '2.41'),
    'SubscriptionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.subscriptions_api_v_2_26', 'SubscriptionsApi', '2.41'),
    'SupportApi': __LazyApiLoader('pypureclient.flasharray._common.apis.support_api_v_2_41', 'SupportApi', '2.41'),
    'SyslogApi': __LazyApiLoader('pypureclient.flasharray._common.apis.syslog_api_v_2_38', 'SyslogApi', '2.41'),
    'VchostConnectionsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.vchost_connections_api_v_2_33', 'VchostConnectionsApi', '2.41'),
    'VchostsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.vchosts_api_v_2_26', 'VchostsApi', '2.41'),
    'VirtualMachinesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.virtual_machines_api_v_2_36', 'VirtualMachinesApi', '2.41'),
    'VolumeGroupsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.volume_groups_api_v_2_39', 'VolumeGroupsApi', '2.41'),
    'VolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.volume_snapshots_api_v_2_38', 'VolumeSnapshotsApi', '2.41'),
    'VolumesApi': __LazyApiLoader('pypureclient.flasharray._common.apis.volumes_api_v_2_38', 'VolumesApi', '2.41'),
    'WorkloadsApi': __LazyApiLoader('pypureclient.flasharray._common.apis.workloads_api_v_2_40', 'WorkloadsApi', '2.41'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
