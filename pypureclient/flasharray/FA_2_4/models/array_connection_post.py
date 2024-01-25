# coding: utf-8

"""
    FlashArray REST API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: 2.4
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re

import six
import typing

from ....properties import Property
if typing.TYPE_CHECKING:
    from pypureclient.flasharray.FA_2_4 import models

class ArrayConnectionPost(object):
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'management_address': 'str',
        'replication_addresses': 'list[str]',
        'type': 'str',
        'replication_transport': 'str',
        'connection_key': 'str'
    }

    attribute_map = {
        'management_address': 'management_address',
        'replication_addresses': 'replication_addresses',
        'type': 'type',
        'replication_transport': 'replication_transport',
        'connection_key': 'connection_key'
    }

    required_args = {
    }

    def __init__(
        self,
        management_address=None,  # type: str
        replication_addresses=None,  # type: List[str]
        type=None,  # type: str
        replication_transport=None,  # type: str
        connection_key=None,  # type: str
    ):
        """
        Keyword args:
            management_address (str): Management IP address of the target array.
            replication_addresses (list[str]): IP addresses and FQDNs of the target arrays. Configurable only when `replication_transport` is set to `ip`. If not configured, will be set to all the replication addresses available on the target array at the time of the POST.
            type (str): The type of replication. Valid values are `async-replication` and `sync-replication`.
            replication_transport (str): The protocol used to transport data between the local array and the remote array. Valid values are `ip` and `fc`. The default is `ip`.
            connection_key (str): The connection key of the target array.
        """
        if management_address is not None:
            self.management_address = management_address
        if replication_addresses is not None:
            self.replication_addresses = replication_addresses
        if type is not None:
            self.type = type
        if replication_transport is not None:
            self.replication_transport = replication_transport
        if connection_key is not None:
            self.connection_key = connection_key

    def __setattr__(self, key, value):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `ArrayConnectionPost`".format(key))
        self.__dict__[key] = value

    def __getattribute__(self, item):
        value = object.__getattribute__(self, item)
        if isinstance(value, Property):
            raise AttributeError
        else:
            return value

    def __getitem__(self, key):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `ArrayConnectionPost`".format(key))
        return object.__getattribute__(self, key)

    def __setitem__(self, key, value):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `ArrayConnectionPost`".format(key))
        object.__setattr__(self, key, value)

    def __delitem__(self, key):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `ArrayConnectionPost`".format(key))
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
        if issubclass(ArrayConnectionPost, dict):
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
        if not isinstance(other, ArrayConnectionPost):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other