import os
import uuid
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException

from app.config import (
    UPLOAD_DIR,
    MAX_FILE_SIZE,
    ALLOWED_FILE_TYPES,
    ALLOWED_MIME_TYPES,
)


class FileService:
    @staticmethod
    def ensure_upload_dir():
        """Ensure upload directory exists."""
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def validate_file(file: UploadFile) -> Tuple[str, int]:
        """
        Validate uploaded file.
        Returns: (file_extension, file_size)
        Raises: HTTPException if validation fails
        """
        # Check file size
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024 * 1024)}MB",
            )

        if file_size == 0:
            raise HTTPException(status_code=400, detail="File is empty")

        # Check file extension
        filename = file.filename or ""
        file_extension = Path(filename).suffix.lower()

        if file_extension not in ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}",
            )

        # Check MIME type if available
        if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
            # Allow if extension is valid (some clients send wrong MIME types)
            pass

        return file_extension, file_size

    @staticmethod
    def save_file(file: UploadFile, file_extension: str) -> str:
        """
        Save uploaded file to disk.
        Returns: relative file path
        """
        FileService.ensure_upload_dir()

        # Generate unique filename
        unique_id = str(uuid.uuid4())
        filename = f"{unique_id}{file_extension}"
        file_path = UPLOAD_DIR / filename

        # Save file
        with open(file_path, "wb") as f:
            content = file.file.read()
            f.write(content)

        return str(file_path.relative_to(UPLOAD_DIR.parent))

    @staticmethod
    def get_file_path(relative_path: str) -> Path:
        """Get absolute file path from relative path."""
        return UPLOAD_DIR.parent / relative_path

    @staticmethod
    def file_exists(relative_path: str) -> bool:
        """Check if file exists."""
        file_path = FileService.get_file_path(relative_path)
        return file_path.exists()

    @staticmethod
    def delete_file(relative_path: str):
        """Delete file from disk."""
        file_path = FileService.get_file_path(relative_path)
        if file_path.exists():
            file_path.unlink()
