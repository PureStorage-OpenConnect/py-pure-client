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
from pydantic import BaseModel, Field, StrictBool, StrictInt, StrictStr


class Hardware(BaseModel):
    """
    Hardware
    """
    name: Optional[StrictStr] = Field(default=None, description="A locally unique, system-generated name. The name cannot be modified.")
    details: Optional[StrictStr] = Field(default=None, description="Details about the status of the component if not healthy.")
    identify_enabled: Optional[StrictBool] = Field(default=None, description="If `true`, the ID LED is lit to visually identify the component.")
    index: Optional[StrictInt] = Field(default=None, description="Number that identifies the relative position of a hardware component within the array.")
    model: Optional[StrictStr] = Field(default=None, description="Model number of the hardware component.")
    serial: Optional[StrictStr] = Field(default=None, description="Serial number of the hardware component.")
    slot: Optional[StrictInt] = Field(default=None, description="Slot number occupied by the PCI Express card that hosts the component.")
    speed: Optional[StrictInt] = Field(default=None, description="Speed (in bytes per second) at which the component is operating.")
    status: Optional[StrictStr] = Field(default=None, description="Component status. Values include `critical`, `healthy`, `identifying`, `unhealthy`, `unknown`, and `unused`.")
    temperature: Optional[StrictInt] = Field(default=None, description="Temperature (in degrees Celsius) reported by the component.")
    type: Optional[StrictStr] = Field(default=None, description="Type of hardware component. Values include `bay`, `ct`, `ch`, `eth`, `fan`, `fb`, `fc`, `fm`, `ib`, `iom`, `nvb`, `pwr`, `sas`, `sh`, and `tmp`.")
    voltage: Optional[StrictInt] = Field(default=None, description="Voltage (in Volts) reported by the component.")
    __properties = ["name", "details", "identify_enabled", "index", "model", "serial", "slot", "speed", "status", "temperature", "type", "voltage"]

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
                "details",
                "identify_enabled",
                "index",
                "model",
                "serial",
                "slot",
                "speed",
                "status",
                "temperature",
                "type",
                "voltage",
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
    def from_json(cls, json_str: str) -> Hardware:
        """Create an instance of Hardware from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> Hardware:
        """Create an instance of Hardware from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return Hardware.parse_obj(obj)

        _obj = Hardware.construct(_fields_set=None, **{
            "name": obj.get("name"),
            "details": obj.get("details"),
            "identify_enabled": obj.get("identify_enabled"),
            "index": obj.get("index"),
            "model": obj.get("model"),
            "serial": obj.get("serial"),
            "slot": obj.get("slot"),
            "speed": obj.get("speed"),
            "status": obj.get("status"),
            "temperature": obj.get("temperature"),
            "type": obj.get("type"),
            "voltage": obj.get("voltage")
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

