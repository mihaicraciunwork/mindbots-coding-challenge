# Document Management REST API

A FastAPI-based REST API for managing document uploads, retrieval, and listing. Supports PDF, TXT, and DOCX file formats.

## Features

- **Document Upload**: Accepts PDF, TXT, and DOCX files up to 10MB
- **Metadata Storage**: Stores filename, size, type, and upload timestamp
- **Document Listing**: Paginated list of all documents
- **Document Retrieval**: Get document metadata by ID
- **File Download**: Download documents by ID
- **Error Handling**: Proper HTTP status codes and error messages
- **Comprehensive Tests**: Unit and integration tests

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **File Storage**: Local filesystem
- **Testing**: pytest with httpx

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mindbots-coding-challenge
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

Interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Upload Document
```http
POST /documents/
Content-Type: multipart/form-data

Body:
  file: <file>
```

**Response** (201 Created):
```json
{
  "id": 1,
  "filename": "document.pdf",
  "size": 1024,
  "type": ".pdf",
  "upload_timestamp": "2024-01-01T12:00:00",
  "file_path": "uploads/uuid.pdf"
}
```

### List Documents
```http
GET /documents/?page=1&page_size=10
```

**Query Parameters**:
- `page` (optional, default: 1): Page number
- `page_size` (optional, default: 10, max: 100): Items per page

**Response** (200 OK):
```json
{
  "documents": [
    {
      "id": 1,
      "filename": "document.pdf",
      "size": 1024,
      "type": ".pdf",
      "upload_timestamp": "2024-01-01T12:00:00",
      "file_path": "uploads/uuid.pdf"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

### Get Document by ID
```http
GET /documents/{id}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "filename": "document.pdf",
  "size": 1024,
  "type": ".pdf",
  "upload_timestamp": "2024-01-01T12:00:00",
  "file_path": "uploads/uuid.pdf"
}
```

### Download Document
```http
GET /documents/{id}/download
```

**Response** (200 OK):
- File download with appropriate headers

### Health Check
```http
GET /health
```

**Response** (200 OK):
```json
{
  "status": "healthy"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "File is empty"
}
```

### 404 Not Found
```json
{
  "detail": "Document not found"
}
```

### 413 Payload Too Large
```json
{
  "detail": "File size exceeds maximum allowed size of 10.0MB"
}
```

### 415 Unsupported Media Type
```json
{
  "detail": "File type not allowed. Allowed types: .pdf, .txt, .docx"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["query", "page"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

## Running Tests

Run all tests:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run with coverage:
```bash
pytest --cov=app
```

## Project Structure

```
mindbots-coding-challenge/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── database.py             # Database configuration
│   ├── config.py               # Application configuration
│   ├── services/
│   │   ├── document_service.py # Document business logic
│   │   └── file_service.py     # File storage operations
│   └── api/
│       └── routes/
│           └── documents.py    # API endpoints
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   └── test_documents.py       # API tests
├── uploads/                    # Stored document files
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Configuration

Configuration can be modified in `app/config.py`:
- `MAX_FILE_SIZE`: Maximum file size (default: 10MB)
- `ALLOWED_FILE_TYPES`: Allowed file extensions
- `DEFAULT_PAGE_SIZE`: Default pagination size
- `UPLOAD_DIR`: Directory for storing uploaded files

## License

MIT
