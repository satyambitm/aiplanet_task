from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from database import Base

# SQLAlchemy Models
class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    path = Column(String)
    upload_date = Column(DateTime, default=datetime.now)
    processed = Column(DateTime, nullable=True)

    @classmethod
    def from_create(cls, document_create):
        return cls(
            id=document_create.id,
            name=document_create.name,
            path=document_create.path,
            upload_date=document_create.upload_date
        )

# Pydantic Models for API
class DocumentBase(BaseModel):
    name: str

class DocumentCreate(DocumentBase):
    id: str
    path: str
    upload_date: datetime

class DocumentResponse(BaseModel):
    document_id: str
    name: str
    upload_date: datetime

    class Config:
        orm_mode = True

class QuestionRequest(BaseModel):
    document_id: str
    question: str

class QuestionResponse(BaseModel):
    answer: str