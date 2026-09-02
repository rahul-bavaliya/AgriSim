from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from agrisim.core.database import Base


class WeatherModel(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    temperature_celsius = Column(Float, nullable=False)
    humidity_percentage = Column(Float, nullable=False)
    precipitation_mm = Column(Float, default=0.0, nullable=False)
    wind_speed_kmh = Column(Float, default=0.0, nullable=False)
    condition = Column(String(50), nullable=True)  # e.g., "Sunny", "Rainy", "Cloudy"

    # Relationship back to Field model
    field = relationship("FieldModel", back_populates="weather_records")
