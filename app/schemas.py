from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class DocumentBase(BaseModel):
    filename: str
    size: int
    type: str


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    upload_timestamp: datetime
    file_path: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_pages: int
