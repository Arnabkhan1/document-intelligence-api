from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from dia.utils.file_validation import (
    validate_content_type,
    validate_file_size,
    validate_filename,
)


def test_valid_filename():
    result = validate_filename("report.pdf")
    assert result == "report.pdf"


def test_invalid_extension():
    with pytest.raises(HTTPException) as exc:
        validate_filename("report.exe")

    assert exc.value.status_code == 415


def test_missing_filename():
    with pytest.raises(HTTPException) as exc:
        validate_filename(None)

    assert exc.value.status_code == 400


def test_path_traversal_filename():
    with pytest.raises(HTTPException) as exc:
        validate_filename("../report.pdf")

    assert exc.value.status_code == 400


def test_valid_content_type():
    validate_content_type("report.pdf", "application/pdf")


def test_invalid_content_type():
    with pytest.raises(HTTPException) as exc:
        validate_content_type("report.pdf", "text/plain")

    assert exc.value.status_code == 415


@pytest.mark.anyio
async def test_valid_file_size():
    content = b"Hello Document Intelligence API"

    upload = UploadFile(
        filename="report.txt",
        file=BytesIO(content),
    )

    size = await validate_file_size(upload)

    assert size == len(content)


@pytest.mark.anyio
async def test_file_size_limit():
    content = b"x" * (20 * 1024 * 1024 + 1)

    upload = UploadFile(
        filename="large.txt",
        file=BytesIO(content),
    )

    with pytest.raises(HTTPException) as exc:
        await validate_file_size(upload)

    assert exc.value.status_code == 413
