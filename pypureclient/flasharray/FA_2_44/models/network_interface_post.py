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
from pypureclient.flasharray.FA_2_44.models.networkinterfacepost_eth import NetworkinterfacepostEth
from pypureclient.flasharray.FA_2_44.models.reference import Reference


class NetworkInterfacePost(BaseModel):
    """
    NetworkInterfacePost
    """
    name: Optional[StrictStr] = Field(default=None, description="A locally unique, system-generated name. The name cannot be modified.")
    attached_servers: Optional[conlist(Reference, max_items=1)] = Field(default=None, description="Applicable only to Ethernet interfaces. List of servers to be associated with the specified network interface for data ingress. At most one server can be specified for each interface. To attach the network interface to a server, `name` or `id` of the desired server must be provided. When `attached_servers` field is not specified in the request, the network interface will be attached to the default `_array_server` instance. To create a network interface that is not attached to any server, an empty list `[]` should be passed to the `attached_servers` field.")
    eth: Optional[NetworkinterfacepostEth] = None
    services: Optional[conlist(StrictStr)] = Field(default=None, description="The services provided by the specified network interface or Fibre Channel port.")
    __properties = ["name", "attached_servers", "eth", "services"]

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
            ])
        none_fields: Set[str] = set()
        for _field in self.__fields__.keys():
            if super().__getattribute__(_field) is None:
                none_fields.add(_field)

        _dict = self.dict(by_alias=True, exclude=excluded_fields, exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of each item in attached_servers (list)
        if _include_in_dict('attached_servers', include_readonly, excluded_fields, none_fields):
            _items = []
            for _item in self.attached_servers:
                if _item:
                    _items.append(_item.to_dict(include_readonly=include_readonly))
            _dict['attached_servers'] = _items
        # override the default output from pydantic by calling `to_dict()` of eth
        if _include_in_dict('eth', include_readonly, excluded_fields, none_fields):
            _dict['eth'] = self.eth.to_dict(include_readonly=include_readonly)
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
    def from_json(cls, json_str: str) -> NetworkInterfacePost:
        """Create an instance of NetworkInterfacePost from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: dict) -> NetworkInterfacePost:
        """Create an instance of NetworkInterfacePost from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return NetworkInterfacePost.parse_obj(obj)

        _obj = NetworkInterfacePost.construct(_fields_set=None, **{
            "name": obj.get("name"),
            "attached_servers": [Reference.from_dict(_item) for _item in obj.get("attached_servers")] if obj.get("attached_servers") is not None else None,
            "eth": NetworkinterfacepostEth.from_dict(obj.get("eth")) if obj.get("eth") is not None else None,
            "services": obj.get("services")
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

