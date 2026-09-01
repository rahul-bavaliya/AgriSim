from sqlalchemy.orm import Session
from uuid import UUID
from agrisim.models.soil import SoilStateModel


class SoilSimulationService:
    @staticmethod
    def update_field_soil_moisture(
        db: Session, field_id: UUID, precipitation_mm: float, temperature_celsius: float
    ) -> SoilStateModel:
        """
        Fetches the current soil state for a field, calculates the new water balance,
        and saves the updated state to the database.
        """
        # 1. Get existing soil state or initialize a default one if none exists yet
        soil_state = (
            db.query(SoilStateModel).filter(SoilStateModel.field_id == field_id).first()
        )

        if not soil_state:
            soil_state = SoilStateModel(
                field_id=field_id,
                soil_moisture_mm=50.0,  # Default starting moisture
                field_capacity_mm=100.0,
                wilting_point_mm=30.0,
            )
            db.add(soil_state)
            db.commit()
            db.refresh(soil_state)

        # 2. Estimate daily evapotranspiration (ET) based on temperature
        estimated_et = (
            max(1.0, temperature_celsius * 0.15) if temperature_celsius > 0 else 0.5
        )

        # 3. Apply water balance equation
        new_moisture = soil_state.soil_moisture_mm + precipitation_mm - estimated_et

        # 4. Bound between 0 and field capacity
        soil_state.soil_moisture_mm = max(
            0.0, min(soil_state.field_capacity_mm, new_moisture)
        )

        db.commit()
        db.refresh(soil_state)
        return soil_state
