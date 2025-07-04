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
from pydantic import BaseModel, Field, StrictBool, StrictInt, StrictStr, conint
from pypureclient.flasharray.FA_2_44.models.container_eradication_config import ContainerEradicationConfig
from pypureclient.flasharray.FA_2_44.models.container_qos import ContainerQos
from pypureclient.flasharray.FA_2_44.models.space_no_deprecated_physical_or_effective import SpaceNoDeprecatedPhysicalOrEffective


class Realm(BaseModel):
    """
    Realm
    """
    id: Optional[StrictStr] = Field(default=None, description="A globally unique, system-generated ID. The ID cannot be modified and cannot refer to another resource.")
    name: Optional[StrictStr] = Field(default=None, description="A user-specified name. The name must be locally unique and can be changed.")
    created: Optional[StrictInt] = Field(default=None, description="Creation timestamp of the realm.")
    destroyed: Optional[StrictBool] = Field(default=None, description="Returns a value of `true` if the realm has been destroyed and is pending eradication. The realm cannot be modified while it is in the destroyed state. The `time_remaining` value displays the amount of time left until the destroyed realm is permanently eradicated. Once eradication has begun, the realm can no longer be recovered. Before the `time_remaining` period has elapsed, the destroyed realm can be recovered through the PATCH method")
    eradication_config: Optional[ContainerEradicationConfig] = None
    qos: Optional[ContainerQos] = Field(default=None, description="Displays QoS limit information.")
    quota_limit: Optional[conint(strict=True, le=4503599627370496)] = Field(default=None, description="The logical quota limit of the realm, measured in bytes.")
    space: Optional[SpaceNoDeprecatedPhysicalOrEffective] = Field(default=None, description="Displays provisioned size and physical storage consumption information for the realm.")
    time_remaining: Optional[StrictInt] = Field(default=None, description="Time in milliseconds before the realm is eradicated. `null` if not destroyed.")
    __properties = ["id", "name", "created", "destroyed", "eradication_config", "qos", "quota_limit", "space", "time_remaining"]

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
                "created",
                "quota_limit",
                "time_remaining",
            ])
        none_fields: Set[str] = set()
        for _field in self.__fields__.keys():
            if super().__getattribute__(_field) is None:
                none_fields.add(_field)

        _dict = self.dict(by_alias=True, exclude=excluded_fields, exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of eradication_config
        if _include_in_dict('eradication_config', include_readonly, excluded_fields, none_fields):
            _dict['eradication_config'] = self.eradication_config.to_dict(include_readonly=include_readonly)
        # override the default output from pydantic by calling `to_dict()` of qos
        if _include_in_dict('qos', include_readonly, excluded_fields, none_fields):
            _dict['qos'] = self.qos.to_dict(include_readonly=include_readonly)
        # override the default output from pydantic by calling `to_dict()` of space
        if _include_in_dict('space', include_readonly, excluded_fields, none_fields):
            _dict['space'] = self.space.to_dict(include_readonly=include_readonly)
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
    def from_json(cls, json_str: str) -> Realm:
        """Create an instance of Realm from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> Realm:
        """Create an instance of Realm from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return Realm.parse_obj(obj)

        _obj = Realm.construct(_fields_set=None, **{
            "id": obj.get("id"),
            "name": obj.get("name"),
            "created": obj.get("created"),
            "destroyed": obj.get("destroyed"),
            "eradication_config": ContainerEradicationConfig.from_dict(obj.get("eradication_config")) if obj.get("eradication_config") is not None else None,
            "qos": ContainerQos.from_dict(obj.get("qos")) if obj.get("qos") is not None else None,
            "quota_limit": obj.get("quota_limit"),
            "space": SpaceNoDeprecatedPhysicalOrEffective.from_dict(obj.get("space")) if obj.get("space") is not None else None,
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

