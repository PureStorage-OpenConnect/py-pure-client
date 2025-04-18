# coding: utf-8

"""
    FlashBlade REST API

    A lightweight client for FlashBlade REST API 2.10, developed by Pure Storage, Inc. (http://www.purestorage.com/). 

    OpenAPI spec version: 2.10
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re

import six
import typing

from ....properties import Property
if typing.TYPE_CHECKING:
    from pypureclient.flashblade.FB_2_10 import models

class SmbSharePolicyRule(object):
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'name': 'str',
        'id': 'str',
        'principal': 'str',
        'full_control': 'str',
        'read': 'str',
        'change': 'str',
        'policy': 'FixedReference'
    }

    attribute_map = {
        'name': 'name',
        'id': 'id',
        'principal': 'principal',
        'full_control': 'full_control',
        'read': 'read',
        'change': 'change',
        'policy': 'policy'
    }

    required_args = {
    }

    def __init__(
        self,
        name=None,  # type: str
        id=None,  # type: str
        principal=None,  # type: str
        full_control=None,  # type: str
        read=None,  # type: str
        change=None,  # type: str
        policy=None,  # type: models.FixedReference
    ):
        """
        Keyword args:
            name (str): Name of the object (e.g., a file system or snapshot).
            id (str): A non-modifiable, globally unique ID chosen by the system. 
            principal (str): The user or group who is the subject of this rule, and their domain. If modifying this value, providing the domain is optional. If no domain is provided, it will be derived if possible. For example, `PURESTORAGE\\Administrator`, `samplegroup@PureStorage`, or `sampleuser`. 
            full_control (str): The state of the principal's Full Control access permission. Valid values are `allow` and `deny`. When not set, value is `null`. When allowed, includes all access granted by the Change permission. Users can also change the permissions for files and folders. When denied, these operations are explicitly blocked. If not set for any applicable rule on any applicable policy, acts as an implicit deny. If set to `allow`, implicitly sets the Change and Read permissions to `allow`. This is incompatible with explicitly setting any permission to `deny`. If set to `deny`, implicitly sets the Change and Read permissions to `deny`. This is incompatible with explicitly setting any permission to `allow`. If set to an empty string (`\"\"`), the value will be cleared. 
            read (str): The state of the principal's Read access permission. Valid values are `allow` and `deny`. When allowed, users can view file names, read the data in those files, and run some programs. When denied, these operations are explicitly blocked. If set to `allow`, implicitly clears the Full Control and Change permissions if they are currently `deny`. This is incompatible with explicitly setting any permission to `deny`. If set to `deny`, implicitly clears the Full Control and Change permissions if they are currently `allow`. This is incompatible with explicitly setting any permission to `allow`. 
            change (str): The state of the principal's Change access permission. Valid values are `allow` and `deny`. When not set, value is `null`. When allowed, includes all access granted by the Read permission. Users can also change data within files and add or delete files and folders. When denied, these operations are explicitly blocked. If not set for any applicable rule on any applicable policy, acts as an implicit deny. If set to `allow`, implicitly sets the Read permission to `allow`. This is incompatible with explicitly setting any permission to `deny`. If set to `deny`, implicitly sets the Read permission to `deny`, and clears the Full Control permission if it is currently `allow`. This is incompatible with explicitly setting any permission to `allow`. If set to an empty string (`\"\"`), the value (and implicitly the Full Control permission) will be cleared. This is incompatible with explicitly setting the Full Control permission to `allow` or `deny`. 
            policy (FixedReference): The policy to which this rule belongs.
        """
        if name is not None:
            self.name = name
        if id is not None:
            self.id = id
        if principal is not None:
            self.principal = principal
        if full_control is not None:
            self.full_control = full_control
        if read is not None:
            self.read = read
        if change is not None:
            self.change = change
        if policy is not None:
            self.policy = policy

    def __setattr__(self, key, value):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `SmbSharePolicyRule`".format(key))
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
        if issubclass(SmbSharePolicyRule, dict):
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
        if not isinstance(other, SmbSharePolicyRule):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
