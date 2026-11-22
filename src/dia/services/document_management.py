import logging
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from dia.core.exceptions import (
    DocumentNotFoundError,
    DocumentProcessingError,
)
from dia.models.document import Document
from dia.repositories.document_repository import (
    delete_document,
    get_all_documents,
    get_document_by_id,
)
from dia.services.document_upload import STORAGE_DIR

logger = logging.getLogger(__name__)


def list_documents(db: Session) -> list[Document]:
    return get_all_documents(db)


def get_document(db: Session, document_id: str) -> Document:
    document = get_document_by_id(db, document_id)

    if document is None:
        raise DocumentNotFoundError()

    return document


def remove_document(db: Session, document_id: str) -> None:
    document = get_document(db, document_id)

    original_path = STORAGE_DIR / document.stored_filename
    temporary_path = STORAGE_DIR / f".{document.stored_filename}.{uuid4().hex}.deleting"

    file_staged = False

    # Step 1: Temporarily rename the physical file.
    try:
        if original_path.exists():
            original_path.replace(temporary_path)
            file_staged = True

    except OSError as exc:
        raise DocumentProcessingError(
            "Could not prepare the document for deletion."
        ) from exc

    # Step 2: Delete the database record.
    try:
        delete_document(db, document)

    except SQLAlchemyError as exc:
        # Step 3: Restore the original file if database deletion fails.
        if file_staged:
            try:
                temporary_path.replace(original_path)
            except OSError:
                logger.exception(
                    "Could not restore document file after database deletion failed."
                )

        raise DocumentProcessingError("Could not delete document metadata.") from exc

    # Step 4: Remove the temporary file after successful database deletion.
    if file_staged:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            logger.exception(
                "Document metadata was deleted, but the temporary file "
                "could not be removed: %s",
                temporary_path,
            )
