from typing import Literal

from pydantic import BaseModel, Field


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
    filename: str
    stored_filename: str
    size_bytes: int
    content_type: str
    status: Literal["uploaded"]
