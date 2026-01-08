import pytest
from fastapi.testclient import TestClient


def test_upload_pdf(client: TestClient, sample_pdf_file):
    """Test uploading a PDF file."""
    filename, content, content_type = sample_pdf_file

    response = client.post(
        "/documents/",
        files={"file": (filename, content, content_type)},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == filename
    assert data["size"] == len(content)
    assert data["type"] == ".pdf"
    assert "id" in data
    assert "upload_timestamp" in data
    assert "file_path" in data


def test_upload_txt(client: TestClient, sample_txt_file):
    """Test uploading a TXT file."""
    filename, content, content_type = sample_txt_file

    response = client.post(
        "/documents/",
        files={"file": (filename, content, content_type)},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == filename
    assert data["type"] == ".txt"


def test_upload_docx(client: TestClient, sample_docx_file):
    """Test uploading a DOCX file."""
    filename, content, content_type = sample_docx_file

    response = client.post(
        "/documents/",
        files={"file": (filename, content, content_type)},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == filename
    assert data["type"] == ".docx"


def test_upload_invalid_file_type(client: TestClient):
    """Test uploading an invalid file type."""
    content = b"fake image content"
    response = client.post(
        "/documents/",
        files={"file": ("test.jpg", content, "image/jpeg")},
    )

    assert response.status_code == 415


def test_upload_empty_file(client: TestClient):
    """Test uploading an empty file."""
    response = client.post(
        "/documents/",
        files={"file": ("empty.txt", b"", "text/plain")},
    )

    assert response.status_code == 400


def test_upload_large_file(client: TestClient):
    """Test uploading a file that exceeds size limit."""
    # Create a file larger than 10MB
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB

    response = client.post(
        "/documents/",
        files={"file": ("large.txt", large_content, "text/plain")},
    )

    assert response.status_code == 413


def test_list_documents_empty(client: TestClient):
    """Test listing documents when none exist."""
    response = client.get("/documents/")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["documents"] == []
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_pages"] == 0


def test_list_documents_with_pagination(client: TestClient, sample_txt_file):
    """Test listing documents with pagination."""
    filename, content, content_type = sample_txt_file

    # Upload 3 documents
    for i in range(3):
        client.post(
            "/documents/",
            files={"file": (f"test{i}.txt", content, content_type)},
        )

    # Test first page
    response = client.get("/documents/?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["documents"]) == 2
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total_pages"] == 2

    # Test second page
    response = client.get("/documents/?page=2&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["documents"]) == 1
    assert data["page"] == 2


def test_get_document_by_id(client: TestClient, sample_pdf_file):
    """Test retrieving a document by ID."""
    filename, content, content_type = sample_pdf_file

    # Upload document
    upload_response = client.post(
        "/documents/",
        files={"file": (filename, content, content_type)},
    )
    document_id = upload_response.json()["id"]

    # Retrieve document
    response = client.get(f"/documents/{document_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == document_id
    assert data["filename"] == filename


def test_get_document_not_found(client: TestClient):
    """Test retrieving a non-existent document."""
    response = client.get("/documents/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_download_document(client: TestClient, sample_txt_file):
    """Test downloading a document file."""
    filename, content, content_type = sample_txt_file

    # Upload document
    upload_response = client.post(
        "/documents/",
        files={"file": (filename, content, content_type)},
    )
    document_id = upload_response.json()["id"]

    # Download document
    response = client.get(f"/documents/{document_id}/download")
    assert response.status_code == 200
    assert response.content == content
    assert filename in response.headers.get("content-disposition", "")


def test_download_document_not_found(client: TestClient):
    """Test downloading a non-existent document."""
    response = client.get("/documents/99999/download")
    assert response.status_code == 404


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_endpoint(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
