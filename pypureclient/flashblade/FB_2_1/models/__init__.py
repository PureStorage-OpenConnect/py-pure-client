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
from .active_directory_patch import ActiveDirectoryPatch
from .active_directory_post import ActiveDirectoryPost
from .active_directory_response import ActiveDirectoryResponse
from .admin_api_token import AdminApiToken
from .admin_api_token_response import AdminApiTokenResponse
from .admin_patch import AdminPatch
from .admin_response import AdminResponse
from .alert_response import AlertResponse
from .alert_watcher_post import AlertWatcherPost
from .alert_watcher_response import AlertWatcherResponse
from .api_clients_post import ApiClientsPost
from .api_clients_response import ApiClientsResponse
from .api_token import ApiToken
from .api_version import ApiVersion
from .array_connection_key import ArrayConnectionKey
from .array_connection_key_response import ArrayConnectionKeyResponse
from .array_connection_response import ArrayConnectionResponse
from .array_factory_reset_token_response import ArrayFactoryResetTokenResponse
from .array_response import ArrayResponse
from .audit_response import AuditResponse
from .bucket_post import BucketPost
from .bucket_replica_link_post import BucketReplicaLinkPost
from .bucket_replica_link_response import BucketReplicaLinkResponse
from .bucket_response import BucketResponse
from .built_in import BuiltIn
from .built_in_no_id import BuiltInNoId
from .built_in_relationship import BuiltInRelationship
from .certificate_certificate_group_response import CertificateCertificateGroupResponse
from .certificate_group_certificate_response import CertificateGroupCertificateResponse
from .certificate_group_response import CertificateGroupResponse
from .certificate_response import CertificateResponse
from .direction import Direction
from .directory_service_management import DirectoryServiceManagement
from .directory_service_nfs import DirectoryServiceNfs
from .directory_service_response import DirectoryServiceResponse
from .directory_service_role import DirectoryServiceRole
from .directory_service_roles_response import DirectoryServiceRolesResponse
from .directory_service_smb import DirectoryServiceSmb
from .dns_response import DnsResponse
from .eula import Eula
from .eula_response import EulaResponse
from .eula_signature import EulaSignature
from .file_system_groups_performance_get_response import FileSystemGroupsPerformanceGetResponse
from .file_system_post import FileSystemPost
from .file_system_replica_link_response import FileSystemReplicaLinkResponse
from .file_system_response import FileSystemResponse
from .file_system_snapshot_post import FileSystemSnapshotPost
from .file_system_snapshot_response import FileSystemSnapshotResponse
from .file_system_snapshot_transfer_response import FileSystemSnapshotTransferResponse
from .file_system_users_performance_get_response import FileSystemUsersPerformanceGetResponse
from .fixed_reference import FixedReference
from .fixed_reference_name_only import FixedReferenceNameOnly
from .fixed_reference_no_resource_type import FixedReferenceNoResourceType
from .group import Group
from .group_quota_response import GroupQuotaResponse
from .hardware_connector_response import HardwareConnectorResponse
from .hardware_response import HardwareResponse
from .http import Http
from .inline_response400 import InlineResponse400
from .inline_response401 import InlineResponse401
from .keytab_file_base64 import KeytabFileBase64
from .keytab_file_binary import KeytabFileBinary
from .keytab_file_response import KeytabFileResponse
from .keytab_post import KeytabPost
from .keytab_response import KeytabResponse
from .kmip_server_response import KmipServerResponse
from .lifecycle_rule_config_extension import LifecycleRuleConfigExtension
from .lifecycle_rule_response import LifecycleRuleResponse
from .link_aggregation_group_response import LinkAggregationGroupResponse
from .linkaggregationgroup import Linkaggregationgroup
from .login import Login
from .login_banner_get_response import LoginBannerGetResponse
from .member import Member
from .member_link import MemberLink
from .multi_protocol import MultiProtocol
from .multi_protocol_post import MultiProtocolPost
from .network_interface_patch import NetworkInterfacePatch
from .network_interface_response import NetworkInterfaceResponse
from .nfs import Nfs
from .oauth_token_response import OauthTokenResponse
from .object_store_access_key_post import ObjectStoreAccessKeyPost
from .object_store_access_key_response import ObjectStoreAccessKeyResponse
from .object_store_access_policies_response import ObjectStoreAccessPoliciesResponse
from .object_store_account_response import ObjectStoreAccountResponse
from .object_store_remote_credentials_post import ObjectStoreRemoteCredentialsPost
from .object_store_remote_credentials_resp import ObjectStoreRemoteCredentialsResp
from .object_store_user_response import ObjectStoreUserResponse
from .object_store_virtual_host_response import ObjectStoreVirtualHostResponse
from .page_info import PageInfo
from .permission import Permission
from .policy_file_system_snapshot_response import PolicyFileSystemSnapshotResponse
from .policy_member import PolicyMember
from .policy_member_response import PolicyMemberResponse
from .policy_member_with_remote_response import PolicyMemberWithRemoteResponse
from .policy_response import PolicyResponse
from .policy_rule import PolicyRule
from .quota_setting_response import QuotaSettingResponse
from .rapid_data_locking import RapidDataLocking
from .rapid_data_locking_response import RapidDataLockingResponse
from .reference import Reference
from .reference_writable import ReferenceWritable
from .replication_performance import ReplicationPerformance
from .resource import Resource
from .smb import Smb
from .smtp_server_response import SmtpServerResponse
from .snmp_agent_mib import SnmpAgentMib
from .snmp_agent_mib_response import SnmpAgentMibResponse
from .snmp_agent_response import SnmpAgentResponse
from .snmp_manager_post import SnmpManagerPost
from .snmp_manager_response import SnmpManagerResponse
from .snmp_v2c import SnmpV2c
from .snmp_v3 import SnmpV3
from .snmp_v3_post import SnmpV3Post
from .space import Space
from .subnet_response import SubnetResponse
from .support_remote_assist_paths import SupportRemoteAssistPaths
from .support_response import SupportResponse
from .syslog_server_post_or_patch import SyslogServerPostOrPatch
from .syslog_server_response import SyslogServerResponse
from .syslog_server_settings_response import SyslogServerSettingsResponse
from .target_post import TargetPost
from .target_response import TargetResponse
from .test_result import TestResult
from .test_result_response import TestResultResponse
from .user import User
from .user_quota_response import UserQuotaResponse
from .active_directory import ActiveDirectory
from .active_directory_get_response import ActiveDirectoryGetResponse
from .admin import Admin
from .admin_api_token_get_response import AdminApiTokenGetResponse
from .admin_cache import AdminCache
from .admin_cache_get_response import AdminCacheGetResponse
from .admin_get_response import AdminGetResponse
from .alert import Alert
from .alert_get_response import AlertGetResponse
from .alert_watcher import AlertWatcher
from .alert_watcher_get_response import AlertWatcherGetResponse
from .api_client import ApiClient
from .array import Array
from .array_connection import ArrayConnection
from .array_connection_get_response import ArrayConnectionGetResponse
from .array_connection_key_get_response import ArrayConnectionKeyGetResponse
from .array_connection_path import ArrayConnectionPath
from .array_connection_path_get_response import ArrayConnectionPathGetResponse
from .array_factory_reset_token import ArrayFactoryResetToken
from .array_factory_reset_token_get_response import ArrayFactoryResetTokenGetResponse
from .array_get_response import ArrayGetResponse
from .array_http_specific_performance import ArrayHttpSpecificPerformance
from .array_http_specific_performance_get import ArrayHttpSpecificPerformanceGet
from .array_nfs_specific_performance import ArrayNfsSpecificPerformance
from .array_nfs_specific_performance_get import ArrayNfsSpecificPerformanceGet
from .array_performance import ArrayPerformance
from .array_performance_get_response import ArrayPerformanceGetResponse
from .array_performance_replication_get_resp import ArrayPerformanceReplicationGetResp
from .array_s3_specific_performance import ArrayS3SpecificPerformance
from .array_s3_specific_performance_get_resp import ArrayS3SpecificPerformanceGetResp
from .array_space import ArraySpace
from .array_space_get_response import ArraySpaceGetResponse
from .arrays_supported_time_zones_get_response import ArraysSupportedTimeZonesGetResponse
from .audit import Audit
from .audit_get_response import AuditGetResponse
from .blade import Blade
from .blade_get_response import BladeGetResponse
from .bucket import Bucket
from .bucket_get_response import BucketGetResponse
from .bucket_performance import BucketPerformance
from .bucket_performance_get_response import BucketPerformanceGetResponse
from .bucket_replica_link_get_response import BucketReplicaLinkGetResponse
from .bucket_s3_specific_performance import BucketS3SpecificPerformance
from .bucket_s3_specific_performance_get_resp import BucketS3SpecificPerformanceGetResp
from .certificate import Certificate
from .certificate_certificate_group_get_resp import CertificateCertificateGroupGetResp
from .certificate_get_response import CertificateGetResponse
from .certificate_group import CertificateGroup
from .certificate_group_certificate_get_resp import CertificateGroupCertificateGetResp
from .certificate_group_get_response import CertificateGroupGetResponse
from .certificate_group_use import CertificateGroupUse
from .certificate_group_use_get_response import CertificateGroupUseGetResponse
from .certificate_patch import CertificatePatch
from .certificate_post import CertificatePost
from .certificate_use import CertificateUse
from .certificate_use_get_response import CertificateUseGetResponse
from .client_performance import ClientPerformance
from .client_performance_get_response import ClientPerformanceGetResponse
from .connection_relationship_performance_replication import ConnectionRelationshipPerformanceReplication
from .connection_relationship_performance_replication_get_resp import ConnectionRelationshipPerformanceReplicationGetResp
from .directory_service import DirectoryService
from .directory_service_get_response import DirectoryServiceGetResponse
from .directory_service_roles_get_response import DirectoryServiceRolesGetResponse
from .dns import Dns
from .dns_get_response import DnsGetResponse
from .eula_get_response import EulaGetResponse
from .file_system import FileSystem
from .file_system_get_response import FileSystemGetResponse
from .file_system_group_performance import FileSystemGroupPerformance
from .file_system_patch import FileSystemPatch
from .file_system_performance import FileSystemPerformance
from .file_system_performance_get_response import FileSystemPerformanceGetResponse
from .file_system_replica_link_get_response import FileSystemReplicaLinkGetResponse
from .file_system_snapshot import FileSystemSnapshot
from .file_system_snapshot_get_response import FileSystemSnapshotGetResponse
from .file_system_snapshot_get_transfer_response import FileSystemSnapshotGetTransferResponse
from .file_system_snapshot_transfer import FileSystemSnapshotTransfer
from .file_system_user_performance import FileSystemUserPerformance
from .fixed_location_reference import FixedLocationReference
from .fixed_reference_with_remote import FixedReferenceWithRemote
from .group_quota import GroupQuota
from .group_quota_get_response import GroupQuotaGetResponse
from .group_quota_post import GroupQuotaPost
from .hardware import Hardware
from .hardware_connector import HardwareConnector
from .hardware_connector_get_response import HardwareConnectorGetResponse
from .hardware_get_response import HardwareGetResponse
from .keytab import Keytab
from .keytab_get_response import KeytabGetResponse
from .kmip_server import KmipServer
from .lifecycle_rule import LifecycleRule
from .lifecycle_rule_get_response import LifecycleRuleGetResponse
from .lifecycle_rule_patch import LifecycleRulePatch
from .lifecycle_rule_post import LifecycleRulePost
from .link_aggregation_group import LinkAggregationGroup
from .link_aggregation_group_get_response import LinkAggregationGroupGetResponse
from .location_reference import LocationReference
from .network_interface import NetworkInterface
from .network_interface_get_response import NetworkInterfaceGetResponse
from .nfs_patch import NfsPatch
from .object_store_access_key import ObjectStoreAccessKey
from .object_store_access_key_get_response import ObjectStoreAccessKeyGetResponse
from .object_store_access_policies_get_response import ObjectStoreAccessPoliciesGetResponse
from .object_store_access_policy import ObjectStoreAccessPolicy
from .object_store_account import ObjectStoreAccount
from .object_store_account_get_response import ObjectStoreAccountGetResponse
from .object_store_remote_credential_get_resp import ObjectStoreRemoteCredentialGetResp
from .object_store_remote_credentials import ObjectStoreRemoteCredentials
from .object_store_user import ObjectStoreUser
from .object_store_user_get_response import ObjectStoreUserGetResponse
from .object_store_virtual_host import ObjectStoreVirtualHost
from .object_store_virtual_host_get_response import ObjectStoreVirtualHostGetResponse
from .policy import Policy
from .policy_file_system_snapshot import PolicyFileSystemSnapshot
from .policy_file_system_snapshot_get_response import PolicyFileSystemSnapshotGetResponse
from .policy_get_response import PolicyGetResponse
from .policy_member_get_response import PolicyMemberGetResponse
from .policy_member_with_remote_get_response import PolicyMemberWithRemoteGetResponse
from .quota_setting import QuotaSetting
from .quota_setting_get_response import QuotaSettingGetResponse
from .relationship_performance_replication import RelationshipPerformanceReplication
from .replica_link_built_in import ReplicaLinkBuiltIn
from .resource_performance_replication import ResourcePerformanceReplication
from .resource_performance_replication_get_response import ResourcePerformanceReplicationGetResponse
from .role import Role
from .role_get_response import RoleGetResponse
from .smtp_server import SmtpServer
from .smtp_server_get_response import SmtpServerGetResponse
from .snmp_agent import SnmpAgent
from .snmp_agent_get_response import SnmpAgentGetResponse
from .snmp_manager import SnmpManager
from .snmp_manager_get_response import SnmpManagerGetResponse
from .snmp_manager_test import SnmpManagerTest
from .subnet import Subnet
from .subnet_get_response import SubnetGetResponse
from .support import Support
from .support_get_response import SupportGetResponse
from .syslog_server import SyslogServer
from .syslog_server_get_response import SyslogServerGetResponse
from .syslog_server_settings import SyslogServerSettings
from .syslog_server_settings_get_response import SyslogServerSettingsGetResponse
from .target import Target
from .target_get_response import TargetGetResponse
from .test_result_get_response import TestResultGetResponse
from .time_zone import TimeZone
from .user_quota import UserQuota
from .user_quota_get_response import UserQuotaGetResponse
from .user_quota_post import UserQuotaPost
from .array_connection_post import ArrayConnectionPost
from .bucket_replica_link import BucketReplicaLink
from .file_system_replica_link import FileSystemReplicaLink
from .group_quota_patch import GroupQuotaPatch
from .policy_member_with_remote import PolicyMemberWithRemote
from .policy_patch import PolicyPatch
from .user_quota_patch import UserQuotaPatch
