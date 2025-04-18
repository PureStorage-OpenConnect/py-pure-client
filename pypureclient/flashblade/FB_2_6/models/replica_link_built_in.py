# coding: utf-8

"""
    FlashBlade REST API

    A lightweight client for FlashBlade REST API 2.6, developed by Pure Storage, Inc. (http://www.purestorage.com/). 

    OpenAPI spec version: 2.6
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re

import six
import typing

from ....properties import Property
if typing.TYPE_CHECKING:
    from pypureclient.flashblade.FB_2_6 import models

class ReplicaLinkBuiltIn(object):
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'id': 'str',
        'lag': 'int',
        'status_details': 'str',
        'direction': 'Direction'
    }

    attribute_map = {
        'id': 'id',
        'lag': 'lag',
        'status_details': 'status_details',
        'direction': 'direction'
    }

    required_args = {
    }

    def __init__(
        self,
        id=None,  # type: str
        lag=None,  # type: int
        status_details=None,  # type: str
        direction=None,  # type: models.Direction
    ):
        """
        Keyword args:
            id (str): A non-modifiable, globally unique ID chosen by the system. 
            lag (int): Duration in milliseconds that represents how far behind the replication target is from the source. This is the time difference between current time and `recovery_point`. 
            status_details (str): Detailed information about the status of the replica link when it is unhealthy. 
            direction (Direction)
        """
        if id is not None:
            self.id = id
        if lag is not None:
            self.lag = lag
        if status_details is not None:
            self.status_details = status_details
        if direction is not None:
            self.direction = direction

    def __setattr__(self, key, value):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `ReplicaLinkBuiltIn`".format(key))
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
        if issubclass(ReplicaLinkBuiltIn, dict):
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
        if not isinstance(other, ReplicaLinkBuiltIn):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
