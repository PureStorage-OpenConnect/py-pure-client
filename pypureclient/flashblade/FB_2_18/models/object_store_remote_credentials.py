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
from pydantic import BaseModel, Field, StrictStr
from pypureclient.flashblade.FB_2_18.models.fixed_reference import FixedReference
from pypureclient.flashblade.FB_2_18.models.reference import Reference


class ObjectStoreRemoteCredentials(BaseModel):
    """
    ObjectStoreRemoteCredentials
    """
    id: Optional[StrictStr] = Field(default=None, description="A non-modifiable, globally unique ID chosen by the system.")
    name: Optional[StrictStr] = Field(default=None, description="A name chosen by the user. Can be changed. Must be locally unique.")
    context: Optional[Reference] = Field(default=None, description="The context in which the operation was performed. Valid values include a reference to any array which is a member of the same fleet. If the array is not a member of a fleet, `context` will always implicitly be set to the array that received the request. Other parameters provided with the request, such as names of volumes or snapshots, are resolved relative to the provided `context`.")
    access_key_id: Optional[StrictStr] = Field(default=None, description="Access Key ID to be used when connecting to a remote object store.")
    remote: Optional[FixedReference] = Field(default=None, description="Reference to the associated remote, which can either be a `target` or remote `array`. If it is an `array`, then the `resource-type` field will not be populated.")
    secret_access_key: Optional[StrictStr] = Field(default=None, description="Secret Access Key to be used when connecting to a remote object store.")
    __properties = ["id", "name", "context", "access_key_id", "remote", "secret_access_key"]

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
                "context",
            ])
        none_fields: Set[str] = set()
        for _field in self.__fields__.keys():
            if super().__getattribute__(_field) is None:
                none_fields.add(_field)

        _dict = self.dict(by_alias=True, exclude=excluded_fields, exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of context
        if _include_in_dict('context', include_readonly, excluded_fields, none_fields):
            _dict['context'] = self.context.to_dict(include_readonly=include_readonly)
        # override the default output from pydantic by calling `to_dict()` of remote
        if _include_in_dict('remote', include_readonly, excluded_fields, none_fields):
            _dict['remote'] = self.remote.to_dict(include_readonly=include_readonly)
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
    def from_json(cls, json_str: str) -> ObjectStoreRemoteCredentials:
        """Create an instance of ObjectStoreRemoteCredentials from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> ObjectStoreRemoteCredentials:
        """Create an instance of ObjectStoreRemoteCredentials from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return ObjectStoreRemoteCredentials.parse_obj(obj)

        _obj = ObjectStoreRemoteCredentials.construct(_fields_set=None, **{
            "id": obj.get("id"),
            "name": obj.get("name"),
            "context": Reference.from_dict(obj.get("context")) if obj.get("context") is not None else None,
            "access_key_id": obj.get("access_key_id"),
            "remote": FixedReference.from_dict(obj.get("remote")) if obj.get("remote") is not None else None,
            "secret_access_key": obj.get("secret_access_key")
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

