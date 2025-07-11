try:
    from pydantic.v1 import BaseModel, Field, StrictStr
except ModuleNotFoundError:
    from pydantic import BaseModel, Field, StrictStr

from typing import List, Optional, Union

class ReferenceType(BaseModel):
    """
    ReferenceType

    It's used for reference arg on api function. This allows user to pass collections of Model objects
    to the method without transforming them to ids or names.
    """

    id: Optional[StrictStr] = Field(default=None, description="A globally unique, system-generated ID. The ID cannot be modified. ")
    name: Optional[StrictStr] = Field(default=None, description="The resource name, such as volume name, pod name, snapshot name, and so on. ")
    __properties: List[str] = ["id", "name"]

    class Config:
        """Pydantic configuration"""
        allow_population_by_field_name = True
        validate_assignment = True

def quoteString(s):
    r"""Quote string according to
    https://wiki.purestorage.com/display/UXReviewers/Filtering

    >>> quote("a")
    "'a'"
    >>> quote("a\\b")
    "'a\\\\b'"
    >>> quote("a\\b")
    "'a\\\\b'"
    >>> quote("a'b")
    "'a\\'b'"
    >>> quote(None)
    None
    """
    if s is None:
        return None
    quoted = str(s).replace("\\", "\\\\").replace("'", "\\'")
    return "'{}'".format(quoted)


def quoteStrings(s):
    if s is None:
        return None
    return [quoteString(x) for x in s]


def quote_string_parameter(input: Union[str, List[str]]) -> Union[str, List[str]]:
    return quoteStrings(input) if isinstance(input, list) else quoteString(input)