from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.models import Document
from app.schemas import DocumentCreate, DocumentResponse
from app.config import DEFAULT_PAGE, DEFAULT_PAGE_SIZE


class DocumentService:
    @staticmethod
    def create_document(
        db: Session, document_data: DocumentCreate, file_path: str
    ) -> Document:
        """Create a new document record."""
        db_document = Document(
            filename=document_data.filename,
            size=document_data.size,
            type=document_data.type,
            file_path=file_path,
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document

    @staticmethod
    def get_document_by_id(db: Session, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        return db.query(Document).filter(Document.id == document_id).first()

    @staticmethod
    def get_documents(
        db: Session, page: int = DEFAULT_PAGE, page_size: int = DEFAULT_PAGE_SIZE
    ) -> Tuple[List[Document], int]:
        """
        Get paginated list of documents.
        Returns: (documents_list, total_count)
        """
        offset = (page - 1) * page_size

        documents = (
            db.query(Document)
            .order_by(Document.upload_timestamp.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        total = db.query(func.count(Document.id)).scalar()

        return documents, total

    @staticmethod
    def delete_document(db: Session, document_id: int) -> bool:
        """Delete document record."""
        document = DocumentService.get_document_by_id(db, document_id)
        if not document:
            return False

        db.delete(document)
        db.commit()
        return True
