from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from starlette.datastructures import Headers

from dia.core.database import Base
from dia.models.document import Document
from dia.repositories.document_repository import get_document_by_id
from dia.services import document_upload
from dia.utils.file_validation import MAX_FILE_SIZE


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    try:
        with Session(engine) as db:
            yield db
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


def create_upload_file(
    filename: str,
    content: bytes,
    content_type: str,
) -> UploadFile:
    return UploadFile(
        file=BytesIO(content),
        filename=filename,
        headers=Headers({"content-type": content_type}),
    )


@pytest.mark.anyio
async def test_successful_pdf_upload(tmp_path, monkeypatch, db_session):
    monkeypatch.setattr(document_upload, "STORAGE_DIR", tmp_path)

    content = b"%PDF-1.7 sample pdf content"
    file = create_upload_file("resume.pdf", content, "application/pdf")

    result = await document_upload.upload_document(file, db_session)

    assert result["id"] is not None
    assert result["filename"] == "resume.pdf"
    assert result["size_bytes"] == len(content)
    assert result["status"] == "uploaded"

    stored_file = tmp_path / result["stored_filename"]
    assert stored_file.exists()
    assert stored_file.read_bytes() == content

    saved_document = get_document_by_id(db_session, result["id"])
    assert saved_document is not None
    assert saved_document.filename == "resume.pdf"


@pytest.mark.anyio
async def test_successful_txt_upload(tmp_path, monkeypatch, db_session):
    monkeypatch.setattr(document_upload, "STORAGE_DIR", tmp_path)

    content = b"Hello, Document Intelligence API!"
    file = create_upload_file("notes.txt", content, "text/plain")

    result = await document_upload.upload_document(file, db_session)

    assert result["id"] is not None
    assert result["filename"] == "notes.txt"
    assert result["status"] == "uploaded"

    saved_document = get_document_by_id(db_session, result["id"])
    assert saved_document is not None
    assert saved_document.content_type == "text/plain"


@pytest.mark.anyio
async def test_invalid_file_signature(tmp_path, monkeypatch, db_session):
    monkeypatch.setattr(document_upload, "STORAGE_DIR", tmp_path)

    file = create_upload_file(
        "fake.pdf",
        b"This is not a PDF",
        "application/pdf",
    )

    with pytest.raises(HTTPException) as exc:
        await document_upload.upload_document(file, db_session)

    assert exc.value.status_code == 415
    assert list(tmp_path.iterdir()) == []


@pytest.mark.anyio
async def test_unsupported_extension(db_session):
    file = create_upload_file(
        "malware.exe",
        b"some content",
        "application/octet-stream",
    )

    with pytest.raises(HTTPException) as exc:
        await document_upload.upload_document(file, db_session)

    assert exc.value.status_code == 415


@pytest.mark.anyio
async def test_oversized_file(db_session):
    content = b"A" * (MAX_FILE_SIZE + 1)
    file = create_upload_file("large.pdf", content, "application/pdf")

    with pytest.raises(HTTPException) as exc:
        await document_upload.upload_document(file, db_session)

    assert exc.value.status_code == 413


@pytest.mark.anyio
async def test_storage_failure(tmp_path, monkeypatch, db_session):
    storage_path = tmp_path / "not_a_directory"
    storage_path.write_text("This is a file, not a directory")

    monkeypatch.setattr(document_upload, "STORAGE_DIR", storage_path)

    file = create_upload_file(
        "resume.pdf",
        b"%PDF-1.7 sample",
        "application/pdf",
    )

    with pytest.raises(HTTPException) as exc:
        await document_upload.upload_document(file, db_session)

    assert exc.value.status_code == 500


@pytest.mark.anyio
async def test_database_failure_cleans_up_file(
    tmp_path,
    monkeypatch,
    db_session,
):
    monkeypatch.setattr(document_upload, "STORAGE_DIR", tmp_path)

    def fail_database_save(db: Session, document: Document):
        raise SQLAlchemyError("Database unavailable")

    monkeypatch.setattr(
        document_upload,
        "create_document",
        fail_database_save,
    )

    file = create_upload_file(
        "resume.pdf",
        b"%PDF-1.7 sample pdf content",
        "application/pdf",
    )

    with pytest.raises(HTTPException) as exc:
        await document_upload.upload_document(file, db_session)

    assert exc.value.status_code == 500
    assert list(tmp_path.iterdir()) == []
