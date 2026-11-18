import pytest
from fastapi.testclient import TestClient

from dia.main import app

client = TestClient(app)


def test_validate_document_success():
    payload = {
        "filename": "research-paper.pdf",
        "content_type": "application/pdf",
        "size_bytes": 2048000,
    }

    response = client.post(
        "/api/v1/documents/validate",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "valid"
    assert data["message"] == "Document metadata is valid"
    assert data["filename"] == "research-paper.pdf"
    assert data["size_bytes"] == 2048000


@pytest.mark.parametrize(
    "payload",
    [
        {
            "filename": "",
            "content_type": "application/pdf",
            "size_bytes": 1000,
        },
        {
            "filename": "research.pdf",
            "content_type": "application/zip",
            "size_bytes": 1000,
        },
        {
            "filename": "research.pdf",
            "content_type": "application/pdf",
            "size_bytes": 0,
        },
        {
            "filename": "research.pdf",
            "content_type": "application/pdf",
            "size_bytes": 21 * 1024 * 1024,
        },
    ],
)
def test_validate_document_invalid(payload):
    response = client.post(
        "/api/v1/documents/validate",
        json=payload,
    )

    assert response.status_code == 422
