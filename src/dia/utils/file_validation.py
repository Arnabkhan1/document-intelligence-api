from pathlib import Path

from fastapi import HTTPException, UploadFile, status

MAX_FILE_SIZE = 20 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
}

ALLOWED_CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ),
    ".txt": "text/plain",
}


def validate_filename(filename: str | None) -> str:
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    safe_name = Path(filename.replace("\\", "/")).name

    if safe_name != filename or safe_name in {".", ".."}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename",
        )

    if Path(safe_name).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file extension",
        )

    return safe_name


def validate_content_type(filename: str, content_type: str | None) -> None:
    extension = Path(filename).suffix.lower()
    expected_type = ALLOWED_CONTENT_TYPES[extension]

    if content_type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid content type",
        )


async def validate_file_size(file: UploadFile) -> int:
    size = 0

    while chunk := await file.read(1024 * 1024):
        size += len(chunk)

        if size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="File exceeds the 20 MB limit",
            )

    await file.seek(0)
    return size
