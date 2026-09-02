import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from agrisim.core.database import get_db
from agrisim.schemas.field import FieldCreate, FieldResponse, FieldUpdate
from agrisim.schemas.envelope import ResponseEnvelope
from agrisim.services import field as field_service
from uuid import UUID
from agrisim.models.soil import SoilStateModel

router = APIRouter(prefix="/fields", tags=["Fields"])


@router.post(
    "/",
    response_model=ResponseEnvelope[FieldResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_field(field_in: FieldCreate, db: Session = Depends(get_db)):
    db_field = field_service.create_field(db=db, field_in=field_in)
    return ResponseEnvelope(
        status="success", code=201, message="Field created successfully", data=db_field
    )


@router.get("/", response_model=ResponseEnvelope[List[FieldResponse]])
def read_fields(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    fields = field_service.get_fields(db=db, skip=skip, limit=limit)
    return ResponseEnvelope(
        status="success", code=200, message="Fields retrieved successfully", data=fields
    )


@router.get("/{field_id}", response_model=ResponseEnvelope[FieldResponse])
def read_field(field_id: uuid.UUID, db: Session = Depends(get_db)):
    db_field = field_service.get_field_by_id(db=db, field_id=field_id)
    if not db_field:
        raise HTTPException(status_code=404, detail="Field not found")
    return ResponseEnvelope(
        status="success",
        code=200,
        message="Field retrieved successfully",
        data=db_field,
    )


@router.delete(
    "/{field_id}", response_model=ResponseEnvelope[None], status_code=status.HTTP_200_OK
)
def remove_field(
    field_id: uuid.UUID, db: Session = Depends(get_db)
) -> ResponseEnvelope[None]:
    success = field_service.delete_field(db=db, field_id=field_id)
    if not success:
        raise HTTPException(status_code=404, detail="Field not found")
    return ResponseEnvelope(
        status="success", code=200, message="Field deleted successfully", data=None
    )


@router.put("/{field_id}", response_model=ResponseEnvelope[FieldResponse])
def update_field(
    field_id: uuid.UUID, field_in: FieldUpdate, db: Session = Depends(get_db)
) -> ResponseEnvelope[FieldResponse]:
    updated_field = field_service.update_field(
        db=db, field_id=field_id, field_in=field_in.model_dump(exclude_unset=True)
    )
    if not updated_field:
        raise HTTPException(status_code=404, detail="Field not found")
    return ResponseEnvelope(
        status="success",
        code=200,
        message="Field updated successfully",
        data=updated_field,
    )


@router.get("/fields/{field_id}/soil-state")
def get_soil_state(field_id: UUID, db: Session = Depends(get_db)):
    soil = db.query(SoilStateModel).filter(SoilStateModel.field_id == field_id).first()
    if not soil:
        raise HTTPException(
            status_code=404, detail="Soil state not found for this field."
        )
    return {
        "field_id": soil.field_id,
        "soil_moisture_mm": soil.soil_moisture_mm,
        "field_capacity_mm": soil.field_capacity_mm,
        "wilting_point_mm": soil.wilting_point_mm,
        "calculated_at": soil.calculated_at,
    }
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from agrisim.core.database import get_db
from agrisim.schemas.field import FieldCreate, FieldResponse, FieldUpdate
from agrisim.schemas.envelope import ResponseEnvelope
from agrisim.services import field as field_service
from uuid import UUID
from agrisim.models.soil import SoilStateModel

router = APIRouter(prefix="/fields", tags=["Fields"])


@router.post(
    "/",
    response_model=ResponseEnvelope[FieldResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_field(field_in: FieldCreate, db: Session = Depends(get_db)):
    db_field = field_service.create_field(db=db, field_in=field_in)
    return ResponseEnvelope(
        status="success", code=201, message="Field created successfully", data=db_field
    )


@router.get("/", response_model=ResponseEnvelope[List[FieldResponse]])
def read_fields(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    fields = field_service.get_fields(db=db, skip=skip, limit=limit)
    return ResponseEnvelope(
        status="success", code=200, message="Fields retrieved successfully", data=fields
    )


@router.get("/{field_id}", response_model=ResponseEnvelope[FieldResponse])
def read_field(field_id: uuid.UUID, db: Session = Depends(get_db)):
    db_field = field_service.get_field_by_id(db=db, field_id=field_id)
    if not db_field:
        raise HTTPException(status_code=404, detail="Field not found")
    return ResponseEnvelope(
        status="success",
        code=200,
        message="Field retrieved successfully",
        data=db_field,
    )


@router.delete(
    "/{field_id}", response_model=ResponseEnvelope[None], status_code=status.HTTP_200_OK
)
def remove_field(
    field_id: uuid.UUID, db: Session = Depends(get_db)
) -> ResponseEnvelope[None]:
    success = field_service.delete_field(db=db, field_id=field_id)
    if not success:
        raise HTTPException(status_code=404, detail="Field not found")
    return ResponseEnvelope(
        status="success", code=200, message="Field deleted successfully", data=None
    )


@router.put("/{field_id}", response_model=ResponseEnvelope[FieldResponse])
def update_field(
    field_id: uuid.UUID, field_in: FieldUpdate, db: Session = Depends(get_db)
) -> ResponseEnvelope[FieldResponse]:
    updated_field = field_service.update_field(
        db=db, field_id=field_id, field_in=field_in.model_dump(exclude_unset=True)
    )
    if not updated_field:
        raise HTTPException(status_code=404, detail="Field not found")
    return ResponseEnvelope(
        status="success",
        code=200,
        message="Field updated successfully",
        data=updated_field,
    )


@router.get("/fields/{field_id}/soil-state")
def get_soil_state(field_id: UUID, db: Session = Depends(get_db)):
    soil = db.query(SoilStateModel).filter(SoilStateModel.field_id == field_id).first()
    if not soil:
        raise HTTPException(
            status_code=404, detail="Soil state not found for this field."
        )
    return {
        "field_id": soil.field_id,
        "soil_moisture_mm": soil.soil_moisture_mm,
        "field_capacity_mm": soil.field_capacity_mm,
        "wilting_point_mm": soil.wilting_point_mm,
        "calculated_at": soil.calculated_at,
    }
