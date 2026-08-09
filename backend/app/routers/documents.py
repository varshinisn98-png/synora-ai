import os
import shutil
from typing import List, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app import models, schemas, auth
from app.services.pdf_service import extract_pdf_text
from app.services.gemini_service import analyze_document, generate_notes, generate_quiz, compare_documents

router = APIRouter(
    prefix="/api/documents",
    tags=["documents"]
)

class CompareRequest(BaseModel):
    document_id_1: int
    document_id_2: int

@router.post("/upload", response_model=schemas.DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Check if file format is supported
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported format. Only PDF files are supported."
        )
        
    # Set default title if not provided
    if not title:
        title = os.path.splitext(file.filename)[0].replace("_", " ").replace("-", " ").title()
        
    # Generate unique filename to avoid collision
    import uuid
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    temp_file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save file locally
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {str(e)}"
        )
        
    try:
        # 1. Extract text from PDF
        print(f"Extracting text from {file.filename}...")
        extracted_data = extract_pdf_text(temp_file_path)
        content = extracted_data["text"]
        pdf_metadata = extracted_data["metadata"]
        
        if not content.strip():
            raise ValueError("The uploaded PDF appears to have no readable text content.")
            
        # 2. Analyze document with Gemini
        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "Gemini API key is not configured. "
                "Please configure the GEMINI_API_KEY environment variable or settings."
            )
            
        print("Starting Gemini analysis...")
        analysis = analyze_document(content, title)
        
        # Merge PDF metadata with Gemini metadata
        metadata_info = {
            "title": analysis.metadata.title or title or pdf_metadata["title"],
            "authors": analysis.metadata.authors or [pdf_metadata["author"]],
            "year": analysis.metadata.year,
            "journal": analysis.metadata.journal,
            "page_count": pdf_metadata["page_count"]
        }
        
        # 3. Create Document in DB
        db_document = models.Document(
            title=metadata_info["title"],
            filename=unique_filename,
            content=content,
            summary=analysis.summary,
            key_points=analysis.key_points,
            citations=analysis.citations,
            quizzes=None,        # Lazy generation
            notes=None,          # Lazy generation
            mind_map=None,       # Lazy generation
            flashcards=None,     # Lazy generation
            citations_data=None, # Lazy generation
            industry_applications=None, # Lazy generation
            metadata_info=metadata_info,
            user_id=current_user.id
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        return db_document
        
    except ValueError as ve:
        # Clean up temp file on failure
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        # Clean up temp file on failure
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        print(f"Error during upload processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing document: {str(e)}"
        )

@router.get("", response_model=List[schemas.DocumentListItem])
def list_documents(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Document).filter(models.Document.user_id == current_user.id).order_by(models.Document.created_at.desc()).all()

@router.get("/{document_id}", response_model=schemas.DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
        
    # Delete local PDF file if exists
    file_path = os.path.join(settings.UPLOAD_DIR, document.filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            
    db.delete(document)
    db.commit()
    return

@router.get("/{document_id}/notes")
def get_document_notes(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
        
    # Lazy generate notes if not present
    if not document.notes:
        try:
            print(f"Generating notes for {document.title}...")
            notes = generate_notes(document.title, document.content)
            document.notes = notes
            db.commit()
            db.refresh(document)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate study notes: {str(e)}"
            )
            
    return {"notes": document.notes}

@router.get("/{document_id}/quiz")
def get_document_quiz(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
        
    # Lazy generate quizzes if not present
    if not document.quizzes:
        try:
            print(f"Generating quiz for {document.title}...")
            quiz_data = generate_quiz(document.title, document.content)
            quizzes_list = [q.model_dump() for q in quiz_data.questions]
            document.quizzes = quizzes_list
            db.commit()
            db.refresh(document)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate quiz: {str(e)}"
            )
            
    return {"quizzes": document.quizzes}

@router.get("/{document_id}/mind-map")
def get_document_mind_map(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
        
    # Lazy generate mind map if not present
    if not document.mind_map:
        try:
            from app.services.gemini_service import generate_mind_map
            print(f"Generating mind map for {document.title}...")
            mind_map = generate_mind_map(document.title, document.summary, document.key_points)
            document.mind_map = mind_map
            db.commit()
            db.refresh(document)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate concept map: {str(e)}"
            )
            
    return {"mind_map": document.mind_map}

@router.get("/{document_id}/flashcards")
def get_document_flashcards(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
        
    # Lazy generate flashcards if not present
    if not document.flashcards:
        try:
            from app.services.gemini_service import generate_flashcards
            print(f"Generating study flashcards for {document.title}...")
            deck = generate_flashcards(document.title, document.content)
            cards_list = [c.model_dump() for c in deck.cards]
            document.flashcards = cards_list
            db.commit()
            db.refresh(document)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate study flashcards: {str(e)}"
            )
            
    return {"flashcards": document.flashcards}

@router.get("/{document_id}/citations")
def get_document_citations(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
        
    # Lazy generate citations if not present
    if not document.citations_data:
        try:
            from app.services.gemini_service import generate_citations
            meta = document.metadata_info or {}
            print(f"Generating citation styles for {document.title}...")
            citations = generate_citations(
                title=document.title,
                authors=meta.get("authors") or ["Unknown Author"],
                year=meta.get("year"),
                journal=meta.get("journal")
            )
            document.citations_data = citations.model_dump()
            db.commit()
            db.refresh(document)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate citation styles: {str(e)}"
            )
            
    return {"citations_data": document.citations_data}

@router.get("/{document_id}/applications")
def get_document_applications(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
        
    # Lazy generate industry applications if not present
    if not document.industry_applications:
        try:
            from app.services.gemini_service import generate_industry_applications
            print(f"Generating industry translation for {document.title}...")
            applications = generate_industry_applications(document.title, document.content)
            document.industry_applications = applications
            db.commit()
            db.refresh(document)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate industry applications: {str(e)}"
            )
            
    return {"industry_applications": document.industry_applications}

@router.post("/compare")
def compare_papers(
    payload: CompareRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Fetch both documents
    doc1 = db.query(models.Document).filter(
        models.Document.id == payload.document_id_1,
        models.Document.user_id == current_user.id
    ).first()
    
    doc2 = db.query(models.Document).filter(
        models.Document.id == payload.document_id_2,
        models.Document.user_id == current_user.id
    ).first()
    
    if not doc1 or not doc2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both documents not found."
        )
        
    try:
        comparison_markdown = compare_documents(
            doc1_title=doc1.title,
            doc1_summary=doc1.summary,
            doc2_title=doc2.title,
            doc2_summary=doc2.summary
        )
        return {"comparison": comparison_markdown}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparison failed: {str(e)}"
        )
