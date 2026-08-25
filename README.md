# Synora AI - Intelligent Academic & Document Workspace

### 🌐 Live Production Deployment Links:
* **🚀 Web Application Dashboard**: [https://bit.ly/synora-ai](https://bit.ly/synora-ai)
* **⚙️ Backend API Endpoint**: [https://synora-backend-lx8c.onrender.com/docs](https://synora-backend-lx8c.onrender.com/docs)
* **🗄️ Cloud Storage Database**: Managed via **Supabase PostgreSQL**

---

Synora AI is a premium, light-themed academic document intelligence workspace designed to help researchers, students, and software engineers read, comprehend, and translate academic papers into practical implementations. 

By leveraging the power of **Google Gemini**, **FAISS Vector Databases**, and **Supabase**, Synora AI automates the extraction of key literature insights, builds visual mind maps, organizes active recall study sessions, and translates theoretical designs into system engineering architecture blueprints.

---

## 🎨 Premium Light Academic Interface
Synora AI features a custom, high-fidelity light theme designed to avoid sterile pure whites:
- **Pastel Mesh Gradients**: Ambient background using subtle lavender (`#8b5cf6`), sky blue (`#0ea5e9`), and rose (`#f43f5e`) radial glows.
- **High-Contrast Typography**: Uses Plus Jakarta Sans and Space Grotesk in dark slate-gray and charcoal for readability.
- **Metric Highlights**: Dynamic cards with color-coded side indicators (violet, cyan, and magenta).
- **Gamified Flashcard Carousels**: Double-sided flip animations with color transitions indicating front (question) and back (answer) sides.

---

## 🚀 Key Features

- **Ingest & Summarize PDFs**: Upload academic PDFs to automatically extract authors, venue details, total pages, publication year, executive summaries, key contributions, and notable citations.
- **Visual Concept Mind Maps**: Automatically charts relationships between paper concepts using dynamic **Mermaid.js** node graphs rendered natively.
- **Active Recall Flashcard Studio**: Generates structured, double-sided study flashcards. Turn over cards using "Reveal Answer" and cycle through them.
- **Reference Citation Generator**: Instantly formats and displays paper bibliography entries in **APA**, **MLA**, **Chicago**, and **raw BibTeX** formats for easy clipboard copying or LaTeX Overleaf imports.
- **Industry Architecture Translator**: A specialized tool translating mathematical or theoretical findings into concrete system engineering designs, database structures, microservice pipelines, and SaaS startup ideas.
- **Interactive Document Chat (RAG)**: Chat with your PDF contextually using local FAISS semantic indexes and Sentence Transformers.
- **Side-by-Side Literature Compare**: Compare the methods, scopes, and results of two papers in your library side-by-side using AI.

---

## 🛠️ Tech Stack

| Layer | Component | Technology |
|---|---|---|
| **Language** | Core | Python 3.13 |
| **Frontend** | UI & Styling | Streamlit with custom CSS injector |
| **Backend** | API Services | FastAPI |
| **Database** | SQL Engine | PostgreSQL (Supabase pooler on port 6543 via SQLAlchemy) |
| **RAG Pipeline** | Vector Search | FAISS & Gemini `text-embedding-004` Cloud API |
| **PDF Extraction** | Text Parsing | PyMuPDF (fitz) |
| **AI Processing** | LLM Engine | Gemini API (`gemini-2.5-flash` with structured Pydantic schemas) |

---

## 🚀 Getting Started

### 1. Installation

It is recommended to run the services in a Python virtual environment:

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
pip install -r frontend/requirements.txt
```

### 2. Run the Services

Start both the FastAPI backend and Streamlit frontend concurrently with a single command:

```bash
python run.py
```

* **FastAPI API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Streamlit Frontend Dashboard**: [http://localhost:8501](http://localhost:8501)

### 3. API Key Setup
Once the dashboard opens, expand the **⚙️ API Configuration** card in the sidebar. Input your **Gemini API Key** and save. The app will automatically configure itself.

---

## 📂 Project Architecture

```
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── pdf_service.py      # Extract text and PDF metadata
│   │   │   ├── gemini_service.py   # RAG prompts, Mermaid graphs, flashcards
│   │   │   └── index_service.py    # FAISS indices & sentence-embeddings
│   │   ├── routers/
│   │   │   ├── auth.py             # User register & login handlers
│   │   │   └── documents.py        # PDF uploads, study tools, comparisons
│   │   ├── models.py               # SQLite schema (SQLAlchemy)
│   │   ├── main.py                 # FastAPI initialization
│   │   └── config.py               # Environmental configuration
│   └── requirements.txt
├── frontend/
│   ├── app.py                      # Main Streamlit light-themed dashboard
│   └── requirements.txt
├── run.py                          # Concurrent server runner
└── README.md
```
