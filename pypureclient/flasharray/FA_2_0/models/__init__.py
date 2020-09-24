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
from .api_version_response import ApiVersionResponse
from .built_in import BuiltIn
from .chap import Chap
from .connection import Connection
from .connection_get_response import ConnectionGetResponse
from .connection_post import ConnectionPost
from .connection_response import ConnectionResponse
from .destroyed_patch_post import DestroyedPatchPost
from .fixed_reference import FixedReference
from .fixed_reference_no_id import FixedReferenceNoId
from .host import Host
from .host_get_response import HostGetResponse
from .host_group import HostGroup
from .host_group_get_response import HostGroupGetResponse
from .host_group_patch import HostGroupPatch
from .host_group_performance import HostGroupPerformance
from .host_group_performance_by_array import HostGroupPerformanceByArray
from .host_group_response import HostGroupResponse
from .host_patch import HostPatch
from .host_performance import HostPerformance
from .host_performance_by_array import HostPerformanceByArray
from .host_port_connectivity import HostPortConnectivity
from .host_post import HostPost
from .host_response import HostResponse
from .inline_response400 import InlineResponse400
from .inline_response401 import InlineResponse401
from .member import Member
from .member_no_id_all import MemberNoIdAll
from .member_no_id_all_get_response import MemberNoIdAllGetResponse
from .member_no_id_all_response import MemberNoIdAllResponse
from .new_name import NewName
from .oauth_token_response import OauthTokenResponse
from .page_info import PageInfo
from .performance import Performance
from .qos import Qos
from .reference import Reference
from .reference_no_id import ReferenceNoId
from .resource import Resource
from .resource_no_id import ResourceNoId
from .resource_performance import ResourcePerformance
from .resource_performance_by_array import ResourcePerformanceByArray
from .resource_performance_by_array_get_response import ResourcePerformanceByArrayGetResponse
from .resource_performance_get_response import ResourcePerformanceGetResponse
from .resource_performance_no_id import ResourcePerformanceNoId
from .resource_performance_no_id_by_array import ResourcePerformanceNoIdByArray
from .resource_performance_no_id_by_array_get_response import ResourcePerformanceNoIdByArrayGetResponse
from .resource_performance_no_id_get_response import ResourcePerformanceNoIdGetResponse
from .resource_space import ResourceSpace
from .resource_space_get_response import ResourceSpaceGetResponse
from .snapshot import Snapshot
from .space import Space
from .transfer import Transfer
from .username import Username
from .username_response import UsernameResponse
from .volume import Volume
from .volume_common import VolumeCommon
from .volume_get_response import VolumeGetResponse
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
