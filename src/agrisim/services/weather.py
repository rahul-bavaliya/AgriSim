from uuid import UUID

from sqlalchemy.orm import Session
from typing import List, Optional

from agrisim.models.weather import WeatherModel
from agrisim.schemas.weather import WeatherCreate


class WeatherService:
    @staticmethod
    def create_weather_record(db: Session, weather_in: WeatherCreate) -> WeatherModel:
        db_weather = WeatherModel(
            field_id=weather_in.field_id,
            temperature_celsius=weather_in.temperature_celsius,
            humidity_percentage=weather_in.humidity_percentage,
            precipitation_mm=weather_in.precipitation_mm,
            wind_speed_kmh=weather_in.wind_speed_kmh,
            condition=weather_in.condition,
        )
        db.add(db_weather)
        db.commit()
        db.refresh(db_weather)
        return db_weather

    @staticmethod
    def get_weather_by_field(
        db: Session, field_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[WeatherModel]:
        return (
            db.query(WeatherModel)
            .filter(WeatherModel.field_id == field_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
