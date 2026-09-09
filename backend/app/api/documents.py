import os
import shutil
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import Document, User, ProcessingStatus, AuditLog
from backend.app.schemas.schemas import DocumentOut
from backend.app.services.auth import get_current_user

router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
ORIGINAL_DIR = os.path.join(UPLOAD_DIR, "original")
ENHANCED_DIR = os.path.join(UPLOAD_DIR, "enhanced")
MAX_SIZE_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_MB", "15")) * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

os.makedirs(ORIGINAL_DIR, exist_ok=True)
os.makedirs(ENHANCED_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Uploads land record document (PDF, JPG, JPEG, PNG).
    Validates file extension, size, and saves to storage.
    """
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed: PDF, JPG, JPEG, PNG",
        )

    # Read contents and validate size
    contents = await file.read()
    file_size = len(contents)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if file_size > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed limit of {MAX_SIZE_BYTES // (1024*1024)} MB.",
        )

    # Save to disk with unique identifier
    unique_filename = f"{uuid.uuid4().hex[:10]}_{filename}"
    file_path = os.path.join(ORIGINAL_DIR, unique_filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    # Create document record in DB
    doc = Document(
        filename=filename,
        file_path=file_path,
        file_type=ext.replace(".", "").upper(),
        file_size=file_size,
        uploaded_by=current_user.id,
        processing_status=ProcessingStatus.UPLOADED.value,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Log to audit trail
    audit = AuditLog(
        user_id=current_user.id,
        action="DOCUMENT_UPLOAD",
        new_value=f"Uploaded {filename} ({file_size} bytes)",
    )
    db.add(audit)
    db.commit()

    return doc


@router.get("", response_model=List[DocumentOut])
def list_documents(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists all uploaded documents with optional status filtering."""
    query = db.query(Document)
    if status:
        query = query.filter(Document.processing_status == status)
    return query.order_by(Document.uploaded_at.desc()).offset(skip).limit(limit).all()


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves document details by ID."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/{document_id}/file")
def get_original_file(document_id: int, db: Session = Depends(get_db)):
    """Serves original uploaded document file for browser preview."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Original document file not found")
    media_type = "application/pdf" if doc.file_type == "PDF" else f"image/{doc.file_type.lower()}"
    return FileResponse(doc.file_path, media_type=media_type)


@router.get("/{document_id}/enhanced-file")
def get_enhanced_file(document_id: int, db: Session = Depends(get_db)):
    """Serves OpenCV-enhanced preprocessed document image."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc or not doc.preprocessed_path or not os.path.exists(doc.preprocessed_path):
        # If enhanced version does not exist yet, fallback to original
        if doc and os.path.exists(doc.file_path):
            return FileResponse(doc.file_path)
        raise HTTPException(status_code=404, detail="Enhanced document file not found")
    return FileResponse(doc.preprocessed_path, media_type="image/png")
