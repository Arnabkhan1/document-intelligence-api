from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DocumentValidationRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: Literal[
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    ]
    size_bytes: int = Field(gt=0, le=20 * 1024 * 1024)


class DocumentValidationResponse(BaseModel):
    status: Literal["valid"]
    message: str
    filename: str
    size_bytes: int


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    stored_filename: str
    size_bytes: int
    content_type: str
    status: Literal["uploaded"]


class DocumentResponse(BaseModel):
    id: str
    filename: str
    stored_filename: str
    content_type: str
    size_bytes: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    total: int
    documents: list[DocumentResponse]


class DocumentDeleteResponse(BaseModel):
    id: str
    message: str
    status: Literal["deleted"]
