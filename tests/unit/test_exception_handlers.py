from fastapi import FastAPI
from fastapi.testclient import TestClient

from dia.core.exception_handlers import register_exception_handlers
from dia.core.exceptions import (
    AppException,
    DocumentNotFoundError,
)

# Create a separate application for testing.
exception_test_app = FastAPI()

# Register global exception handlers.
register_exception_handlers(exception_test_app)


@exception_test_app.get("/test-document-error")
async def document_error():
    raise DocumentNotFoundError()


@exception_test_app.get("/test-custom-error")
async def custom_error():
    raise AppException(
        message="Custom test error",
        code="CUSTOM_ERROR",
        status_code=400,
    )


@exception_test_app.get("/test-validation")
async def validation_error(quantity: int):
    return {"quantity": quantity}


@exception_test_app.get("/test-unexpected-error")
async def unexpected_error():
    raise RuntimeError("Internal database failure")


# Configure TestClient to capture server errors as HTTP responses.
client = TestClient(
    exception_test_app,
    raise_server_exceptions=False,
)


def test_document_not_found_error():
    response = client.get("/test-document-error")

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "DOCUMENT_NOT_FOUND"
    assert data["error"]["message"] == "The requested document was not found."


def test_custom_application_error():
    response = client.get("/test-custom-error")

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "CUSTOM_ERROR"
    assert data["error"]["message"] == "Custom test error"


def test_validation_error():
    response = client.get(
        "/test-validation",
        params={"quantity": "invalid"},
    )

    assert response.status_code == 422

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == ("The request contains invalid data.")
    assert isinstance(data["error"]["details"], list)


def test_unexpected_error():
    response = client.get("/test-unexpected-error")

    assert response.status_code == 500

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"

    # Internal exception details must never be exposed to clients.
    assert "database failure" not in response.text.lower()
