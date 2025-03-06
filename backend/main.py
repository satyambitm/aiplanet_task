from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import shutil
from datetime import datetime

from database import get_db, init_db
from models import Document, DocumentCreate, DocumentResponse, QuestionRequest, QuestionResponse
from pdf_processor import process_document, ask_question

app = FastAPI(title="PDF Question Answering API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/upload", response_model=DocumentResponse)
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Generate unique ID and create file path
    document_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{document_id}.pdf")
    
    # Save the file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create document record in database
    document = DocumentCreate(
        id=document_id,
        name=file.filename,
        path=file_path,
        upload_date=datetime.now()
    )
    
    db_document = Document.from_create(document)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Process document in background
    if background_tasks:
        background_tasks.add_task(process_document, file_path, document_id)
    
    return DocumentResponse(
        document_id=document_id,
        name=file.filename,
        upload_date=db_document.upload_date
    )

@app.get("/documents", response_model=List[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).all()
    return [
        DocumentResponse(
            document_id=doc.id,
            name=doc.name,
            upload_date=doc.upload_date
        ) for doc in documents
    ]

@app.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        document_id=document.id,
        name=document.name,
        upload_date=document.upload_date
    )

@app.post("/ask", response_model=QuestionResponse)
async def ask_document_question(request: QuestionRequest, db: Session = Depends(get_db)):
    # Verify document exists
    document = db.query(Document).filter(Document.id == request.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Process question and get answer
        answer = ask_question(document.path, request.question)
        return QuestionResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)