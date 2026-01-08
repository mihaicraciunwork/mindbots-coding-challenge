import pytest
import tempfile
import shutil
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.config import UPLOAD_DIR


@pytest.fixture(scope="function")
def test_db():
    """Create a test database."""
    # Create temporary database
    # Note, StaticPool is used to create a thread-safe in-memory database
    # Use with sqlite:///:memory
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestingSessionLocal()

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_upload_dir(monkeypatch):
    """Create a temporary upload directory."""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    # Override UPLOAD_DIR in config module
    import app.config as config
    monkeypatch.setattr(config, "UPLOAD_DIR", temp_path)

    # Also override in file_service module since it imports UPLOAD_DIR
    import app.services.file_service as file_service
    monkeypatch.setattr(file_service, "UPLOAD_DIR", temp_path)

    yield temp_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def client(test_db, test_upload_dir):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing."""
    content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
    return ("test.pdf", content, "application/pdf")


@pytest.fixture
def sample_txt_file():
    """Create a sample TXT file for testing."""
    content = b"This is a test text file."
    return ("test.txt", content, "text/plain")


@pytest.fixture
def sample_docx_file():
    """Create a sample DOCX file for testing (minimal valid DOCX)."""
    # Minimal DOCX structure (zip file with specific structure)
    import zipfile
    import io

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
        zip_file.writestr("_rels/.rels", '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>')
        zip_file.writestr("word/document.xml", '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"></w:document>')

    return ("test.docx", zip_buffer.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
