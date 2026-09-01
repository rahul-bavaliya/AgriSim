from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class WeatherBase(BaseModel):
    temperature_celsius: float = Field(..., description="Temperature in Celsius")
    humidity_percentage: float = Field(
        ..., ge=0.0, le=100.0, description="Humidity percentage"
    )
    precipitation_mm: float = Field(
        default=0.0, ge=0.0, description="Precipitation in mm"
    )
    wind_speed_kmh: float = Field(default=0.0, ge=0.0, description="Wind speed in km/h")
    condition: Optional[str] = Field(
        default=None, description="General weather condition (e.g., Sunny, Rainy)"
    )


class WeatherCreate(WeatherBase):
    field_id: UUID = Field(..., description="ID of the associated agricultural field")


class WeatherResponse(WeatherBase):
    id: int
    field_id: UUID
    date: datetime
    model_config = ConfigDict(from_attributes=True)
