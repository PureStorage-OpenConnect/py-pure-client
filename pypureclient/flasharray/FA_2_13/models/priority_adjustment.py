# coding: utf-8

"""
    FlashArray REST API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: 2.13
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re

import six
import typing

from ....properties import Property
if typing.TYPE_CHECKING:
    from pypureclient.flasharray.FA_2_13 import models

class PriorityAdjustment(object):
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'priority_adjustment_operator': 'str',
        'priority_adjustment_value': 'int'
    }

    attribute_map = {
        'priority_adjustment_operator': 'priority_adjustment_operator',
        'priority_adjustment_value': 'priority_adjustment_value'
    }

    required_args = {
    }

    def __init__(
        self,
        priority_adjustment_operator=None,  # type: str
        priority_adjustment_value=None,  # type: int
    ):
        """
        Keyword args:
            priority_adjustment_operator (str): Valid values are `+`, `-`, and `=`. The values `+` and `-` may be applied to volumes and volume groups to reflect the relative importance of their workloads. Volumes and volume groups can be assigned a priority adjustment of -10, 0, or +10. In addition, volumes can be assigned values of =-10, =0, or =+10. Volumes with settings of -10, 0, +10 can be modified by the priority adjustment setting of a volume group that contains the volume. However, if a volume has a priority adjustment set with the `=` operator (for example, =+10), it retains that value and is unaffected by any volume group priority adjustment settings.
            priority_adjustment_value (int): Adjust priority by the specified amount, using the `priority_adjustment_operator`. Valid values are 0 and +10 for `+` and `-` operators, -10, 0, and +10 for the `=` operator.
        """
        if priority_adjustment_operator is not None:
            self.priority_adjustment_operator = priority_adjustment_operator
        if priority_adjustment_value is not None:
            self.priority_adjustment_value = priority_adjustment_value

    def __setattr__(self, key, value):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `PriorityAdjustment`".format(key))
        self.__dict__[key] = value

    def __getattribute__(self, item):
        value = object.__getattribute__(self, item)
        if isinstance(value, Property):
            raise AttributeError
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
        if issubclass(PriorityAdjustment, dict):
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
        if not isinstance(other, PriorityAdjustment):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other