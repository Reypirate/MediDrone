def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_list_hospitals(client):
    response = client.get("/hospitals")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "name" in data[0]

def test_get_hospital(client):
    response = client.get("/hospitals/HOSP-001")
    assert response.status_code == 200
    assert response.json()["hospital_id"] == "HOSP-001"

def test_get_invalid_hospital(client):
    response = client.get("/hospitals/INVALID")
    assert response.status_code == 404
