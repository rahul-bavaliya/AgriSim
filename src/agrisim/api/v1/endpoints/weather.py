from typing import List
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from agrisim.core.database import get_db
from agrisim.schemas.envelope import ResponseEnvelope
from agrisim.schemas.weather import WeatherCreate, WeatherResponse
from agrisim.services.weather import WeatherService

router = APIRouter(prefix="/weather", tags=["weather"])


@router.post(
    "/",
    response_model=ResponseEnvelope[WeatherResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_weather_record(weather_in: WeatherCreate, db: Session = Depends(get_db)):
    """Log a new weather record for a specific agricultural field."""
    weather = WeatherService.create_weather_record(db=db, weather_in=weather_in)
    return ResponseEnvelope(
        status="success",
        code=status.HTTP_201_CREATED,
        message="Weather record created successfully",
        data=WeatherResponse.model_validate(weather),
    )


@router.get("/field/{field_id}", response_model=ResponseEnvelope[List[WeatherResponse]])
def get_weather_by_field(
    field_id: uuid.UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Retrieve historical weather records for a specific agricultural field."""
    weather_records = WeatherService.get_weather_by_field(
        db=db, field_id=field_id, skip=skip, limit=limit
    )
    return ResponseEnvelope(
        status="success",
        code=status.HTTP_200_OK,
        message="Weather records retrieved successfully",
        data=[WeatherResponse.model_validate(w) for w in weather_records],
    )
