import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=True) # Full extracted text
    summary = Column(Text, nullable=True)  # Executive/academic summary
    
    # Store key points, citations, quizzes and metadata as JSON fields
    key_points = Column(JSON, nullable=True)     # List of strings
    notes = Column(Text, nullable=True)          # Markdown study notes
    citations = Column(JSON, nullable=True)      # List of strings or structures
    quizzes = Column(JSON, nullable=True)        # List of MCQ objects
    metadata_info = Column(JSON, nullable=True)  # Authors, year, journal, etc.
    
    # Enhanced Creative Fields
    mind_map = Column(Text, nullable=True)              # Mermaid diagram code string
    flashcards = Column(JSON, nullable=True)            # List of flashcard Q&As
    citations_data = Column(JSON, nullable=True)        # Dict: {APA, MLA, Chicago, BibTeX}
    industry_applications = Column(Text, nullable=True) # Markdown report

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="documents")
    chat_messages = relationship("ChatMessage", back_populates="document", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False) # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    document = relationship("Document", back_populates="chat_messages")
