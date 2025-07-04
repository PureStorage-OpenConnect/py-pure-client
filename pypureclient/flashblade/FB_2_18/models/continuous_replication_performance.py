# coding: utf-8

"""
    FlashBlade REST API

    A lightweight client for FlashBlade REST API 2.18, developed by Pure Storage, Inc. (http://www.purestorage.com/).

    The version of the OpenAPI document: 2.18
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json
from typing import Set, Dict, Any

from typing import Optional, Union
from pydantic import BaseModel, Field, confloat, conint
from pypureclient.flashblade.FB_2_18.models.object_backlog import ObjectBacklog


class ContinuousReplicationPerformance(BaseModel):
    """
    ContinuousReplicationPerformance
    """
    received_bytes_per_sec: Optional[Union[confloat(ge=0, strict=True), conint(ge=0, strict=True)]] = Field(default=None, description="Total bytes received per second.")
    transmitted_bytes_per_sec: Optional[Union[confloat(ge=0, strict=True), conint(ge=0, strict=True)]] = Field(default=None, description="Total bytes transmitted per second.")
    object_backlog: Optional[ObjectBacklog] = Field(default=None, description="The total number of pending object operations and their size that are currently in the backlog.")
    __properties = ["received_bytes_per_sec", "transmitted_bytes_per_sec", "object_backlog"]

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
                "received_bytes_per_sec",
                "transmitted_bytes_per_sec",
            ])
        none_fields: Set[str] = set()
        for _field in self.__fields__.keys():
            if super().__getattribute__(_field) is None:
                none_fields.add(_field)

        _dict = self.dict(by_alias=True, exclude=excluded_fields, exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of object_backlog
        if _include_in_dict('object_backlog', include_readonly, excluded_fields, none_fields):
            _dict['object_backlog'] = self.object_backlog.to_dict(include_readonly=include_readonly)
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
    def from_json(cls, json_str: str) -> ContinuousReplicationPerformance:
        """Create an instance of ContinuousReplicationPerformance from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> ContinuousReplicationPerformance:
        """Create an instance of ContinuousReplicationPerformance from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return ContinuousReplicationPerformance.parse_obj(obj)

        _obj = ContinuousReplicationPerformance.construct(_fields_set=None, **{
            "received_bytes_per_sec": obj.get("received_bytes_per_sec"),
            "transmitted_bytes_per_sec": obj.get("transmitted_bytes_per_sec"),
            "object_backlog": ObjectBacklog.from_dict(obj.get("object_backlog")) if obj.get("object_backlog") is not None else None
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

