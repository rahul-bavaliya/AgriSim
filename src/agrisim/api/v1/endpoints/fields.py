# src/agrisim/api/v1/endpoints/fields.py
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from agrisim.core.database import get_db
from agrisim.schemas.field import FieldCreate, FieldUpdate, FieldResponse
from agrisim.schemas.response_envelope import ResponseEnvelope
from agrisim.services.field_service import FieldService

router = APIRouter(prefix="/fields", tags=["Fields"])


@router.post(
    "/",
    response_model=ResponseEnvelope[FieldResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_field(
    payload: FieldCreate, db: Session = Depends(get_db)
) -> ResponseEnvelope[FieldResponse]:
    try:
        new_field = FieldService.create_field(db, payload)
        field_res = FieldResponse.model_validate(new_field)
        return ResponseEnvelope(
            status="success",
            code=201,
            message="Field created successfully",
            data=field_res,
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create field: {str(e)}",
        )


@router.get("/", response_model=ResponseEnvelope[List[FieldResponse]])
def list_fields(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> ResponseEnvelope[List[FieldResponse]]:
    fields = FieldService.get_fields(db, skip=skip, limit=limit)
    field_list = [FieldResponse.model_validate(f) for f in fields]

    return ResponseEnvelope(
        status="success",
        code=200,
        message="Fields retrieved successfully",
        data=field_list,
    )


@router.get("/{field_id}", response_model=ResponseEnvelope[FieldResponse])
def get_field(
    field_id: UUID, db: Session = Depends(get_db)
) -> ResponseEnvelope[FieldResponse]:
    field = FieldService.get_field_by_id(db, field_id)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Field not found"
        )

    return ResponseEnvelope(
        status="success",
        code=200,
        message="Field retrieved successfully",
        data=FieldResponse.model_validate(field),
    )


@router.put("/{field_id}", response_model=ResponseEnvelope[FieldResponse])
def update_field(
    field_id: UUID, payload: FieldUpdate, db: Session = Depends(get_db)
) -> ResponseEnvelope[FieldResponse]:
    field = FieldService.get_field_by_id(db, field_id)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Field not found"
        )

    updated_field = FieldService.update_field(db, field, payload)
    return ResponseEnvelope(
        status="success",
        code=200,
        message="Field updated successfully",
        data=FieldResponse.model_validate(updated_field),
    )


@router.delete("/{field_id}", response_model=ResponseEnvelope[dict[str, Any]])
def delete_field(
    field_id: UUID, db: Session = Depends(get_db)
) -> ResponseEnvelope[dict[str, Any]]:
    field = FieldService.get_field_by_id(db, field_id)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Field not found"
        )

    FieldService.delete_field(db, field)
    return ResponseEnvelope(
        status="success",
        code=200,
        message="Field deleted successfully",
        data={"id": str(field_id)},
    )


@router.get("/search/point", response_model=ResponseEnvelope[FieldResponse])
def get_field_by_point(
    lat: float, lon: float, db: Session = Depends(get_db)
) -> ResponseEnvelope[FieldResponse]:
    """Finds the agricultural field containing the specified latitude and longitude."""
    field = FieldService.get_field_by_point(db, lat=lat, lon=lon)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No field found containing the specified coordinates",
        )

    return ResponseEnvelope(
        status="success",
        code=200,
        message="Field found successfully",
        data=FieldResponse.model_validate(field),
    )
