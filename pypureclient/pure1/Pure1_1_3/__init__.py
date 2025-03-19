from __future__ import absolute_import
import os

from .client import Client
from ...exceptions import PureError
from ...properties import Property, Filter
from ...responses import ValidResponse, ErrorResponse, ApiError, ResponseHeaders

from .models.asset_org import AssetOrg
from .models.asset_space import AssetSpace
from .models.base_address import BaseAddress
from .models.current_metric import CurrentMetric
from .models.error import Error
from .models.error_errors import ErrorErrors
from .models.error_no_context import ErrorNoContext
from .models.fixed_reference import FixedReference
from .models.geolocation import Geolocation
from .models.http import Http
from .models.install_address import InstallAddress
from .models.invoice import Invoice
from .models.invoice_line import InvoiceLine
from .models.invoice_line_component import InvoiceLineComponent
from .models.marketplace_partner import MarketplacePartner
from .models.metric_availability import MetricAvailability
from .models.nfs import Nfs
from .models.policy_rule import PolicyRule
from .models.smb import Smb
from .models.subscription_asset_array import SubscriptionAssetArray
from .models.subscription_asset_array_advanced_space import SubscriptionAssetArrayAdvancedSpace
from .models.support_contract import SupportContract
from .models.tag import Tag
from .models.tag_put import TagPut
from .models.tax import Tax
from .models.time_interval import TimeInterval
from .models.asset_address import AssetAddress
from .models.asset_space_total_used_ratio import AssetSpaceTotalUsedRatio
from .models.blade_array_status import BladeArrayStatus
from .models.drive_array_status import DriveArrayStatus
from .models.fixed_reference_fqdn import FixedReferenceFqdn
from .models.policy_member import PolicyMember
from .models.resource import Resource
from .models.resource_no_name import ResourceNoName
from .models.resource_with_location import ResourceWithLocation
from .models.resource_with_locations import ResourceWithLocations
from .models.subscription_license_pre_ratio import SubscriptionLicensePreRatio
from .models.sustainability_assessment import SustainabilityAssessment
from .models.sustainability_insight_array import SustainabilityInsightArray
from .models.array import Array
from .models.blade import Blade
from .models.drive import Drive
from .models.license_resource_reference import LicenseResourceReference
from .models.metric import Metric
from .models.metric_history import MetricHistory
from .models.replica_link import ReplicaLink
from .models.subscription import Subscription
from .models.subscription_asset import SubscriptionAsset
from .models.subscription_license import SubscriptionLicense
from .models.sustainability_array import SustainabilityArray
from .models.alert import Alert
from .models.audit import Audit
from .models.bucket import Bucket
from .models.bucket_replica_link import BucketReplicaLink
from .models.controller import Controller
from .models.directory import Directory
from .models.file_system import FileSystem
from .models.file_system_replica_link import FileSystemReplicaLink
from .models.file_system_snapshot import FileSystemSnapshot
from .models.hardware import Hardware
from .models.hardware_connector import HardwareConnector
from .models.network_interface import NetworkInterface
from .models.object_store_account import ObjectStoreAccount
from .models.pod import Pod
from .models.pod_replica_link import PodReplicaLink
from .models.policy import Policy
from .models.port import Port
from .models.target import Target
from .models.volume import Volume
from .models.volume_snapshot import VolumeSnapshot


def add_properties(model):
    for name, value in model.attribute_map.items():
        setattr(model, name, Property(value))


def add_all_properties():
    for model in CLASSES_TO_ADD_PROPS:
        add_properties(model)


CLASSES_TO_ADD_PROPS = [
    AssetOrg,
    AssetSpace,
    BaseAddress,
    CurrentMetric,
    Error,
    ErrorErrors,
    ErrorNoContext,
    FixedReference,
    Geolocation,
    Http,
    InstallAddress,
    Invoice,
    InvoiceLine,
    InvoiceLineComponent,
    MarketplacePartner,
    MetricAvailability,
    Nfs,
    PolicyRule,
    Smb,
    SubscriptionAssetArray,
    SubscriptionAssetArrayAdvancedSpace,
    SupportContract,
    Tag,
    TagPut,
    Tax,
    TimeInterval,
    AssetAddress,
    AssetSpaceTotalUsedRatio,
    BladeArrayStatus,
    DriveArrayStatus,
    FixedReferenceFqdn,
    PolicyMember,
    Resource,
    ResourceNoName,
    ResourceWithLocation,
    ResourceWithLocations,
    SubscriptionLicensePreRatio,
    SustainabilityAssessment,
    SustainabilityInsightArray,
    Array,
    Blade,
    Drive,
    LicenseResourceReference,
    Metric,
    MetricHistory,
    ReplicaLink,
    Subscription,
    SubscriptionAsset,
    SubscriptionLicense,
    SustainabilityArray,
    Alert,
    Audit,
    Bucket,
    BucketReplicaLink,
    Controller,
    Directory,
    FileSystem,
    FileSystemReplicaLink,
    FileSystemSnapshot,
    Hardware,
    HardwareConnector,
    NetworkInterface,
    ObjectStoreAccount,
    Pod,
    PodReplicaLink,
    Policy,
    Port,
    Target,
    Volume,
    VolumeSnapshot
]

if os.environ.get('DOCS_GENERATION') is None:
    add_all_properties()
