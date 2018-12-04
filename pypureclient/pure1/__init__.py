# coding: utf-8
# flake8: noqa


from __future__ import absolute_import

from pypureclient.pure1.client import Client
from pypureclient.pure1.exceptions import PureError
from pypureclient.pure1.properties import Property, Filter
from pypureclient.pure1.responses import ValidResponse, ErrorResponse, ApiError, Pure1Headers

from pypureclient.pure1.models.array import Array
from pypureclient.pure1.models.file_system import FileSystem
from pypureclient.pure1.models.file_system_snapshot import FileSystemSnapshot
from pypureclient.pure1.models.fixed_reference import FixedReference
from pypureclient.pure1.models.http import Http
from pypureclient.pure1.models.metric import Metric
from pypureclient.pure1.models.metric_availability import MetricAvailability
from pypureclient.pure1.models.metric_history import MetricHistory
from pypureclient.pure1.models.network_interface import NetworkInterface
from pypureclient.pure1.models.nfs import Nfs
from pypureclient.pure1.models.pod import Pod
from pypureclient.pure1.models.pod_array_status import PodArrayStatus
from pypureclient.pure1.models.smb import Smb
from pypureclient.pure1.models.tag import Tag
from pypureclient.pure1.models.volume import Volume
from pypureclient.pure1.models.volume_snapshot import VolumeSnapshot


def addProperties(model):
    for name, value in model.attribute_map.items():
        setattr(model, name, Property(value))

CLASSES_TO_ADD_PROPS = [Array, FileSystem, FileSystemSnapshot, Http, Metric,
                        MetricAvailability, MetricHistory, NetworkInterface, Nfs,
                        Pod, PodArrayStatus, Smb, Tag, Volume, VolumeSnapshot]

for model in CLASSES_TO_ADD_PROPS:
    addProperties(model)
