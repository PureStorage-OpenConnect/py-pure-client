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
from pydantic import BaseModel, Field, StrictBool, StrictStr
from pypureclient.flashblade.FB_2_18.models.bucket_eradication_config import BucketEradicationConfig
from pypureclient.flashblade.FB_2_18.models.object_lock_config_request_body import ObjectLockConfigRequestBody
from pypureclient.flashblade.FB_2_18.models.reference_writable import ReferenceWritable


class BucketPost(BaseModel):
    """
    BucketPost
    """
    account: Optional[ReferenceWritable] = Field(default=None, description="The account name for bucket creation.")
    bucket_type: Optional[StrictStr] = Field(default=None, description="The bucket type for the bucket. Valid values are `classic`, and `multi-site-writable`. Default value is `multi-site-writable`.")
    eradication_config: Optional[BucketEradicationConfig] = None
    hard_limit_enabled: Optional[StrictBool] = Field(default=None, description="If set to `true`, the bucket's size, as defined by `quota_limit`, is used as a hard limit quota. If set to `false`, a hard limit quota will not be applied to the bucket, but soft quota alerts will still be sent if the bucket has a value set for `quota_limit`. If not specified, defaults to the value of `bucket_defaults.hard_limit_enabled` of the object store account this bucket is associated with.")
    object_lock_config: Optional[ObjectLockConfigRequestBody] = None
    quota_limit: Optional[StrictStr] = Field(default=None, description="The effective quota limit applied against the size of the bucket, displayed in bytes. If set to an empty string (`\"\"`), the bucket is unlimited in size. If not specified, defaults to the value of `bucket_defaults.quota_limit` of the object store account this bucket is associated with.")
    retention_lock: Optional[StrictStr] = Field(default=None, description="If set to `ratcheted`, then `object_lock_config.default_retention_mode` cannot be changed if set to `compliance`. In this case, the value of `object_lock_config.default_retention` can only be increased and `object_lock_config.default_retention_mode` cannot be changed once set to `compliance`. Valid values are `unlocked` and `ratcheted`. If not specified, defaults to `unlocked`.")
    __properties = ["account", "bucket_type", "eradication_config", "hard_limit_enabled", "object_lock_config", "quota_limit", "retention_lock"]

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
        # override the default output from pydantic by calling `to_dict()` of account
        if _include_in_dict('account', include_readonly, excluded_fields, none_fields):
            _dict['account'] = self.account.to_dict(include_readonly=include_readonly)
        # override the default output from pydantic by calling `to_dict()` of eradication_config
        if _include_in_dict('eradication_config', include_readonly, excluded_fields, none_fields):
            _dict['eradication_config'] = self.eradication_config.to_dict(include_readonly=include_readonly)
        # override the default output from pydantic by calling `to_dict()` of object_lock_config
        if _include_in_dict('object_lock_config', include_readonly, excluded_fields, none_fields):
            _dict['object_lock_config'] = self.object_lock_config.to_dict(include_readonly=include_readonly)
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
    def from_json(cls, json_str: str) -> BucketPost:
        """Create an instance of BucketPost from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> BucketPost:
        """Create an instance of BucketPost from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return BucketPost.parse_obj(obj)

        _obj = BucketPost.construct(_fields_set=None, **{
            "account": ReferenceWritable.from_dict(obj.get("account")) if obj.get("account") is not None else None,
            "bucket_type": obj.get("bucket_type"),
            "eradication_config": BucketEradicationConfig.from_dict(obj.get("eradication_config")) if obj.get("eradication_config") is not None else None,
            "hard_limit_enabled": obj.get("hard_limit_enabled"),
            "object_lock_config": ObjectLockConfigRequestBody.from_dict(obj.get("object_lock_config")) if obj.get("object_lock_config") is not None else None,
            "quota_limit": obj.get("quota_limit"),
            "retention_lock": obj.get("retention_lock")
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

