import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from agrisim.services.nasa_service import fetch_nasa_seasonal_data
from agrisim.core.database import get_db
from agrisim.schemas.field import FieldCreate, FieldResponse, FieldUpdate
from agrisim.schemas.envelope import ResponseEnvelope
from agrisim.services import field as field_service
from agrisim.models.user import UserModel
from agrisim.services.deps import get_current_user

router = APIRouter(prefix="/fields", tags=["Fields"])


@router.post(
    "/",
    response_model=ResponseEnvelope[FieldResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_field(
    field_in: FieldCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    # Pass current_user.id to service layer so the field belongs to the authenticated user
    db_field = field_service.create_field(
        db=db, field_in=field_in, owner_id=current_user.id
    )
    return ResponseEnvelope(
        status="success", code=201, message="Field created successfully", data=db_field
    )


@router.get("/", response_model=ResponseEnvelope[List[FieldResponse]])
def read_fields(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    # Restrict field listing to the logged-in user
    fields = field_service.get_fields_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return ResponseEnvelope(
        status="success", code=200, message="Fields retrieved successfully", data=fields
    )


@router.get("/{field_id}", response_model=ResponseEnvelope[FieldResponse])
def read_field(
    field_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    db_field = field_service.get_field_by_id(db=db, field_id=field_id)
    if not db_field or db_field.owner_id != current_user.id:
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
    field_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> ResponseEnvelope[None]:
    db_field = field_service.get_field_by_id(db=db, field_id=field_id)
    if not db_field or db_field.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Field not found")

    success = field_service.delete_field(db=db, field_id=field_id)
    return ResponseEnvelope(
        status="success", code=200, message="Field deleted successfully", data=None
    )


@router.put("/{field_id}", response_model=ResponseEnvelope[FieldResponse])
def update_field(
    field_id: uuid.UUID,
    field_in: FieldUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> ResponseEnvelope[FieldResponse]:
    db_field = field_service.get_field_by_id(db=db, field_id=field_id)
    if not db_field or db_field.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Field not found")

    updated_field = field_service.update_field(
        db=db, field_id=field_id, field_in=field_in.model_dump(exclude_unset=True)
    )
    return ResponseEnvelope(
        status="success",
        code=200,
        message="Field updated successfully",
        data=updated_field,
    )


from shapely.geometry import shape


from geoalchemy2.shape import to_shape


@router.get("/{field_id}/analyze")
async def analyze_field_season(
    field_id: uuid.UUID,
    season_start: str,
    season_end: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    # 1. Fetch the field and check ownership
    db_field = field_service.get_field_by_id(db=db, field_id=field_id)
    if not db_field or db_field.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Field not found")

    # 2. Convert GeoAlchemy2 WKBElement boundary to Shapely geometry & get centroid
    geom_shape = to_shape(db_field.boundary)
    centroid = geom_shape.centroid
    lat, lon = centroid.y, centroid.x

    # 3. Call NASA service (Note: For future dates like 2027, ensure your NASA
    # service maps these to historical equivalent dates so metrics aren't empty)
    # Inside your analyze endpoint:
    raw_nasa_data = await fetch_nasa_seasonal_data(lat, lon, season_start, season_end)

    # 1. Aggregate raw metrics
    aggregated_metrics = aggregate_nasa_metrics(raw_nasa_data["nasa_metrics"])

    # 2. Run crop simulation using those aggregated metrics
    simulation_results = run_simple_crop_model(aggregated_metrics, crop_type="wheat")

    # 3. Return both together in your response envelope
    return ResponseEnvelope(
        status="success",
        code=200,
        message="Field seasonal analysis and crop simulation retrieved successfully",
        data={
            "field_id": field_id,
            "coordinates": {"lat": lat, "lon": lon},
            "weather_summary": aggregated_metrics,
            "simulation": simulation_results
        }
    )
