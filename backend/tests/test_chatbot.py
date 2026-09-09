import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_get_state_land_rates():
    """Verifies retrieval of state land circle rates and district benchmarks."""
    res = client.get("/api/land-rates")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 10
    rates = data["rates"]
    states = [r["state"] for r in rates]
    assert "Uttar Pradesh" in states
    assert "Madhya Pradesh" in states
    assert "Maharashtra" in states
    assert "Delhi (NCT)" in states


def test_get_specific_state_land_rate():
    """Verifies fetching specific state land valuation details."""
    res = client.get("/api/land-rates/Uttar Pradesh")
    assert res.status_code == 200
    data = res.json()
    assert data["state"] == "Uttar Pradesh"
    assert "Circle Rate" in data["official_term"]
    assert "urban_avg_per_sqm" in data
    assert "rural_avg_per_hectare" in data
    assert len(data["key_districts"]) >= 4


def test_get_government_projects():
    """Verifies retrieval of active mega government projects and land acquisition metrics."""
    res = client.get("/api/gov-projects")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 7
    projects = data["projects"]
    names = [p["name"] for p in projects]
    assert any("Jewar" in n or "Noida" in n for n in names)
    assert any("Bullet Train" in n or "High-Speed" in n for n in names)
    assert any("Bharatmala" in n for n in names)


def test_get_government_projects_filter_sector():
    """Verifies sector-based filtering of mega infrastructure projects."""
    res = client.get("/api/gov-projects?sector=Aviation")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert any("Noida International Airport" in p["name"] for p in data["projects"])


def test_get_chat_suggestions_and_updates():
    """Verifies dynamic suggestions and real-time revenue updates ticker."""
    res = client.get("/api/chat/suggestions")
    assert res.status_code == 200
    data = res.json()
    assert len(data["suggestions"]) >= 5
    assert len(data["realtime_updates"]) >= 4
    first_upd = data["realtime_updates"][0]
    assert "title" in first_upd
    assert "date" in first_upd


def test_chat_message_endpoint_gemini_3_1_pro():
    """Verifies Gemini 3.1 Pro text conversation on state circle rates and legal rules."""
    res = client.post(
        "/api/chat/message",
        json={"message": "What is the circle rate and stamp duty in Uttar Pradesh?"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["model"] == "gemini-3.1-pro"
    assert len(data["reply"]) > 100
    assert "Uttar Pradesh" in data["reply"]
    assert "Circle Rate" in data["reply"]
    assert len(data["suggestions"]) >= 2


def test_chat_message_endpoint_project_query():
    """Verifies Gemini 3.1 Pro text response on live government infrastructure projects."""
    res = client.post(
        "/api/chat/message",
        json={"message": "Tell me about the Mumbai Ahmedabad Bullet Train project and land acquired"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["model"] == "gemini-3.1-pro"
    assert "Bullet Train" in data["reply"] or "High-Speed Rail" in data["reply"]
    assert "Land Acquired" in data["reply"]


def test_chat_message_empty_validation():
    """Verifies rejection of empty chat messages."""
    res = client.post("/api/chat/message", json={"message": "   "})
    assert res.status_code == 400
