# coding: utf-8

"""
    FlashBlade REST API

    A lightweight client for FlashBlade REST API 2.17, developed by Pure Storage, Inc. (http://www.purestorage.com/). 

    OpenAPI spec version: 2.17
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re

import six
import typing

from ....properties import Property
if typing.TYPE_CHECKING:
    from pypureclient.flashblade.FB_2_17 import models

class NetworkInterfacesConnectorsSettingRoceEcn(object):
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'max_ecn_marked_threshold': 'int',
        'min_ecn_marked_threshold': 'int',
        'marking_probability': 'float'
    }

    attribute_map = {
        'max_ecn_marked_threshold': 'max_ecn_marked_threshold',
        'min_ecn_marked_threshold': 'min_ecn_marked_threshold',
        'marking_probability': 'marking_probability'
    }

    required_args = {
    }

    def __init__(
        self,
        max_ecn_marked_threshold=None,  # type: int
        min_ecn_marked_threshold=None,  # type: int
        marking_probability=None,  # type: float
    ):
        """
        Keyword args:
            max_ecn_marked_threshold (int): The maximum threshold value in bytes at which the packets start being marked with ECN at the highest probability or dropped. 
            min_ecn_marked_threshold (int): The minimum threshold value in bytes at which the packets start being marked with ECN. 
            marking_probability (float): The ECN marking probability when min ECN marked threshold is reached. 
        """
        if max_ecn_marked_threshold is not None:
            self.max_ecn_marked_threshold = max_ecn_marked_threshold
        if min_ecn_marked_threshold is not None:
            self.min_ecn_marked_threshold = min_ecn_marked_threshold
        if marking_probability is not None:
            self.marking_probability = marking_probability

    def __setattr__(self, key, value):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `NetworkInterfacesConnectorsSettingRoceEcn`".format(key))
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
        if issubclass(NetworkInterfacesConnectorsSettingRoceEcn, dict):
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
        if not isinstance(other, NetworkInterfacesConnectorsSettingRoceEcn):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
