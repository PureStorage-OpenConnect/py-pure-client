from __future__ import absolute_import
import os

from .client import Client
from ...exceptions import PureError
from ...properties import Property, Filter
from ...responses import ValidResponse, ErrorResponse, ApiError, ResponseHeaders

from .models.active_directory import ActiveDirectory
from .models.active_directory_patch import ActiveDirectoryPatch
from .models.active_directory_post import ActiveDirectoryPost
from .models.admin import Admin
from .models.admin_api_token import AdminApiToken
from .models.admin_cache import AdminCache
from .models.admin_patch import AdminPatch
from .models.alert import Alert
from .models.alert_watcher import AlertWatcher
from .models.alert_watcher_post import AlertWatcherPost
from .models.api_client import ApiClient
from .models.api_clients_post import ApiClientsPost
from .models.api_token import ApiToken
from .models.api_version import ApiVersion
from .models.array import Array
from .models.array_connection import ArrayConnection
from .models.array_connection_key import ArrayConnectionKey
from .models.array_connection_path import ArrayConnectionPath
from .models.array_connection_post import ArrayConnectionPost
from .models.array_http_specific_performance import ArrayHttpSpecificPerformance
from .models.array_http_specific_performance_get import ArrayHttpSpecificPerformanceGet
from .models.array_nfs_specific_performance import ArrayNfsSpecificPerformance
from .models.array_nfs_specific_performance_get import ArrayNfsSpecificPerformanceGet
from .models.array_performance import ArrayPerformance
from .models.array_performance_replication_get_resp import ArrayPerformanceReplicationGetResp
from .models.array_s3_specific_performance import ArrayS3SpecificPerformance
from .models.array_s3_specific_performance_get_resp import ArrayS3SpecificPerformanceGetResp
from .models.array_space import ArraySpace
from .models.audit import Audit
from .models.blade import Blade
from .models.bucket import Bucket
from .models.bucket_performance import BucketPerformance
from .models.bucket_post import BucketPost
from .models.bucket_replica_link import BucketReplicaLink
from .models.bucket_replica_link_post import BucketReplicaLinkPost
from .models.bucket_s3_specific_performance import BucketS3SpecificPerformance
from .models.bucket_s3_specific_performance_get_resp import BucketS3SpecificPerformanceGetResp
from .models.built_in import BuiltIn
from .models.built_in_no_id import BuiltInNoId
from .models.built_in_relationship import BuiltInRelationship
from .models.certificate import Certificate
from .models.certificate_certificate_group_get_resp import CertificateCertificateGroupGetResp
from .models.certificate_group import CertificateGroup
from .models.certificate_group_certificate_get_resp import CertificateGroupCertificateGetResp
from .models.certificate_group_use import CertificateGroupUse
from .models.certificate_patch import CertificatePatch
from .models.certificate_post import CertificatePost
from .models.certificate_use import CertificateUse
from .models.client_performance import ClientPerformance
from .models.connection_relationship_performance_replication import ConnectionRelationshipPerformanceReplication
from .models.connection_relationship_performance_replication_get_resp import ConnectionRelationshipPerformanceReplicationGetResp
from .models.direction import Direction
from .models.directory_service import DirectoryService
from .models.directory_service_management import DirectoryServiceManagement
from .models.directory_service_nfs import DirectoryServiceNfs
from .models.directory_service_role import DirectoryServiceRole
from .models.directory_service_smb import DirectoryServiceSmb
from .models.dns import Dns
from .models.eula import Eula
from .models.eula_signature import EulaSignature
from .models.file_system import FileSystem
from .models.file_system_group_performance import FileSystemGroupPerformance
from .models.file_system_patch import FileSystemPatch
from .models.file_system_performance import FileSystemPerformance
from .models.file_system_post import FileSystemPost
from .models.file_system_replica_link import FileSystemReplicaLink
from .models.file_system_snapshot import FileSystemSnapshot
from .models.file_system_snapshot_post import FileSystemSnapshotPost
from .models.file_system_snapshot_transfer import FileSystemSnapshotTransfer
from .models.file_system_user_performance import FileSystemUserPerformance
from .models.fixed_location_reference import FixedLocationReference
from .models.fixed_reference import FixedReference
from .models.fixed_reference_name_only import FixedReferenceNameOnly
from .models.fixed_reference_no_resource_type import FixedReferenceNoResourceType
from .models.fixed_reference_with_remote import FixedReferenceWithRemote
from .models.group import Group
from .models.group_quota import GroupQuota
from .models.group_quota_patch import GroupQuotaPatch
from .models.group_quota_post import GroupQuotaPost
from .models.hardware import Hardware
from .models.hardware_connector import HardwareConnector
from .models.http import Http
from .models.keytab import Keytab
from .models.keytab_file_base64 import KeytabFileBase64
from .models.keytab_file_binary import KeytabFileBinary
from .models.keytab_post import KeytabPost
from .models.lifecycle_rule import LifecycleRule
from .models.lifecycle_rule_patch import LifecycleRulePatch
from .models.lifecycle_rule_post import LifecycleRulePost
from .models.link_aggregation_group import LinkAggregationGroup
from .models.linkaggregationgroup import Linkaggregationgroup
from .models.location_reference import LocationReference
from .models.login import Login
from .models.member import Member
from .models.member_link import MemberLink
from .models.multi_protocol import MultiProtocol
from .models.multi_protocol_post import MultiProtocolPost
from .models.network_interface import NetworkInterface
from .models.network_interface_patch import NetworkInterfacePatch
from .models.nfs import Nfs
from .models.nfs_patch import NfsPatch
from .models.object_store_access_key import ObjectStoreAccessKey
from .models.object_store_access_key_post import ObjectStoreAccessKeyPost
from .models.object_store_access_policy import ObjectStoreAccessPolicy
from .models.object_store_account import ObjectStoreAccount
from .models.object_store_remote_credential_get_resp import ObjectStoreRemoteCredentialGetResp
from .models.object_store_remote_credentials import ObjectStoreRemoteCredentials
from .models.object_store_remote_credentials_post import ObjectStoreRemoteCredentialsPost
from .models.object_store_remote_credentials_resp import ObjectStoreRemoteCredentialsResp
from .models.object_store_user import ObjectStoreUser
from .models.object_store_virtual_host import ObjectStoreVirtualHost
from .models.page_info import PageInfo
from .models.permission import Permission
from .models.policy import Policy
from .models.policy_file_system_snapshot import PolicyFileSystemSnapshot
from .models.policy_local_member import PolicyLocalMember
from .models.policy_member import PolicyMember
from .models.policy_member_with_remote import PolicyMemberWithRemote
from .models.policy_patch import PolicyPatch
from .models.policy_rule import PolicyRule
from .models.quota_setting import QuotaSetting
from .models.reference import Reference
from .models.reference_writable import ReferenceWritable
from .models.relationship_performance_replication import RelationshipPerformanceReplication
from .models.replica_link_built_in import ReplicaLinkBuiltIn
from .models.replication_performance import ReplicationPerformance
from .models.resource import Resource
from .models.resource_performance_replication import ResourcePerformanceReplication
from .models.resource_type import ResourceType
from .models.role import Role
from .models.smtp import SMTP
from .models.smb import Smb
from .models.smtp_server import SmtpServer
from .models.snmp_agent import SnmpAgent
from .models.snmp_agent_mib import SnmpAgentMib
from .models.snmp_manager import SnmpManager
from .models.snmp_manager_post import SnmpManagerPost
from .models.snmp_manager_test import SnmpManagerTest
from .models.snmp_v2c import SnmpV2c
from .models.snmp_v3 import SnmpV3
from .models.snmp_v3_post import SnmpV3Post
from .models.space import Space
from .models.subnet import Subnet
from .models.support import Support
from .models.support_remote_assist_paths import SupportRemoteAssistPaths
from .models.syslog_server import SyslogServer
from .models.syslog_server_post_or_patch import SyslogServerPostOrPatch
from .models.syslog_server_settings import SyslogServerSettings
from .models.target import Target
from .models.target_post import TargetPost
from .models.test_result import TestResult
from .models.time_zone import TimeZone
from .models.user import User
from .models.user_quota import UserQuota
from .models.user_quota_patch import UserQuotaPatch
from .models.user_quota_post import UserQuotaPost


def add_properties(model):
    for name, value in model.attribute_map.items():
        setattr(model, name, Property(value))


CLASSES_TO_ADD_PROPS = [
    ActiveDirectory,
    ActiveDirectoryPatch,
    ActiveDirectoryPost,
    Admin,
    AdminApiToken,
    AdminCache,
    AdminPatch,
    Alert,
    AlertWatcher,
    AlertWatcherPost,
    ApiClient,
    ApiClientsPost,
    ApiToken,
    ApiVersion,
    Array,
    ArrayConnection,
    ArrayConnectionKey,
    ArrayConnectionPath,
    ArrayConnectionPost,
    ArrayHttpSpecificPerformance,
    ArrayHttpSpecificPerformanceGet,
    ArrayNfsSpecificPerformance,
    ArrayNfsSpecificPerformanceGet,
    ArrayPerformance,
    ArrayPerformanceReplicationGetResp,
    ArrayS3SpecificPerformance,
    ArrayS3SpecificPerformanceGetResp,
    ArraySpace,
    Audit,
    Blade,
    Bucket,
    BucketPerformance,
    BucketPost,
    BucketReplicaLink,
    BucketReplicaLinkPost,
    BucketS3SpecificPerformance,
    BucketS3SpecificPerformanceGetResp,
    BuiltIn,
    BuiltInNoId,
    BuiltInRelationship,
    Certificate,
    CertificateCertificateGroupGetResp,
    CertificateGroup,
    CertificateGroupCertificateGetResp,
    CertificateGroupUse,
    CertificatePatch,
    CertificatePost,
    CertificateUse,
    ClientPerformance,
    ConnectionRelationshipPerformanceReplication,
    ConnectionRelationshipPerformanceReplicationGetResp,
    Direction,
    DirectoryService,
    DirectoryServiceManagement,
    DirectoryServiceNfs,
    DirectoryServiceRole,
    DirectoryServiceSmb,
    Dns,
    Eula,
    EulaSignature,
    FileSystem,
    FileSystemGroupPerformance,
    FileSystemPatch,
    FileSystemPerformance,
    FileSystemPost,
    FileSystemReplicaLink,
    FileSystemSnapshot,
    FileSystemSnapshotPost,
    FileSystemSnapshotTransfer,
    FileSystemUserPerformance,
    FixedLocationReference,
    FixedReference,
    FixedReferenceNameOnly,
    FixedReferenceNoResourceType,
    FixedReferenceWithRemote,
    Group,
    GroupQuota,
    GroupQuotaPatch,
    GroupQuotaPost,
    Hardware,
    HardwareConnector,
    Http,
    Keytab,
    KeytabFileBase64,
    KeytabFileBinary,
    KeytabPost,
    LifecycleRule,
    LifecycleRulePatch,
    LifecycleRulePost,
    LinkAggregationGroup,
    Linkaggregationgroup,
    LocationReference,
    Login,
    Member,
    MemberLink,
    MultiProtocol,
    MultiProtocolPost,
    NetworkInterface,
    NetworkInterfacePatch,
    Nfs,
    NfsPatch,
    ObjectStoreAccessKey,
    ObjectStoreAccessKeyPost,
    ObjectStoreAccessPolicy,
    ObjectStoreAccount,
    ObjectStoreRemoteCredentialGetResp,
    ObjectStoreRemoteCredentials,
    ObjectStoreRemoteCredentialsPost,
    ObjectStoreRemoteCredentialsResp,
    ObjectStoreUser,
    ObjectStoreVirtualHost,
    PageInfo,
    Permission,
    Policy,
    PolicyFileSystemSnapshot,
    PolicyLocalMember,
    PolicyMember,
    PolicyMemberWithRemote,
    PolicyPatch,
    PolicyRule,
    QuotaSetting,
    Reference,
    ReferenceWritable,
    RelationshipPerformanceReplication,
    ReplicaLinkBuiltIn,
    ReplicationPerformance,
    Resource,
    ResourcePerformanceReplication,
    ResourceType,
    Role,
    SMTP,
    Smb,
    SmtpServer,
    SnmpAgent,
    SnmpAgentMib,
    SnmpManager,
    SnmpManagerPost,
    SnmpManagerTest,
    SnmpV2c,
    SnmpV3,
    SnmpV3Post,
    Space,
    Subnet,
    Support,
    SupportRemoteAssistPaths,
    SyslogServer,
    SyslogServerPostOrPatch,
    SyslogServerSettings,
    Target,
    TargetPost,
    TestResult,
    TimeZone,
    User,
    UserQuota,
    UserQuotaPatch,
    UserQuotaPost
]

if os.environ.get('DOCS_GENERATION') is None:
    for model in CLASSES_TO_ADD_PROPS:
        add_properties(model)
