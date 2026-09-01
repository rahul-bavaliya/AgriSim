import datetime
from pydantic import BaseModel, Field

class WeatherCreate(BaseModel):
    date: datetime.date
    temperature_max: float = Field(..., examples=[30.5])
    temperature_min: float = Field(..., examples=[15.2])
    precipitation_mm: float = Field(..., examples=[4.2])
    solar_radiation: float = Field(..., examples=[18.5])

class WeatherResponse(BaseModel):
    id: int
    field_id: str
    date: datetime.date
    temperature_max: float
    temperature_min: float
    precipitation_mm: float
    solar_radiation: float

    class Config:
        from_attributes = True