# coding: utf-8

"""
    FlashBlade REST API

    A lightweight client for FlashBlade REST API 2.14, developed by Pure Storage, Inc. (http://www.purestorage.com/). 

    OpenAPI spec version: 2.14
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re

import six
import typing

from ....properties import Property
if typing.TYPE_CHECKING:
    from pypureclient.flashblade.FB_2_14 import models

class ArrayHttpSpecificPerformance(object):
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
        'read_files_per_sec': 'float',
        'others_per_sec': 'float',
        'usec_per_write_file_op': 'float',
        'usec_per_other_op': 'float',
        'write_dirs_per_sec': 'float',
        'usec_per_write_dir_op': 'float',
        'time': 'int',
        'usec_per_read_file_op': 'float',
        'usec_per_read_dir_op': 'float',
        'read_dirs_per_sec': 'float',
        'write_files_per_sec': 'float'
    }

    attribute_map = {
        'name': 'name',
        'id': 'id',
        'read_files_per_sec': 'read_files_per_sec',
        'others_per_sec': 'others_per_sec',
        'usec_per_write_file_op': 'usec_per_write_file_op',
        'usec_per_other_op': 'usec_per_other_op',
        'write_dirs_per_sec': 'write_dirs_per_sec',
        'usec_per_write_dir_op': 'usec_per_write_dir_op',
        'time': 'time',
        'usec_per_read_file_op': 'usec_per_read_file_op',
        'usec_per_read_dir_op': 'usec_per_read_dir_op',
        'read_dirs_per_sec': 'read_dirs_per_sec',
        'write_files_per_sec': 'write_files_per_sec'
    }

    required_args = {
    }

    def __init__(
        self,
        name=None,  # type: str
        id=None,  # type: str
        read_files_per_sec=None,  # type: float
        others_per_sec=None,  # type: float
        usec_per_write_file_op=None,  # type: float
        usec_per_other_op=None,  # type: float
        write_dirs_per_sec=None,  # type: float
        usec_per_write_dir_op=None,  # type: float
        time=None,  # type: int
        usec_per_read_file_op=None,  # type: float
        usec_per_read_dir_op=None,  # type: float
        read_dirs_per_sec=None,  # type: float
        write_files_per_sec=None,  # type: float
    ):
        """
        Keyword args:
            name (str): Name of the object (e.g., a file system or snapshot).
            id (str): A non-modifiable, globally unique ID chosen by the system. 
            read_files_per_sec (float): Read file requests processed per second.
            others_per_sec (float): Other operations processed per second.
            usec_per_write_file_op (float): Average time, measured in microseconds, it takes the array to process a write file request. 
            usec_per_other_op (float): Average time, measured in microseconds, it takes the array to process other operations. 
            write_dirs_per_sec (float): Write directory requests processed per second.
            usec_per_write_dir_op (float): Average time, measured in microseconds, it takes the array to process a write directory request. 
            time (int): Sample time in milliseconds since UNIX epoch.
            usec_per_read_file_op (float): Average time, measured in microseconds, it takes the array to process a read file request. 
            usec_per_read_dir_op (float): Average time, measured in microseconds, it takes the array to process a read directory request. 
            read_dirs_per_sec (float): Read directory requests processed per second.
            write_files_per_sec (float): Write file requests processed per second.
        """
        if name is not None:
            self.name = name
        if id is not None:
            self.id = id
        if read_files_per_sec is not None:
            self.read_files_per_sec = read_files_per_sec
        if others_per_sec is not None:
            self.others_per_sec = others_per_sec
        if usec_per_write_file_op is not None:
            self.usec_per_write_file_op = usec_per_write_file_op
        if usec_per_other_op is not None:
            self.usec_per_other_op = usec_per_other_op
        if write_dirs_per_sec is not None:
            self.write_dirs_per_sec = write_dirs_per_sec
        if usec_per_write_dir_op is not None:
            self.usec_per_write_dir_op = usec_per_write_dir_op
        if time is not None:
            self.time = time
        if usec_per_read_file_op is not None:
            self.usec_per_read_file_op = usec_per_read_file_op
        if usec_per_read_dir_op is not None:
            self.usec_per_read_dir_op = usec_per_read_dir_op
        if read_dirs_per_sec is not None:
            self.read_dirs_per_sec = read_dirs_per_sec
        if write_files_per_sec is not None:
            self.write_files_per_sec = write_files_per_sec

    def __setattr__(self, key, value):
        if key not in self.attribute_map:
            raise KeyError("Invalid key `{}` for `ArrayHttpSpecificPerformance`".format(key))
        if key == "read_files_per_sec" and value is not None:
            if value < 0:
                raise ValueError("Invalid value for `read_files_per_sec`, must be a value greater than or equal to `0`")
        if key == "others_per_sec" and value is not None:
            if value < 0:
                raise ValueError("Invalid value for `others_per_sec`, must be a value greater than or equal to `0`")
        if key == "usec_per_write_file_op" and value is not None:
            if value < 0:
                raise ValueError("Invalid value for `usec_per_write_file_op`, must be a value greater than or equal to `0`")
        if key == "usec_per_other_op" and value is not None:
            if value < 0:
                raise ValueError("Invalid value for `usec_per_other_op`, must be a value greater than or equal to `0`")
        if key == "write_dirs_per_sec" and value is not None:
            if value < 0:
                raise ValueError("Invalid value for `write_dirs_per_sec`, must be a value greater than or equal to `0`")
        if key == "usec_per_write_dir_op" and value is not None:
            if value < 0:
                raise ValueError("Invalid value for `usec_per_write_dir_op`, must be a value greater than or equal to `0`")
        if key == "usec_per_read_file_op" and value is not None:
            if value < 0:
                raise ValueError("Invalid value for `usec_per_read_file_op`, must be a value greater than or equal to `0`")
        if key == "usec_per_read_dir_op" and value is not None:
            if value < 0:
                raise ValueError("Invalid value for `usec_per_read_dir_op`, must be a value greater than or equal to `0`")
        if key == "read_dirs_per_sec" and value is not None:
            if value < 0:
                raise ValueError("Invalid value for `read_dirs_per_sec`, must be a value greater than or equal to `0`")
        if key == "write_files_per_sec" and value is not None:
            if value < 0:
                raise ValueError("Invalid value for `write_files_per_sec`, must be a value greater than or equal to `0`")
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
        if issubclass(ArrayHttpSpecificPerformance, dict):
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
        if not isinstance(other, ArrayHttpSpecificPerformance):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
