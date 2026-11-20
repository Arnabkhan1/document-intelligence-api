from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers

from dia.services import document_upload
from dia.utils.file_validation import MAX_FILE_SIZE


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
async def test_successful_pdf_upload(tmp_path, monkeypatch):
    monkeypatch.setattr(document_upload, "STORAGE_DIR", tmp_path)

    content = b"%PDF-1.7 sample pdf content"

    file = create_upload_file(
        "resume.pdf",
        content,
        "application/pdf",
    )

    result = await document_upload.upload_document(file)

    assert result["filename"] == "resume.pdf"
    assert result["size_bytes"] == len(content)
    assert result["status"] == "uploaded"

    stored_file = tmp_path / result["stored_filename"]

    assert stored_file.exists()
    assert stored_file.read_bytes() == content


@pytest.mark.anyio
async def test_successful_txt_upload(tmp_path, monkeypatch):
    monkeypatch.setattr(document_upload, "STORAGE_DIR", tmp_path)

    content = b"Hello, Document Intelligence API!"

    file = create_upload_file(
        "notes.txt",
        content,
        "text/plain",
    )

    result = await document_upload.upload_document(file)

    assert result["filename"] == "notes.txt"
    assert result["status"] == "uploaded"


@pytest.mark.anyio
async def test_invalid_file_signature(tmp_path, monkeypatch):
    monkeypatch.setattr(document_upload, "STORAGE_DIR", tmp_path)

    file = create_upload_file(
        "fake.pdf",
        b"This is not a PDF",
        "application/pdf",
    )

    with pytest.raises(HTTPException) as exc:
        await document_upload.upload_document(file)

    assert exc.value.status_code == 415
    assert list(tmp_path.iterdir()) == []


@pytest.mark.anyio
async def test_unsupported_extension():
    file = create_upload_file(
        "malware.exe",
        b"some content",
        "application/octet-stream",
    )

    with pytest.raises(HTTPException) as exc:
        await document_upload.upload_document(file)

    assert exc.value.status_code == 415


@pytest.mark.anyio
async def test_oversized_file():
    content = b"A" * (MAX_FILE_SIZE + 1)

    file = create_upload_file(
        "large.pdf",
        content,
        "application/pdf",
    )

    with pytest.raises(HTTPException) as exc:
        await document_upload.upload_document(file)

    assert exc.value.status_code == 413


@pytest.mark.anyio
async def test_storage_failure(tmp_path, monkeypatch):
    storage_path = tmp_path / "not_a_directory"
    storage_path.write_text("This is a file, not a directory")

    monkeypatch.setattr(
        document_upload,
        "STORAGE_DIR",
        storage_path,
    )

    file = create_upload_file(
        "resume.pdf",
        b"%PDF-1.7 sample",
        "application/pdf",
    )

    with pytest.raises(HTTPException) as exc:
        await document_upload.upload_document(file)

    assert exc.value.status_code == 500
