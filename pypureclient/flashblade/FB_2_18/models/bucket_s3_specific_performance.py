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

from typing import Optional, Union
from pydantic import BaseModel, Field, StrictInt, StrictStr, confloat, conint


class BucketS3SpecificPerformance(BaseModel):
    """
    BucketS3SpecificPerformance
    """
    id: Optional[StrictStr] = Field(default=None, description="A non-modifiable, globally unique ID chosen by the system.")
    name: Optional[StrictStr] = Field(default=None, description="Name of the object (e.g., a file system or snapshot).")
    others_per_sec: Optional[Union[confloat(ge=0, strict=True), conint(ge=0, strict=True)]] = Field(default=None, description="Other operations processed per second.")
    read_buckets_per_sec: Optional[Union[confloat(ge=0, strict=True), conint(ge=0, strict=True)]] = Field(default=None, description="Read buckets requests processed per second.")
    read_objects_per_sec: Optional[Union[confloat(ge=0, strict=True), conint(ge=0, strict=True)]] = Field(default=None, description="Read object requests processed per second.")
    time: Optional[StrictInt] = Field(default=None, description="Sample time in milliseconds since UNIX epoch.")
    usec_per_other_op: Optional[Union[confloat(ge=0, strict=True), conint(ge=0, strict=True)]] = Field(default=None, description="Average time, measured in microseconds, it takes the array to process other operations.")
    usec_per_read_bucket_op: Optional[Union[confloat(ge=0, strict=True), conint(ge=0, strict=True)]] = Field(default=None, description="Average time, measured in microseconds, it takes the array to process a read bucket request.")
    usec_per_read_object_op: Optional[Union[confloat(ge=0, strict=True), conint(ge=0, strict=True)]] = Field(default=None, description="Average time, measured in microseconds, it takes the array to process a read object request.")
    usec_per_write_bucket_op: Optional[Union[confloat(ge=0, strict=True), conint(ge=0, strict=True)]] = Field(default=None, description="Average time, measured in microseconds, it takes the array to process a write bucket request.")
    usec_per_write_object_op: Optional[Union[confloat(ge=0, strict=True), conint(ge=0, strict=True)]] = Field(default=None, description="Average time, measured in microseconds, it takes the array to process a write object request.")
    write_buckets_per_sec: Optional[Union[confloat(ge=0, strict=True), conint(ge=0, strict=True)]] = Field(default=None, description="Write buckets requests processed per second.")
    write_objects_per_sec: Optional[Union[confloat(ge=0, strict=True), conint(ge=0, strict=True)]] = Field(default=None, description="Write object requests processed per second.")
    __properties = ["id", "name", "others_per_sec", "read_buckets_per_sec", "read_objects_per_sec", "time", "usec_per_other_op", "usec_per_read_bucket_op", "usec_per_read_object_op", "usec_per_write_bucket_op", "usec_per_write_object_op", "write_buckets_per_sec", "write_objects_per_sec"]

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
                "others_per_sec",
                "read_buckets_per_sec",
                "read_objects_per_sec",
                "time",
                "usec_per_other_op",
                "usec_per_read_bucket_op",
                "usec_per_read_object_op",
                "usec_per_write_bucket_op",
                "usec_per_write_object_op",
                "write_buckets_per_sec",
                "write_objects_per_sec",
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
    def from_json(cls, json_str: str) -> BucketS3SpecificPerformance:
        """Create an instance of BucketS3SpecificPerformance from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> BucketS3SpecificPerformance:
        """Create an instance of BucketS3SpecificPerformance from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return BucketS3SpecificPerformance.parse_obj(obj)

        _obj = BucketS3SpecificPerformance.construct(_fields_set=None, **{
            "id": obj.get("id"),
            "name": obj.get("name"),
            "others_per_sec": obj.get("others_per_sec"),
            "read_buckets_per_sec": obj.get("read_buckets_per_sec"),
            "read_objects_per_sec": obj.get("read_objects_per_sec"),
            "time": obj.get("time"),
            "usec_per_other_op": obj.get("usec_per_other_op"),
            "usec_per_read_bucket_op": obj.get("usec_per_read_bucket_op"),
            "usec_per_read_object_op": obj.get("usec_per_read_object_op"),
            "usec_per_write_bucket_op": obj.get("usec_per_write_bucket_op"),
            "usec_per_write_object_op": obj.get("usec_per_write_object_op"),
            "write_buckets_per_sec": obj.get("write_buckets_per_sec"),
            "write_objects_per_sec": obj.get("write_objects_per_sec")
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

