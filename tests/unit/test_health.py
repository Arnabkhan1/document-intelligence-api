from fastapi.testclient import TestClient

from dia.core.config import get_settings
from dia.main import app

client = TestClient(app)
settings = get_settings()


def test_health_check():
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == settings.app_name
    assert data["version"] == settings.app_version
    assert data["environment"] == settings.app_env
