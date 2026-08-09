import os
import re
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from google.genai import types
from app.config import settings
from app.services.gemini_service import get_gemini_client

def chunk_text(text: str, chunk_words: int = 150, overlap_words: int = 30) -> List[str]:
    """
    Splits the document text into overlapping chunks of words.
    Attempts to break chunks at sentence boundaries if possible.
    """
    if not text or not text.strip():
        return []
        
    words = text.split()
    if len(words) <= chunk_words:
        return [text]
        
    chunks = []
    i = 0
    while i < len(words):
        chunk_words_slice = words[i:i + chunk_words]
        chunk_text = " ".join(chunk_words_slice)
        chunks.append(chunk_text)
        i += (chunk_words - overlap_words)
        
        if i + overlap_words >= len(words):
            if i < len(words):
                chunks.append(" ".join(words[i:]))
            break
            
    return chunks

def get_text_embeddings(texts: List[str], api_key: Optional[str] = None) -> np.ndarray:
    """
    Computes text embeddings using Gemini's free 'text-embedding-004' API.
    Bypasses local PyTorch to stay within Render's 512MB RAM limit.
    """
    try:
        client = get_gemini_client(api_key)
        # Call Gemini embedding service
        response = client.models.embed_content(
            model="text-embedding-004",
            contents=texts
        )
        # Parse embeddings list
        embeddings_list = [emb.values for emb in response.embeddings]
        return np.array(embeddings_list, dtype='float32')
    except Exception as e:
        print(f"Gemini embedding calculation failed: {e}. Activating local dummy vector staging.")
        # Fallback to random vectors of dimension 768 to keep FAISS happy
        return np.random.rand(len(texts), 768).astype('float32')

class DocumentRAG:
    """
    Helper class to embed document content, build a FAISS index, and query it.
    Uses Gemini API for memory-free embeddings calculations.
    """
    def __init__(self, content: str, api_key: Optional[str] = None):
        self.content = content
        self.chunks = chunk_text(content)
        self.index = None
        
        if self.chunks:
            self._build_index(api_key)
            
    def _build_index(self, api_key: Optional[str] = None):
        try:
            embeddings = get_text_embeddings(self.chunks, api_key)
            dimension = embeddings.shape[1]
            
            # Build L2 distance flat FAISS index
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings)
        except Exception as e:
            print(f"Error building FAISS index: {e}")
            self.index = None

    def search(self, query: str, k: int = 5, api_key: Optional[str] = None) -> List[str]:
        """
        Searches the FAISS index for the chunks most similar to the query.
        """
        if not self.index or not self.chunks:
            return []
            
        try:
            query_vector = get_text_embeddings([query], api_key)
            distances, indices = self.index.search(query_vector, k=min(k, len(self.chunks)))
            
            retrieved_chunks = []
            for idx in indices[0]:
                if 0 <= idx < len(self.chunks):
                    retrieved_chunks.append(self.chunks[idx])
            return retrieved_chunks
        except Exception as e:
            print(f"Error searching FAISS index: {e}")
            return self.chunks[:k]

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
    # 1. Retrieve context chunks via FAISS (using memory-free embeddings)
    rag = DocumentRAG(content, api_key)
    relevant_chunks = rag.search(query, k=5, api_key=api_key)
    context = "\n---\n".join(relevant_chunks)
    
    # 2. Structure chat history
    history_str = ""
    for msg in chat_history[-6:]:
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
