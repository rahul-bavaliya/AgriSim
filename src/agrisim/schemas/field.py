# src/agrisim/schemas/field.py
from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field as PydanticField, field_validator
from shapely.geometry import shape, mapping
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape


class FieldBase(BaseModel):
    name: str = PydanticField(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the field",
        examples=["North Valley Pasture"],
    )
    total_acres: Optional[float] = PydanticField(
        None,
        gt=0,
        description="Total acreage of the field (auto-calculated if omitted)",
        examples=[125.5],
    )
    boundary: Any = PydanticField(
        ...,
        description="Polygon boundary coordinates or GeoJSON dictionary",
        examples=[
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [50.462480, -104.480302],
                        [50.462507, -104.469316],
                        [50.455384, -104.469268],
                        [50.455442, -104.480193],
                        [50.462480, -104.480302],
                    ]
                ],
            }
        ],
    )


class FieldCreate(FieldBase):
    @field_validator("boundary", mode="before")
    @classmethod
    def validate_boundary_input(cls, v: Any) -> Any:
        """Ensure incoming GeoJSON dict is valid."""
        if isinstance(v, dict):
            try:
                # Just validate that shapely can read it, but return the dict
                shape(v)
                return v
            except Exception as e:
                raise ValueError(f"Invalid GeoJSON boundary format: {e}")
        return v


class FieldUpdate(BaseModel):
    name: Optional[str] = PydanticField(None, min_length=1, max_length=255)
    total_acres: Optional[float] = PydanticField(None, gt=0)
    boundary: Optional[Any] = PydanticField(
        None,  # <-- Change this from ... to None
        description="Polygon boundary coordinates or GeoJSON dictionary",
        examples=[
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [50.462480, -104.480302],
                        [50.462507, -104.469316],
                        [50.455384, -104.469268],
                        [50.455442, -104.480193],
                        [50.462480, -104.480302],
                    ]
                ],
            }
        ],
    )

    @field_validator("boundary", mode="before")
    @classmethod
    def validate_boundary_input(cls, v: Any) -> Any:
        # If boundary is None (not provided in update), skip validation
        if v is None:
            return None
        if isinstance(v, dict):
            try:
                shape(v)
                return v
            except Exception as e:
                raise ValueError(f"Invalid GeoJSON boundary format: {e}")
        return v


class FieldResponse(FieldBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None  # Make it optional with a default of None

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    @field_validator("boundary", mode="before")
    @classmethod
    def parse_boundary(cls, v: Any) -> Any:
        """Convert database WKBElement object back into a standard GeoJSON dictionary."""
        if isinstance(v, WKBElement):
            polygon = to_shape(v)
            return mapping(polygon)
        return v
