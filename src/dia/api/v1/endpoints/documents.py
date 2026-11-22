from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from dia.core.database import get_db
from dia.schemas.documents import (
    DocumentDeleteResponse,
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadResponse,
    DocumentValidationRequest,
    DocumentValidationResponse,
)
from dia.services.document_management import (
    get_document,
    list_documents,
    remove_document,
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
    db: Annotated[Session, Depends(get_db)],
) -> DocumentUploadResponse:
    result = await upload_document(file, db)

    return DocumentUploadResponse(**result)


@router.get("", response_model=DocumentListResponse)
def list_documents_endpoint(
    db: Annotated[Session, Depends(get_db)],
) -> DocumentListResponse:
    documents = list_documents(db)

    return DocumentListResponse(
        total=len(documents),
        documents=documents,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document_endpoint(
    document_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> DocumentResponse:
    return get_document(db, document_id)


@router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse,
)
def delete_document_endpoint(
    document_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> DocumentDeleteResponse:
    remove_document(db, document_id)

    return DocumentDeleteResponse(
        id=document_id,
        message="Document deleted successfully",
        status="deleted",
    )
