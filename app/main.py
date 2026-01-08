from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from app.database import init_db
from app.api.routes import documents
from app.config import UPLOAD_DIR

logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Document Management API",
    description="REST API for managing document uploads, retrieval, and listing",
    version="1.0.0",
)

# Include routers
app.include_router(documents.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.get("/")
async def root():
    """Root endpoint."""
    try:
        return {
            "message": "Document Management API",
            "version": "1.0.0",
            "docs": "/docs",
        }
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch root endpoint information"
        )


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Error in health endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch health status"
        )
