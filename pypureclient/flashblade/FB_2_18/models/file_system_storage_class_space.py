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
from pypureclient.flashblade.FB_2_18.models.space import Space


class FileSystemStorageClassSpace(BaseModel):
    """
    FileSystemStorageClassSpace
    """
    id: Optional[StrictStr] = Field(default=None, description="A non-modifiable, globally unique ID chosen by the system.")
    name: Optional[StrictStr] = Field(default=None, description="Name of the object (e.g., a file system or snapshot).")
    space: Optional[Space] = None
    storage_class: Optional[StrictStr] = Field(default=None, description="The storage class type of the space information, either `S500X-S` (speed) or `S500X-A` (archival).")
    time: Optional[StrictInt] = Field(default=None, description="Sample time in milliseconds since UNIX epoch.")
    __properties = ["id", "name", "space", "storage_class", "time"]

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
            ])
        none_fields: Set[str] = set()
        for _field in self.__fields__.keys():
            if super().__getattribute__(_field) is None:
                none_fields.add(_field)

        _dict = self.dict(by_alias=True, exclude=excluded_fields, exclude_none=True)
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
    def from_json(cls, json_str: str) -> FileSystemStorageClassSpace:
        """Create an instance of FileSystemStorageClassSpace from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> FileSystemStorageClassSpace:
        """Create an instance of FileSystemStorageClassSpace from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return FileSystemStorageClassSpace.parse_obj(obj)

        _obj = FileSystemStorageClassSpace.construct(_fields_set=None, **{
            "id": obj.get("id"),
            "name": obj.get("name"),
            "space": Space.from_dict(obj.get("space")) if obj.get("space") is not None else None,
            "storage_class": obj.get("storage_class"),
            "time": obj.get("time")
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

