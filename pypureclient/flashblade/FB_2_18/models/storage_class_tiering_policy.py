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

from typing import List, Optional
from pydantic import BaseModel, Field, StrictBool, StrictStr, conlist
from pypureclient.flashblade.FB_2_18.models.fixed_reference import FixedReference
from pypureclient.flashblade.FB_2_18.models.tiering_policy_archival_rule import TieringPolicyArchivalRule
from pypureclient.flashblade.FB_2_18.models.tiering_policy_retrieval_rule import TieringPolicyRetrievalRule


class StorageClassTieringPolicy(BaseModel):
    """
    StorageClassTieringPolicy
    """
    id: Optional[StrictStr] = Field(default=None, description="A non-modifiable, globally unique ID chosen by the system.")
    name: Optional[StrictStr] = Field(default=None, description="Name of the object (e.g., a file system or snapshot).")
    enabled: Optional[StrictBool] = Field(default=None, description="If `true`, the policy is enabled. If not specified, defaults to `true`.")
    is_local: Optional[StrictBool] = Field(default=None, description="Whether the policy is defined on the local array.")
    location: Optional[FixedReference] = Field(default=None, description="Reference to the array where the policy is defined.")
    policy_type: Optional[StrictStr] = Field(default=None, description="Type of the policy. Valid values include `alert`, `audit`, `bucket-access`, `cross-origin-resource-sharing`, `network-access`, `nfs`, `object-access`, `smb-client`, `smb-share`, `snapshot`, `ssh-certificate-authority`, and `worm-data`.")
    archival_rules: Optional[conlist(TieringPolicyArchivalRule)] = Field(default=None, description="The list of archival rules for this policy.")
    retrieval_rules: Optional[conlist(TieringPolicyRetrievalRule)] = Field(default=None, description="The list of retrieval rules for this policy.")
    __properties = ["id", "name", "enabled", "is_local", "location", "policy_type", "archival_rules", "retrieval_rules"]

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
                "is_local",
                "policy_type",
            ])
        none_fields: Set[str] = set()
        for _field in self.__fields__.keys():
            if super().__getattribute__(_field) is None:
                none_fields.add(_field)

        _dict = self.dict(by_alias=True, exclude=excluded_fields, exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of location
        if _include_in_dict('location', include_readonly, excluded_fields, none_fields):
            _dict['location'] = self.location.to_dict(include_readonly=include_readonly)
        # override the default output from pydantic by calling `to_dict()` of each item in archival_rules (list)
        if _include_in_dict('archival_rules', include_readonly, excluded_fields, none_fields):
            _items = []
            for _item in self.archival_rules:
                if _item:
                    _items.append(_item.to_dict(include_readonly=include_readonly))
            _dict['archival_rules'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in retrieval_rules (list)
        if _include_in_dict('retrieval_rules', include_readonly, excluded_fields, none_fields):
            _items = []
            for _item in self.retrieval_rules:
                if _item:
                    _items.append(_item.to_dict(include_readonly=include_readonly))
            _dict['retrieval_rules'] = _items
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
    def from_json(cls, json_str: str) -> StorageClassTieringPolicy:
        """Create an instance of StorageClassTieringPolicy from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> StorageClassTieringPolicy:
        """Create an instance of StorageClassTieringPolicy from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return StorageClassTieringPolicy.parse_obj(obj)

        _obj = StorageClassTieringPolicy.construct(_fields_set=None, **{
            "id": obj.get("id"),
            "name": obj.get("name"),
            "enabled": obj.get("enabled"),
            "is_local": obj.get("is_local"),
            "location": FixedReference.from_dict(obj.get("location")) if obj.get("location") is not None else None,
            "policy_type": obj.get("policy_type"),
            "archival_rules": [TieringPolicyArchivalRule.from_dict(_item) for _item in obj.get("archival_rules")] if obj.get("archival_rules") is not None else None,
            "retrieval_rules": [TieringPolicyRetrievalRule.from_dict(_item) for _item in obj.get("retrieval_rules")] if obj.get("retrieval_rules") is not None else None
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

