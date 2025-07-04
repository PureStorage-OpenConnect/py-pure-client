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

from typing import Optional
from pydantic import BaseModel, Field, StrictBool, StrictStr


class ProtectionGroupsVolumesMember(BaseModel):
    """
    ProtectionGroupsVolumesMember
    """
    id: Optional[StrictStr] = Field(default=None, description="A globally unique, system-generated ID. The ID cannot be modified.")
    name: Optional[StrictStr] = Field(default=None, description="The resource name, such as volume name, pod name, snapshot name, and so on.")
    destroyed: Optional[StrictBool] = Field(default=None, description="Returns a value of `true` if the volume has been destroyed and is pending eradication. Through the `volumes` endpoint, the user can see `time_remaining` of the destroyed volume, recover, or eradicate the destroyed volume.")
    __properties = ["id", "name", "destroyed"]

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
            ])
        none_fields: Set[str] = set()
        for _field in self.__fields__.keys():
            if super().__getattribute__(_field) is None:
                none_fields.add(_field)

        _dict = self.dict(by_alias=True, exclude=excluded_fields, exclude_none=True)
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
    def from_json(cls, json_str: str) -> ProtectionGroupsVolumesMember:
        """Create an instance of ProtectionGroupsVolumesMember from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> ProtectionGroupsVolumesMember:
        """Create an instance of ProtectionGroupsVolumesMember from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return ProtectionGroupsVolumesMember.parse_obj(obj)

        _obj = ProtectionGroupsVolumesMember.construct(_fields_set=None, **{
            "id": obj.get("id"),
            "name": obj.get("name"),
            "destroyed": obj.get("destroyed")
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

