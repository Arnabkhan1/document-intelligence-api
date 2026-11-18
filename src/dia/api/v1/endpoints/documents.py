from typing import Annotated

from fastapi import APIRouter, File, UploadFile, status

from dia.schemas.documents import (
    DocumentUploadResponse,
    DocumentValidationRequest,
    DocumentValidationResponse,
)
from dia.services.document_upload import upload_document

router = APIRouter()


@router.post(
    "/validate",
    response_model=DocumentValidationResponse,
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


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document_endpoint(
    file: Annotated[UploadFile, File()],
) -> DocumentUploadResponse:
    result = await upload_document(file)
    return DocumentUploadResponse(**result)
