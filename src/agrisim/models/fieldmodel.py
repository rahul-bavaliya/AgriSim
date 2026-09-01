import uuid
import datetime
from sqlalchemy import String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry
from agrisim.core.database import Base
from sqlalchemy.orm import relationship


class FieldModel(Base):
    __tablename__ = "fields"
    __table_args__ = {"extend_existing": True}

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

    # Add this inside your FieldModel class definition:
    weather_records = relationship(
        "WeatherModel", back_populates="field", cascade="all, delete-orphan"
    )
