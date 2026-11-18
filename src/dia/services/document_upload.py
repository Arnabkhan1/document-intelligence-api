from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from dia.utils.file_signatures import validate_file_signature
from dia.utils.file_validation import (
    validate_content_type,
    validate_file_size,
    validate_filename,
)

STORAGE_DIR = Path("storage/documents")


async def upload_document(file: UploadFile) -> dict:
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

    # Step 7: Save the uploaded document
    try:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)

        with destination.open("xb") as output:
            output.write(content)

    except OSError as exc:
        try:
            destination.unlink(missing_ok=True)
        except OSError:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not store the uploaded document",
        ) from exc

    # Step 8: Return upload information
    return {
        "filename": original_filename,
        "stored_filename": stored_filename,
        "size_bytes": file_size,
        "content_type": file.content_type,
        "status": "uploaded",
    }
