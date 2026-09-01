import uuid
import datetime
from pydantic import BaseModel, Field


class WeatherCreate(BaseModel):
    temperature: float = Field(..., examples=[24.5])
    rainfall: float = Field(..., examples=[2.1])
    soil_moisture: float = Field(..., examples=[45.2])


class WeatherResponse(BaseModel):
    id: uuid.UUID
    field_id: uuid.UUID
    temperature: float
    rainfall: float
    soil_moisture: float
    recorded_at: datetime.datetime

    class Config:
        from_attributes = True
