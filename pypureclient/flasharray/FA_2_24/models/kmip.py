# coding: utf-8

"""
    FlashArray REST API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: 2.24
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re

import six
import typing

from ....properties import Property
if typing.TYPE_CHECKING:
    from pypureclient.flasharray.FA_2_24 import models

class Kmip(object):
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'ca_certificate': 'str',
        'certificate': 'KmipCertificate',
        'kmip_objects': 'list[KmipObject]',
        'name': 'str',
        'uris': 'list[str]'
    }

    attribute_map = {
        'ca_certificate': 'ca_certificate',
        'certificate': 'certificate',
        'kmip_objects': 'kmip_objects',
        'name': 'name',
        'uris': 'uris'
    }

    required_args = {
    }

    def __init__(
        self,
        ca_certificate=None,  # type: str
        certificate=None,  # type: models.KmipCertificate
        kmip_objects=None,  # type: List[models.KmipObject]
        name=None,  # type: str
        uris=None,  # type: List[str]
    ):
        """
        Keyword args:
            ca_certificate (str): CA certificate text for the KMIP server.
            certificate (KmipCertificate): The certificate used to verify FlashArray authenticity to the KMIP servers.
            kmip_objects (list[KmipObject]): List of the name and UID of the KMIP objects.
            name (str): A locally unique, system-generated name. The name cannot be modified.
            uris (list[str]): List of URIs for the configured KMIP servers.
        """
        if ca_certificate is not None:
            self.ca_certificate = ca_certificate
        if certificate is not None:
            self.certificate = certificate
        if kmip_objects is not None:
            self.kmip_objects = kmip_objects
        if name is not None:
            self.name = name
        if uris is not None:
            self.uris = uris

    def __setattr__(self, key, value):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `Kmip`".format(key))
        if key == "ca_certificate" and value is not None:
            if len(value) > 3000:
                raise ValueError("Invalid value for `ca_certificate`, length must be less than or equal to `3000`")
        self.__dict__[key] = value

    def __getattribute__(self, item):
        value = object.__getattribute__(self, item)
        if isinstance(value, Property):
            raise AttributeError
        else:
            return value

    def __getitem__(self, key):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `Kmip`".format(key))
        return object.__getattribute__(self, key)

    def __setitem__(self, key, value):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `Kmip`".format(key))
        object.__setattr__(self, key, value)

    def __delitem__(self, key):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `Kmip`".format(key))
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
        if issubclass(Kmip, dict):
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
        if not isinstance(other, Kmip):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other