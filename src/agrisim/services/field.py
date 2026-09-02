import uuid
from sqlalchemy.orm import Session
from shapely.geometry import shape
from geoalchemy2.shape import from_shape
from agrisim.models import FieldModel
from agrisim.schemas.field import FieldCreate
from agrisim.services import soil

def create_field(db: Session, field_in: FieldCreate, owner_id: uuid.UUID) -> FieldModel:
    geom = shape(field_in.boundary)
    wkb_element = from_shape(geom, srid=4326)

    db_field = FieldModel(
        name=field_in.name,
        owner_id=owner_id,
        total_acres=field_in.total_acres,
        boundary=wkb_element,
    )

    db.add(db_field)
    db.commit()
    db.refresh(db_field)

    # Automatically create the matching soil state entry
    soil.SoilSimulationService.initialize_for_field(db=db, field_id=db_field.id)


    return db_field


def get_fields(db: Session, skip: int = 0, limit: int = 100):
    return db.query(FieldModel).offset(skip).limit(limit).all()


def get_field_by_id(db: Session, field_id: uuid.UUID) -> FieldModel | None:
    return db.query(FieldModel).filter(FieldModel.id == field_id).first()


def delete_field(db: Session, field_id: uuid.UUID) -> bool:
    db_field = get_field_by_id(db, field_id)
    if not db_field:
        return False
    db.delete(db_field)
    db.commit()
    return True

def update_field(db: Session, field_id: uuid.UUID, field_in: dict) -> FieldModel | None:
    db_field = get_field_by_id(db, field_id)
    if not db_field:
        return None
    
    # If boundary is being updated, convert it to a WKBElement
    if "boundary" in field_in and field_in["boundary"] is not None:
        geom = shape(field_in["boundary"])
        field_in["boundary"] = from_shape(geom, srid=4326)

    for key, value in field_in.items():
        setattr(db_field, key, value)
        
    db.commit()
    db.refresh(db_field)
    return db_field

def get_fields_by_owner(db: Session, owner_id: uuid.UUID, skip: int = 0, limit: int = 100):
    return (
        db.query(FieldModel)
        .filter(FieldModel.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )