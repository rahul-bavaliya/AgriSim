from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from agrisim.core.database import SessionLocal
from agrisim.services.recommendation import RecommendationService

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/fields/{field_id}/recommendation")
def get_field_crop_recommendation(
    field_id: UUID,
    temperature: float = 20.0,
    precipitation: float = 5.0,
    humidity: float = 65.0,
    db: Session = Depends(get_db),
):
    """Evaluates soil moisture and weather inputs for a field and returns Scikit-Learn crop recommendations with confidence scores."""
    return RecommendationService.get_crop_recommendation(
        db=db,
        field_id=field_id,
        temperature_celsius=temperature,
        precipitation_mm=precipitation,
        humidity_percentage=humidity,
    )
