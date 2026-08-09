import os
import re
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from google.genai import types
from app.config import settings
from app.services.gemini_service import get_gemini_client

# Globals for caching models
_embedding_model = None

def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        print("Loading Sentence Transformer model (all-MiniLM-L6-v2)...")
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Sentence Transformer model loaded successfully.")
    return _embedding_model

def chunk_text(text: str, chunk_words: int = 150, overlap_words: int = 30) -> List[str]:
    """
    Splits the document text into overlapping chunks of words.
    Attempts to break chunks at sentence boundaries if possible.
    """
    if not text or not text.strip():
        return []
        
    # Split by whitespace into words
    words = text.split()
    if len(words) <= chunk_words:
        return [text]
        
    chunks = []
    i = 0
    while i < len(words):
        # Slice the words for the chunk
        chunk_words_slice = words[i:i + chunk_words]
        chunk_text = " ".join(chunk_words_slice)
        chunks.append(chunk_text)
        
        # Advance index by chunk size minus overlap
        i += (chunk_words - overlap_words)
        
        # If remaining words are less than overlap, we are done
        if i + overlap_words >= len(words):
            # Add final slice if there are leftover words not fully captured
            if i < len(words):
                chunks.append(" ".join(words[i:]))
            break
            
    return chunks

class DocumentRAG:
    """
    Helper class to embed document content, build a FAISS index, and query it.
    """
    def __init__(self, content: str):
        self.content = content
        self.chunks = chunk_text(content)
        self.index = None
        
        if self.chunks:
            self._build_index()
            
    def _build_index(self):
        try:
            model = get_embedding_model()
            embeddings = model.encode(self.chunks, convert_to_numpy=True)
            
            # Dimension of all-MiniLM-L6-v2 embeddings is 384
            dimension = embeddings.shape[1]
            
            # Build L2 distance flat FAISS index
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings.astype('float32'))
        except Exception as e:
            print(f"Error building FAISS index: {e}")
            self.index = None

    def search(self, query: str, k: int = 5) -> List[str]:
        """
        Searches the FAISS index for the chunks most similar to the query.
        """
        if not self.index or not self.chunks:
            return []
            
        try:
            model = get_embedding_model()
            query_vector = model.encode([query], convert_to_numpy=True)
            
            # Search FAISS index
            distances, indices = self.index.search(query_vector.astype('float32'), k=min(k, len(self.chunks)))
            
            retrieved_chunks = []
            for idx in indices[0]:
                if 0 <= idx < len(self.chunks):
                    retrieved_chunks.append(self.chunks[idx])
            return retrieved_chunks
        except Exception as e:
            print(f"Error searching FAISS index: {e}")
            return self.chunks[:k] # fallback to first k chunks

def query_document_rag(
    content: str, 
    query: str, 
    chat_history: List[Dict[str, str]] = [], 
    api_key: Optional[str] = None
) -> str:
    """
    Executes a RAG query: retrieves relevant chunks of the document,
    creates a context-filled prompt, and calls Gemini to generate the answer.
    """
    # 1. Retrieve context chunks via FAISS
    rag = DocumentRAG(content)
    relevant_chunks = rag.search(query, k=5)
    context = "\n---\n".join(relevant_chunks)
    
    # 2. Structure chat history
    history_str = ""
    for msg in chat_history[-6:]: # Include last 6 messages for context
        role = "User" if msg.get("role") == "user" else "Assistant"
        msg_content = msg.get("content", "")
        history_str += f"{role}: {msg_content}\n"
        
    # 3. Build detailed RAG prompt
    prompt = f"""
    You are an expert academic research assistant. Answer the user's question about the research paper using the provided context.
    If the question cannot be answered using the context, answer using your general knowledge but clearly state that this specific information was not found in the paper.
    Be precise, scholarly, and reference specific sections or findings when appropriate.
    
    ---
    RESEARCH PAPER CONTEXT (RELEVANT SEGMENTS):
    {context}
    ---
    
    RECENT CHAT HISTORY:
    {history_str}
    
    USER QUESTION: {query}
    
    Please provide a professional, clear, and comprehensive answer. Use LaTeX formatting for mathematical expressions if needed.
    """
    
    try:
        client = get_gemini_client(api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API rate limit or key error during RAG chat: {e}. Activating local FAISS semantic fallback.")
        if relevant_chunks:
            # Synthesize answer from the top retrieved vector search chunks
            formatted_chunks = ""
            for idx, chunk in enumerate(relevant_chunks[:3]):
                formatted_chunks += f"\n> ... {chunk.strip()} ...\n"
                
            answer = f"""### 🔍 Direct Document Search (AI Service Exhausted Fallback)

Due to Gemini rate limits, I have retrieved the matching segments from the document directly using your local **FAISS Vector Index**:

{formatted_chunks}
---
*This context was extracted locally using semantic search matching your query.*"""
            return answer
        else:
            return "No matching segments could be retrieved from the document locally, and the AI API is currently rate-limited. Please try again in a few seconds."
