# coding: utf-8

"""
    Pure1 Public REST API

    Pure1 Public REST API, developed by [Pure Storage, Inc.](https://www.purestorage.com)   The Pure1 REST API 2.0 offers one single form of authentication: OAuth 2.0 via the [Token Exchange protocol](https://datatracker.ietf.org/doc/draft-ietf-oauth-token-exchange).  OAuth 2.0 is an open protocol to allow secure authorization in a simple and standard method from web, mobile, desktop and background applications.  Note that the [Authentication](#section/Authentication) section below mentions 'API Key' as the security scheme type. This is solely for the purpose of allowing testing this API with [Swagger UI](https://static.pure1.purestorage.com/api-swagger/index.html).  [Knowledge base reference documentation](https://support.purestorage.com/Pure1/Pure1_Manage/Pure1_Manage_-_REST_API/Pure1_Manage_-_REST_API__Reference)

    OpenAPI spec version: 1.3
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re

import six
import typing

from ....properties import Property
if typing.TYPE_CHECKING:
    from pypureclient.pure1.Pure1_1_3 import models

class SubscriptionAssetArray(object):
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'chassis_serial_number': 'str',
        'model': 'str',
        'advanced_space': 'SubscriptionAssetArrayAdvancedSpace',
        'version': 'str',
        'space': 'AssetSpace'
    }

    attribute_map = {
        'chassis_serial_number': 'chassis_serial_number',
        'model': 'model',
        'advanced_space': 'advanced_space',
        'version': 'version',
        'space': 'space'
    }

    required_args = {
    }

    def __init__(
        self,
        chassis_serial_number=None,  # type: str
        model=None,  # type: str
        advanced_space=None,  # type: models.SubscriptionAssetArrayAdvancedSpace
        version=None,  # type: str
        space=None,  # type: models.AssetSpace
    ):
        """
        Keyword args:
            chassis_serial_number (str): The chassis serial number of the appliance.
            model (str): The model of the appliance.
            advanced_space (SubscriptionAssetArrayAdvancedSpace): The physical and effective space information. Only visible when the query parameter `advanced_space` is set to `true`. 
            version (str): The Purity version of the appliance.
            space (AssetSpace): Displays size and space consumption information. For Evergreen//One and Evergreen//Flex this is the effective space information. For Evergreen//Forever and Evergreen//Foundation this is the physical space information. 
        """
        if chassis_serial_number is not None:
            self.chassis_serial_number = chassis_serial_number
        if model is not None:
            self.model = model
        if advanced_space is not None:
            self.advanced_space = advanced_space
        if version is not None:
            self.version = version
        if space is not None:
            self.space = space

    def __setattr__(self, key, value):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `SubscriptionAssetArray`".format(key))
        self.__dict__[key] = value

    def __getattribute__(self, item):
        value = object.__getattribute__(self, item)
        if isinstance(value, Property):
            raise AttributeError
        else:
            return value

    def __getitem__(self, key):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `SubscriptionAssetArray`".format(key))
        return object.__getattribute__(self, key)

    def __setitem__(self, key, value):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `SubscriptionAssetArray`".format(key))
        object.__setattr__(self, key, value)

    def __delitem__(self, key):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `SubscriptionAssetArray`".format(key))
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
        if issubclass(SubscriptionAssetArray, dict):
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
        if not isinstance(other, SubscriptionAssetArray):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
