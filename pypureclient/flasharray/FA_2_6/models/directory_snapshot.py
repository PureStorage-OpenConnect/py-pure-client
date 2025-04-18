# coding: utf-8

"""
    FlashArray REST API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: 2.6
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re

import six
import typing

from ....properties import Property
if typing.TYPE_CHECKING:
    from pypureclient.flasharray.FA_2_6 import models

class DirectorySnapshot(object):
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
        'time_remaining': 'int',
        'destroyed': 'bool',
        'created': 'int',
        'source': 'FixedReference',
        'suffix': 'int',
        'client_name': 'str',
        'space': 'Space',
        'policy': 'FixedReference'
    }

    attribute_map = {
        'name': 'name',
        'id': 'id',
        'time_remaining': 'time_remaining',
        'destroyed': 'destroyed',
        'created': 'created',
        'source': 'source',
        'suffix': 'suffix',
        'client_name': 'client_name',
        'space': 'space',
        'policy': 'policy'
    }

    required_args = {
    }

    def __init__(
        self,
        name=None,  # type: str
        id=None,  # type: str
        time_remaining=None,  # type: int
        destroyed=None,  # type: bool
        created=None,  # type: int
        source=None,  # type: models.FixedReference
        suffix=None,  # type: int
        client_name=None,  # type: str
        space=None,  # type: models.Space
        policy=None,  # type: models.FixedReference
    ):
        """
        Keyword args:
            name (str): A user-specified name. The name must be locally unique and can be changed. 
            id (str): A globally unique, system-generated ID. The ID cannot be modified and cannot refer to another resource. 
            time_remaining (int): The amount of time left until the directory snapshot is permanently eradicated. Measured in milliseconds. Before the `time_remaining` period has elapsed, the snapshot can be recovered by setting `destroyed=false` if it is destroyed, by setting `policy=\"\"` if it is managed by a snapshot policy, or by setting `keep_for=\"\" ` if it is a manual snapshot. 
            destroyed (bool): Returns a value of `true` if the snapshot has been destroyed and is pending eradication. The `time_remaining` value displays the amount of time left until the destroyed directory snapshot is permanently eradicated. Before the `time_remaining` period has elapsed, the destroyed directory snapshot can be recovered by setting `destroyed=false`.  Once the `time_remaining` period has elapsed, the directory snapshot is permanently eradicated and can no longer be recovered. 
            created (int): The snapshot creation time, measured in milliseconds since the UNIX epoch. 
            source (FixedReference): The directory from which this snapshot was taken. 
            suffix (int): The suffix that is appended to the `source_name` value and the `client_name` value to generate the full directory snapshot name in the form of `DIR.CLIENT_NAME.SUFFIX` where `DIR` is the managed directory name, `CLIENT_NAME` is the client name, and `SUFFIX` is the suffix. If the suffix is a string, this field returns `null`. See the `name` value for the full snapshot name including the suffix. 
            client_name (str): The customizable portion of the client visible snapshot name. A full snapshot name is constructed in the form of `DIR.CLIENT_NAME.SUFFIX` where `DIR` is the full managed directory name, `CLIENT_NAME` is the client name, and `SUFFIX` is the suffix. The client visible snapshot name is `CLIENT_NAME.SUFFIX`. 
            space (Space): Displays size and space consumption information. 
            policy (FixedReference): The snapshot policy that manages this snapshot, if applicable. 
        """
        if name is not None:
            self.name = name
        if id is not None:
            self.id = id
        if time_remaining is not None:
            self.time_remaining = time_remaining
        if destroyed is not None:
            self.destroyed = destroyed
        if created is not None:
            self.created = created
        if source is not None:
            self.source = source
        if suffix is not None:
            self.suffix = suffix
        if client_name is not None:
            self.client_name = client_name
        if space is not None:
            self.space = space
        if policy is not None:
            self.policy = policy

    def __setattr__(self, key, value):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `DirectorySnapshot`".format(key))
        self.__dict__[key] = value

    def __getattribute__(self, item):
        value = object.__getattribute__(self, item)
        if isinstance(value, Property):
            raise AttributeError
        else:
            return value

    def __getitem__(self, key):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `DirectorySnapshot`".format(key))
        return object.__getattribute__(self, key)

    def __setitem__(self, key, value):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `DirectorySnapshot`".format(key))
        object.__setattr__(self, key, value)

    def __delitem__(self, key):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `DirectorySnapshot`".format(key))
        object.__delattr__(self, key)

    def keys(self):
        return self.attribute_map.keys()

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
        if issubclass(DirectorySnapshot, dict):
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
        if not isinstance(other, DirectorySnapshot):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
