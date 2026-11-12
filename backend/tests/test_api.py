"""API endpoints integration tests."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "system" in data


def test_list_agents():
    response = client.get("/api/agents")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 10
    agent_ids = [a["id"] for a in data["agents"]]
    assert "coordinator" in agent_ids
    assert "legal_researcher" in agent_ids


def test_create_and_get_project():
    payload = {
        "name": "Integration Test Project",
        "description": "Building a college bus route optimization service",
        "project_type": "web",
        "technologies": ["Python", "FastAPI"]
    }
    create_res = client.post("/api/projects", json=payload)
    assert create_res.status_code == 200
    project = create_res.json()
    assert project["name"] == payload["name"]
    proj_id = project["id"]

    get_res = client.get(f"/api/projects/{proj_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == proj_id


def test_legal_curated_sources():
    response = client.get("/api/legal/sources/curated")
    assert response.status_code == 200
    sources = response.json()
    assert len(sources) >= 3
    assert any("FTC" in s["title"] or "Contracts" in s["title"] for s in sources)
