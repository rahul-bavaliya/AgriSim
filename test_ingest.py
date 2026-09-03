import uuid

from agrisim.core.database import SessionLocal
from agrisim.models.field import FieldModel
from agrisim.tasks.weather_tasks import fetch_field_weather


def main():
    db = SessionLocal()

    # Provide the boundary as an EWKT string instead of a dictionary
    wkt_boundary = "SRID=4326;POLYGON((-76.0 45.0, -75.0 45.0, -75.0 46.0, -76.0 46.0, -76.0 45.0))"

    new_field = FieldModel(
        name="Ottawa Test Farm",
        owner_id=uuid.uuid4(),
        boundary=wkt_boundary,
        total_acres=150.0,
    )
    db.add(new_field)
    db.commit()
    db.refresh(new_field)

    real_field_id = new_field.id
    db.close()

    print(f"Created real field with ID: {real_field_id}")

    result = fetch_field_weather.delay(real_field_id, 45.4215, -75.6972)
    print("Dispatched task ID:", result.id)


if __name__ == "__main__":
    main()
