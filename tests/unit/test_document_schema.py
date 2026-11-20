import pytest
from pydantic import ValidationError

from dia.schemas.documents import DocumentValidationRequest


def test_valid_document_metadata():
    document = DocumentValidationRequest(
        filename="research-paper.pdf",
        content_type="application/pdf",
        size_bytes=2048000,
    )

    assert document.filename == "research-paper.pdf"
    assert document.content_type == "application/pdf"
    assert document.size_bytes == 2048000


@pytest.mark.parametrize(
    "payload",
    [
        {
            "filename": "",
            "content_type": "application/pdf",
            "size_bytes": 1000,
        },
        {
            "filename": "research.pdf",
            "content_type": "application/zip",
            "size_bytes": 1000,
        },
        {
            "filename": "research.pdf",
            "content_type": "application/pdf",
            "size_bytes": 0,
        },
        {
            "filename": "research.pdf",
            "content_type": "application/pdf",
            "size_bytes": 21 * 1024 * 1024,
        },
    ],
)
def test_invalid_document_metadata(payload):
    with pytest.raises(ValidationError):
        DocumentValidationRequest(**payload)
