import os
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.config import settings
from app.database import engine, Base
from app.routers import auth, documents, chat

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for AI Research Assistant with PDF summarization, RAG chat, notes, quizzes, and paper comparison."
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local Streamlit integration
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)

class ApiKeyPayload(BaseModel):
    api_key: str

@app.get("/api/settings/apikey")
def get_apikey_status():
    """
    Returns whether the Gemini API key is configured on the backend.
    """
    return {
        "configured": len(settings.GEMINI_API_KEY.strip()) > 0
    }

@app.post("/api/settings/apikey")
def save_apikey(payload: ApiKeyPayload):
    """
    Saves a new Gemini API key to the active settings and persists it in the local .env file.
    """
    api_key_val = payload.api_key.strip()
    if not api_key_val:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API Key cannot be empty"
        )
        
    # Update current runtime config
    settings.GEMINI_API_KEY = api_key_val
    
    # Persist in backend/.env file
    try:
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(backend_dir, ".env")
        
        lines = []
        key_found = False
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()
                
        for i, line in enumerate(lines):
            if line.strip().startswith("GEMINI_API_KEY="):
                lines[i] = f"GEMINI_API_KEY={api_key_val}\n"
                key_found = True
                break
                
        if not key_found:
            lines.append(f"\nGEMINI_API_KEY={api_key_val}\n")
            
        with open(env_path, "w") as f:
            f.writelines(lines)
            
        return {"status": "success", "message": "API key updated and saved to .env"}
    except Exception as e:
        # Fallback to in-memory only update if file write fails
        return {
            "status": "warning", 
            "message": f"API key updated in memory only. Persistent write failed: {str(e)}"
        }

@app.get("/")
def read_root():
    return {
        "message": "Welcome to AI Research Assistant API",
        "docs_url": "/docs",
        "api_key_configured": len(settings.GEMINI_API_KEY.strip()) > 0
    }
