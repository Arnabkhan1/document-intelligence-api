
from fastapi import FastAPI

from fastapi.testclient import TestClient

from dia.core.exception_handlers import register_exception_handlers
from dia.core.exceptions import (
    AppException,
    DocumentNotFoundError,
)


test_app = FastAPI()

register_exception_handlers(test_app)


@test_app.get("/test-document-error")
async def document_error():
    raise DocumentNotFoundError()


@test_app.get("/test-custom-error")
async def custom_error():
    raise AppException(
        message="Custom test error",
        code="CUSTOM_ERROR",
        status_code=400,
    )


@test_app.get("/test-validation")
async def validation_error(quantity: int):
    return {"quantity": quantity}


@test_app.get("/test-unexpected-error")
async def unexpected_error():
    raise RuntimeError("Internal database failure")


client = TestClient(
    test_app,
    raise_server_exceptions=False,
)


def test_document_not_found_error():
    response = client.get("/test-document-error")

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "DOCUMENT_NOT_FOUND"


def test_custom_application_error():
    response = client.get("/test-custom-error")

    assert response.status_code == 400

    data = response.json()

    assert data["error"]["code"] == "CUSTOM_ERROR"


def test_validation_error():
    response = client.get(
        "/test-validation",
        params={"quantity": "invalid"},
    )

    assert response.status_code == 422

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_unexpected_error():
    response = client.get("/test-unexpected-error")

    assert response.status_code == 500

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"

    # Internal exception details must not reach the client.
    assert "database failure" not in response.text.lower()
