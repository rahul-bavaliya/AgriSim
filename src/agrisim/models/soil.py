from datetime import datetime
from uuid import UUID
import uuid
from sqlalchemy import Column, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from agrisim.core.database import Base


class SoilStateModel(Base):
    __tablename__ = "soil_states"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("fields.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Moisture metrics in millimeters (mm)
    soil_moisture_mm = Column(Float, nullable=False, default=50.0)
    field_capacity_mm = Column(Float, nullable=False, default=100.0)
    wilting_point_mm = Column(Float, nullable=False, default=30.0)

    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
