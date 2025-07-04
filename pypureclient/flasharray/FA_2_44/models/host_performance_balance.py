# coding: utf-8

"""
    FlashArray REST API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 2.44
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json
from typing import Set, Dict, Any

from typing import Optional, Union
from pydantic import BaseModel, Field, StrictFloat, StrictInt, StrictStr
from pypureclient.flasharray.FA_2_44.models.fixed_reference import FixedReference
from pypureclient.flasharray.FA_2_44.models.port_common import PortCommon
from pypureclient.flasharray.FA_2_44.models.port_initiator_target import PortInitiatorTarget


class HostPerformanceBalance(BaseModel):
    """
    HostPerformanceBalance
    """
    name: Optional[StrictStr] = Field(default=None, description="A user-specified name. The name must be locally unique and can be changed.")
    context: Optional[FixedReference] = Field(default=None, description="The context in which the operation was performed. Valid values include a reference to any array which is a member of the same fleet. If the array is not a member of a fleet, `context` will always implicitly be set to the array that received the request. Other parameters provided with the request, such as names of volumes or snapshots, are resolved relative to the provided `context`.")
    fraction_relative_to_max: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The path with the highest number of operation counts is displayed with a fraction_relative_to_max of 1.0. The fraction values of all other paths in the host are then calculated relative to the path with the highest number of operation counts.")
    initiator: Optional[PortCommon] = None
    op_count: Optional[StrictInt] = Field(default=None, description="Count of I/O operations for the host path, over the specified resolution.")
    target: Optional[PortInitiatorTarget] = None
    time: Optional[StrictInt] = Field(default=None, description="Sample time in milliseconds since UNIX epoch.")
    __properties = ["name", "context", "fraction_relative_to_max", "initiator", "op_count", "target", "time"]

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
                "fraction_relative_to_max",
                "op_count",
                "time",
            ])
        none_fields: Set[str] = set()
        for _field in self.__fields__.keys():
            if super().__getattribute__(_field) is None:
                none_fields.add(_field)

        _dict = self.dict(by_alias=True, exclude=excluded_fields, exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of context
        if _include_in_dict('context', include_readonly, excluded_fields, none_fields):
            _dict['context'] = self.context.to_dict(include_readonly=include_readonly)
        # override the default output from pydantic by calling `to_dict()` of initiator
        if _include_in_dict('initiator', include_readonly, excluded_fields, none_fields):
            _dict['initiator'] = self.initiator.to_dict(include_readonly=include_readonly)
        # override the default output from pydantic by calling `to_dict()` of target
        if _include_in_dict('target', include_readonly, excluded_fields, none_fields):
            _dict['target'] = self.target.to_dict(include_readonly=include_readonly)
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
    def from_json(cls, json_str: str) -> HostPerformanceBalance:
        """Create an instance of HostPerformanceBalance from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> HostPerformanceBalance:
        """Create an instance of HostPerformanceBalance from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return HostPerformanceBalance.parse_obj(obj)

        _obj = HostPerformanceBalance.construct(_fields_set=None, **{
            "name": obj.get("name"),
            "context": FixedReference.from_dict(obj.get("context")) if obj.get("context") is not None else None,
            "fraction_relative_to_max": obj.get("fraction_relative_to_max"),
            "initiator": PortCommon.from_dict(obj.get("initiator")) if obj.get("initiator") is not None else None,
            "op_count": obj.get("op_count"),
            "target": PortInitiatorTarget.from_dict(obj.get("target")) if obj.get("target") is not None else None,
            "time": obj.get("time")
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

