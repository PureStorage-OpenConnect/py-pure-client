# coding: utf-8

"""
    FlashBlade REST API

    A lightweight client for FlashBlade REST API 2.8, developed by Pure Storage, Inc. (http://www.purestorage.com/). 

    OpenAPI spec version: 2.8
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re

import six
import typing

from ....properties import Property
if typing.TYPE_CHECKING:
    from pypureclient.flashblade.FB_2_8 import models

class NfsExportPolicyGetResponse(object):
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'continuation_token': 'str',
        'total_item_count': 'int',
        'items': 'list[NfsExportPolicy]'
    }

    attribute_map = {
        'continuation_token': 'continuation_token',
        'total_item_count': 'total_item_count',
        'items': 'items'
    }

    required_args = {
    }

    def __init__(
        self,
        continuation_token=None,  # type: str
        total_item_count=None,  # type: int
        items=None,  # type: List[models.NfsExportPolicy]
    ):
        """
        Keyword args:
            continuation_token (str): Continuation token that can be provided in the `continuation_token` query param to get the next page of data. If you use the `continuation_token` to page through data you are guaranteed to get all items exactly once regardless of how items are modified. If an item is added or deleted during the pagination then it may or may not be returned. The `continuation_token` is generated if the `limit` is less than the remaining number of items, and the default sort is used (no sort is specified). 
            total_item_count (int): Total number of items after applying `filter` params.
            items (list[NfsExportPolicy]): A list of NFS export policy objects.
        """
        if continuation_token is not None:
            self.continuation_token = continuation_token
        if total_item_count is not None:
            self.total_item_count = total_item_count
        if items is not None:
            self.items = items

    def __setattr__(self, key, value):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `NfsExportPolicyGetResponse`".format(key))
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
        if issubclass(NfsExportPolicyGetResponse, dict):
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
        if not isinstance(other, NfsExportPolicyGetResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
