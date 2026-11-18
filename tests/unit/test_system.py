from fastapi.testclient import TestClient

from dia.core.config import get_settings
from dia.main import app

client = TestClient(app)
settings = get_settings()


def test_system_info():
    response = client.get("/api/v1/system/info")

    assert response.status_code == 200

    data = response.json()

    assert data["app_name"] == settings.app_name
    assert data["app_version"] == settings.app_version
    assert data["environment"] == settings.app_env
    assert data["api_prefix"] == settings.api_v1_prefix
