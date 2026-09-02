from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from agrisim.ml.recommendation_model import crop_engine
from agrisim.models.soil import SoilStateModel


class RecommendationService:
    @staticmethod
    def get_crop_recommendation(
        db: Session,
        field_id: UUID,
        temperature_celsius: float = 20.0,
        precipitation_mm: float = 5.0,
        humidity_percentage: float = 65.0,
    ) -> dict:
        """Fetches the latest soil state for a field and generates ML crop recommendations."""
        soil_state = (
            db.query(SoilStateModel)
            .filter(SoilStateModel.field_id == field_id)
            .order_by(SoilStateModel.calculated_at.desc())
            .first()
        )

        if not soil_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No soil state record found for this field. Ensure weather/soil tasks have run.",
            )

        # Run Scikit-Learn prediction
        prediction = crop_engine.predict_crop(
            soil_moisture=soil_state.soil_moisture_mm,
            temperature=temperature_celsius,
            precipitation=precipitation_mm,
            humidity=humidity_percentage,
        )

        return {
            "field_id": str(field_id),
            "inputs_evaluated": {
                "soil_moisture_mm": soil_state.soil_moisture_mm,
                "temperature_celsius": temperature_celsius,
                "precipitation_mm": precipitation_mm,
                "humidity_percentage": humidity_percentage,
                "calculated_at": soil_state.calculated_at,
            },
            "recommendation": prediction,
        }
