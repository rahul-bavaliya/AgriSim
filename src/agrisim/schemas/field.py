import uuid
from typing import Any, Dict, Optional
from geoalchemy2.shape import to_shape
from pydantic import BaseModel, ConfigDict, Field, field_validator
from shapely.geometry import mapping


class FieldCreate(BaseModel):
    name: str = Field(..., examples=["North Valley Farm"])
    # owner_id: uuid.UUID = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])
    total_acres: float = Field(..., examples=[150.5])
    boundary: Dict[str, Any] = Field(
        ...,
        examples=[
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-93.63, 42.02],
                        [-93.62, 42.02],
                        [-93.62, 42.01],
                        [-93.63, 42.01],
                        [-93.63, 42.02],
                    ]
                ],
            }
        ],
    )


class FieldUpdate(BaseModel):
    name: Optional[str] = Field(None, examples=["South Valley Farm"])
    total_acres: Optional[float] = Field(None, examples=[125.0])
    boundary: Optional[Dict[str, Any]] = Field(
        None,
        examples=[
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-93.2, 44.9],
                        [-93.1, 44.9],
                        [-93.1, 44.8],
                        [-93.2, 44.8],
                        [-93.2, 44.9],
                    ]
                ],
            }
        ],
    )


class FieldResponse(BaseModel):
    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    total_acres: float
    boundary: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("boundary", mode="before")
    @classmethod
    def assemble_boundary(cls, v: Any) -> Any:
        if isinstance(v, dict):
            return v
        try:
            shape = to_shape(v)
            return mapping(shape)
        except Exception:
            return v
