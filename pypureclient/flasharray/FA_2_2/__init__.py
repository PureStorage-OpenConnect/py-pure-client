from __future__ import absolute_import
import os

from .client import Client
from ...exceptions import PureError
from ...properties import Property, Filter
from ...responses import ValidResponse, ErrorResponse, ApiError, ResponseHeaders

from .models.admin_post import AdminPost
from .models.admin_settings import AdminSettings
from .models.aggregate_replication_performance import AggregateReplicationPerformance
from .models.api_client import ApiClient
from .models.api_client_patch import ApiClientPatch
from .models.api_client_post import ApiClientPost
from .models.api_token import ApiToken
from .models.app_node import AppNode
from .models.built_in import BuiltIn
from .models.built_in_relationship import BuiltInRelationship
from .models.built_in_resource_no_id import BuiltInResourceNoId
from .models.chap import Chap
from .models.connection import Connection
from .models.connection_post import ConnectionPost
from .models.destroyed_patch_post import DestroyedPatchPost
from .models.directory_service_management import DirectoryServiceManagement
from .models.directory_service_role import DirectoryServiceRole
from .models.dns import Dns
from .models.dns_patch import DnsPatch
from .models.eula import Eula
from .models.eula_signature import EulaSignature
from .models.fixed_name_resource_no_id import FixedNameResourceNoId
from .models.fixed_reference import FixedReference
from .models.fixed_reference_no_id import FixedReferenceNoId
from .models.host_port_connectivity import HostPortConnectivity
from .models.host_post import HostPost
from .models.kmip_patch import KmipPatch
from .models.kmip_post import KmipPost
from .models.kmip_test_result import KmipTestResult
from .models.maintenance_window_post import MaintenanceWindowPost
from .models.member import Member
from .models.member_no_id_all import MemberNoIdAll
from .models.member_no_id_group import MemberNoIdGroup
from .models.new_name import NewName
from .models.offload_azure import OffloadAzure
from .models.offload_google_cloud import OffloadGoogleCloud
from .models.offload_nfs import OffloadNfs
from .models.offload_post import OffloadPost
from .models.offload_s3 import OffloadS3
from .models.override_check import OverrideCheck
from .models.page_info import PageInfo
from .models.performance import Performance
from .models.pod_performance_replication import PodPerformanceReplication
from .models.pod_replica_link_patch import PodReplicaLinkPatch
from .models.port_common import PortCommon
from .models.port_initiator import PortInitiator
from .models.protection_group_target import ProtectionGroupTarget
from .models.qos import Qos
from .models.reference import Reference
from .models.reference_no_id import ReferenceNoId
from .models.replica_link_lag import ReplicaLinkLag
from .models.replica_link_performance_replication import ReplicaLinkPerformanceReplication
from .models.replication_performance_with_total import ReplicationPerformanceWithTotal
from .models.resource import Resource
from .models.resource_fixed_non_unique_name import ResourceFixedNonUniqueName
from .models.resource_no_id import ResourceNoId
from .models.retention_policy import RetentionPolicy
from .models.smis import Smis
from .models.snapshot import Snapshot
from .models.snapshot_schedule import SnapshotSchedule
from .models.software_installation_patch import SoftwareInstallationPatch
from .models.software_installation_post import SoftwareInstallationPost
from .models.software_installation_steps_checks import SoftwareInstallationStepsChecks
from .models.space import Space
from .models.start_end_time import StartEndTime
from .models.subnet_post import SubnetPost
from .models.support_patch import SupportPatch
from .models.support_remote_assist_paths import SupportRemoteAssistPaths
from .models.tag import Tag
from .models.target_protection_group import TargetProtectionGroup
from .models.target_protection_group_post_patch import TargetProtectionGroupPostPatch
from .models.test_result import TestResult
from .models.time_window import TimeWindow
from .models.transfer import Transfer
from .models.username import Username
from .models.admin import Admin
from .models.admin_api_token import AdminApiToken
from .models.admin_cache import AdminCache
from .models.admin_role import AdminRole
from .models.alert import Alert
from .models.alert_event import AlertEvent
from .models.app import App
from .models.array_performance import ArrayPerformance
from .models.array_space import ArraySpace
from .models.arrays import Arrays
from .models.audit import Audit
from .models.controller import Controller
from .models.directory_service import DirectoryService
from .models.hardware import Hardware
from .models.hardware_patch import HardwarePatch
from .models.host import Host
from .models.host_group import HostGroup
from .models.host_group_patch import HostGroupPatch
from .models.host_patch import HostPatch
from .models.kmip import Kmip
from .models.maintenance_window import MaintenanceWindow
from .models.offload import Offload
from .models.pod import Pod
from .models.pod_array_status import PodArrayStatus
from .models.pod_patch import PodPatch
from .models.pod_performance_replication import PodPerformanceReplication
from .models.pod_performance_replication_by_array import PodPerformanceReplicationByArray
from .models.pod_post import PodPost
from .models.pod_replica_link import PodReplicaLink
from .models.pod_replica_link_lag import PodReplicaLinkLag
from .models.pod_replica_link_performance_replication import PodReplicaLinkPerformanceReplication
from .models.pod_space import PodSpace
from .models.port import Port
from .models.protection_group import ProtectionGroup
from .models.protection_group_performance import ProtectionGroupPerformance
from .models.protection_group_performance_array import ProtectionGroupPerformanceArray
from .models.protection_group_snapshot import ProtectionGroupSnapshot
from .models.protection_group_snapshot_post import ProtectionGroupSnapshotPost
from .models.protection_group_snapshot_transfer import ProtectionGroupSnapshotTransfer
from .models.remote_pod import RemotePod
from .models.remote_protection_group import RemoteProtectionGroup
from .models.remote_protection_group_snapshot import RemoteProtectionGroupSnapshot
from .models.remote_protection_group_snapshot_transfer import RemoteProtectionGroupSnapshotTransfer
from .models.remote_volume_snapshot import RemoteVolumeSnapshot
from .models.remote_volume_snapshot_transfer import RemoteVolumeSnapshotTransfer
from .models.replication_schedule import ReplicationSchedule
from .models.resource_performance import ResourcePerformance
from .models.resource_performance_no_id import ResourcePerformanceNoId
from .models.resource_pod_space import ResourcePodSpace
from .models.resource_space import ResourceSpace
from .models.resource_space_no_id import ResourceSpaceNoId
from .models.software import Software
from .models.software_installation import SoftwareInstallation
from .models.software_installation_step import SoftwareInstallationStep
from .models.space import Space
from .models.subnet import Subnet
from .models.subnet_patch import SubnetPatch
from .models.support import Support
from .models.test_result_with_resource import TestResultWithResource
from .models.volume_common import VolumeCommon
from .models.volume_group import VolumeGroup
from .models.volume_group_performance import VolumeGroupPerformance
from .models.volume_group_post import VolumeGroupPost
from .models.volume_patch import VolumePatch
from .models.volume_performance import VolumePerformance
from .models.volume_post import VolumePost
from .models.volume_snapshot import VolumeSnapshot
from .models.volume_snapshot_patch import VolumeSnapshotPatch
from .models.volume_snapshot_post import VolumeSnapshotPost
from .models.volume_snapshot_transfer import VolumeSnapshotTransfer
from .models.admin_patch import AdminPatch
from .models.protection_group_snapshot_patch import ProtectionGroupSnapshotPatch
from .models.resource_performance_by_array import ResourcePerformanceByArray
from .models.resource_performance_no_id_by_array import ResourcePerformanceNoIdByArray
from .models.volume import Volume


def add_properties(model):
    for name, value in model.attribute_map.items():
        setattr(model, name, Property(value))


def add_all_properties():
    for model in CLASSES_TO_ADD_PROPS:
        add_properties(model)


CLASSES_TO_ADD_PROPS = [
    AdminPost,
    AdminSettings,
    AggregateReplicationPerformance,
    ApiClient,
    ApiClientPatch,
    ApiClientPost,
    ApiToken,
    AppNode,
    BuiltIn,
    BuiltInRelationship,
    BuiltInResourceNoId,
    Chap,
    Connection,
    ConnectionPost,
    DestroyedPatchPost,
    DirectoryServiceManagement,
    DirectoryServiceRole,
    Dns,
    DnsPatch,
    Eula,
    EulaSignature,
    FixedNameResourceNoId,
    FixedReference,
    FixedReferenceNoId,
    HostPortConnectivity,
    HostPost,
    KmipPatch,
    KmipPost,
    KmipTestResult,
    MaintenanceWindowPost,
    Member,
    MemberNoIdAll,
    MemberNoIdGroup,
    NewName,
    OffloadAzure,
    OffloadGoogleCloud,
    OffloadNfs,
    OffloadPost,
    OffloadS3,
    OverrideCheck,
    PageInfo,
    Performance,
    PodPerformanceReplication,
    PodReplicaLinkPatch,
    PortCommon,
    PortInitiator,
    ProtectionGroupTarget,
    Qos,
    Reference,
    ReferenceNoId,
    ReplicaLinkLag,
    ReplicaLinkPerformanceReplication,
    ReplicationPerformanceWithTotal,
    Resource,
    ResourceFixedNonUniqueName,
    ResourceNoId,
    RetentionPolicy,
    Smis,
    Snapshot,
    SnapshotSchedule,
    SoftwareInstallationPatch,
    SoftwareInstallationPost,
    SoftwareInstallationStepsChecks,
    Space,
    StartEndTime,
    SubnetPost,
    SupportPatch,
    SupportRemoteAssistPaths,
    Tag,
    TargetProtectionGroup,
    TargetProtectionGroupPostPatch,
    TestResult,
    TimeWindow,
    Transfer,
    Username,
    Admin,
    AdminApiToken,
    AdminCache,
    AdminRole,
    Alert,
    AlertEvent,
    App,
    ArrayPerformance,
    ArraySpace,
    Arrays,
    Audit,
    Controller,
    DirectoryService,
    Hardware,
    HardwarePatch,
    Host,
    HostGroup,
    HostGroupPatch,
    HostPatch,
    Kmip,
    MaintenanceWindow,
    Offload,
    Pod,
    PodArrayStatus,
    PodPatch,
    PodPerformanceReplication,
    PodPerformanceReplicationByArray,
    PodPost,
    PodReplicaLink,
    PodReplicaLinkLag,
    PodReplicaLinkPerformanceReplication,
    PodSpace,
    Port,
    ProtectionGroup,
    ProtectionGroupPerformance,
    ProtectionGroupPerformanceArray,
    ProtectionGroupSnapshot,
    ProtectionGroupSnapshotPost,
    ProtectionGroupSnapshotTransfer,
    RemotePod,
    RemoteProtectionGroup,
    RemoteProtectionGroupSnapshot,
    RemoteProtectionGroupSnapshotTransfer,
    RemoteVolumeSnapshot,
    RemoteVolumeSnapshotTransfer,
    ReplicationSchedule,
    ResourcePerformance,
    ResourcePerformanceNoId,
    ResourcePodSpace,
    ResourceSpace,
    ResourceSpaceNoId,
    Software,
    SoftwareInstallation,
    SoftwareInstallationStep,
    Space,
    Subnet,
    SubnetPatch,
    Support,
    TestResultWithResource,
    VolumeCommon,
    VolumeGroup,
    VolumeGroupPerformance,
    VolumeGroupPost,
    VolumePatch,
    VolumePerformance,
    VolumePost,
    VolumeSnapshot,
    VolumeSnapshotPatch,
    VolumeSnapshotPost,
    VolumeSnapshotTransfer,
    AdminPatch,
    ProtectionGroupSnapshotPatch,
    ResourcePerformanceByArray,
    ResourcePerformanceNoIdByArray,
    Volume
]

if os.environ.get('DOCS_GENERATION') is None:
    add_all_properties()
