import uuid
import datetime
from sqlalchemy import Float, DateTime, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from agrisim.core.database import Base


class WeatherTelemetryModel(Base):
    __tablename__ = "weather_telemetry"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False
    )
    temperature: Mapped[float] = mapped_column(Float, nullable=False)  # in Celsius
    rainfall: Mapped[float] = mapped_column(Float, nullable=False)  # in mm
    soil_moisture: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # percentage or index
    recorded_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    field = relationship("FieldModel", back_populates="weather_telemetry")
