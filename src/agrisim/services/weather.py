import uuid
from sqlalchemy.orm import Session
from agrisim.models.models import WeatherTelemetryModel
from agrisim.schemas.weather import WeatherCreate

def record_weather(db: Session, field_id: uuid.UUID, weather_in: WeatherCreate) -> WeatherTelemetryModel:
    db_weather = WeatherTelemetryModel(
        field_id=field_id,
        date=weather_in.date,
        temperature_max=weather_in.temperature_max,
        temperature_min=weather_in.temperature_min,
        precipitation_mm=weather_in.precipitation_mm,
        solar_radiation=weather_in.solar_radiation
    )
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    return db_weather

def get_field_weather(db: Session, field_id: uuid.UUID, skip: int = 0, limit: int = 100):
    return (
        db.query(WeatherTelemetryModel)
        .filter(WeatherTelemetryModel.field_id == field_id)
        .offset(skip)
        .limit(limit)
        .all()
    )