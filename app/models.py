from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False, index=True)
    size = Column(Integer, nullable=False)  # Size in bytes
    type = Column(String, nullable=False)  # File extension
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    file_path = Column(String, nullable=False, unique=True)
