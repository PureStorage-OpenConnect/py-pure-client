from __future__ import absolute_import
import os

from .client import Client
from ...exceptions import PureError
from ...properties import Property, Filter
from ...responses import ValidResponse, ErrorResponse, ApiError, ResponseHeaders

from .models.active_directory_directory_servers import ActiveDirectoryDirectoryServers
from .models.admin_api_token import AdminApiToken
from .models.admin_patch import AdminPatch
from .models.admin_post import AdminPost
from .models.admin_setting import AdminSetting
from .models.alert_watcher_post import AlertWatcherPost
from .models.api_clients_post import ApiClientsPost
from .models.api_token import ApiToken
from .models.api_version import ApiVersion
from .models.array_connection_key import ArrayConnectionKey
from .models.array_encryption import ArrayEncryption
from .models.array_encryption_data_at_rest import ArrayEncryptionDataAtRest
from .models.array_eradication_config import ArrayEradicationConfig
from .models.bucket_access_policy_post import BucketAccessPolicyPost
from .models.bucket_access_policy_rule_post import BucketAccessPolicyRulePost
from .models.bucket_access_policy_rule_principal import BucketAccessPolicyRulePrincipal
from .models.bucket_defaults import BucketDefaults
from .models.bucket_defaults_readonly import BucketDefaultsReadonly
from .models.bucket_eradication_config import BucketEradicationConfig
from .models.bucket_patch import BucketPatch
from .models.bucket_post import BucketPost
from .models.bucket_replica_link_post import BucketReplicaLinkPost
from .models.built_in import BuiltIn
from .models.built_in_no_id import BuiltInNoId
from .models.built_in_relationship import BuiltInRelationship
from .models.context import Context
from .models.cross_origin_resource_sharing_policy_patch import CrossOriginResourceSharingPolicyPatch
from .models.cross_origin_resource_sharing_policy_rule_post import CrossOriginResourceSharingPolicyRulePost
from .models.direction import Direction
from .models.directory_service_management import DirectoryServiceManagement
from .models.directory_service_nfs import DirectoryServiceNfs
from .models.directory_service_role import DirectoryServiceRole
from .models.directory_service_smb import DirectoryServiceSmb
from .models.dns_post import DnsPost
from .models.eula import Eula
from .models.eula_signature import EulaSignature
from .models.file_lock_range import FileLockRange
from .models.file_system_eradication_config import FileSystemEradicationConfig
from .models.file_system_export_post import FileSystemExportPost
from .models.file_system_lock_nlm_reclamation import FileSystemLockNlmReclamation
from .models.file_system_open_file import FileSystemOpenFile
from .models.file_system_post import FileSystemPost
from .models.file_system_snapshot_post import FileSystemSnapshotPost
from .models.fixed_reference import FixedReference
from .models.fixed_reference_name_only import FixedReferenceNameOnly
from .models.fixed_reference_no_id import FixedReferenceNoId
from .models.fixed_reference_no_resource_type import FixedReferenceNoResourceType
from .models.fleet_key import FleetKey
from .models.fleet_member import FleetMember
from .models.fleet_member_post import FleetMemberPost
from .models.fleet_member_post_members import FleetMemberPostMembers
from .models.fleet_member_post_members_member import FleetMemberPostMembersMember
from .models.fleet_patch import FleetPatch
from .models.group import Group
from .models.http import Http
from .models.index import Index
from .models.keytab_file_base64 import KeytabFileBase64
from .models.keytab_file_binary import KeytabFileBinary
from .models.keytab_post import KeytabPost
from .models.legal_hold_held_entity import LegalHoldHeldEntity
from .models.lifecycle_rule_config_extension import LifecycleRuleConfigExtension
from .models.linkaggregationgroup import Linkaggregationgroup
from .models.login import Login
from .models.maintenance_window_post import MaintenanceWindowPost
from .models.member import Member
from .models.member_link import MemberLink
from .models.multi_protocol import MultiProtocol
from .models.multi_protocol_post import MultiProtocolPost
from .models.network_interface_patch import NetworkInterfacePatch
from .models.network_interface_ping import NetworkInterfacePing
from .models.network_interface_trace import NetworkInterfaceTrace
from .models.network_interfaces_connectors_setting_roce import NetworkInterfacesConnectorsSettingRoce
from .models.network_interfaces_connectors_setting_roce_ecn import NetworkInterfacesConnectorsSettingRoceEcn
from .models.network_interfaces_connectors_setting_roce_pfc import NetworkInterfacesConnectorsSettingRocePfc
from .models.nfs import Nfs
from .models.object_backlog import ObjectBacklog
from .models.object_lock_config_base import ObjectLockConfigBase
from .models.object_store_access_key_post import ObjectStoreAccessKeyPost
from .models.object_store_access_policy_patch import ObjectStoreAccessPolicyPatch
from .models.object_store_account_patch import ObjectStoreAccountPatch
from .models.object_store_account_post import ObjectStoreAccountPost
from .models.object_store_remote_credentials_post import ObjectStoreRemoteCredentialsPost
from .models.object_store_remote_credentials_resp import ObjectStoreRemoteCredentialsResp
from .models.object_store_role_post import ObjectStoreRolePost
from .models.object_store_trust_policy_iam import ObjectStoreTrustPolicyIam
from .models.oidc_sso_post import OidcSsoPost
from .models.oidc_sso_post_idp import OidcSsoPostIdp
from .models.page_info import PageInfo
from .models.permission import Permission
from .models.policy_member import PolicyMember
from .models.policy_rule import PolicyRule
from .models.policy_rule_index import PolicyRuleIndex
from .models.policy_rule_index_in_policy import PolicyRuleIndexInPolicy
from .models.policy_rule_object_access_condition import PolicyRuleObjectAccessCondition
from .models.policy_rule_object_access_post import PolicyRuleObjectAccessPost
from .models.public_access_config import PublicAccessConfig
from .models.public_key_post import PublicKeyPost
from .models.rapid_data_locking import RapidDataLocking
from .models.reference import Reference
from .models.reference_name_only import ReferenceNameOnly
from .models.reference_writable import ReferenceWritable
from .models.replication_performance import ReplicationPerformance
from .models.resource import Resource
from .models.resource_fixed_non_unique_name import ResourceFixedNonUniqueName
from .models.saml2_sso_idp import Saml2SsoIdp
from .models.saml2_sso_post import Saml2SsoPost
from .models.saml2_sso_sp_credential import Saml2SsoSpCredential
from .models.server_post import ServerPost
from .models.smb import Smb
from .models.snmp_agent_mib import SnmpAgentMib
from .models.snmp_manager_post import SnmpManagerPost
from .models.snmp_v2c import SnmpV2c
from .models.snmp_v3 import SnmpV3
from .models.snmp_v3_post import SnmpV3Post
from .models.software_checks_checks import SoftwareChecksChecks
from .models.space import Space
from .models.start_end_time import StartEndTime
from .models.support_diagnostics_severity_count import SupportDiagnosticsSeverityCount
from .models.support_remote_assist_paths import SupportRemoteAssistPaths
from .models.syslog_server_post_or_patch import SyslogServerPostOrPatch
from .models.target_post import TargetPost
from .models.test_result import TestResult
from .models.throttle import Throttle
from .models.time_window import TimeWindow
from .models.trust_policy_rule_condition import TrustPolicyRuleCondition
from .models.trust_policy_rule_post import TrustPolicyRulePost
from .models.user import User
from .models.user_no_id import UserNoId
from .models.verification_key import VerificationKey
from .models.verification_key_patch import VerificationKeyPatch
from .models.version import Version
from .models.worm_data_policy_retention_config import WormDataPolicyRetentionConfig
from .models.active_directory import ActiveDirectory
from .models.active_directory_patch import ActiveDirectoryPatch
from .models.active_directory_post import ActiveDirectoryPost
from .models.admin import Admin
from .models.admin_cache import AdminCache
from .models.alert import Alert
from .models.alert_watcher import AlertWatcher
from .models.api_client import ApiClient
from .models.array import Array
from .models.array_connection import ArrayConnection
from .models.array_connection_path import ArrayConnectionPath
from .models.array_factory_reset_token import ArrayFactoryResetToken
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
from .models.bucket_access_policy_rule import BucketAccessPolicyRule
from .models.bucket_access_policy_rule_bulk_manage import BucketAccessPolicyRuleBulkManage
from .models.bucket_performance import BucketPerformance
from .models.bucket_s3_specific_performance import BucketS3SpecificPerformance
from .models.bucket_s3_specific_performance_get_resp import BucketS3SpecificPerformanceGetResp
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
from .models.continuous_replication_performance import ContinuousReplicationPerformance
from .models.cross_origin_resource_sharing_policy_rule import CrossOriginResourceSharingPolicyRule
from .models.cross_origin_resource_sharing_policy_rule_bulk_manage import CrossOriginResourceSharingPolicyRuleBulkManage
from .models.directory_service import DirectoryService
from .models.dns import Dns
from .models.drive import Drive
from .models.file_info import FileInfo
from .models.file_lock import FileLock
from .models.file_session import FileSession
from .models.file_system import FileSystem
from .models.file_system_client import FileSystemClient
from .models.file_system_export import FileSystemExport
from .models.file_system_group_performance import FileSystemGroupPerformance
from .models.file_system_patch import FileSystemPatch
from .models.file_system_performance import FileSystemPerformance
from .models.file_system_snapshot import FileSystemSnapshot
from .models.file_system_snapshot_transfer import FileSystemSnapshotTransfer
from .models.file_system_user_performance import FileSystemUserPerformance
from .models.fixed_location_reference import FixedLocationReference
from .models.fixed_reference_with_is_local import FixedReferenceWithIsLocal
from .models.fixed_reference_with_remote import FixedReferenceWithRemote
from .models.fixed_reference_with_type import FixedReferenceWithType
from .models.fleet import Fleet
from .models.group_quota import GroupQuota
from .models.group_quota_post import GroupQuotaPost
from .models.hardware import Hardware
from .models.hardware_connector import HardwareConnector
from .models.hardware_connector_performance import HardwareConnectorPerformance
from .models.keytab import Keytab
from .models.kmip_server import KmipServer
from .models.legal_hold import LegalHold
from .models.lifecycle_rule import LifecycleRule
from .models.lifecycle_rule_patch import LifecycleRulePatch
from .models.lifecycle_rule_post import LifecycleRulePost
from .models.link_aggregation_group import LinkAggregationGroup
from .models.location_reference import LocationReference
from .models.logs_async import LogsAsync
from .models.maintenance_window import MaintenanceWindow
from .models.network_access_policy_rule_base import NetworkAccessPolicyRuleBase
from .models.network_access_policy_rule_post_base import NetworkAccessPolicyRulePostBase
from .models.network_interface import NetworkInterface
from .models.network_interfaces_connectors_setting import NetworkInterfacesConnectorsSetting
from .models.nfs_export_policy_rule_base import NfsExportPolicyRuleBase
from .models.nfs_patch import NfsPatch
from .models.object_lock_config_request_body import ObjectLockConfigRequestBody
from .models.object_store_access_key import ObjectStoreAccessKey
from .models.object_store_access_policy_action import ObjectStoreAccessPolicyAction
from .models.object_store_access_policy_post import ObjectStoreAccessPolicyPost
from .models.object_store_account import ObjectStoreAccount
from .models.object_store_remote_credential_get_resp import ObjectStoreRemoteCredentialGetResp
from .models.object_store_remote_credentials import ObjectStoreRemoteCredentials
from .models.object_store_role import ObjectStoreRole
from .models.object_store_user import ObjectStoreUser
from .models.object_store_virtual_host import ObjectStoreVirtualHost
from .models.oidc_sso import OidcSso
from .models.oidc_sso_patch import OidcSsoPatch
from .models.policy_base_renameable import PolicyBaseRenameable
from .models.policy_file_system_snapshot import PolicyFileSystemSnapshot
from .models.policy_member_context import PolicyMemberContext
from .models.policy_rule_object_access import PolicyRuleObjectAccess
from .models.policy_rule_object_access_bulk_manage import PolicyRuleObjectAccessBulkManage
from .models.public_key import PublicKey
from .models.public_key_use import PublicKeyUse
from .models.quota_setting import QuotaSetting
from .models.relationship_performance_replication import RelationshipPerformanceReplication
from .models.remote_array import RemoteArray
from .models.replica_link_built_in import ReplicaLinkBuiltIn
from .models.resource_performance_replication import ResourcePerformanceReplication
from .models.role import Role
from .models.saml2_sso import Saml2Sso
from .models.saml2_sso_sp import Saml2SsoSp
from .models.server import Server
from .models.session import Session
from .models.smb_client_policy_rule_base import SmbClientPolicyRuleBase
from .models.smb_client_policy_rule_post_base import SmbClientPolicyRulePostBase
from .models.smb_post import SmbPost
from .models.smb_share_policy_rule import SmbSharePolicyRule
from .models.smb_share_policy_rule_post import SmbSharePolicyRulePost
from .models.smtp_server import SmtpServer
from .models.snmp_agent import SnmpAgent
from .models.snmp_manager import SnmpManager
from .models.snmp_manager_test import SnmpManagerTest
from .models.software_check import SoftwareCheck
from .models.storage_class_info import StorageClassInfo
from .models.storage_class_space import StorageClassSpace
from .models.subnet import Subnet
from .models.support import Support
from .models.support_diagnostics import SupportDiagnostics
from .models.support_diagnostics_details import SupportDiagnosticsDetails
from .models.syslog_server_patch import SyslogServerPatch
from .models.syslog_server_post import SyslogServerPost
from .models.syslog_server_settings import SyslogServerSettings
from .models.target import Target
from .models.time_zone import TimeZone
from .models.trust_policy_rule import TrustPolicyRule
from .models.user_quota import UserQuota
from .models.user_quota_post import UserQuotaPost
from .models.array_connection_post import ArrayConnectionPost
from .models.audit_file_systems_policy_no_context import AuditFileSystemsPolicyNoContext
from .models.bucket_access_policy_rule_with_context import BucketAccessPolicyRuleWithContext
from .models.bucket_replica_link import BucketReplicaLink
from .models.cross_origin_resource_sharing_policy_rule_with_context import CrossOriginResourceSharingPolicyRuleWithContext
from .models.file_system_replica_link import FileSystemReplicaLink
from .models.group_quota_patch import GroupQuotaPatch
from .models.network_access_policy import NetworkAccessPolicy
from .models.network_access_policy_rule import NetworkAccessPolicyRule
from .models.network_access_policy_rule_in_policy import NetworkAccessPolicyRuleInPolicy
from .models.network_access_policy_rule_post import NetworkAccessPolicyRulePost
from .models.network_interfaces_connectors_performance import NetworkInterfacesConnectorsPerformance
from .models.nfs_export_policy import NfsExportPolicy
from .models.nfs_export_policy_rule import NfsExportPolicyRule
from .models.nfs_export_policy_rule_in_policy import NfsExportPolicyRuleInPolicy
from .models.password_policy import PasswordPolicy
from .models.policy_base import PolicyBase
from .models.policy_member_with_remote import PolicyMemberWithRemote
from .models.qos_policy import QosPolicy
from .models.server_context import ServerContext
from .models.smb_client_policy import SmbClientPolicy
from .models.smb_client_policy_rule import SmbClientPolicyRule
from .models.smb_client_policy_rule_in_policy import SmbClientPolicyRuleInPolicy
from .models.smb_client_policy_rule_post import SmbClientPolicyRulePost
from .models.smb_client_policy_rule_post_in_policy import SmbClientPolicyRulePostInPolicy
from .models.smb_share_policy import SmbSharePolicy
from .models.smb_share_policy_rule_with_context import SmbSharePolicyRuleWithContext
from .models.syslog_server import SyslogServer
from .models.target_with_context import TargetWithContext
from .models.trust_policy_rule_with_context import TrustPolicyRuleWithContext
from .models.user_quota_patch import UserQuotaPatch
from .models.audit_file_systems_policies_patch import AuditFileSystemsPoliciesPatch
from .models.audit_file_systems_policies_post import AuditFileSystemsPoliciesPost
from .models.audit_file_systems_policy import AuditFileSystemsPolicy
from .models.bucket_access_policy import BucketAccessPolicy
from .models.cross_origin_resource_sharing_policy import CrossOriginResourceSharingPolicy
from .models.nfs_export_policy_post import NfsExportPolicyPost
from .models.object_store_access_policy import ObjectStoreAccessPolicy
from .models.object_store_trust_policy import ObjectStoreTrustPolicy
from .models.policy import Policy
from .models.policy_base_context import PolicyBaseContext
from .models.smb_client_policy_post import SmbClientPolicyPost
from .models.smb_share_policy_post import SmbSharePolicyPost
from .models.ssh_certificate_authority_policy_post import SshCertificateAuthorityPolicyPost
from .models.syslog_server_context import SyslogServerContext
from .models.tls_policy_post import TlsPolicyPost
from .models.worm_data_policy import WormDataPolicy
from .models.policy_patch import PolicyPatch
from .models.ssh_certificate_authority_policy import SshCertificateAuthorityPolicy
from .models.tls_policy import TlsPolicy


def add_properties(model):
    for name, value in model.attribute_map.items():
        setattr(model, name, Property(value))


def add_all_properties():
    for model in CLASSES_TO_ADD_PROPS:
        add_properties(model)


CLASSES_TO_ADD_PROPS = [
    ActiveDirectoryDirectoryServers,
    AdminApiToken,
    AdminPatch,
    AdminPost,
    AdminSetting,
    AlertWatcherPost,
    ApiClientsPost,
    ApiToken,
    ApiVersion,
    ArrayConnectionKey,
    ArrayEncryption,
    ArrayEncryptionDataAtRest,
    ArrayEradicationConfig,
    BucketAccessPolicyPost,
    BucketAccessPolicyRulePost,
    BucketAccessPolicyRulePrincipal,
    BucketDefaults,
    BucketDefaultsReadonly,
    BucketEradicationConfig,
    BucketPatch,
    BucketPost,
    BucketReplicaLinkPost,
    BuiltIn,
    BuiltInNoId,
    BuiltInRelationship,
    Context,
    CrossOriginResourceSharingPolicyPatch,
    CrossOriginResourceSharingPolicyRulePost,
    Direction,
    DirectoryServiceManagement,
    DirectoryServiceNfs,
    DirectoryServiceRole,
    DirectoryServiceSmb,
    DnsPost,
    Eula,
    EulaSignature,
    FileLockRange,
    FileSystemEradicationConfig,
    FileSystemExportPost,
    FileSystemLockNlmReclamation,
    FileSystemOpenFile,
    FileSystemPost,
    FileSystemSnapshotPost,
    FixedReference,
    FixedReferenceNameOnly,
    FixedReferenceNoId,
    FixedReferenceNoResourceType,
    FleetKey,
    FleetMember,
    FleetMemberPost,
    FleetMemberPostMembers,
    FleetMemberPostMembersMember,
    FleetPatch,
    Group,
    Http,
    Index,
    KeytabFileBase64,
    KeytabFileBinary,
    KeytabPost,
    LegalHoldHeldEntity,
    LifecycleRuleConfigExtension,
    Linkaggregationgroup,
    Login,
    MaintenanceWindowPost,
    Member,
    MemberLink,
    MultiProtocol,
    MultiProtocolPost,
    NetworkInterfacePatch,
    NetworkInterfacePing,
    NetworkInterfaceTrace,
    NetworkInterfacesConnectorsSettingRoce,
    NetworkInterfacesConnectorsSettingRoceEcn,
    NetworkInterfacesConnectorsSettingRocePfc,
    Nfs,
    ObjectBacklog,
    ObjectLockConfigBase,
    ObjectStoreAccessKeyPost,
    ObjectStoreAccessPolicyPatch,
    ObjectStoreAccountPatch,
    ObjectStoreAccountPost,
    ObjectStoreRemoteCredentialsPost,
    ObjectStoreRemoteCredentialsResp,
    ObjectStoreRolePost,
    ObjectStoreTrustPolicyIam,
    OidcSsoPost,
    OidcSsoPostIdp,
    PageInfo,
    Permission,
    PolicyMember,
    PolicyRule,
    PolicyRuleIndex,
    PolicyRuleIndexInPolicy,
    PolicyRuleObjectAccessCondition,
    PolicyRuleObjectAccessPost,
    PublicAccessConfig,
    PublicKeyPost,
    RapidDataLocking,
    Reference,
    ReferenceNameOnly,
    ReferenceWritable,
    ReplicationPerformance,
    Resource,
    ResourceFixedNonUniqueName,
    Saml2SsoIdp,
    Saml2SsoPost,
    Saml2SsoSpCredential,
    ServerPost,
    Smb,
    SnmpAgentMib,
    SnmpManagerPost,
    SnmpV2c,
    SnmpV3,
    SnmpV3Post,
    SoftwareChecksChecks,
    Space,
    StartEndTime,
    SupportDiagnosticsSeverityCount,
    SupportRemoteAssistPaths,
    SyslogServerPostOrPatch,
    TargetPost,
    TestResult,
    Throttle,
    TimeWindow,
    TrustPolicyRuleCondition,
    TrustPolicyRulePost,
    User,
    UserNoId,
    VerificationKey,
    VerificationKeyPatch,
    Version,
    WormDataPolicyRetentionConfig,
    ActiveDirectory,
    ActiveDirectoryPatch,
    ActiveDirectoryPost,
    Admin,
    AdminCache,
    Alert,
    AlertWatcher,
    ApiClient,
    Array,
    ArrayConnection,
    ArrayConnectionPath,
    ArrayFactoryResetToken,
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
    BucketAccessPolicyRule,
    BucketAccessPolicyRuleBulkManage,
    BucketPerformance,
    BucketS3SpecificPerformance,
    BucketS3SpecificPerformanceGetResp,
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
    ContinuousReplicationPerformance,
    CrossOriginResourceSharingPolicyRule,
    CrossOriginResourceSharingPolicyRuleBulkManage,
    DirectoryService,
    Dns,
    Drive,
    FileInfo,
    FileLock,
    FileSession,
    FileSystem,
    FileSystemClient,
    FileSystemExport,
    FileSystemGroupPerformance,
    FileSystemPatch,
    FileSystemPerformance,
    FileSystemSnapshot,
    FileSystemSnapshotTransfer,
    FileSystemUserPerformance,
    FixedLocationReference,
    FixedReferenceWithIsLocal,
    FixedReferenceWithRemote,
    FixedReferenceWithType,
    Fleet,
    GroupQuota,
    GroupQuotaPost,
    Hardware,
    HardwareConnector,
    HardwareConnectorPerformance,
    Keytab,
    KmipServer,
    LegalHold,
    LifecycleRule,
    LifecycleRulePatch,
    LifecycleRulePost,
    LinkAggregationGroup,
    LocationReference,
    LogsAsync,
    MaintenanceWindow,
    NetworkAccessPolicyRuleBase,
    NetworkAccessPolicyRulePostBase,
    NetworkInterface,
    NetworkInterfacesConnectorsSetting,
    NfsExportPolicyRuleBase,
    NfsPatch,
    ObjectLockConfigRequestBody,
    ObjectStoreAccessKey,
    ObjectStoreAccessPolicyAction,
    ObjectStoreAccessPolicyPost,
    ObjectStoreAccount,
    ObjectStoreRemoteCredentialGetResp,
    ObjectStoreRemoteCredentials,
    ObjectStoreRole,
    ObjectStoreUser,
    ObjectStoreVirtualHost,
    OidcSso,
    OidcSsoPatch,
    PolicyBaseRenameable,
    PolicyFileSystemSnapshot,
    PolicyMemberContext,
    PolicyRuleObjectAccess,
    PolicyRuleObjectAccessBulkManage,
    PublicKey,
    PublicKeyUse,
    QuotaSetting,
    RelationshipPerformanceReplication,
    RemoteArray,
    ReplicaLinkBuiltIn,
    ResourcePerformanceReplication,
    Role,
    Saml2Sso,
    Saml2SsoSp,
    Server,
    Session,
    SmbClientPolicyRuleBase,
    SmbClientPolicyRulePostBase,
    SmbPost,
    SmbSharePolicyRule,
    SmbSharePolicyRulePost,
    SmtpServer,
    SnmpAgent,
    SnmpManager,
    SnmpManagerTest,
    SoftwareCheck,
    StorageClassInfo,
    StorageClassSpace,
    Subnet,
    Support,
    SupportDiagnostics,
    SupportDiagnosticsDetails,
    SyslogServerPatch,
    SyslogServerPost,
    SyslogServerSettings,
    Target,
    TimeZone,
    TrustPolicyRule,
    UserQuota,
    UserQuotaPost,
    ArrayConnectionPost,
    AuditFileSystemsPolicyNoContext,
    BucketAccessPolicyRuleWithContext,
    BucketReplicaLink,
    CrossOriginResourceSharingPolicyRuleWithContext,
    FileSystemReplicaLink,
    GroupQuotaPatch,
    NetworkAccessPolicy,
    NetworkAccessPolicyRule,
    NetworkAccessPolicyRuleInPolicy,
    NetworkAccessPolicyRulePost,
    NetworkInterfacesConnectorsPerformance,
    NfsExportPolicy,
    NfsExportPolicyRule,
    NfsExportPolicyRuleInPolicy,
    PasswordPolicy,
    PolicyBase,
    PolicyMemberWithRemote,
    QosPolicy,
    ServerContext,
    SmbClientPolicy,
    SmbClientPolicyRule,
    SmbClientPolicyRuleInPolicy,
    SmbClientPolicyRulePost,
    SmbClientPolicyRulePostInPolicy,
    SmbSharePolicy,
    SmbSharePolicyRuleWithContext,
    SyslogServer,
    TargetWithContext,
    TrustPolicyRuleWithContext,
    UserQuotaPatch,
    AuditFileSystemsPoliciesPatch,
    AuditFileSystemsPoliciesPost,
    AuditFileSystemsPolicy,
    BucketAccessPolicy,
    CrossOriginResourceSharingPolicy,
    NfsExportPolicyPost,
    ObjectStoreAccessPolicy,
    ObjectStoreTrustPolicy,
    Policy,
    PolicyBaseContext,
    SmbClientPolicyPost,
    SmbSharePolicyPost,
    SshCertificateAuthorityPolicyPost,
    SyslogServerContext,
    TlsPolicyPost,
    WormDataPolicy,
    PolicyPatch,
    SshCertificateAuthorityPolicy,
    TlsPolicy
]

if os.environ.get('DOCS_GENERATION') is None:
    add_all_properties()
