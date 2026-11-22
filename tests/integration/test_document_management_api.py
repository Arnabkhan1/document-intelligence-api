import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from dia.core.database import Base, get_db
from dia.main import app
from dia.models.document import Document
from dia.services import document_management


@pytest.fixture
def test_environment(tmp_path, monkeypatch):
    # Create an isolated in-memory database.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(engine)

    def override_get_db():
        with TestingSessionLocal() as db:
            yield db

    # Override the application's database dependency.
    app.dependency_overrides[get_db] = override_get_db

    # Use temporary storage for uploaded documents.
    monkeypatch.setattr(
        document_management,
        "STORAGE_DIR",
        tmp_path,
    )

    with TestClient(app) as client:
        yield client, TestingSessionLocal, tmp_path

    app.dependency_overrides.clear()
    engine.dispose()


def create_test_document(session_factory, storage_dir):
    with session_factory() as db:
        document = Document(
            filename="research.pdf",
            stored_filename="test-document.pdf",
            content_type="application/pdf",
            size_bytes=2048,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        document_id = document.id

    file_path = storage_dir / "test-document.pdf"
    file_path.write_bytes(b"%PDF-test-content")

    return document_id, file_path


def test_list_documents_api(test_environment):
    client, session_factory, storage_dir = test_environment

    document_id, _ = create_test_document(
        session_factory,
        storage_dir,
    )

    response = client.get("/api/v1/documents")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["documents"]) == 1
    assert data["documents"][0]["id"] == document_id
    assert data["documents"][0]["filename"] == "research.pdf"


def test_get_document_api(test_environment):
    client, session_factory, storage_dir = test_environment

    document_id, _ = create_test_document(
        session_factory,
        storage_dir,
    )

    response = client.get(f"/api/v1/documents/{document_id}")

    assert response.status_code == 200
    assert response.json()["id"] == document_id
    assert response.json()["filename"] == "research.pdf"


def test_get_missing_document_api(test_environment):
    client, _, _ = test_environment

    response = client.get("/api/v1/documents/missing-document-id")

    assert response.status_code == 404


def test_delete_document_api(test_environment):
    client, session_factory, storage_dir = test_environment

    document_id, file_path = create_test_document(
        session_factory,
        storage_dir,
    )

    response = client.delete(f"/api/v1/documents/{document_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == document_id
    assert data["status"] == "deleted"
    assert not file_path.exists()

    with session_factory() as db:
        deleted_document = db.get(Document, document_id)
        assert deleted_document is None


def test_delete_missing_document_api(test_environment):
    client, _, _ = test_environment

    response = client.delete("/api/v1/documents/missing-document-id")

    assert response.status_code == 404
