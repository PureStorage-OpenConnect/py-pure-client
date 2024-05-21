# coding: utf-8

"""
    FlashBlade REST API

    A lightweight client for FlashBlade REST API 2.13, developed by Pure Storage, Inc. (http://www.purestorage.com/).

    OpenAPI spec version: 2.13
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re

import six
import typing

from ....properties import Property
if typing.TYPE_CHECKING:
    from pypureclient.flashblade.FB_2_13 import models

class Space(object):
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'data_reduction': 'float',
        'snapshots': 'int',
        'total_physical': 'int',
        'unique': 'int',
        'virtual': 'int',
        'total_provisioned': 'int',
        'available_provisioned': 'int',
        'available_ratio': 'float',
        'destroyed': 'int',
        'destroyed_virtual': 'int'
    }

    attribute_map = {
        'data_reduction': 'data_reduction',
        'snapshots': 'snapshots',
        'total_physical': 'total_physical',
        'unique': 'unique',
        'virtual': 'virtual',
        'total_provisioned': 'total_provisioned',
        'available_provisioned': 'available_provisioned',
        'available_ratio': 'available_ratio',
        'destroyed': 'destroyed',
        'destroyed_virtual': 'destroyed_virtual'
    }

    required_args = {
    }

    def __init__(
        self,
        data_reduction=None,  # type: float
        snapshots=None,  # type: int
        total_physical=None,  # type: int
        unique=None,  # type: int
        virtual=None,  # type: int
        total_provisioned=None,  # type: int
        available_provisioned=None,  # type: int
        available_ratio=None,  # type: float
        destroyed=None,  # type: int
        destroyed_virtual=None,  # type: int
    ):
        """
        Keyword args:
            data_reduction (float): Reduction of data.
            snapshots (int): Physical usage by snapshots, other than unique in bytes.
            total_physical (int): Total physical usage (including snapshots) in bytes.
            unique (int): Unique physical space occupied by customer data, in bytes. Excludes snapshots, destroyed.
            virtual (int): The amount of logically written data, in bytes. Excludes destroyed data.
            total_provisioned (int): The effective provisioned size of the container, at which a hard limit will be applied. For a bucket with a `quota_limit` value and `hard_limit_enabled` set to `true`, this is its `quota_limit` value, unless the available space of the associated object store account, as defined by its `quota_limit` value, would prevent the bucket from reaching its own `quota_limit` value. In such a case, `total_provisioned` will reflect the smaller value. For a file system with a `provisioned` value and `hard_limit_enabled` set to `true`, this is the `provisioned` value of the file system. For an object store account with a `quota_limit` value and `hard_limit_enabled` set to `true`, this is the `quota_limit` value of the object store account. For the array, this is the sum of the file systems and accounts. Measured in bytes.
            available_provisioned (int): The amount of space left that the current object can grow before writes are stopped due to a hard limit quota being hit. This is total_provisioned minus the virtual space used for file-systems and buckets. For array and object store accounts it is total_provisioned minus the virtual space used by non-destroyed file-systems and buckets.
            available_ratio (float): The ratio of the available space versus the total provisioned space.
            destroyed (int): Unique physical space (excluding snapshots) occupied by destroyed data within the child containers, in bytes. For buckets and filesystems, the destroyed space will be 0 as they cannot have child containers. For the whole array, the space will be the sum of all destroyed buckets and filesystems.
            destroyed_virtual (int): The amount of destroyed logically written data within the child containers, in bytes. For buckets and filesystems, the destroyed virtual space will be 0 as they cannot have child containers. For the whole array, the space will be the sum of all destroyed buckets and filesystems.
        """
        if data_reduction is not None:
            self.data_reduction = data_reduction
        if snapshots is not None:
            self.snapshots = snapshots
        if total_physical is not None:
            self.total_physical = total_physical
        if unique is not None:
            self.unique = unique
        if virtual is not None:
            self.virtual = virtual
        if total_provisioned is not None:
            self.total_provisioned = total_provisioned
        if available_provisioned is not None:
            self.available_provisioned = available_provisioned
        if available_ratio is not None:
            self.available_ratio = available_ratio
        if destroyed is not None:
            self.destroyed = destroyed
        if destroyed_virtual is not None:
            self.destroyed_virtual = destroyed_virtual

    def __setattr__(self, key, value):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `Space`".format(key))
        if key == "total_provisioned" and value is not None:
            if value < 0:
                raise ValueError("Invalid value for `total_provisioned`, must be a value greater than or equal to `0`")
        if key == "available_provisioned" and value is not None:
            if value < 0:
                raise ValueError("Invalid value for `available_provisioned`, must be a value greater than or equal to `0`")
        if key == "available_ratio" and value is not None:
            if value > 1.0:
                raise ValueError("Invalid value for `available_ratio`, value must be less than or equal to `1.0`")
            if value < 0.0:
                raise ValueError("Invalid value for `available_ratio`, must be a value greater than or equal to `0.0`")
        self.__dict__[key] = value

    def __getattribute__(self, item):
        value = object.__getattribute__(self, item)
        if isinstance(value, Property):
            return None
        else:
            return value

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            if hasattr(self, attr):
                value = getattr(self, attr)
                if isinstance(value, list):
                    result[attr] = list(map(
                        lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                        value
                    ))
                elif hasattr(value, "to_dict"):
                    result[attr] = value.to_dict()
                elif isinstance(value, dict):
                    result[attr] = dict(map(
                        lambda item: (item[0], item[1].to_dict())
                        if hasattr(item[1], "to_dict") else item,
                        value.items()
                    ))
                else:
                    result[attr] = value
        if issubclass(Space, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Space):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other