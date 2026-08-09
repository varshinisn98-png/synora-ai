from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Token & Authentication Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Chat Message Schemas ---
class ChatMessageBase(BaseModel):
    role: str
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: int
    created_at: datetime
    document_id: int

    model_config = ConfigDict(from_attributes=True)

# --- Document Schemas ---
class DocumentBase(BaseModel):
    title: str

class DocumentCreate(DocumentBase):
    filename: str

class DocumentListItem(DocumentBase):
    id: int
    created_at: datetime
    metadata_info: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(DocumentBase):
    id: int
    filename: str
    content: Optional[str] = None
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    notes: Optional[str] = None
    citations: Optional[List[Any]] = None
    quizzes: Optional[List[Dict[str, Any]]] = None
    metadata_info: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    # Enhanced Creative Fields
    mind_map: Optional[str] = None
    flashcards: Optional[List[Dict[str, Any]]] = None
    citations_data: Optional[Dict[str, str]] = None
    industry_applications: Optional[str] = None
    
    chat_messages: List[ChatMessageResponse] = []

    model_config = ConfigDict(from_attributes=True)
