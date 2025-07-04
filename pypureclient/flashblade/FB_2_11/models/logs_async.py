# coding: utf-8

"""
    FlashBlade REST API

    A lightweight client for FlashBlade REST API 2.11, developed by Pure Storage, Inc. (http://www.purestorage.com/).

    The version of the OpenAPI document: 2.11
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json
from typing import Set, Dict, Any

from typing import List, Optional, Union
from pydantic import BaseModel, Field, StrictBool, StrictFloat, StrictInt, StrictStr, conint, conlist
from pypureclient.flashblade.FB_2_11.models.file_info import FileInfo
from pypureclient.flashblade.FB_2_11.models.reference import Reference


class LogsAsync(BaseModel):
    """
    LogsAsync
    """
    id: Optional[StrictStr] = Field(default=None, description="A non-modifiable, globally unique ID chosen by the system.")
    name: Optional[StrictStr] = Field(default=None, description="Name of the object (e.g., a file system or snapshot).")
    available_files: Optional[conlist(FileInfo)] = Field(default=None, description="All of the available files ready for download.")
    end_time: Optional[conint(strict=True, ge=0)] = Field(default=None, description="When the time window ends (in milliseconds since epoch). start_time and end_time determine the number of hours for which the logs are prepared for. At most 6 hours of logs can be prepared in one request. start_time and end_time are truncated to hour boundaries.")
    hardware_components: Optional[conlist(Reference)] = Field(default=None, description="All of the hardware components for which logs are being processed.")
    last_request_time: Optional[conint(strict=True, ge=0)] = Field(default=None, description="The last time log preparation was requested (in milliseconds since epoch).")
    processing: Optional[StrictBool] = Field(default=None, description="Returns a value of `true` if the logs are being prepared.")
    progress: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="A representation of log preparation progress. Ranges from 0 to 1.0.")
    start_time: Optional[conint(strict=True, ge=0)] = Field(default=None, description="When the time window starts (in milliseconds since epoch). start_time and end_time determine the number of hours for which the logs are prepared for. At most 6 hours of logs can be prepared in one request. start_time and end_time are truncated to hour boundaries.")
    __properties = ["id", "name", "available_files", "end_time", "hardware_components", "last_request_time", "processing", "progress", "start_time"]

    class Config:
        """Pydantic configuration"""
        allow_population_by_field_name = True
        validate_assignment = True

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.to_dict(include_readonly=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(self.as_request_dict())

    def as_request_dict(self) -> Dict[str, Any]:
        return self.to_dict(include_readonly=False)

    def to_dict(self, include_readonly: bool=True) -> Dict[str, Any]:

        """Returns the dictionary representation of the model using alias"""
        excluded_fields: Set[str] = set()
        if not include_readonly:
            excluded_fields.update([
                "id",
                "name",
                "available_files",
                "last_request_time",
                "processing",
                "progress",
            ])
        none_fields: Set[str] = set()
        for _field in self.__fields__.keys():
            if super().__getattribute__(_field) is None:
                none_fields.add(_field)

        _dict = self.dict(by_alias=True, exclude=excluded_fields, exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of each item in available_files (list)
        if _include_in_dict('available_files', include_readonly, excluded_fields, none_fields):
            _items = []
            for _item in self.available_files:
                if _item:
                    _items.append(_item.to_dict(include_readonly=include_readonly))
            _dict['available_files'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in hardware_components (list)
        if _include_in_dict('hardware_components', include_readonly, excluded_fields, none_fields):
            _items = []
            for _item in self.hardware_components:
                if _item:
                    _items.append(_item.to_dict(include_readonly=include_readonly))
            _dict['hardware_components'] = _items
        return _dict

    def __getitem__(self, key):
        return super().__getattribute__(key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __delitem__(self, key):
        setattr(self, key, None)

    def __getattribute__(self, name: str) -> Any:
        _value = super().__getattribute__(name)
        if _value is None and name in self.__fields__.keys() and _should_raise_on_none():
            raise AttributeError
        return _value

    def __str__(self) -> str:
        return self.to_str()

    def __repr__(self) -> str:
        return self.to_str()

    @classmethod
    def from_json(cls, json_str: str) -> LogsAsync:
        """Create an instance of LogsAsync from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> LogsAsync:
        """Create an instance of LogsAsync from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return LogsAsync.parse_obj(obj)

        _obj = LogsAsync.construct(_fields_set=None, **{
            "id": obj.get("id"),
            "name": obj.get("name"),
            "available_files": [FileInfo.from_dict(_item) for _item in obj.get("available_files")] if obj.get("available_files") is not None else None,
            "end_time": obj.get("end_time"),
            "hardware_components": [Reference.from_dict(_item) for _item in obj.get("hardware_components")] if obj.get("hardware_components") is not None else None,
            "last_request_time": obj.get("last_request_time"),
            "processing": obj.get("processing"),
            "progress": obj.get("progress"),
            "start_time": obj.get("start_time")
        })
        return _obj

def _should_raise_on_none() -> bool:
    import importlib
    _package = importlib.import_module(__package__)
    return _package._attribute_error_on_none

def _include_in_dict(name: str, include_readonly: bool, excluded_fields: Set[str], none_fields: Set[str]) -> bool:
    if name in none_fields:
        return False
    return (include_readonly or name not in excluded_fields)

