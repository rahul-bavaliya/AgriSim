import uuid
from fastapi.testclient import TestClient
from httpx import Response
from agrisim.main import app

client: TestClient = TestClient(app)


def test_create_field():
    payload = {
        "name": "Test South Plot",
        "owner_id": str(uuid.uuid4()),
        "boundary": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-93.2, 44.9],
                    [-93.1, 44.9],
                    [-93.1, 44.8],
                    [-93.2, 44.8],
                    [-93.2, 44.9]
                ]
            ]
        },
        "total_acres": 85.5,
    }
    response = client.post("/api/v1/fields/", json=payload)
    
    if response.status_code != 201:
        print("\nVALIDATION ERROR:", response.json())
        
    assert response.status_code == 201


def test_read_fields():
    response = client.get("/api/v1/fields/")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert isinstance(data["data"], list)


def test_read_field_not_found():
    fake_id = uuid.uuid4()
    response = client.get(f"/api/v1/fields/{fake_id}")
    assert response.status_code == 404

    data = response.json()
    assert data["status"] == "error"
    assert data["code"] == 404


def test_update_field():
    # 1. Create a field first
    payload = {
        "name": "Plot to Update",
        "owner_id": str(uuid.uuid4()),
        "boundary": {
            "type": "Polygon",
            "coordinates": [[[-93.2, 44.9], [-93.1, 44.9], [-93.1, 44.8], [-93.2, 44.8], [-93.2, 44.9]]]
        },
        "total_acres": 50.0,
    }
    create_res = client.post("/api/v1/fields/", json=payload)
    field_id = create_res.json()["data"]["id"]

    # 2. Update the field name/acres
    update_payload = {"name": "Updated Plot Name", "total_acres": 55.0}
    response = client.put(f"/api/v1/fields/{field_id}", json=update_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["name"] == "Updated Plot Name"
    assert data["data"]["total_acres"] == 55.0


def test_delete_field():
    # 1. Create a field to delete
    payload = {
        "name": "Plot to Delete",
        "owner_id": str(uuid.uuid4()),
        "boundary": {
            "type": "Polygon",
            "coordinates": [[[-93.2, 44.9], [-93.1, 44.9], [-93.1, 44.8], [-93.2, 44.8], [-93.2, 44.9]]]
        },
        "total_acres": 25.0,
    }
    create_res = client.post("/api/v1/fields/", json=payload)
    field_id = create_res.json()["data"]["id"]

    # 2. Delete the field
    response = client.delete(f"/api/v1/fields/{field_id}")
    assert response.status_code == 200

    # 3. Verify it's gone (404)
    get_res = client.get(f"/api/v1/fields/{field_id}")
    assert get_res.status_code == 404
