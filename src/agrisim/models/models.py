import uuid
import datetime
from typing import Any
from sqlalchemy import String, Float, Date, ForeignKey, DateTime, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from geoalchemy2 import Geometry
from agrisim.core.database import Base


class FieldModel(Base):
    __tablename__ = "fields"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    boundary = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326), nullable=False
    )
    total_acres: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    weather_telemetry = relationship(
        "WeatherTelemetryModel", back_populates="field", cascade="all, delete-orphan"
    )
    simulations = relationship(
        "SimulationModel", back_populates="field", cascade="all, delete-orphan"
    )


class WeatherTelemetryModel(Base):
    __tablename__ = "weather_telemetry"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[datetime.date] = mapped_column(Date, index=True, nullable=False)
    temperature_max: Mapped[float] = mapped_column(Float, nullable=False)
    temperature_min: Mapped[float] = mapped_column(Float, nullable=False)
    precipitation_mm: Mapped[float] = mapped_column(Float, nullable=False)
    solar_radiation: Mapped[float] = mapped_column(Float, nullable=False)

    field = relationship("FieldModel", back_populates="weather_telemetry")


class SimulationModel(Base):
    __tablename__ = "simulations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False
    )
    crop_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending")
    predicted_yield_bushels_per_acre: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    parameters_snapshot: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True
    )
    completed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    field = relationship("FieldModel", back_populates="simulations")
