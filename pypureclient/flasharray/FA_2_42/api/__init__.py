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
    'APIClientsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.api_clients_api_v_1', 'APIClientsApi', '2.42'),
    'ActiveDirectoryApi': __LazyApiLoader('pypureclient.flasharray.common.apis.active_directory_api_v_15', 'ActiveDirectoryApi', '2.42'),
    'AdministratorsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.administrators_api_v_38', 'AdministratorsApi', '2.42'),
    'AlertWatchersApi': __LazyApiLoader('pypureclient.flasharray.common.apis.alert_watchers_api_v_38', 'AlertWatchersApi', '2.42'),
    'AlertsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.alerts_api_v_38', 'AlertsApi', '2.42'),
    'AppsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.apps_api_v_2', 'AppsApi', '2.42'),
    'ArrayConnectionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.array_connections_api_v_40', 'ArrayConnectionsApi', '2.42'),
    'ArraysApi': __LazyApiLoader('pypureclient.flasharray.common.apis.arrays_api_v_40', 'ArraysApi', '2.42'),
    'AuditsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.audits_api_v_38', 'AuditsApi', '2.42'),
    'AuthorizationApi': __LazyApiLoader('pypureclient.flasharray.common.apis.authorization_api_v_0', 'AuthorizationApi', '2.42'),
    'CertificateGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.certificate_groups_api_v_41', 'CertificateGroupsApi', '2.42'),
    'CertificatesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.certificates_api_v_41', 'CertificatesApi', '2.42'),
    'ConnectionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.connections_api_v_38', 'ConnectionsApi', '2.42'),
    'ContainerDefaultProtectionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.container_default_protections_api_v_38', 'ContainerDefaultProtectionsApi', '2.42'),
    'ControllersApi': __LazyApiLoader('pypureclient.flasharray.common.apis.controllers_api_v_2', 'ControllersApi', '2.42'),
    'DNSApi': __LazyApiLoader('pypureclient.flasharray.common.apis.dns_api_v_15', 'DNSApi', '2.42'),
    'DirectoriesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directories_api_v_42', 'DirectoriesApi', '2.42'),
    'DirectoryExportsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_exports_api_v_42', 'DirectoryExportsApi', '2.42'),
    'DirectoryQuotasApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_quotas_api_v_42', 'DirectoryQuotasApi', '2.42'),
    'DirectoryServicesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_services_api_v_42', 'DirectoryServicesApi', '2.42'),
    'DirectorySnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.directory_snapshots_api_v_42', 'DirectorySnapshotsApi', '2.42'),
    'DrivesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.drives_api_v_4', 'DrivesApi', '2.42'),
    'FileSystemsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.file_systems_api_v_38', 'FileSystemsApi', '2.42'),
    'FilesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.files_api_v_26', 'FilesApi', '2.42'),
    'FleetsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.fleets_api_v_39', 'FleetsApi', '2.42'),
    'HardwareApi': __LazyApiLoader('pypureclient.flasharray.common.apis.hardware_api_v_2', 'HardwareApi', '2.42'),
    'HostGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.host_groups_api_v_40', 'HostGroupsApi', '2.42'),
    'HostsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.hosts_api_v_40', 'HostsApi', '2.42'),
    'KMIPApi': __LazyApiLoader('pypureclient.flasharray.common.apis.kmip_api_v_2', 'KMIPApi', '2.42'),
    'LogTargetsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.log_targets_api_v_38', 'LogTargetsApi', '2.42'),
    'MaintenanceWindowsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.maintenance_windows_api_v_2', 'MaintenanceWindowsApi', '2.42'),
    'NetworkInterfacesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.network_interfaces_api_v_22', 'NetworkInterfacesApi', '2.42'),
    'OffloadsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.offloads_api_v_38', 'OffloadsApi', '2.42'),
    'PodReplicaLinksApi': __LazyApiLoader('pypureclient.flasharray.common.apis.pod_replica_links_api_v_38', 'PodReplicaLinksApi', '2.42'),
    'PodsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.pods_api_v_39', 'PodsApi', '2.42'),
    'PoliciesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.policies_api_v_38', 'PoliciesApi', '2.42'),
    'PortsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.ports_api_v_38', 'PortsApi', '2.42'),
    'PresetsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.presets_api_v_40', 'PresetsApi', '2.42'),
    'ProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.protection_group_snapshots_api_v_38', 'ProtectionGroupSnapshotsApi', '2.42'),
    'ProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.protection_groups_api_v_41', 'ProtectionGroupsApi', '2.42'),
    'RealmsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.realms_api_v_41', 'RealmsApi', '2.42'),
    'RemoteArraysApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_arrays_api_v_36', 'RemoteArraysApi', '2.42'),
    'RemotePodsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_pods_api_v_38', 'RemotePodsApi', '2.42'),
    'RemoteProtectionGroupSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_protection_group_snapshots_api_v_38', 'RemoteProtectionGroupSnapshotsApi', '2.42'),
    'RemoteProtectionGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_protection_groups_api_v_38', 'RemoteProtectionGroupsApi', '2.42'),
    'RemoteVolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.remote_volume_snapshots_api_v_38', 'RemoteVolumeSnapshotsApi', '2.42'),
    'ResourceAccessesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.resource_accesses_api_v_40', 'ResourceAccessesApi', '2.42'),
    'SAML2SSOApi': __LazyApiLoader('pypureclient.flasharray.common.apis.saml2_sso_api_v_38', 'SAML2SSOApi', '2.42'),
    'SMISApi': __LazyApiLoader('pypureclient.flasharray.common.apis.smis_api_v_2', 'SMISApi', '2.42'),
    'SMTPApi': __LazyApiLoader('pypureclient.flasharray.common.apis.smtp_api_v_4', 'SMTPApi', '2.42'),
    'SNMPAgentsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.snmp_agents_api_v_4', 'SNMPAgentsApi', '2.42'),
    'SNMPManagersApi': __LazyApiLoader('pypureclient.flasharray.common.apis.snmp_managers_api_v_38', 'SNMPManagersApi', '2.42'),
    'SessionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.sessions_api_v_4', 'SessionsApi', '2.42'),
    'SoftwareApi': __LazyApiLoader('pypureclient.flasharray.common.apis.software_api_v_29', 'SoftwareApi', '2.42'),
    'SubnetsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.subnets_api_v_2', 'SubnetsApi', '2.42'),
    'SubscriptionAssetsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.subscription_assets_api_v_26', 'SubscriptionAssetsApi', '2.42'),
    'SubscriptionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.subscriptions_api_v_26', 'SubscriptionsApi', '2.42'),
    'SupportApi': __LazyApiLoader('pypureclient.flasharray.common.apis.support_api_v_41', 'SupportApi', '2.42'),
    'SyslogApi': __LazyApiLoader('pypureclient.flasharray.common.apis.syslog_api_v_38', 'SyslogApi', '2.42'),
    'VchostConnectionsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.vchost_connections_api_v_33', 'VchostConnectionsApi', '2.42'),
    'VchostsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.vchosts_api_v_26', 'VchostsApi', '2.42'),
    'VirtualMachinesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.virtual_machines_api_v_36', 'VirtualMachinesApi', '2.42'),
    'VolumeGroupsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.volume_groups_api_v_39', 'VolumeGroupsApi', '2.42'),
    'VolumeSnapshotsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.volume_snapshots_api_v_38', 'VolumeSnapshotsApi', '2.42'),
    'VolumesApi': __LazyApiLoader('pypureclient.flasharray.common.apis.volumes_api_v_38', 'VolumesApi', '2.42'),
    'WorkloadsApi': __LazyApiLoader('pypureclient.flasharray.common.apis.workloads_api_v_40', 'WorkloadsApi', '2.42'),
}

__all__ = list(__class_apis_dict.keys())

def __getattr__(name, default=None):
    if '_apis_list' == name:
        return __class_apis_dict.keys()
    if name not in __class_apis_dict:
        raise AttributeError(f'module {__name__} has no attribute {name}')
    return __class_apis_dict[name].load()
