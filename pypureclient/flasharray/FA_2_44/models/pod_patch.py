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
from pydantic import BaseModel, Field, StrictBool, StrictStr, conint, conlist
from pypureclient.flasharray.FA_2_44.models.reference import Reference


class PodPatch(BaseModel):
    """
    PodPatch
    """
    id: Optional[StrictStr] = Field(default=None, description="A globally unique, system-generated ID. The ID cannot be modified and cannot refer to another resource.")
    name: Optional[StrictStr] = Field(default=None, description="A user-specified name. The name must be locally unique and can be changed.")
    destroyed: Optional[StrictBool] = Field(default=None, description="If set to `true`, the pod has been destroyed and is pending eradication. The `time_remaining` value displays the amount of time left until the destroyed pod is permanently eradicated. A pod can only be destroyed if it is empty, so before destroying a pod, ensure all volumes and protection groups inside the pod have been either moved out of the pod or destroyed. A stretched pod cannot be destroyed unless you unstretch it first. Before the `time_remaining` period has elapsed, the destroyed pod can be recovered by setting `destroyed=false`. Once the `time_remaining` period has elapsed, the pod is permanently eradicated and can no longer be recovered.")
    failover_preferences: Optional[conlist(Reference)] = Field(default=None, description="Determines which array within a stretched pod should be given priority to stay online should the arrays ever lose contact with each other. The current array and any peer arrays that are connected to the current array for synchronous replication can be added to a pod for failover preference. By default, `failover_preferences=null`, meaning no arrays have been configured for failover preference. Enter multiple arrays in comma-separated format.")
    ignore_usage: Optional[StrictBool] = Field(default=None, description="Set to `true` to set a `quota_limit` that is lower than the existing usage. This ensures that no new volumes can be created until the existing usage drops below the `quota_limit`. If not specified, defaults to `false`.")
    mediator: Optional[StrictStr] = Field(default=None, description="Sets the URL of the mediator for this pod, replacing the URL of the current mediator. By default, the Pure1 Cloud Mediator (`purestorage`) serves as the mediator.")
    quota_limit: Optional[conint(strict=True, le=4503599627370496, ge=1048576)] = Field(default=None, description="The logical quota limit of the pod, measured in bytes. Must be a multiple of 512.")
    requested_promotion_state: Optional[StrictStr] = Field(default=None, description="Patch `requested_promotion_state` to `demoted` to demote the pod so that it can be used as a link target for continuous replication between pods. Demoted pods do not accept write requests, and a destroyed version of the pod with `undo-demote` appended to the pod name is created on the array with the state of the pod when it was in the promoted state. Patch `requested_promotion_state` to `promoted` to start the process of promoting the pod. The `promotion_status` indicates when the pod has been successfully promoted. Promoted pods stop incorporating replicated data from the source pod and start accepting write requests. The replication process does not stop when the source pod continues replicating data to the pod. The space consumed by the unique replicated data is tracked by the `space.journal` field of the pod.")
    __properties = ["id", "name", "destroyed", "failover_preferences", "ignore_usage", "mediator", "quota_limit", "requested_promotion_state"]

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
            ])
        none_fields: Set[str] = set()
        for _field in self.__fields__.keys():
            if super().__getattribute__(_field) is None:
                none_fields.add(_field)

        _dict = self.dict(by_alias=True, exclude=excluded_fields, exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of each item in failover_preferences (list)
        if _include_in_dict('failover_preferences', include_readonly, excluded_fields, none_fields):
            _items = []
            for _item in self.failover_preferences:
                if _item:
                    _items.append(_item.to_dict(include_readonly=include_readonly))
            _dict['failover_preferences'] = _items
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
    def from_json(cls, json_str: str) -> PodPatch:
        """Create an instance of PodPatch from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> PodPatch:
        """Create an instance of PodPatch from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return PodPatch.parse_obj(obj)

        _obj = PodPatch.construct(_fields_set=None, **{
            "id": obj.get("id"),
            "name": obj.get("name"),
            "destroyed": obj.get("destroyed"),
            "failover_preferences": [Reference.from_dict(_item) for _item in obj.get("failover_preferences")] if obj.get("failover_preferences") is not None else None,
            "ignore_usage": obj.get("ignore_usage"),
            "mediator": obj.get("mediator"),
            "quota_limit": obj.get("quota_limit"),
            "requested_promotion_state": obj.get("requested_promotion_state")
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

