from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from agrisim.core.database import get_db
from agrisim.schemas.envelope import ResponseEnvelope

# Import your recommendation service function
from agrisim.services.recommendation import get_upcoming_seasons
from agrisim.models.user import UserModel
from agrisim.services.deps import get_current_user

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/seasons", response_model=ResponseEnvelope[list])
def get_available_seasons(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Returns upcoming farming seasons and month ranges based on the current calendar date.
    """
    seasons = get_upcoming_seasons()
    return ResponseEnvelope(
        status="success",
        code=200,
        message="Upcoming seasons retrieved successfully",
        data=seasons,
    )
