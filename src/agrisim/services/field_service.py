from typing import List, Optional, Dict, Any, cast as type_cast
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import func, cast
from shapely.geometry import shape
from geoalchemy2.shape import from_shape
from geoalchemy2.elements import WKTElement, WKBElement
from geoalchemy2 import Geography

from agrisim.models.field import Field
from agrisim.schemas.field import FieldCreate, FieldUpdate


class FieldService:
    @staticmethod
    def _transform_coordinates(geojson: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively converts [lat, lon] coordinate arrays to [lon, lat] for PostGIS/OGC compliance.
        """
        if not geojson or "coordinates" not in geojson:
            return geojson

        def recursive_swap(coords: Any) -> Any:
            if isinstance(coords, list):
                coordinate_list = type_cast(List[Any], coords)
                if len(coordinate_list) == 2 and all(
                    isinstance(x, (int, float)) for x in coordinate_list
                ):
                    return [coordinate_list[1], coordinate_list[0]]
                return [recursive_swap(sub) for sub in coordinate_list]
            return coords

        transformed = geojson.copy()
        transformed["coordinates"] = recursive_swap(geojson["coordinates"])
        return transformed

    @staticmethod
    def _calculate_acres(db: Session, wkb_element: WKBElement) -> float:
        """Calculates area in acres from a geometry using PostGIS geography for precision."""
        # Correctly cast using SQLAlchemy cast() and GeoAlchemy2's Geography type
        query = select(func.ST_Area(cast(wkb_element, Geography)))
        sq_meters = db.execute(query).scalar()
        if sq_meters is None:
            return 0.0
        return round(sq_meters * 0.000247105381, 2)

    @classmethod
    def create_field(cls, db: Session, payload: FieldCreate) -> Field:
        corrected_boundary = cls._transform_coordinates(payload.boundary)
        geometry_shape = shape(corrected_boundary)
        wkb_element = from_shape(geometry_shape, srid=4326)

        # Dynamically calculate acreage if omitted
        acres = (
            payload.total_acres
            if payload.total_acres is not None
            else cls._calculate_acres(db, wkb_element)
        )

        new_field = Field(name=payload.name, total_acres=acres, boundary=wkb_element)
        db.add(new_field)
        db.commit()
        db.refresh(new_field)
        return new_field

    @staticmethod
    def get_fields(db: Session, skip: int = 0, limit: int = 100) -> List[Field]:
        statement = select(Field).offset(skip).limit(limit)
        result = db.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    def get_field_by_id(db: Session, field_id: UUID) -> Optional[Field]:
        statement = select(Field).filter(Field.id == field_id)
        result = db.execute(statement)
        return result.scalars().first()

    @staticmethod
    def get_field_by_point(db: Session, lat: float, lon: float) -> Optional[Field]:
        """Spatial query: Finds a field containing/intersecting the given latitude and longitude point."""
        point_wkt = f"POINT({lon} {lat})"
        point_element = WKTElement(point_wkt, srid=4326)

        # Use ST_Intersects instead of ST_Contains to avoid precision/boundary edge-case misses
        statement = select(Field).filter(
            func.ST_Intersects(Field.boundary, point_element)
        )
        result = db.execute(statement)
        return result.scalars().first()

    @classmethod
    def update_field(cls, db: Session, field: Field, payload: FieldUpdate) -> Field:
        update_data = payload.model_dump(exclude_unset=True)

        if "boundary" in update_data and update_data["boundary"] is not None:
            corrected_boundary = cls._transform_coordinates(update_data.pop("boundary"))
            geometry_shape = shape(corrected_boundary)
            field.boundary = type_cast(str, from_shape(geometry_shape, srid=4326))

            # Recalculate acreage if boundary updates and total_acres wasn't explicitly given
            if "total_acres" not in update_data or update_data["total_acres"] is None:
                field.total_acres = cls._calculate_acres(
                    db, type_cast(WKBElement, field.boundary)
                )

        for key, value in update_data.items():
            if value is not None:
                setattr(field, key, value)

        db.commit()
        db.refresh(field)
        return field

    @staticmethod
    def delete_field(db: Session, field: Field) -> None:
        db.delete(field)
        db.commit()
