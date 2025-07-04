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

from typing import Optional
from pydantic import BaseModel, Field, StrictInt, StrictStr
from pypureclient.flashblade.FB_2_18.models.fixed_reference import FixedReference
from pypureclient.flashblade.FB_2_18.models.reference import Reference
from pypureclient.flashblade.FB_2_18.models.user import User


class UserQuota(BaseModel):
    """
    UserQuota
    """
    name: Optional[StrictStr] = Field(default=None, description="Name of the object (e.g., a file system or snapshot).")
    context: Optional[Reference] = Field(default=None, description="The context in which the operation was performed. Valid values include a reference to any array which is a member of the same fleet. If the array is not a member of a fleet, `context` will always implicitly be set to the array that received the request. Other parameters provided with the request, such as names of volumes or snapshots, are resolved relative to the provided `context`.")
    file_system: Optional[FixedReference] = None
    file_system_default_quota: Optional[StrictInt] = Field(default=None, description="File system's default user quota (in bytes). If it is `0`, it means there is no default quota. This will be the effective user quota if the user doesn't have an individual quota. This default quota is set through the `file-systems` endpoint.")
    quota: Optional[StrictInt] = Field(default=None, description="The limit of the quota (in bytes) for the specified user, cannot be `0`. If specified, this value will override the file system's default user quota.")
    usage: Optional[StrictInt] = Field(default=None, description="The usage of the file system (in bytes) by the specified user.")
    user: Optional[User] = Field(default=None, description="The user on which this quota is enforced.")
    __properties = ["name", "context", "file_system", "file_system_default_quota", "quota", "usage", "user"]

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
                "name",
                "context",
                "file_system_default_quota",
                "usage",
            ])
        none_fields: Set[str] = set()
        for _field in self.__fields__.keys():
            if super().__getattribute__(_field) is None:
                none_fields.add(_field)

        _dict = self.dict(by_alias=True, exclude=excluded_fields, exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of context
        if _include_in_dict('context', include_readonly, excluded_fields, none_fields):
            _dict['context'] = self.context.to_dict(include_readonly=include_readonly)
        # override the default output from pydantic by calling `to_dict()` of file_system
        if _include_in_dict('file_system', include_readonly, excluded_fields, none_fields):
            _dict['file_system'] = self.file_system.to_dict(include_readonly=include_readonly)
        # override the default output from pydantic by calling `to_dict()` of user
        if _include_in_dict('user', include_readonly, excluded_fields, none_fields):
            _dict['user'] = self.user.to_dict(include_readonly=include_readonly)
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
    def from_json(cls, json_str: str) -> UserQuota:
        """Create an instance of UserQuota from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> UserQuota:
        """Create an instance of UserQuota from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return UserQuota.parse_obj(obj)

        _obj = UserQuota.construct(_fields_set=None, **{
            "name": obj.get("name"),
            "context": Reference.from_dict(obj.get("context")) if obj.get("context") is not None else None,
            "file_system": FixedReference.from_dict(obj.get("file_system")) if obj.get("file_system") is not None else None,
            "file_system_default_quota": obj.get("file_system_default_quota"),
            "quota": obj.get("quota"),
            "usage": obj.get("usage"),
            "user": User.from_dict(obj.get("user")) if obj.get("user") is not None else None
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

