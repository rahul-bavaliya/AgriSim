import uuid
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class FieldCreate(BaseModel):
    name: str = Field(..., examples=["North Valley Farm"])
    owner_id: uuid.UUID = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])
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


class FieldResponse(BaseModel):
    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    total_acres: float

    class Config:
        from_attributes = True
