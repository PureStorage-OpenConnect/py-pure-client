from __future__ import absolute_import
import os

from .client import Client
from ..exceptions import PureError
from ..properties import Property, Filter
from ..responses import ValidResponse, ErrorResponse, ApiError, ResponseHeaders

from .models.alert import Alert
from .models.array import Array
from .models.audit import Audit
from .models.error import Error
from .models.error_errors import ErrorErrors
from .models.error_no_context import ErrorNoContext
from .models.file_system import FileSystem
from .models.file_system_snapshot import FileSystemSnapshot
from .models.fixed_reference import FixedReference
from .models.http import Http
from .models.metric import Metric
from .models.metric_availability import MetricAvailability
from .models.metric_history import MetricHistory
from .models.network_interface import NetworkInterface
from .models.nfs import Nfs
from .models.pod import Pod
from .models.pod_array_status import PodArrayStatus
from .models.policy import Policy
from .models.policy_member import PolicyMember
from .models.policy_rule import PolicyRule
from .models.smb import Smb
from .models.tag import Tag
from .models.tag_put import TagPut
from .models.volume import Volume
from .models.volume_snapshot import VolumeSnapshot


def add_properties(model):
    for name, value in model.attribute_map.items():
        setattr(model, name, Property(value))


CLASSES_TO_ADD_PROPS = [
    Alert,
    Array,
    Audit,
    Error,
    ErrorErrors,
    ErrorNoContext,
    FileSystem,
    FileSystemSnapshot,
    FixedReference,
    Http,
    Metric,
    MetricAvailability,
    MetricHistory,
    NetworkInterface,
    Nfs,
    Pod,
    PodArrayStatus,
    Policy,
    PolicyMember,
    PolicyRule,
    Smb,
    Tag,
    TagPut,
    Volume,
    VolumeSnapshot
]

if os.environ.get('DOCS_GENERATION') is None:
    for model in CLASSES_TO_ADD_PROPS:
        add_properties(model)
