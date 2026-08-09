import fitz  # PyMuPDF
import os
from typing import Dict, Any

def extract_pdf_text(file_path: str) -> Dict[str, Any]:
    """
    Extracts text and metadata from a PDF file using PyMuPDF.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at {file_path}")
        
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise ValueError(f"Failed to open PDF file: {str(e)}")
        
    text_content = []
    for page_num in range(len(doc)):
        try:
            page = doc.load_page(page_num)
            page_text = page.get_text()
            if page_text:
                text_content.append(page_text)
        except Exception as e:
            print(f"Warning: Failed to extract text from page {page_num}: {e}")
            
    full_text = "\n".join(text_content).strip()
    
    # Extract metadata properties from PDF
    pdf_metadata = doc.metadata or {}
    
    # Try to clean up titles/authors if they are raw or empty
    title = pdf_metadata.get("title")
    if not title or title.strip() == "" or title.lower().startswith("microsoft word") or title.lower().startswith("untitled"):
        title = os.path.splitext(os.path.basename(file_path))[0].replace("_", " ").replace("-", " ").title()
        
    extracted_metadata = {
        "title": title,
        "author": pdf_metadata.get("author") or "Unknown Author",
        "subject": pdf_metadata.get("subject") or "",
        "keywords": pdf_metadata.get("keywords") or "",
        "page_count": len(doc)
    }
    
    doc.close()
    
    return {
        "text": full_text,
        "metadata": extracted_metadata
    }
