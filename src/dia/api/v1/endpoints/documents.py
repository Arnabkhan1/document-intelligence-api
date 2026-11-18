from fastapi import APIRouter

from dia.schemas.documents import (
    DocumentValidationRequest,
    DocumentValidationResponse,
)

router = APIRouter()


@router.post(
    "/documents/validate",
    response_model=DocumentValidationResponse,
    tags=["Documents"],
    summary="Validate document metadata",
)
async def validate_document(
    document: DocumentValidationRequest,
) -> DocumentValidationResponse:
    return DocumentValidationResponse(
        status="valid",
        message="Document metadata is valid",
        filename=document.filename,
        size_bytes=document.size_bytes,
    )
