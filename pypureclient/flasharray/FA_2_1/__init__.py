from __future__ import absolute_import
import os

from .client import Client
from ...exceptions import PureError
from ...properties import Property, Filter
from ...responses import ValidResponse, ErrorResponse, ApiError, ResponseHeaders

from .models.aggregate_replication_performance import AggregateReplicationPerformance
from .models.api_client import ApiClient
from .models.api_client_patch import ApiClientPatch
from .models.api_client_post import ApiClientPost
from .models.built_in import BuiltIn
from .models.built_in_resource_no_id import BuiltInResourceNoId
from .models.chap import Chap
from .models.connection import Connection
from .models.connection_post import ConnectionPost
from .models.destroyed_patch_post import DestroyedPatchPost
from .models.fixed_reference import FixedReference
from .models.fixed_reference_no_id import FixedReferenceNoId
from .models.host_port_connectivity import HostPortConnectivity
from .models.host_post import HostPost
from .models.member import Member
from .models.member_no_id_all import MemberNoIdAll
from .models.member_no_id_group import MemberNoIdGroup
from .models.new_name import NewName
from .models.offload_azure import OffloadAzure
from .models.offload_nfs import OffloadNfs
from .models.offload_post import OffloadPost
from .models.offload_s3 import OffloadS3
from .models.page_info import PageInfo
from .models.performance import Performance
from .models.protection_group_target import ProtectionGroupTarget
from .models.qos import Qos
from .models.reference import Reference
from .models.reference_no_id import ReferenceNoId
from .models.resource import Resource
from .models.resource_no_id import ResourceNoId
from .models.retention_policy import RetentionPolicy
from .models.snapshot import Snapshot
from .models.snapshot_schedule import SnapshotSchedule
from .models.space import Space
from .models.target_protection_group import TargetProtectionGroup
from .models.target_protection_group_post_patch import TargetProtectionGroupPostPatch
from .models.time_window import TimeWindow
from .models.transfer import Transfer
from .models.username import Username
from .models.host import Host
from .models.host_group import HostGroup
from .models.host_group_patch import HostGroupPatch
from .models.host_patch import HostPatch
from .models.offload import Offload
from .models.pod import Pod
from .models.pod_array_status import PodArrayStatus
from .models.pod_patch import PodPatch
from .models.pod_post import PodPost
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
from .models.resource_space import ResourceSpace
from .models.resource_space_no_id import ResourceSpaceNoId
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
    AggregateReplicationPerformance,
    ApiClient,
    ApiClientPatch,
    ApiClientPost,
    BuiltIn,
    BuiltInResourceNoId,
    Chap,
    Connection,
    ConnectionPost,
    DestroyedPatchPost,
    FixedReference,
    FixedReferenceNoId,
    HostPortConnectivity,
    HostPost,
    Member,
    MemberNoIdAll,
    MemberNoIdGroup,
    NewName,
    OffloadAzure,
    OffloadNfs,
    OffloadPost,
    OffloadS3,
    PageInfo,
    Performance,
    ProtectionGroupTarget,
    Qos,
    Reference,
    ReferenceNoId,
    Resource,
    ResourceNoId,
    RetentionPolicy,
    Snapshot,
    SnapshotSchedule,
    Space,
    TargetProtectionGroup,
    TargetProtectionGroupPostPatch,
    TimeWindow,
    Transfer,
    Username,
    Host,
    HostGroup,
    HostGroupPatch,
    HostPatch,
    Offload,
    Pod,
    PodArrayStatus,
    PodPatch,
    PodPost,
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
    ResourceSpace,
    ResourceSpaceNoId,
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
    ProtectionGroupSnapshotPatch,
    ResourcePerformanceByArray,
    ResourcePerformanceNoIdByArray,
    Volume
]

if os.environ.get('DOCS_GENERATION') is None:
    add_all_properties()
