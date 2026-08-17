from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


# =========================================================
# BASIC API TESTS
# =========================================================

def test_root():

    response = client.get("/")

    assert response.status_code == 200


def test_health():

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "UP"


# =========================================================
# CITY / WEATHER TESTS
# =========================================================

def test_create_city():

    response = client.post(
        "/cities",
        json={
            "city_name": "Test City",
            "state": "Test State",
            "country": "India",
            "temperature": 30.5,
            "humidity": 60,
            "weather_condition": "Sunny"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["city_name"] == "Test City"
    assert data["temperature"] == 30.5


def test_get_cities():

    response = client.get("/cities")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_city():

    response = client.get("/cities/1")

    assert response.status_code == 200
    assert response.json()["city_id"] == 1


def test_get_missing_city():

    response = client.get("/cities/999999")

    assert response.status_code == 404


def test_filter_by_state():

    response = client.get(
        "/cities?state=Telangana"
    )

    assert response.status_code == 200

    for city in response.json():
        assert city["state"].lower() == "telangana"


def test_filter_by_temperature():

    response = client.get(
        "/cities?min_temperature=30"
    )

    assert response.status_code == 200

    for city in response.json():
        assert city["temperature"] >= 30


def test_city_statistics():

    response = client.get(
        "/cities/statistics"
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_cities" in data
    assert "average_temperature" in data
    assert "maximum_temperature" in data
    assert "minimum_temperature" in data


def test_invalid_humidity():

    response = client.post(
        "/cities",
        json={
            "city_name": "Invalid City",
            "state": "Telangana",
            "country": "India",
            "temperature": 30,
            "humidity": 150,
            "weather_condition": "Sunny"
        }
    )

    assert response.status_code == 422


# =========================================================
# DISASTER TESTS
# =========================================================

def test_create_disaster():

    response = client.post(
        "/disasters",
        json={
            "region_name": "Test Region",
            "state": "Telangana",
            "country": "India",
            "disaster_type": "Flood",
            "severity": "High",
            "affected_population": 1000,
            "status": "Active",
            "description": "Test flood disaster."
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["region_name"] == "Test Region"
    assert data["disaster_type"] == "Flood"
    assert data["severity"] == "High"


def test_get_disasters():

    response = client.get(
        "/disasters"
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_disaster():

    response = client.get(
        "/disasters/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["disaster_id"] == 1


def test_get_missing_disaster():

    response = client.get(
        "/disasters/999999"
    )

    assert response.status_code == 404


def test_filter_disasters_by_state():

    response = client.get(
        "/disasters?state=Telangana"
    )

    assert response.status_code == 200

    for disaster in response.json():
        assert disaster["state"].lower() == "telangana"


def test_filter_disasters_by_type():

    response = client.get(
        "/disasters?disaster_type=Flood"
    )

    assert response.status_code == 200

    for disaster in response.json():
        assert disaster["disaster_type"] == "Flood"


def test_filter_disasters_by_severity():

    response = client.get(
        "/disasters?severity=High"
    )

    assert response.status_code == 200

    for disaster in response.json():
        assert disaster["severity"] == "High"


def test_filter_disasters_by_status():

    response = client.get(
        "/disasters?status=Active"
    )

    assert response.status_code == 200

    for disaster in response.json():
        assert disaster["status"] == "Active"


def test_disaster_statistics():

    response = client.get(
        "/disasters/statistics/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_disasters" in data
    assert "active_disasters" in data
    assert "high_severity_disasters" in data
    assert "total_affected_population" in data


def test_invalid_disaster():

    response = client.post(
        "/disasters",
        json={
            "region_name": "Test Region",
            "state": "Telangana",
            "country": "India",
            "disaster_type": "InvalidType",
            "severity": "High",
            "affected_population": 1000,
            "status": "Active",
            "description": "Invalid disaster."
        }
    )

    assert response.status_code == 400