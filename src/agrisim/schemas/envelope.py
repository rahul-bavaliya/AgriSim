from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class ResponseEnvelope(BaseModel, Generic[T]):
    status: str = "success"  # "success" or "error"
    code: int = 200  # HTTP status code
    message: str = "Success"  # Human-readable description
    data: Optional[T] = None  # The actual payload (or null on error)
