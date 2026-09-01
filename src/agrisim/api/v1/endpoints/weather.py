import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from agrisim.core.database import get_db
from agrisim.schemas.weather import WeatherCreate, WeatherResponse
from agrisim.schemas.envelope import ResponseEnvelope
from agrisim.services import weather as weather_service, field as field_service

router = APIRouter(prefix="/fields/{field_id}/weather", tags=["Weather Telemetry"])


@router.post(
    "/",
    response_model=ResponseEnvelope[WeatherResponse],
    status_code=status.HTTP_201_CREATED,
)
def add_weather_data(
    field_id: uuid.UUID, weather_in: WeatherCreate, db: Session = Depends(get_db)
):
    # Verify the field exists first
    field = field_service.get_field_by_id(db=db, field_id=field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    db_weather = weather_service.record_weather(
        db=db, field_id=field_id, weather_in=weather_in
    )
    return ResponseEnvelope(
        status="success",
        code=201,
        message="Weather telemetry recorded successfully",
        data=db_weather,
    )


@router.get("/", response_model=ResponseEnvelope[List[WeatherResponse]])
def get_weather_data(
    field_id: uuid.UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    field = field_service.get_field_by_id(db=db, field_id=field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    records = weather_service.get_field_weather(
        db=db, field_id=field_id, skip=skip, limit=limit
    )
    return ResponseEnvelope(
        status="success",
        code=200,
        message="Weather records retrieved successfully",
        data=records,
    )
