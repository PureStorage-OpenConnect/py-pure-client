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
from pydantic import BaseModel, Field
from pypureclient.flasharray.FA_2_44.models.reference_no_id import ReferenceNoId
from pypureclient.flasharray.FA_2_44.models.reference_with_type import ReferenceWithType


class PolicyrulemanagementaccessRules(BaseModel):
    """
    PolicyrulemanagementaccessRules
    """
    role: Optional[ReferenceNoId] = Field(default=None, description="Role defines a set of permissions applicable in a scope. `viewer` grants users the ability to read a resource. `support` grants the ability to perform general support-related actions, as well as read resources. `storage` grants access to all storage operations on a resource. `admin` grants access to all operations.")
    scope: Optional[ReferenceWithType] = Field(default=None, description="Reference to the resource (e.g. arrays, realms) which specifies the scope that the role applies. The `id` or `name` parameter is required, but they cannot be set together. Also, `resource_type` must be set.")
    __properties = ["role", "scope"]

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
        # override the default output from pydantic by calling `to_dict()` of role
        if _include_in_dict('role', include_readonly, excluded_fields, none_fields):
            _dict['role'] = self.role.to_dict(include_readonly=include_readonly)
        # override the default output from pydantic by calling `to_dict()` of scope
        if _include_in_dict('scope', include_readonly, excluded_fields, none_fields):
            _dict['scope'] = self.scope.to_dict(include_readonly=include_readonly)
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
    def from_json(cls, json_str: str) -> PolicyrulemanagementaccessRules:
        """Create an instance of PolicyrulemanagementaccessRules from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> PolicyrulemanagementaccessRules:
        """Create an instance of PolicyrulemanagementaccessRules from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return PolicyrulemanagementaccessRules.parse_obj(obj)

        _obj = PolicyrulemanagementaccessRules.construct(_fields_set=None, **{
            "role": ReferenceNoId.from_dict(obj.get("role")) if obj.get("role") is not None else None,
            "scope": ReferenceWithType.from_dict(obj.get("scope")) if obj.get("scope") is not None else None
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

