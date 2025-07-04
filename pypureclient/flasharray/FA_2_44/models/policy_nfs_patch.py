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
from pydantic import BaseModel, Field, StrictBool, StrictStr, conlist


class PolicyNfsPatch(BaseModel):
    """
    PolicyNfsPatch
    """
    name: Optional[StrictStr] = Field(default=None, description="The new name for the resource.")
    enabled: Optional[StrictBool] = Field(default=None, description="If set to `true`, enables the policy. If set to `false`, disables the policy.")
    nfs_version: Optional[conlist(StrictStr)] = Field(default=None, description="NFS protocol version allowed for the export to set for the policy. This operation updates all rules of the specified policy. Valid values are `nfsv3` and `nfsv4`.")
    security: Optional[conlist(StrictStr)] = Field(default=None, description="The security flavors to use for accessing files on this mount point. Values include `auth_sys`, `krb5`, `krb5i`, and `krb5p`. If the server does not support the requested flavor, the mount operation fails. This operation updates all rules of the specified policy. If `auth_sys`, the client is trusted to specify the identity of the user. If `krb5`, cryptographic proof of the identity of the user is provided in each RPC request. This provides strong verification of the identity of users accessing data on the server. Note that additional configuration besides adding this mount option is required to enable Kerberos security. If `krb5i`, integrity checking is added to krb5. This ensures the data has not been tampered with. If `krb5p`, integrity checking and encryption is added to `krb5`. This is the most secure setting, but it also involves the most performance overhead.")
    user_mapping_enabled: Optional[StrictBool] = Field(default=None, description="If set to `true`, FlashArray queries the joined AD/OpenLDAP server to find the user corresponding to the incoming UID. If set to `false`, users are defined by UID/GID pair.")
    __properties = ["name", "enabled", "nfs_version", "security", "user_mapping_enabled"]

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
    def from_json(cls, json_str: str) -> PolicyNfsPatch:
        """Create an instance of PolicyNfsPatch from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> PolicyNfsPatch:
        """Create an instance of PolicyNfsPatch from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return PolicyNfsPatch.parse_obj(obj)

        _obj = PolicyNfsPatch.construct(_fields_set=None, **{
            "name": obj.get("name"),
            "enabled": obj.get("enabled"),
            "nfs_version": obj.get("nfs_version"),
            "security": obj.get("security"),
            "user_mapping_enabled": obj.get("user_mapping_enabled")
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

