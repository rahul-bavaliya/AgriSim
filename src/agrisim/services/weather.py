import uuid
from sqlalchemy.orm import Session
from agrisim.models.weather import WeatherTelemetryModel
from agrisim.schemas.schemas import WeatherCreate


def record_weather(
    db: Session, field_id: uuid.UUID, weather_in: WeatherCreate
) -> WeatherTelemetryModel:
    db_weather = WeatherTelemetryModel(
        field_id=field_id,
        temperature=weather_in.temperature,
        rainfall=weather_in.rainfall,
        soil_moisture=weather_in.soil_moisture,
    )
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    return db_weather


def get_field_weather(
    db: Session, field_id: uuid.UUID, skip: int = 0, limit: int = 100
):
    return (
        db.query(WeatherTelemetryModel)
        .filter(WeatherTelemetryModel.field_id == field_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
