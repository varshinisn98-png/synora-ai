from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, auth
from app.services.rag_service import query_document_rag

router = APIRouter(
    prefix="/api/documents",
    tags=["chat"]
)

class ChatRequest(BaseModel):
    query: str

@router.post("/{document_id}/chat", response_model=schemas.ChatMessageResponse)
def chat_with_document(
    document_id: int,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # 1. Fetch document and verify ownership
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
        
    if not document.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This document has no content. Cannot initiate chat."
        )
        
    # 2. Get past chat messages to include in context
    past_messages = db.query(models.ChatMessage).filter(
        models.ChatMessage.document_id == document_id
    ).order_by(models.ChatMessage.created_at.asc()).all()
    
    chat_history = [{"role": msg.role, "content": msg.content} for msg in past_messages]
    
    # 3. Query RAG pipeline (FAISS + Embeddings + Gemini API)
    try:
        answer = query_document_rag(
            document_id=document_id,
            content=document.content,
            query=payload.query,
            chat_history=chat_history
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG query failed: {str(e)}"
        )
        
    # 4. Save User Message
    user_msg = models.ChatMessage(
        role="user",
        content=payload.query,
        document_id=document_id
    )
    db.add(user_msg)
    
    # 5. Save Assistant Message
    assistant_msg = models.ChatMessage(
        role="assistant",
        content=answer,
        document_id=document_id
    )
    db.add(assistant_msg)
    
    db.commit()
    db.refresh(assistant_msg)
    
    return assistant_msg

@router.get("/{document_id}/chat", response_model=List[schemas.ChatMessageResponse])
def get_chat_history(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verify document exists and belongs to user
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
        
    messages = db.query(models.ChatMessage).filter(
        models.ChatMessage.document_id == document_id
    ).order_by(models.ChatMessage.created_at.asc()).all()
    
    return messages
