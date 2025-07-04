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
from pydantic import BaseModel, Field, StrictStr, conlist


class PolicyrulenfsclientpostRules(BaseModel):
    """
    PolicyrulenfsclientpostRules
    """
    access: Optional[StrictStr] = Field(default=None, description="Specifies access control for the export. Valid values include `root-squash`, `all-squash`, and `no-root-squash`. The value `root-squash` prevents client users and groups with root privilege from mapping their root privilege to a file system. All users with UID 0 will have their UID mapped to `anonuid`. All users with GID 0 will have their GID mapped to `anongid`. The value `all-squash` maps all UIDs (including root) to `anonuid` and all GIDs (including root) to `anongid`. The value `no-root-squash` allows users and groups to access the file system with their UIDs and GIDs. If not specified, the default value is `root-squash`.")
    anongid: Optional[StrictStr] = Field(default=None, description="Any user whose GID is affected by an `access` of `root_squash` or `all_squash` will have their GID mapped to `anongid`. The default `anongid` is null, which means 65534. Use \"\" to clear. This value is ignored when user mapping is enabled.")
    anonuid: Optional[StrictStr] = Field(default=None, description="Any user whose UID is affected by an `access` of `root_squash` or `all_squash` will have their UID mapped to `anonuid`. The default `anonuid` is null, which means 65534. Use \"\" to clear.")
    client: Optional[StrictStr] = Field(default=None, description="Specifies which clients are given access. Valid values include `IP`, `IP mask`, or `hostname`. The default is `*` if not specified.")
    nfs_version: Optional[conlist(StrictStr)] = Field(default=None, description="NFS protocol version allowed for the export. Valid values are `nfsv3` and `nfsv4`. If not specified, defaults to `nfsv3`.")
    permission: Optional[StrictStr] = Field(default=None, description="Specifies which read-write client access permissions are allowed for the export. Values include `rw` and `ro`. The default value is `rw` if not specified.")
    security: Optional[conlist(StrictStr)] = Field(default=None, description="The security flavors to use for accessing files on this mount point. Values include `auth_sys`, `krb5`, `krb5i`, and `krb5p`. If the server does not support the requested flavor, the mount operation fails. This operation updates all rules of the specified policy. If `auth_sys`, the client is trusted to specify the identity of the user. If `krb5`, cryptographic proof of the identity of the user is provided in each RPC request. This provides strong verification of the identity of users accessing data on the server. Note that additional configuration besides adding this mount option is required to enable Kerberos security. If `krb5i`, integrity checking is added to krb5. This ensures the data has not been tampered with. If `krb5p`, integrity checking and encryption is added to krb5. This is the most secure setting, but it also involves the most performance overhead.")
    __properties = ["access", "anongid", "anonuid", "client", "nfs_version", "permission", "security"]

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
    def from_json(cls, json_str: str) -> PolicyrulenfsclientpostRules:
        """Create an instance of PolicyrulenfsclientpostRules from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> PolicyrulenfsclientpostRules:
        """Create an instance of PolicyrulenfsclientpostRules from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return PolicyrulenfsclientpostRules.parse_obj(obj)

        _obj = PolicyrulenfsclientpostRules.construct(_fields_set=None, **{
            "access": obj.get("access"),
            "anongid": obj.get("anongid"),
            "anonuid": obj.get("anonuid"),
            "client": obj.get("client"),
            "nfs_version": obj.get("nfs_version"),
            "permission": obj.get("permission"),
            "security": obj.get("security")
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

