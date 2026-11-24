from sqlalchemy import select
from sqlalchemy.orm import Session

from dia.models.document import Document


def create_document(
    db: Session,
    document: Document,
) -> Document:
    try:
        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()
        raise


def get_document_by_id(
    db: Session,
    document_id: str,
) -> Document | None:
    statement = select(Document).where(Document.id == document_id)

    return db.scalar(statement)


def get_all_documents(
    db: Session,
) -> list[Document]:
    statement = select(Document).order_by(Document.created_at.desc())

    return list(db.scalars(statement).all())


def delete_document(db: Session, document: Document) -> None:
    try:
        db.delete(document)
        db.commit()
    except Exception:
        db.rollback()
        raise
