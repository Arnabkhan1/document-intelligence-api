from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from dia.models.document import Document
from dia.repositories.document_repository import create_document
from dia.utils.file_signatures import validate_file_signature
from dia.utils.file_validation import (
    validate_content_type,
    validate_file_size,
    validate_filename,
)

STORAGE_DIR = Path("storage/documents")


async def upload_document(file: UploadFile, db: Session) -> dict:
    # Step 1: Validate the original filename
    original_filename = validate_filename(file.filename)

    # Step 2: Validate the MIME content type
    validate_content_type(
        original_filename,
        file.content_type,
    )

    # Step 3: Validate the file size
    file_size = await validate_file_size(file)

    # Step 4: Read the file content
    content = await file.read()

    # Step 5: Validate the actual file signature
    if not validate_file_signature(original_filename, content):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid file content or signature",
        )

    # Step 6: Generate a unique stored filename
    stored_filename = f"{uuid4().hex}{Path(original_filename).suffix.lower()}"
    destination = STORAGE_DIR / stored_filename

    # Step 7: Save the physical document
    try:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)

        with destination.open("xb") as output:
            output.write(content)

    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not store the uploaded document",
        ) from exc

    # Step 8: Create document metadata
    document = Document(
        filename=original_filename,
        stored_filename=stored_filename,
        content_type=file.content_type,
        size_bytes=file_size,
        status="uploaded",
    )

    # Step 9: Save metadata in SQLite
    try:
        saved_document = create_document(db, document)

    except SQLAlchemyError as exc:
        # Database persistence failed. Remove the saved file.
        try:
            destination.unlink(missing_ok=True)
        except OSError:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save document metadata",
        ) from exc

    # Step 10: Return document information
    return {
        "id": saved_document.id,
        "filename": saved_document.filename,
        "stored_filename": saved_document.stored_filename,
        "size_bytes": saved_document.size_bytes,
        "content_type": saved_document.content_type,
        "status": saved_document.status,
    }
