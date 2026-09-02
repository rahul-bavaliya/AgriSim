from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from agrisim.core.database import SessionLocal
from agrisim.services.recommendation import RecommendationService
from agrisim.services import field as field_service
from agrisim.models.user import UserModel
from agrisim.services.deps import get_current_user

router = APIRouter(prefix="/fields", tags=["Crop Recommendations"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{field_id}/recommendation")
def get_field_crop_recommendation(
    field_id: UUID,
    temperature: float = 20.0,
    precipitation: float = 5.0,
    humidity: float = 65.0,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Evaluates soil moisture and weather inputs for a field and returns Scikit-Learn crop recommendations with confidence scores."""

    # Verify the field exists and belongs to the authenticated user
    db_field = field_service.get_field_by_id(db=db, field_id=field_id)
    if not db_field or db_field.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found or unauthorized",
        )

    # Proceed with fetching the recommendation via the ML service
    return RecommendationService.get_crop_recommendation(
        db=db,
        field_id=field_id,
        temperature_celsius=temperature,
        precipitation_mm=precipitation,
        humidity_percentage=humidity,
    )
