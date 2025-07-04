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
from pydantic import BaseModel, Field, StrictBool, StrictInt
from pypureclient.flasharray.FA_2_44.models.fixed_reference import FixedReference
from pypureclient.flasharray.FA_2_44.models.fixed_reference_with_type import FixedReferenceWithType


class PolicyMember(BaseModel):
    """
    PolicyMember
    """
    context: Optional[FixedReference] = Field(default=None, description="The context in which the operation was performed. Valid values include a reference to any array which is a member of the same fleet. If the array is not a member of a fleet, `context` will always implicitly be set to the array that received the request. Other parameters provided with the request, such as names of volumes or snapshots, are resolved relative to the provided `context`.")
    destroyed: Optional[StrictBool] = Field(default=None, description="Returns a value of `true` if the member is destroyed.")
    enabled: Optional[StrictBool] = Field(default=None, description="Returns a value of `true` if the policy is enabled.")
    member: Optional[FixedReferenceWithType] = Field(default=None, description="Reference to the resource that the policy is applied to.")
    policy: Optional[FixedReferenceWithType] = Field(default=None, description="Reference to the policy.")
    time_remaining: Optional[StrictInt] = Field(default=None, description="The amount of time left, in milliseconds, until the destroyed policy member is permanently eradicated.")
    __properties = ["context", "destroyed", "enabled", "member", "policy", "time_remaining"]

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
                "destroyed",
                "enabled",
                "time_remaining",
            ])
        none_fields: Set[str] = set()
        for _field in self.__fields__.keys():
            if super().__getattribute__(_field) is None:
                none_fields.add(_field)

        _dict = self.dict(by_alias=True, exclude=excluded_fields, exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of context
        if _include_in_dict('context', include_readonly, excluded_fields, none_fields):
            _dict['context'] = self.context.to_dict(include_readonly=include_readonly)
        # override the default output from pydantic by calling `to_dict()` of member
        if _include_in_dict('member', include_readonly, excluded_fields, none_fields):
            _dict['member'] = self.member.to_dict(include_readonly=include_readonly)
        # override the default output from pydantic by calling `to_dict()` of policy
        if _include_in_dict('policy', include_readonly, excluded_fields, none_fields):
            _dict['policy'] = self.policy.to_dict(include_readonly=include_readonly)
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
    def from_json(cls, json_str: str) -> PolicyMember:
        """Create an instance of PolicyMember from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> PolicyMember:
        """Create an instance of PolicyMember from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return PolicyMember.parse_obj(obj)

        _obj = PolicyMember.construct(_fields_set=None, **{
            "context": FixedReference.from_dict(obj.get("context")) if obj.get("context") is not None else None,
            "destroyed": obj.get("destroyed"),
            "enabled": obj.get("enabled"),
            "member": FixedReferenceWithType.from_dict(obj.get("member")) if obj.get("member") is not None else None,
            "policy": FixedReferenceWithType.from_dict(obj.get("policy")) if obj.get("policy") is not None else None,
            "time_remaining": obj.get("time_remaining")
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

