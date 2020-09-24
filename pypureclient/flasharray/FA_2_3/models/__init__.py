# coding: utf-8

from __future__ import absolute_import


class ReferenceType(object):
    """Class just for type annotations.

    It's used for reference arg on api function. This allows user to pass collections of Model objects
    to the method without transforming them to ids or names.

    Should be Protocol type when the typing module will get support of it.
    """
    def __init__(self):
        self.id = ''
        self.name = ''


def quoteString(s):
    r"""Quote string according to
    https://wiki.purestorage.com/display/UXReviewers/Filtering

    >>> quote("a")
    "'a'"
    >>> quote("a\\b")
    "'a\\\\b'"
    >>> quote("a\\b")
    "'a\\\\b'"
    >>> quote("a'b")
    "'a\\'b'"
    >>> quote(None)
    None
    """
    if s is None:
        return None
    quoted = str(s).replace("\\", "\\\\").replace("'", "\\'")
    return "'{}'".format(quoted)


def quoteStrings(s):
    if s is None:
        return None
    return [quoteString(x) for x in s]


# import models into model package
from .active_directory import ActiveDirectory
from .active_directory_get_response import ActiveDirectoryGetResponse
from .active_directory_post import ActiveDirectoryPost
from .active_directory_response import ActiveDirectoryResponse
from .admin import Admin
from .admin_api_token import AdminApiToken
from .admin_api_token_get_response import AdminApiTokenGetResponse
from .admin_api_token_response import AdminApiTokenResponse
from .admin_cache import AdminCache
from .admin_cache_get_response import AdminCacheGetResponse
from .admin_cache_response import AdminCacheResponse
from .admin_get_response import AdminGetResponse
from .admin_patch import AdminPatch
from .admin_post import AdminPost
from .admin_response import AdminResponse
from .admin_role import AdminRole
from .admin_settings import AdminSettings
from .admin_settings_response import AdminSettingsResponse
from .aggregate_replication_performance import AggregateReplicationPerformance
from .alert import Alert
from .alert_event import AlertEvent
from .alert_event_get_response import AlertEventGetResponse
from .alert_event_response import AlertEventResponse
from .alert_get_response import AlertGetResponse
from .alert_response import AlertResponse
from .api_client import ApiClient
from .api_client_get_response import ApiClientGetResponse
from .api_client_patch import ApiClientPatch
from .api_client_post import ApiClientPost
from .api_client_response import ApiClientResponse
from .api_token import ApiToken
from .api_version_response import ApiVersionResponse
from .app import App
from .app_get_response import AppGetResponse
from .app_node import AppNode
from .app_node_get_response import AppNodeGetResponse
from .app_node_response import AppNodeResponse
from .app_response import AppResponse
from .array import Array
from .array_get_response import ArrayGetResponse
from .array_performance import ArrayPerformance
from .array_performance_get_response import ArrayPerformanceGetResponse
from .array_response import ArrayResponse
from .array_space import ArraySpace
from .array_space_get_response import ArraySpaceGetResponse
from .arrays import Arrays
from .audit import Audit
from .audit_get_response import AuditGetResponse
from .audit_response import AuditResponse
from .built_in import BuiltIn
from .built_in_relationship import BuiltInRelationship
from .built_in_resource_no_id import BuiltInResourceNoId
from .chap import Chap
from .connection import Connection
from .connection_get_response import ConnectionGetResponse
from .connection_post import ConnectionPost
from .connection_response import ConnectionResponse
from .controller import Controller
from .controller_get_response import ControllerGetResponse
from .controllers import Controllers
from .destroyed_patch_post import DestroyedPatchPost
from .directory import Directory
from .directory_export import DirectoryExport
from .directory_export_get_response import DirectoryExportGetResponse
from .directory_export_post import DirectoryExportPost
from .directory_export_response import DirectoryExportResponse
from .directory_get_response import DirectoryGetResponse
from .directory_patch import DirectoryPatch
from .directory_performance import DirectoryPerformance
from .directory_performance_get_response import DirectoryPerformanceGetResponse
from .directory_policy_export_post import DirectoryPolicyExportPost
from .directory_policy_post import DirectoryPolicyPost
from .directory_post import DirectoryPost
from .directory_response import DirectoryResponse
from .directory_service import DirectoryService
from .directory_service_get_response import DirectoryServiceGetResponse
from .directory_service_management import DirectoryServiceManagement
from .directory_service_response import DirectoryServiceResponse
from .directory_service_role import DirectoryServiceRole
from .directory_service_role_get_response import DirectoryServiceRoleGetResponse
from .directory_service_role_response import DirectoryServiceRoleResponse
from .directory_snapshot import DirectorySnapshot
from .directory_snapshot_get_response import DirectorySnapshotGetResponse
from .directory_snapshot_patch import DirectorySnapshotPatch
from .directory_snapshot_post import DirectorySnapshotPost
from .directory_snapshot_response import DirectorySnapshotResponse
from .directory_space import DirectorySpace
from .directorypolicyexportpost_policies import DirectorypolicyexportpostPolicies
from .directorypolicypost_policies import DirectorypolicypostPolicies
from .dns import Dns
from .dns_get_response import DnsGetResponse
from .dns_patch import DnsPatch
from .dns_response import DnsResponse
from .eula import Eula
from .eula_get_response import EulaGetResponse
from .eula_response import EulaResponse
from .eula_signature import EulaSignature
from .file_system import FileSystem
from .file_system_get_response import FileSystemGetResponse
from .file_system_patch import FileSystemPatch
from .file_system_response import FileSystemResponse
from .fixed_name_resource_no_id import FixedNameResourceNoId
from .fixed_reference import FixedReference
from .fixed_reference_no_id import FixedReferenceNoId
from .fixed_reference_with_type import FixedReferenceWithType
from .hardware import Hardware
from .hardware_get_response import HardwareGetResponse
from .hardware_patch import HardwarePatch
from .hardware_response import HardwareResponse
from .host import Host
from .host_get_response import HostGetResponse
from .host_group import HostGroup
from .host_group_get_response import HostGroupGetResponse
from .host_group_patch import HostGroupPatch
from .host_group_performance import HostGroupPerformance
from .host_group_performance_by_array import HostGroupPerformanceByArray
from .host_group_response import HostGroupResponse
from .host_group_space import HostGroupSpace
from .host_patch import HostPatch
from .host_performance import HostPerformance
from .host_performance_by_array import HostPerformanceByArray
from .host_port_connectivity import HostPortConnectivity
from .host_post import HostPost
from .host_response import HostResponse
from .host_space import HostSpace
from .inline_response400 import InlineResponse400
from .inline_response401 import InlineResponse401
from .kmip import Kmip
from .kmip_get_response import KmipGetResponse
from .kmip_patch import KmipPatch
from .kmip_post import KmipPost
from .kmip_response import KmipResponse
from .kmip_test_result import KmipTestResult
from .kmip_test_result_get_response import KmipTestResultGetResponse
from .maintenance_window import MaintenanceWindow
from .maintenance_window_post import MaintenanceWindowPost
from .maintenance_windows_get_response import MaintenanceWindowsGetResponse
from .maintenance_windows_response import MaintenanceWindowsResponse
from .member import Member
from .member_get_response import MemberGetResponse
from .member_no_id_all import MemberNoIdAll
from .member_no_id_all_get_response import MemberNoIdAllGetResponse
from .member_no_id_all_response import MemberNoIdAllResponse
from .member_no_id_group import MemberNoIdGroup
from .member_response import MemberResponse
from .new_name import NewName
from .oauth_token_response import OauthTokenResponse
from .offload import Offload
from .offload_azure import OffloadAzure
from .offload_get_response import OffloadGetResponse
from .offload_google_cloud import OffloadGoogleCloud
from .offload_nfs import OffloadNfs
from .offload_post import OffloadPost
from .offload_response import OffloadResponse
from .offload_s3 import OffloadS3
from .override_check import OverrideCheck
from .page_info import PageInfo
from .performance import Performance
from .pod import Pod
from .pod_array_status import PodArrayStatus
from .pod_get_response import PodGetResponse
from .pod_patch import PodPatch
from .pod_performance import PodPerformance
from .pod_performance_by_array import PodPerformanceByArray
from .pod_performance_replication import PodPerformanceReplication
from .pod_performance_replication_by_array import PodPerformanceReplicationByArray
from .pod_performance_replication_by_array_get_response import PodPerformanceReplicationByArrayGetResponse
from .pod_performance_replication_by_array_response import PodPerformanceReplicationByArrayResponse
from .pod_performance_replication_get_response import PodPerformanceReplicationGetResponse
from .pod_performance_replication_response import PodPerformanceReplicationResponse
from .pod_post import PodPost
from .pod_replica_link import PodReplicaLink
from .pod_replica_link_get_response import PodReplicaLinkGetResponse
from .pod_replica_link_lag import PodReplicaLinkLag
from .pod_replica_link_lag_get_response import PodReplicaLinkLagGetResponse
from .pod_replica_link_lag_response import PodReplicaLinkLagResponse
from .pod_replica_link_patch import PodReplicaLinkPatch
from .pod_replica_link_performance import PodReplicaLinkPerformance
from .pod_replica_link_performance_replication import PodReplicaLinkPerformanceReplication
from .pod_replica_link_performance_replication_get_response import PodReplicaLinkPerformanceReplicationGetResponse
from .pod_replica_link_performance_replication_response import PodReplicaLinkPerformanceReplicationResponse
from .pod_replica_link_response import PodReplicaLinkResponse
from .pod_response import PodResponse
from .pod_space import PodSpace
from .policy import Policy
from .policy_get_response import PolicyGetResponse
from .policy_member import PolicyMember
from .policy_member_export import PolicyMemberExport
from .policy_member_export_get_response import PolicyMemberExportGetResponse
from .policy_member_export_post import PolicyMemberExportPost
from .policy_member_export_response import PolicyMemberExportResponse
from .policy_member_get_response import PolicyMemberGetResponse
from .policy_member_post import PolicyMemberPost
from .policy_member_response import PolicyMemberResponse
from .policy_patch import PolicyPatch
from .policy_post import PolicyPost
from .policy_response import PolicyResponse
from .policy_rule_nfs_client import PolicyRuleNfsClient
from .policy_rule_nfs_client_get_response import PolicyRuleNfsClientGetResponse
from .policy_rule_nfs_client_post import PolicyRuleNfsClientPost
from .policy_rule_nfs_client_response import PolicyRuleNfsClientResponse
from .policy_rule_smb_client import PolicyRuleSmbClient
from .policy_rule_smb_client_get_response import PolicyRuleSmbClientGetResponse
from .policy_rule_smb_client_post import PolicyRuleSmbClientPost
from .policy_rule_smb_client_response import PolicyRuleSmbClientResponse
from .policy_rule_snapshot import PolicyRuleSnapshot
from .policy_rule_snapshot_get_response import PolicyRuleSnapshotGetResponse
from .policy_rule_snapshot_post import PolicyRuleSnapshotPost
from .policy_rule_snapshot_response import PolicyRuleSnapshotResponse
from .policymemberexportpost_members import PolicymemberexportpostMembers
from .policymemberpost_members import PolicymemberpostMembers
from .policyrulenfsclientpost_rules import PolicyrulenfsclientpostRules
from .policyrulesmbclientpost_rules import PolicyrulesmbclientpostRules
from .policyrulesnapshotpost_rules import PolicyrulesnapshotpostRules
from .port import Port
from .port_common import PortCommon
from .port_get_response import PortGetResponse
from .port_initiator import PortInitiator
from .port_initiators_get_response import PortInitiatorsGetResponse
from .protection_group import ProtectionGroup
from .protection_group_get_response import ProtectionGroupGetResponse
from .protection_group_performance import ProtectionGroupPerformance
from .protection_group_performance_array import ProtectionGroupPerformanceArray
from .protection_group_performance_array_response import ProtectionGroupPerformanceArrayResponse
from .protection_group_performance_by_array import ProtectionGroupPerformanceByArray
from .protection_group_performance_response import ProtectionGroupPerformanceResponse
from .protection_group_response import ProtectionGroupResponse
from .protection_group_snapshot import ProtectionGroupSnapshot
from .protection_group_snapshot_get_response import ProtectionGroupSnapshotGetResponse
from .protection_group_snapshot_patch import ProtectionGroupSnapshotPatch
from .protection_group_snapshot_post import ProtectionGroupSnapshotPost
from .protection_group_snapshot_response import ProtectionGroupSnapshotResponse
from .protection_group_snapshot_transfer import ProtectionGroupSnapshotTransfer
from .protection_group_snapshot_transfer_get_response import ProtectionGroupSnapshotTransferGetResponse
from .protection_group_snapshot_transfer_response import ProtectionGroupSnapshotTransferResponse
from .protection_group_space import ProtectionGroupSpace
from .protection_group_target import ProtectionGroupTarget
from .protection_group_target_get_response import ProtectionGroupTargetGetResponse
from .protection_group_target_response import ProtectionGroupTargetResponse
from .qos import Qos
from .reference import Reference
from .reference_no_id import ReferenceNoId
from .reference_with_type import ReferenceWithType
from .remote_pod import RemotePod
from .remote_pods_response import RemotePodsResponse
from .remote_protection_group import RemoteProtectionGroup
from .remote_protection_group_get_response import RemoteProtectionGroupGetResponse
from .remote_protection_group_response import RemoteProtectionGroupResponse
from .remote_protection_group_snapshot import RemoteProtectionGroupSnapshot
from .remote_protection_group_snapshot_get_response import RemoteProtectionGroupSnapshotGetResponse
from .remote_protection_group_snapshot_response import RemoteProtectionGroupSnapshotResponse
from .remote_protection_group_snapshot_transfer import RemoteProtectionGroupSnapshotTransfer
from .remote_protection_group_snapshot_transfer_get_response import RemoteProtectionGroupSnapshotTransferGetResponse
from .remote_protection_group_snapshot_transfer_response import RemoteProtectionGroupSnapshotTransferResponse
from .remote_volume_snapshot import RemoteVolumeSnapshot
from .remote_volume_snapshot_get_response import RemoteVolumeSnapshotGetResponse
from .remote_volume_snapshot_response import RemoteVolumeSnapshotResponse
from .remote_volume_snapshot_transfer import RemoteVolumeSnapshotTransfer
from .remote_volume_snapshot_transfer_get_response import RemoteVolumeSnapshotTransferGetResponse
from .remote_volume_snapshot_transfer_response import RemoteVolumeSnapshotTransferResponse
from .replica_link_lag import ReplicaLinkLag
from .replica_link_performance_replication import ReplicaLinkPerformanceReplication
from .replication_performance_with_total import ReplicationPerformanceWithTotal
from .replication_schedule import ReplicationSchedule
from .resource import Resource
from .resource_fixed_non_unique_name import ResourceFixedNonUniqueName
from .resource_no_id import ResourceNoId
from .resource_performance import ResourcePerformance
from .resource_performance_by_array import ResourcePerformanceByArray
from .resource_performance_by_array_get_response import ResourcePerformanceByArrayGetResponse
from .resource_performance_get_response import ResourcePerformanceGetResponse
from .resource_performance_no_id import ResourcePerformanceNoId
from .resource_performance_no_id_by_array import ResourcePerformanceNoIdByArray
from .resource_performance_no_id_by_array_get_response import ResourcePerformanceNoIdByArrayGetResponse
from .resource_performance_no_id_get_response import ResourcePerformanceNoIdGetResponse
from .resource_pod_space import ResourcePodSpace
from .resource_pod_space_get_response import ResourcePodSpaceGetResponse
from .resource_space import ResourceSpace
from .resource_space_get_response import ResourceSpaceGetResponse
from .resource_space_no_id import ResourceSpaceNoId
from .resource_space_no_id_get_response import ResourceSpaceNoIdGetResponse
from .retention_policy import RetentionPolicy
from .smis import Smis
from .smis_get_response import SmisGetResponse
from .smis_response import SmisResponse
from .snapshot import Snapshot
from .snapshot_schedule import SnapshotSchedule
from .software import Software
from .software_get_response import SoftwareGetResponse
from .software_installation import SoftwareInstallation
from .software_installation_patch import SoftwareInstallationPatch
from .software_installation_post import SoftwareInstallationPost
from .software_installation_step import SoftwareInstallationStep
from .software_installation_steps import SoftwareInstallationSteps
from .software_installation_steps_checks import SoftwareInstallationStepsChecks
from .software_installation_steps_get_response import SoftwareInstallationStepsGetResponse
from .software_installation_steps_response import SoftwareInstallationStepsResponse
from .software_installations import SoftwareInstallations
from .software_installations_get_response import SoftwareInstallationsGetResponse
from .software_installations_response import SoftwareInstallationsResponse
from .software_response import SoftwareResponse
from .space import Space
from .start_end_time import StartEndTime
from .subnet import Subnet
from .subnet_get_response import SubnetGetResponse
from .subnet_patch import SubnetPatch
from .subnet_post import SubnetPost
from .subnet_response import SubnetResponse
from .support import Support
from .support_get_response import SupportGetResponse
from .support_patch import SupportPatch
from .support_remote_assist_paths import SupportRemoteAssistPaths
from .support_response import SupportResponse
from .tag import Tag
from .tag_get_response import TagGetResponse
from .tag_response import TagResponse
from .target_protection_group import TargetProtectionGroup
from .target_protection_group_post_patch import TargetProtectionGroupPostPatch
from .test_result import TestResult
from .test_result_get_response import TestResultGetResponse
from .test_result_response import TestResultResponse
from .test_result_with_resource import TestResultWithResource
from .test_result_with_resource_response import TestResultWithResourceResponse
from .time_window import TimeWindow
from .transfer import Transfer
from .username import Username
from .username_response import UsernameResponse
from .volume import Volume
from .volume_common import VolumeCommon
from .volume_get_response import VolumeGetResponse
from .volume_group import VolumeGroup
from .volume_group_get_response import VolumeGroupGetResponse
from .volume_group_performance import VolumeGroupPerformance
from .volume_group_post import VolumeGroupPost
from .volume_group_response import VolumeGroupResponse
from .volume_group_space import VolumeGroupSpace
from .volume_patch import VolumePatch
from .volume_performance import VolumePerformance
from .volume_performance_by_array import VolumePerformanceByArray
from .volume_post import VolumePost
from .volume_response import VolumeResponse
from .volume_snapshot import VolumeSnapshot
from .volume_snapshot_get_response import VolumeSnapshotGetResponse
from .volume_snapshot_patch import VolumeSnapshotPatch
from .volume_snapshot_post import VolumeSnapshotPost
from .volume_snapshot_response import VolumeSnapshotResponse
from .volume_snapshot_transfer import VolumeSnapshotTransfer
from .volume_snapshot_transfer_get_response import VolumeSnapshotTransferGetResponse
from .volume_snapshot_transfer_response import VolumeSnapshotTransferResponse
from .volume_space import VolumeSpace
