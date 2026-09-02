import uuid
from fastapi.testclient import TestClient
from agrisim.main import app

client: TestClient = TestClient(app)


def test_create_and_read_weather():
    # 1. First, create a dummy field so the foreign key constraint is satisfied
    field_payload = {
        "name": "Weather Test Plot",
        "owner_id": str(uuid.uuid4()),
        "boundary": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-93.2, 44.9],
                    [-93.1, 44.9],
                    [-93.1, 44.8],
                    [-93.2, 44.8],
                    [-93.2, 44.9],
                ]
            ],
        },
        "total_acres": 100.0,
    }
    field_res = client.post("/api/v1/fields/", json=field_payload)
    assert field_res.status_code == 201
    field_id = field_res.json()["data"]["id"]

    # 2. Create a weather record linked to that field
    weather_payload = {
        "field_id": field_id,
        "temperature_celsius": 24.5,
        "humidity_percentage": 65.0,
        "precipitation_mm": 0.0,
        "wind_speed_kmh": 12.5,
        "condition": "Sunny",
    }
    weather_res = client.post("/api/v1/weather/", json=weather_payload)
    assert weather_res.status_code == 201

    weather_data = weather_res.json()["data"]
    assert weather_data["temperature_celsius"] == 24.5
    assert weather_data["condition"] == "Sunny"

    # 3. Retrieve weather records by field ID
    get_res = client.get(f"/api/v1/weather/field/{field_id}")
    assert get_res.status_code == 200

    get_data = get_res.json()
    assert get_data["status"] == "success"
    assert isinstance(get_data["data"], list)
    assert len(get_data["data"]) >= 1
    assert get_data["data"][0]["temperature_celsius"] == 24.5


def test_get_weather_empty_field():
    # Test getting weather for a random field ID that has no records
    fake_field_id = uuid.uuid4()
    response = client.get(f"/api/v1/weather/field/{fake_field_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"] == []
