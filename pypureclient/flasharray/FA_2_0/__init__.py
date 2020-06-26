from __future__ import absolute_import
import os

from .client import Client
from ...exceptions import PureError
from ...properties import Property, Filter
from ...responses import ValidResponse, ErrorResponse, ApiError, ResponseHeaders

from .models.built_in import BuiltIn
from .models.chap import Chap
from .models.connection import Connection
from .models.connection_post import ConnectionPost
from .models.destroyed_patch_post import DestroyedPatchPost
from .models.fixed_reference import FixedReference
from .models.fixed_reference_no_id import FixedReferenceNoId
from .models.host import Host
from .models.host_group import HostGroup
from .models.host_group_patch import HostGroupPatch
from .models.host_group_performance import HostGroupPerformance
from .models.host_group_performance_by_array import HostGroupPerformanceByArray
from .models.host_patch import HostPatch
from .models.host_performance import HostPerformance
from .models.host_performance_by_array import HostPerformanceByArray
from .models.host_port_connectivity import HostPortConnectivity
from .models.host_post import HostPost
from .models.member import Member
from .models.member_no_id_all import MemberNoIdAll
from .models.new_name import NewName
from .models.page_info import PageInfo
from .models.performance import Performance
from .models.qos import Qos
from .models.reference import Reference
from .models.reference_no_id import ReferenceNoId
from .models.resource import Resource
from .models.resource_no_id import ResourceNoId
from .models.resource_performance import ResourcePerformance
from .models.resource_performance_by_array import ResourcePerformanceByArray
from .models.resource_performance_no_id import ResourcePerformanceNoId
from .models.resource_performance_no_id_by_array import ResourcePerformanceNoIdByArray
from .models.resource_space import ResourceSpace
from .models.snapshot import Snapshot
from .models.space import Space
from .models.transfer import Transfer
from .models.username import Username
from .models.volume import Volume
from .models.volume_common import VolumeCommon
from .models.volume_patch import VolumePatch
from .models.volume_performance import VolumePerformance
from .models.volume_performance_by_array import VolumePerformanceByArray
from .models.volume_post import VolumePost
from .models.volume_snapshot import VolumeSnapshot
from .models.volume_snapshot_patch import VolumeSnapshotPatch
from .models.volume_snapshot_post import VolumeSnapshotPost
from .models.volume_snapshot_transfer import VolumeSnapshotTransfer
from .models.volume_space import VolumeSpace


def add_properties(model):
    for name, value in model.attribute_map.items():
        setattr(model, name, Property(value))


CLASSES_TO_ADD_PROPS = [
    BuiltIn,
    Chap,
    Connection,
    ConnectionPost,
    DestroyedPatchPost,
    FixedReference,
    FixedReferenceNoId,
    Host,
    HostGroup,
    HostGroupPatch,
    HostGroupPerformance,
    HostGroupPerformanceByArray,
    HostPatch,
    HostPerformance,
    HostPerformanceByArray,
    HostPortConnectivity,
    HostPost,
    Member,
    MemberNoIdAll,
    NewName,
    PageInfo,
    Performance,
    Qos,
    Reference,
    ReferenceNoId,
    Resource,
    ResourceNoId,
    ResourcePerformance,
    ResourcePerformanceByArray,
    ResourcePerformanceNoId,
    ResourcePerformanceNoIdByArray,
    ResourceSpace,
    Snapshot,
    Space,
    Transfer,
    Username,
    Volume,
    VolumeCommon,
    VolumePatch,
    VolumePerformance,
    VolumePerformanceByArray,
    VolumePost,
    VolumeSnapshot,
    VolumeSnapshotPatch,
    VolumeSnapshotPost,
    VolumeSnapshotTransfer,
    VolumeSpace
]

if os.environ.get('DOCS_GENERATION') is None:
    for model in CLASSES_TO_ADD_PROPS:
        add_properties(model)
