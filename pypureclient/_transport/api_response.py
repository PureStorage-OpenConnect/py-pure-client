from typing import Optional, Dict, Any

try:
    from pydantic.v1 import Field, StrictStr, StrictInt, StrictBytes
except ModuleNotFoundError:
    from pydantic import Field, StrictStr, StrictInt, StrictBytes

class ApiResponse:
    """
    API response object
    """

    status_code: Optional[StrictInt] = Field(None, description="HTTP status code")
    headers: Optional[Dict[StrictStr, StrictStr]] = Field(None, description="HTTP headers")
    data: Optional[Any] = Field(None, description="Deserialized data given the data type")
    raw_data: Optional[Any] = Field(None, description="Raw data (HTTP response body)")

    def __init__(self,
                 status_code=None,
                 headers=None,
                 data=None,
                 raw_data=None) -> None:
        self.status_code = status_code
        self.headers = headers
        self.data = data
        self.raw_data = raw_data