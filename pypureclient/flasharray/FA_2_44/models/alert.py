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
from pypureclient.flasharray.FA_2_44.models.fixed_reference import FixedReference


class Alert(BaseModel):
    """
    Alert
    """
    id: Optional[StrictStr] = Field(default=None, description="A globally unique, system-generated ID. The ID cannot be modified and cannot refer to another resource.")
    name: Optional[StrictStr] = Field(default=None, description="A locally unique, system-generated name. The name cannot be modified.")
    context: Optional[FixedReference] = Field(default=None, description="The context in which the operation was performed. Valid values include a reference to any array which is a member of the same fleet. If the array is not a member of a fleet, `context` will always implicitly be set to the array that received the request. Other parameters provided with the request, such as names of volumes or snapshots, are resolved relative to the provided `context`.")
    actual: Optional[StrictStr] = Field(default=None, description="Actual condition at the time the alert is created.")
    category: Optional[StrictStr] = Field(default=None, description="The category of the alert. Valid values include `array`, `hardware` and `software`.")
    closed: Optional[StrictInt] = Field(default=None, description="The time the alert was closed in milliseconds since the UNIX epoch.")
    code: Optional[StrictInt] = Field(default=None, description="The code number of the alert.")
    component_name: Optional[StrictStr] = Field(default=None, description="The name of the component that generated the alert.")
    component_type: Optional[StrictStr] = Field(default=None, description="The type of component that generated the alert.")
    created: Optional[StrictInt] = Field(default=None, description="The time the alert was created in milliseconds since the UNIX epoch.")
    description: Optional[StrictStr] = Field(default=None, description="A short description of the alert.")
    expected: Optional[StrictStr] = Field(default=None, description="Expected state or threshold under normal conditions.")
    flagged: Optional[StrictBool] = Field(default=None, description="If set to `true`, the message is flagged. Important messages can can be flagged and listed separately.")
    issue: Optional[StrictStr] = Field(default=None, description="Information about the alert cause.")
    knowledge_base_url: Optional[StrictStr] = Field(default=None, description="The URL of the relevant knowledge base page.")
    notified: Optional[StrictInt] = Field(default=None, description="The time the most recent alert notification was sent in milliseconds since the UNIX epoch.")
    severity: Optional[StrictStr] = Field(default=None, description="The severity level of the alert. Valid values include `info`, `warning`, `critical`, and `hidden`.")
    state: Optional[StrictStr] = Field(default=None, description="The current state of the alert. Valid values include `open`, `closing`, and `closed`.")
    summary: Optional[StrictStr] = Field(default=None, description="A summary of the alert.")
    updated: Optional[StrictInt] = Field(default=None, description="The time the alert was last updated in milliseconds since the UNIX epoch.")
    __properties = ["id", "name", "context", "actual", "category", "closed", "code", "component_name", "component_type", "created", "description", "expected", "flagged", "issue", "knowledge_base_url", "notified", "severity", "state", "summary", "updated"]

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
                "actual",
                "category",
                "closed",
                "code",
                "component_name",
                "component_type",
                "created",
                "description",
                "expected",
                "issue",
                "knowledge_base_url",
                "notified",
                "severity",
                "state",
                "summary",
                "updated",
            ])
        none_fields: Set[str] = set()
        for _field in self.__fields__.keys():
            if super().__getattribute__(_field) is None:
                none_fields.add(_field)

        _dict = self.dict(by_alias=True, exclude=excluded_fields, exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of context
        if _include_in_dict('context', include_readonly, excluded_fields, none_fields):
            _dict['context'] = self.context.to_dict(include_readonly=include_readonly)
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
    def from_json(cls, json_str: str) -> Alert:
        """Create an instance of Alert from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> Alert:
        """Create an instance of Alert from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return Alert.parse_obj(obj)

        _obj = Alert.construct(_fields_set=None, **{
            "id": obj.get("id"),
            "name": obj.get("name"),
            "context": FixedReference.from_dict(obj.get("context")) if obj.get("context") is not None else None,
            "actual": obj.get("actual"),
            "category": obj.get("category"),
            "closed": obj.get("closed"),
            "code": obj.get("code"),
            "component_name": obj.get("component_name"),
            "component_type": obj.get("component_type"),
            "created": obj.get("created"),
            "description": obj.get("description"),
            "expected": obj.get("expected"),
            "flagged": obj.get("flagged"),
            "issue": obj.get("issue"),
            "knowledge_base_url": obj.get("knowledge_base_url"),
            "notified": obj.get("notified"),
            "severity": obj.get("severity"),
            "state": obj.get("state"),
            "summary": obj.get("summary"),
            "updated": obj.get("updated")
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

