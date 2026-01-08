from pathlib import Path
from typing import Set

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database configuration
DATABASE_URL = "sqlite:///./documents.db"

# File upload configuration
UPLOAD_DIR = BASE_DIR / "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
ALLOWED_FILE_TYPES: Set[str] = {".pdf", ".txt", ".docx"}
ALLOWED_MIME_TYPES: Set[str] = {
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

# Pagination defaults
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
