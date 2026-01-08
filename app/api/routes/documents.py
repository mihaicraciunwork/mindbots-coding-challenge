from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import DocumentResponse, DocumentListResponse
from app.services.document_service import DocumentService
from app.services.file_service import FileService
from app.config import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """
    Upload a document.
    Accepts PDF, TXT, and DOCX files up to 10MB.
    """
    try:
        # Validate file
        file_extension, file_size = FileService.validate_file(file)

        # Save file
        relative_path = FileService.save_file(file, file_extension)

        # Create document record
        from app.schemas import DocumentCreate

        document_data = DocumentCreate(
            filename=file.filename or "unknown",
            size=file_size,
            type=file_extension,
        )

        db_document = DocumentService.create_document(db, document_data, relative_path)

        return DocumentResponse.model_validate(db_document)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.get("/", response_model=DocumentListResponse)
def list_documents(
    page: int = Query(DEFAULT_PAGE, ge=1, description="Page number"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    List all documents with pagination.
    """
    documents, total = DocumentService.get_documents(db, page=page, page_size=page_size)

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Get document metadata by ID.
    """
    document = DocumentService.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse.model_validate(document)


@router.get("/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db)):
    """
    Download document file by ID.
    """
    document = DocumentService.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = FileService.get_file_path(document.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=404, detail="Document file not found on disk"
        )

    return FileResponse(
        path=str(file_path),
        filename=document.filename,
        media_type="application/octet-stream",
    )
