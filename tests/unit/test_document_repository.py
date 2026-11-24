from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from dia.core.database import Base
from dia.models.document import Document
from dia.repositories.document_repository import (
    create_document,
    delete_document,
    get_all_documents,
    get_document_by_id,
)


def test_document_repository_operations():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    try:
        with Session(engine) as db:
            document = Document(
                filename="research.pdf",
                stored_filename="abc123.pdf",
                content_type="application/pdf",
                size_bytes=2048000,
            )

            # CREATE
            created = create_document(db, document)

            assert created.id is not None
            assert created.filename == "research.pdf"

            # READ ONE
            retrieved = get_document_by_id(db, created.id)

            assert retrieved is not None
            assert retrieved.id == created.id

            # READ ALL
            documents = get_all_documents(db)

            assert len(documents) == 1
            assert documents[0].filename == "research.pdf"

            # DELETE
            delete_document(db, retrieved)

            deleted = get_document_by_id(db, created.id)

            assert deleted is None

    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()
