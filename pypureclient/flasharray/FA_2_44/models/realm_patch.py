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
from pydantic import BaseModel, Field, StrictBool, StrictStr, conint
from pypureclient.flasharray.FA_2_44.models.container_qos import ContainerQos


class RealmPatch(BaseModel):
    """
    RealmPatch
    """
    name: Optional[StrictStr] = Field(default=None, description="The new name for the resource.")
    destroyed: Optional[StrictBool] = Field(default=None, description="If set to `true`, the realm will be destroyed and pending eradication. The `time_remaining` value displays the amount of time left until the destroyed realm is permanently eradicated. A realm can only be destroyed if it is empty or destroy_contents is set to true. Before the `time_remaining` period has elapsed, the destroyed realm can be recovered by setting `destroyed=false`. Once the `time_remaining` period has elapsed, the realm is permanently eradicated and can no longer be recovered.")
    qos: Optional[ContainerQos] = Field(default=None, description="Sets QoS limits.")
    quota_limit: Optional[conint(strict=True, le=4503599627370496, ge=1048576)] = Field(default=None, description="The logical quota limit of the realm, measured in bytes.")
    __properties = ["name", "destroyed", "qos", "quota_limit"]

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
        # override the default output from pydantic by calling `to_dict()` of qos
        if _include_in_dict('qos', include_readonly, excluded_fields, none_fields):
            _dict['qos'] = self.qos.to_dict(include_readonly=include_readonly)
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
    def from_json(cls, json_str: str) -> RealmPatch:
        """Create an instance of RealmPatch from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> RealmPatch:
        """Create an instance of RealmPatch from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return RealmPatch.parse_obj(obj)

        _obj = RealmPatch.construct(_fields_set=None, **{
            "name": obj.get("name"),
            "destroyed": obj.get("destroyed"),
            "qos": ContainerQos.from_dict(obj.get("qos")) if obj.get("qos") is not None else None,
            "quota_limit": obj.get("quota_limit")
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

