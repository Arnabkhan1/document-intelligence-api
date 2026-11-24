import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from dia.core.database import Base
from dia.core.exceptions import (
    DocumentNotFoundError,
    DocumentProcessingError,
)
from dia.models.document import Document
from dia.services import document_management


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    with Session(engine) as db:
        yield db

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def uploaded_document(db_session, tmp_path, monkeypatch):
    monkeypatch.setattr(document_management, "STORAGE_DIR", tmp_path)

    document = Document(
        filename="research.pdf",
        stored_filename="test-document.pdf",
        content_type="application/pdf",
        size_bytes=2048,
    )

    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    file_path = tmp_path / document.stored_filename
    file_path.write_bytes(b"%PDF-test-content")

    return document, file_path


def test_list_documents(db_session, uploaded_document):
    document, _ = uploaded_document

    documents = document_management.list_documents(db_session)

    assert len(documents) == 1
    assert documents[0].id == document.id


def test_get_document(db_session, uploaded_document):
    document, _ = uploaded_document

    result = document_management.get_document(
        db_session,
        document.id,
    )

    assert result.id == document.id
    assert result.filename == "research.pdf"


def test_get_missing_document(db_session):
    with pytest.raises(DocumentNotFoundError):
        document_management.get_document(
            db_session,
            "missing-document-id",
        )


def test_remove_document_success(db_session, uploaded_document):
    document, file_path = uploaded_document
    document_id = document.id

    document_management.remove_document(db_session, document_id)

    assert not file_path.exists()

    deleted_document = db_session.get(Document, document_id)
    assert deleted_document is None


def test_remove_missing_document(db_session):
    with pytest.raises(DocumentNotFoundError):
        document_management.remove_document(
            db_session,
            "missing-document-id",
        )


def test_database_failure_restores_file(
    db_session,
    uploaded_document,
    monkeypatch,
):
    document, file_path = uploaded_document
    document_id = document.id

    def simulate_database_failure(db, document):
        raise SQLAlchemyError("Simulated database failure")

    monkeypatch.setattr(
        document_management,
        "delete_document",
        simulate_database_failure,
    )

    with pytest.raises(DocumentProcessingError):
        document_management.remove_document(db_session, document_id)

    # The original file should be restored.
    assert file_path.exists()

    # The database record should still exist.
    existing_document = db_session.get(Document, document_id)
    assert existing_document is not None

    # No temporary deletion file should remain.
    temporary_files = list(file_path.parent.glob("*.deleting"))
    assert temporary_files == []
