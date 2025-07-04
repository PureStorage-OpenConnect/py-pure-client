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

from typing import List, Optional
from pydantic import BaseModel, Field, StrictBool, StrictInt, StrictStr, conlist
from pypureclient.flasharray.FA_2_44.models.admin_role import AdminRole
from pypureclient.flasharray.FA_2_44.models.api_token import ApiToken
from pypureclient.flasharray.FA_2_44.models.reference_with_type import ReferenceWithType


class Admin(BaseModel):
    """
    Admin
    """
    name: Optional[StrictStr] = Field(default=None, description="A user-specified name. The name must be locally unique and cannot be changed.")
    api_token: Optional[ApiToken] = None
    is_local: Optional[StrictBool] = Field(default=None, description="Returns a value of `true` if the user is local to the machine.")
    locked: Optional[StrictBool] = Field(default=None, description="Returns a value of `true` if the user is currently locked out. otherwise `false`. Change to `false` to unlock a user. This field is only visible to `array_admin` roles. For all other users, the value is always `null`.")
    lockout_remaining: Optional[StrictInt] = Field(default=None, description="The remaining lockout period if the user is locked out, in milliseconds. This field is only visible to `array_admin` roles. For all other users, the value is always `null`.")
    management_access_policies: Optional[conlist(ReferenceWithType)] = Field(default=None, description="List of management access policies associated with the administrator.")
    password: Optional[StrictStr] = Field(default=None, description="Password associated with the account.")
    public_key: Optional[StrictStr] = Field(default=None, description="Public key for SSH access. Multiple public keys can be specified, separated by newlines.")
    role: Optional[AdminRole] = None
    __properties = ["name", "api_token", "is_local", "locked", "lockout_remaining", "management_access_policies", "password", "public_key", "role"]

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
                "is_local",
                "lockout_remaining",
                "management_access_policies",
            ])
        none_fields: Set[str] = set()
        for _field in self.__fields__.keys():
            if super().__getattribute__(_field) is None:
                none_fields.add(_field)

        _dict = self.dict(by_alias=True, exclude=excluded_fields, exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of api_token
        if _include_in_dict('api_token', include_readonly, excluded_fields, none_fields):
            _dict['api_token'] = self.api_token.to_dict(include_readonly=include_readonly)
        # override the default output from pydantic by calling `to_dict()` of each item in management_access_policies (list)
        if _include_in_dict('management_access_policies', include_readonly, excluded_fields, none_fields):
            _items = []
            for _item in self.management_access_policies:
                if _item:
                    _items.append(_item.to_dict(include_readonly=include_readonly))
            _dict['management_access_policies'] = _items
        # override the default output from pydantic by calling `to_dict()` of role
        if _include_in_dict('role', include_readonly, excluded_fields, none_fields):
            _dict['role'] = self.role.to_dict(include_readonly=include_readonly)
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
    def from_json(cls, json_str: str) -> Admin:
        """Create an instance of Admin from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> Admin:
        """Create an instance of Admin from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return Admin.parse_obj(obj)

        _obj = Admin.construct(_fields_set=None, **{
            "name": obj.get("name"),
            "api_token": ApiToken.from_dict(obj.get("api_token")) if obj.get("api_token") is not None else None,
            "is_local": obj.get("is_local"),
            "locked": obj.get("locked"),
            "lockout_remaining": obj.get("lockout_remaining"),
            "management_access_policies": [ReferenceWithType.from_dict(_item) for _item in obj.get("management_access_policies")] if obj.get("management_access_policies") is not None else None,
            "password": obj.get("password"),
            "public_key": obj.get("public_key"),
            "role": AdminRole.from_dict(obj.get("role")) if obj.get("role") is not None else None
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

