import os
import time
import streamlit as st
import requests
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Set Page Config
st.set_page_config(
    page_title="Synora AI - Study & Literature Review Companion",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "active_document_id" not in st.session_state:
    st.session_state.active_document_id = None
if "api_key_configured" not in st.session_state:
    st.session_state.api_key_configured = False
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# Custom CSS Styling (Clean Academic Light theme, Space Grotesk/Plus Jakarta fonts, Glassmorphism elements)
CSS_STYLES = """
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    html, body, [class*="css"], [data-testid="stWidgetLabel"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #1e293b !important;
    }
    
    h1, h2, h3, h4, h5, h6, .title-font {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: #0f172a !important;
    }

    /* Ambient light pastel iridescent gradient background */
    .stApp {
        background-color: #f3f4f6;
        background-image: 
            linear-gradient(135deg, #f5f3ff 0%, #edd8fd 25%, #e0e7ff 50%, #e0f2fe 75%, #fdf2f8 100%);
        background-attachment: fixed;
    }

    /* Maximize working space by hiding default headers and footers */
    header, footer, [data-testid="stHeader"] {
        visibility: hidden !important;
        height: 0px !important;
    }
    
    /* Document title custom purple/blue linear gradient */
    .app-title {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        text-shadow: 0 0 35px rgba(124, 58, 237, 0.05);
    }
    
    /* Sidebar aesthetic adjustments (Clean light slate-violet sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #f1f5f9 !important;
        border-right: 1px solid rgba(226, 232, 240, 0.8) !important;
        box-shadow: 4px 0 15px rgba(0,0,0,0.01);
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(226, 232, 240, 0.9) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"], section[data-testid="stSidebar"] p {
        color: #475569 !important;
    }

    /* Sidebar navigation button custom styles */
    section[data-testid="stSidebar"] .stButton button {
        background-color: transparent !important;
        color: #475569 !important;
        border: 1px solid transparent !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        padding: 8px 12px !important;
        transition: all 0.2s ease !important;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        color: #7c3aed !important;
        background-color: rgba(139, 92, 246, 0.06) !important;
        border-color: rgba(139, 92, 246, 0.12) !important;
    }

    /* Standard Glassmorphism Card Wrapper with Hover Micro-Animations */
    .glass-card {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 30px rgba(31, 38, 135, 0.02);
        transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease, border-color 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 40px rgba(31, 38, 135, 0.05);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    /* Glowing card accent for success or primary actions */
    .glass-card-accent {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(245, 243, 255, 0.9) 100%);
        border: 1px solid rgba(139, 92, 246, 0.18);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 30px rgba(139, 92, 246, 0.02);
        transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease, border-color 0.3s ease;
    }
    .glass-card-accent:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 40px rgba(139, 92, 246, 0.06);
        border-color: rgba(139, 92, 246, 0.4);
    }

    /* Beautiful Centered Glassmorphic Form */
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(139, 92, 246, 0.2) !important;
        border-radius: 20px !important;
        padding: 30px !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.04), 0 0 50px rgba(139, 92, 246, 0.01) !important;
        backdrop-filter: blur(16px) !important;
    }

    /* Submit / Primary Buttons inside forms with glowing gradients */
    div[data-testid="stForm"] button[type="submit"], .btn-primary button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2) !important;
        width: 100% !important;
        letter-spacing: -0.01em !important;
    }
    div[data-testid="stForm"] button[type="submit"]:hover, .btn-primary button:hover {
        transform: translateY(-1.5px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.35) !important;
        filter: brightness(1.05);
    }

    /* Secondary Switch-auth button custom design */
    .btn-secondary button {
        background-color: transparent !important;
        color: #475569 !important;
        border: 1px solid rgba(203, 213, 225, 0.8) !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    .btn-secondary button:hover {
        color: #0f172a !important;
        border-color: rgba(139, 92, 246, 0.3) !important;
        background-color: rgba(241, 245, 249, 0.5) !important;
    }

    /* Input Field Overrides */
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.98) !important;
        border: 1px solid rgba(203, 213, 225, 0.9) !important;
        color: #0f172a !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput input:focus {
        border-color: #7c3aed !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.08) !important;
    }

    /* Styled Tabpill Controls */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px !important;
        background-color: rgba(241, 245, 249, 0.95) !important;
        padding: 8px !important;
        border-radius: 16px !important;
        border: 1px solid rgba(226, 232, 240, 0.9) !important;
        margin-bottom: 28px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.01) !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px !important;
        background-color: transparent !important;
        border-radius: 10px !important;
        color: #475569 !important;
        border: none !important;
        padding: 0px 24px !important;
        font-weight: 600 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #0f172a !important;
        background-color: rgba(226, 232, 240, 0.7) !important;
        transform: translateY(-0.5px);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2) !important;
    }

    /* Glassmorphic Metrics Container with Left Colored Accents */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid rgba(226, 232, 240, 0.85) !important;
        border-radius: 16px !important;
        padding: 20px 24px !important;
        backdrop-filter: blur(8px) !important;
        box-shadow: 0 4px 25px rgba(0, 0, 0, 0.005) !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.02);
    }
    
    /* Give each metric card a visual accent on the left */
    div[data-testid="stMetric"]:nth-child(1) {
        border-left: 6px solid #8b5cf6 !important;
    }
    div[data-testid="stMetric"]:nth-child(2) {
        border-left: 6px solid #06b6d4 !important;
    }
    div[data-testid="stMetric"]:nth-child(3) {
        border-left: 6px solid #ec4899 !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #1e293b !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Dashed Border Drag-and-Drop Uploader */
    div[data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.5) !important;
        border: 2px dashed rgba(139, 92, 246, 0.25) !important;
        border-radius: 12px !important;
        padding: 24px !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: rgba(139, 92, 246, 0.6) !important;
        background-color: rgba(255, 255, 255, 0.8) !important;
    }

    /* Premium RAG Capsule Chat Message styling */
    [data-testid="stChatMessage"] {
        border-radius: 18px !important;
        padding: 20px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.005) !important;
        color: #1e293b !important;
        transition: transform 0.2s ease;
    }
    [data-testid="stChatMessage"]:hover {
        transform: translateX(2px);
    }
    
    /* User Chat Bubble - Soft Indigo Pastel */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: rgba(139, 92, 246, 0.06) !important;
        border: 1px solid rgba(139, 92, 246, 0.12) !important;
    }
    
    /* Assistant Chat Bubble - Soft Sky Blue Pastel */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: rgba(14, 165, 233, 0.04) !important;
        border: 1px solid rgba(14, 165, 233, 0.1) !important;
    }
"""

# Inject global style sheet
st.markdown(f"<style>{CSS_STYLES}</style>", unsafe_allow_html=True)

# Helper API functions
def get_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

# Check API key configuration on startup only once
if "api_key_status_checked" not in st.session_state or not st.session_state.api_key_status_checked:
    try:
        res = requests.get(f"{BACKEND_URL}/api/settings/apikey")
        if res.status_code == 200:
            st.session_state.api_key_configured = res.json()["configured"]
            st.session_state.api_key_status_checked = True
    except Exception:
        pass

# --- 1. SEPARATE AUTHENTICATION PAGE (IF NOT LOGGED IN) ---
if not st.session_state.token:
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    left_pad, center_col, right_pad = st.columns([1, 1.8, 1])
    
    with center_col:
        st.markdown("<div style='height: 70px;'></div>", unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center; margin-bottom: 25px;">
                <img src="https://img.icons8.com/isometric-line/100/purple/literature.png" width="80" style="filter: drop-shadow(0px 0px 20px rgba(168, 85, 247, 0.65));" />
                <h1 class="app-title" style="font-size: 42px; margin-top: 15px; margin-bottom: 5px;">Synora AI</h1>
                <p style="color: #a1a1aa; font-size: 16px; margin-top: 0px;">Your Intelligent Academic & Document Workspace</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.auth_mode == "login":
            st.markdown("<h3 style='text-align: center; margin-bottom: 20px; font-weight: 500;'>Sign In to Workspace</h3>", unsafe_allow_html=True)
            
            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="e.g. varshini@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In")
                
                if submitted:
                    if not email or not password:
                        st.error("Please fill in both fields.")
                    else:
                        try:
                            cleaned_email = email.replace(" ", "").lower()
                            res = requests.post(f"{BACKEND_URL}/api/auth/login", json={"email": cleaned_email, "password": password})
                            if res.status_code == 200:
                                st.session_state.token = res.json()["access_token"]
                                st.session_state.user_email = cleaned_email
                                st.success("Successfully authenticated!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("Authentication failed. Check your email or password.")
                        except Exception as e:
                            st.error(f"Cannot communicate with auth server: {e}")
            
            st.write("")
            st.markdown("<p style='text-align: center; color: #71717a; margin-bottom: 5px;'>Don't have an account yet?</p>", unsafe_allow_html=True)
            st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
            if st.button("Create an account"):
                st.session_state.auth_mode = "register"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.markdown("<h3 style='text-align: center; margin-bottom: 20px; font-weight: 500;'>Create New Account</h3>", unsafe_allow_html=True)
            
            with st.form("register_form"):
                email = st.text_input("Email Address", placeholder="e.g. varshini@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Create Workspace Account")
                
                if submitted:
                    if not email or not password:
                        st.error("Please complete all input fields.")
                    elif password != confirm_password:
                        st.error("Passwords match verification failed.")
                    else:
                        try:
                            cleaned_email = email.replace(" ", "").lower()
                            res = requests.post(f"{BACKEND_URL}/api/auth/register", json={"email": cleaned_email, "password": password})
                            if res.status_code == 201:
                                st.success("Account registered successfully!")
                                st.session_state.auth_mode = "login"
                                time.sleep(1.0)
                                st.rerun()
                            else:
                                st.error(res.json().get("detail", "Registration failed. Email may already be in use."))
                        except Exception as e:
                            st.error(f"Failed to communicate with register backend: {e}")
            
            st.write("")
            st.markdown("<p style='text-align: center; color: #71717a; margin-bottom: 5px;'>Already registered?</p>", unsafe_allow_html=True)
            st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
            if st.button("Sign in to existing account"):
                st.session_state.auth_mode = "login"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- 2. WORKSPACE DASHBOARD PAGE (AFTER LOGGING IN) ---
else:
    # Function to reload library cache
    def refresh_library():
        try:
            res = requests.get(f"{BACKEND_URL}/api/documents", headers=get_headers())
            if res.status_code == 200:
                st.session_state.library_cache = res.json()
        except Exception:
            st.session_state.library_cache = []

    if "library_cache" not in st.session_state:
        refresh_library()
        
    all_documents = st.session_state.get("library_cache", [])

    with st.sidebar:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px; margin-top: 15px;">
                <img src="https://img.icons8.com/isometric-line/100/purple/literature.png" width="38" />
                <h2 style="margin: 0; font-size: 20px; background: linear-gradient(135deg, #c084fc 0%, #6366f1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Synora AI</h2>
            </div>
        """, unsafe_allow_html=True)
        st.write("Logged in as: `" + st.session_state.user_email + "`")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user_email = None
            st.session_state.active_document_id = None
            st.rerun()
            
        st.markdown("---")
        st.subheader("📚 Library")
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("➕ Ingest New Paper", use_container_width=True):
            st.session_state.active_document_id = None
            if "active_document" in st.session_state:
                del st.session_state.active_document
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")
        
        if all_documents:
            for doc in all_documents:
                col1, col2 = st.columns([5, 1.2])
                is_active = (st.session_state.active_document_id == doc["id"])
                emoji = "🟣" if is_active else "📄"
                
                doc_title = doc["title"]
                doc_title = doc_title[:24] + "..." if len(doc_title) > 27 else doc_title
                
                with col1:
                    if st.button(f"{emoji} {doc_title}", key=f"sel_{doc['id']}", use_container_width=True):
                        st.session_state.active_document_id = doc["id"]
                        if "active_document" in st.session_state:
                            del st.session_state.active_document
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"del_{doc['id']}", use_container_width=True):
                        try:
                            requests.delete(f"{BACKEND_URL}/api/documents/{doc['id']}", headers=get_headers())
                            if st.session_state.active_document_id == doc["id"]:
                                st.session_state.active_document_id = None
                            # Invalidate cache to force reload
                            if "library_cache" in st.session_state:
                                del st.session_state.library_cache
                            if "active_document" in st.session_state:
                                del st.session_state.active_document
                            st.rerun()
                        except Exception as e:
                            st.error("Delete failed.")
        else:
            st.info("No saved documents.")

        st.markdown("---")
        
        with st.expander("⚙️ API Configuration"):
            status_text = "Configured" if st.session_state.api_key_configured else "Not Configured"
            st.write(f"Gemini API Status: **{status_text}**")
            new_key = st.text_input("Change Gemini API Key", type="password")
            if st.button("Save Key"):
                if new_key:
                    try:
                        res = requests.post(f"{BACKEND_URL}/api/settings/apikey", json={"api_key": new_key})
                        if res.status_code == 200:
                            st.session_state.api_key_configured = True
                            st.success("API Key saved!")
                            time.sleep(1.0)
                            st.rerun()
                        else:
                            st.error("Failed to save API key.")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # CASE A: UPLOAD NEW PDF VIEW
    if st.session_state.active_document_id is None:
        st.markdown("<h1 class='app-title' style='margin-bottom:5px;'>🔬 Ingest Research Paper</h1>", unsafe_allow_html=True)
        st.write("Upload academic PDFs to automatically extract summaries, generate visual mind maps, take flashcard sessions, and review code architectures.")
        st.write("")
        
        with st.container():
            st.markdown('<div class="glass-card-accent">', unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Drag & drop academic PDF file (.pdf)",
                type=["pdf"]
            )
            custom_title = st.text_input("Custom Document Title (Optional)", placeholder="Leave blank to extract title automatically")
            
            st.markdown('<div class="btn-primary" style="margin-top: 15px; max-width: 300px;">', unsafe_allow_html=True)
            process_btn = st.button("🚀 Process & Analyze Paper")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if process_btn:
                if not uploaded_file:
                    st.error("Please upload a PDF file first.")
                elif not st.session_state.api_key_configured:
                    st.error("Gemini API Key is not configured. Please set it in the sidebar settings first.")
                else:
                    with st.spinner("Processing Document (Extracting Text + Building Vector Index + Gemini Structuring)..."):
                        try:
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                            data = {}
                            if custom_title:
                                data["title"] = custom_title
                                
                            res = requests.post(
                                f"{BACKEND_URL}/api/documents/upload",
                                headers=get_headers(),
                                files=files,
                                data=data
                            )
                            
                            if res.status_code == 201:
                                result_doc = res.json()
                                st.success("Document analyzed and indexed successfully!")
                                st.session_state.active_document_id = result_doc["id"]
                                st.session_state.active_document = result_doc
                                if "library_cache" in st.session_state:
                                    del st.session_state.library_cache
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(res.json().get("detail", "Error processing PDF. Ensure your API Key is valid and PDF has readable text."))
                        except Exception as e:
                            st.error(f"Upload error: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

    # CASE B: ACTIVE DOCUMENT DETAILED VIEW
    else:
        try:
            doc = None
            if "active_document" in st.session_state and st.session_state.active_document.get("id") == st.session_state.active_document_id:
                doc = st.session_state.active_document
            else:
                res = requests.get(
                    f"{BACKEND_URL}/api/documents/{st.session_state.active_document_id}",
                    headers=get_headers()
                )
                if res.status_code == 200:
                    doc = res.json()
                    st.session_state.active_document = doc
            
            if doc:
                meta = doc.get("metadata_info") or {}
                
                st.markdown(f"<h1 class='app-title' style='margin-bottom:0px;'>📄 {doc['title']}</h1>", unsafe_allow_html=True)
                
                authors_list = meta.get("authors") or ["Unknown Author"]
                authors_str = ", ".join(authors_list)
                st.write(f"✍️ *{authors_str}*")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    year_val = meta.get("year")
                    year_str = str(year_val) if year_val else "N/A"
                    st.metric("Publication Year", year_str)
                with col2:
                    journal_val = meta.get("journal") or "Academic Source"
                    journal_val = journal_val[:28] + "..." if len(journal_val) > 30 else journal_val
                    st.metric("Journal / Venue", journal_val)
                with col3:
                    pages = meta.get("page_count") or 0
                    st.metric("Total Pages", f"{pages} Pages")
                    
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                
                if "active_tab" not in st.session_state:
                    st.session_state.active_tab = "📊 Paper Overview"
                    
                nav_cols = st.columns(6)
                tabs = [
                    "📊 Paper Overview", 
                    "🗺️ Concept Mind Map",
                    "💬 Chat with PDF (RAG)", 
                    "🎓 Study Companion", 
                    "🏗️ Industry Application",
                    "🔄 Literature Compare"
                ]
                
                for idx, t_name in enumerate(tabs):
                    with nav_cols[idx]:
                        b_type = "primary" if st.session_state.active_tab == t_name else "secondary"
                        if st.button(t_name, key=f"nav_{idx}", use_container_width=True, type=b_type):
                            st.session_state.active_tab = t_name
                            st.rerun()
                            
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                
                # Tab 1: Paper Overview & Citations
                if st.session_state.active_tab == "📊 Paper Overview":
                    st.markdown("""
                        <div class="glass-card-accent" style="margin-bottom: 25px;">
                            <h3 style="margin-top: 0px; color: #c084fc;">Executive Summary</h3>
                            <p style="line-height: 1.6; font-size: 15px;">""" + doc.get("summary", "No summary generated.") + """</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    left_col, right_col = st.columns(2)
                    with left_col:
                        st.markdown('<div class="glass-card" style="min-height: 250px;">', unsafe_allow_html=True)
                        st.subheader("💡 Key Takeaways & Contributions")
                        points = doc.get("key_points", [])
                        if points:
                            for pt in points:
                                st.markdown(f"- {pt}")
                        else:
                            st.info("No key points logged.")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    with right_col:
                        st.markdown('<div class="glass-card" style="min-height: 250px;">', unsafe_allow_html=True)
                        st.subheader("📌 Key Citations & Notable References")
                        citations = doc.get("citations", [])
                        if citations:
                            for cit in citations:
                                st.markdown(f"- {cit}")
                        else:
                            st.info("No citations extracted.")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    # Visual Cite Section
                    cit_res = requests.get(f"{BACKEND_URL}/api/documents/{doc['id']}/citations", headers=get_headers())
                    if cit_res.status_code == 200:
                        cit_data = cit_res.json().get("citations_data", {})
                        if cit_data:
                            st.write("")
                            with st.expander("📚 Cite this Paper (Reference Formats)"):
                                c_tab_apa, c_tab_mla, c_tab_chicago, c_tab_bibtex = st.tabs(["APA", "MLA", "Chicago", "BibTeX"])
                                with c_tab_apa:
                                    st.code(cit_data.get("APA", ""), language="text")
                                with c_tab_mla:
                                    st.code(cit_data.get("MLA", ""), language="text")
                                with c_tab_chicago:
                                    st.code(cit_data.get("Chicago", ""), language="text")
                                with c_tab_bibtex:
                                    st.code(cit_data.get("BibTeX", ""), language="text")

                # Tab 2: Visual Concept Mind Map
                elif st.session_state.active_tab == "🗺️ Concept Mind Map":
                    with st.spinner("Loading concept mind map..."):
                        mm_res = requests.get(f"{BACKEND_URL}/api/documents/{doc['id']}/mind-map", headers=get_headers())
                        if mm_res.status_code == 200:
                            mm_data = mm_res.json()
                            mind_map_str = mm_data.get("mind_map", "")
                            if mind_map_str:
                                st.markdown('<div class="glass-card-accent">', unsafe_allow_html=True)
                                st.subheader("Concept Mind Map")
                                st.write("Visual hierarchy of core paper concepts and connections:")
                                st.write("")
                                st.markdown(f"""
                                ```mermaid
                                {mind_map_str}
                                ```
                                """)
                                st.markdown('</div>', unsafe_allow_html=True)
                            else:
                                st.info("Concept map could not be loaded.")
                        else:
                            st.error("Failed to fetch concept map.")

                # Tab 3: Chat with PDF
                elif st.session_state.active_tab == "💬 Chat with PDF (RAG)":
                    st.subheader("Interactive Research Assistant")
                    st.write("Ask questions about this paper's formulas, datasets, algorithms, and conclusions:")
                    
                    chat_res = requests.get(
                        f"{BACKEND_URL}/api/documents/{doc['id']}/chat",
                        headers=get_headers()
                    )
                    
                    if chat_res.status_code == 200:
                        chat_messages = chat_res.json()
                        for msg in chat_messages:
                            with st.chat_message(msg["role"]):
                                st.markdown(msg["content"])
                        st.write("")
                        
                        st.write("💡 Suggested Questions:")
                        s_col1, s_col2, s_col3 = st.columns(3)
                        s_query = None
                        with s_col1:
                            if st.button("🔬 What methodology is used?", use_container_width=True):
                                s_query = "What methodology or experimental setup did the authors use?"
                        with s_col2:
                            if st.button("📊 Summarize the main results.", use_container_width=True):
                                s_query = "What are the core experimental results, numbers, and main achievements?"
                        with s_col3:
                            if st.button("⚠️ What are the limitations?", use_container_width=True):
                                s_query = "What limitations, weaknesses, or critiques did the authors mention?"
                                
                        user_input = st.chat_input("Ask a question about the research details...")
                        active_query = user_input or s_query
                        if active_query:
                            with st.spinner("Searching document context..."):
                                try:
                                    chat_post = requests.post(
                                        f"{BACKEND_URL}/api/documents/{doc['id']}/chat",
                                        headers=get_headers(),
                                        json={"query": active_query}
                                    )
                                    if chat_post.status_code == 200:
                                        st.rerun()
                                    else:
                                        st.error(chat_post.json().get("detail", "Error posting chat inquiry."))
                                except Exception as e:
                                    st.error(f"Chat connection error: {e}")
                    else:
                        st.error("Failed to load chat history.")
                        
                # Tab 4: Study Companion (Notes, Flashcards, Quiz)
                elif st.session_state.active_tab == "🎓 Study Companion":
                    subtab_notes, subtab_cards, subtab_quiz = st.tabs([
                        "📓 Detailed Revision Notes", 
                        "🎴 Active Recall Flashcards",
                        "📝 Practice Comprehension Quiz"
                    ])
                    
                    with subtab_notes:
                        notes_loaded = False
                        notes_content = ""
                        with st.spinner("Retrieving notes..."):
                            try:
                                n_res = requests.get(f"{BACKEND_URL}/api/documents/{doc['id']}/notes", headers=get_headers())
                                if n_res.status_code == 200:
                                    notes_content = n_res.json()["notes"]
                                    notes_loaded = True
                            except Exception:
                                pass
                                
                        if notes_loaded:
                            st.markdown('<div class="glass-card-accent">', unsafe_allow_html=True)
                            st.markdown(notes_content)
                            st.write("")
                            st.download_button(
                                label="📥 Download Study Guide (Markdown)",
                                data=notes_content,
                                file_name=f"{doc['title'].lower().replace(' ', '_')}_notes.md",
                                mime="text/markdown"
                            )
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.info("Revision notes could not be loaded.")
                                
                    with subtab_cards:
                        with st.spinner("Loading study flashcards..."):
                            f_res = requests.get(f"{BACKEND_URL}/api/documents/{doc['id']}/flashcards", headers=get_headers())
                            if f_res.status_code == 200:
                                cards = f_res.json().get("flashcards", [])
                                if cards:
                                    fc_idx_key = f"fc_idx_{doc['id']}"
                                    fc_flip_key = f"fc_flip_{doc['id']}"
                                    
                                    if fc_idx_key not in st.session_state:
                                        st.session_state[fc_idx_key] = 0
                                    if fc_flip_key not in st.session_state:
                                        st.session_state[fc_flip_key] = False
                                        
                                    current_idx = st.session_state[fc_idx_key]
                                    is_flipped = st.session_state[fc_flip_key]
                                    
                                    st.write(f"Study Deck: **Card {current_idx + 1} of {len(cards)}**")
                                    card = cards[current_idx]
                                    
                                    if not is_flipped:
                                        st.markdown(f"""
                                            <div class="glass-card-accent" style="height: 220px; display: flex; flex-direction: column; justify-content: center; align-items: center; border-color: rgba(139, 92, 246, 0.45); text-align: center; transition: all 0.3s ease;">
                                                <span style="font-size: 12px; color: #a1a1aa; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px;">❓ Front of Card</span>
                                                <h3 style="margin: 0; color: #ffffff; padding: 0 15px; font-weight: 500;">{card['question']}</h3>
                                            </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"""
                                            <div class="glass-card" style="height: 220px; display: flex; flex-direction: column; justify-content: center; align-items: center; border-color: rgba(34, 197, 94, 0.45); text-align: center; transition: all 0.3s ease;">
                                                <span style="font-size: 12px; color: #4ade80; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px;">💡 Revealed Answer</span>
                                                <p style="margin: 0; font-size: 16px; color: #f4f4f5; padding: 0 20px; line-height: 1.5;">{card['answer']}</p>
                                            </div>
                                        """, unsafe_allow_html=True)
                                        
                                    st.write("")
                                    col_prev, col_flip, col_next = st.columns([1, 2, 1])
                                    with col_prev:
                                        if st.button("⬅️ Previous", key="fc_prev_btn", use_container_width=True, disabled=(current_idx == 0)):
                                            st.session_state[fc_idx_key] = current_idx - 1
                                            st.session_state[fc_flip_key] = False
                                            st.rerun()
                                    with col_flip:
                                        flip_text = "🔄 Reveal Answer" if not is_flipped else "🔄 Hide Answer"
                                        if st.button(flip_text, key="fc_flip_btn", use_container_width=True):
                                            st.session_state[fc_flip_key] = not is_flipped
                                            st.rerun()
                                    with col_next:
                                        if st.button("Next Card ➡️", key="fc_next_btn", use_container_width=True, disabled=(current_idx == len(cards) - 1)):
                                            st.session_state[fc_idx_key] = current_idx + 1
                                            st.session_state[fc_flip_key] = False
                                            st.rerun()
                                else:
                                    st.info("No study cards generated for this paper.")
                            else:
                                st.error("Failed to load study cards.")
                                
                    with subtab_quiz:
                        quiz_loaded = False
                        quizzes = []
                        with st.spinner("Loading comprehension quiz..."):
                            try:
                                q_res = requests.get(f"{BACKEND_URL}/api/documents/{doc['id']}/quiz", headers=get_headers())
                                if q_res.status_code == 200:
                                    quizzes = q_res.json().get("quizzes", [])
                                    if quizzes:
                                        quiz_loaded = True
                            except Exception:
                                pass
                                
                        if quiz_loaded:
                            quiz_key = f"quiz_state_{doc['id']}"
                            if quiz_key not in st.session_state:
                                st.session_state[quiz_key] = {
                                    "answers": {},
                                    "submitted": {},
                                    "score": 0
                                }
                                
                            q_state = st.session_state[quiz_key]
                            st.markdown(f"### Interactive MCQ Quiz")
                            st.write(f"Answer the questions below to test your knowledge of this paper. Score: **{q_state['score']} / {len(quizzes)}**")
                            st.write("")
                            
                            for idx, question in enumerate(quizzes):
                                st.markdown(f"**Q{idx + 1}. {question['question']}**")
                                options = question["options"]
                                is_sub = q_state["submitted"].get(idx, False)
                                saved_selection = q_state["answers"].get(idx, None)
                                default_idx = options.index(saved_selection) if saved_selection in options else 0
                                
                                user_sel = st.radio(
                                    "Select one:",
                                    options,
                                    index=default_idx,
                                    key=f"opt_{doc['id']}_{idx}",
                                    disabled=is_sub
                                )
                                q_state["answers"][idx] = user_sel
                                correct_option = options[question["correct_option_idx"]]
                                
                                if not is_sub:
                                    if st.button(f"Submit Answer {idx + 1}", key=f"btn_quiz_{doc['id']}_{idx}"):
                                        q_state["submitted"][idx] = True
                                        if user_sel == correct_option:
                                            q_state["score"] += 1
                                        st.rerun()
                                else:
                                    if user_sel == correct_option:
                                        st.success(f"Correct! 🎉 {correct_option}")
                                    else:
                                        st.error(f"Incorrect. The correct answer is: **{correct_option}**")
                                    st.info(f"**Explanation:** {question['explanation']}")
                                    
                                st.markdown("<hr style='border-color: rgba(63, 63, 70, 0.25);' />", unsafe_allow_html=True)
                                
                            if st.button("🔄 Reset Quiz Answers", use_container_width=True):
                                del st.session_state[quiz_key]
                                st.rerun()
                        else:
                            st.info("Comprehension quiz is not yet generated.")
                            
                # Tab 5: Industry Application Translator
                elif st.session_state.active_tab == "🏗️ Industry Application":
                    with st.spinner("Translating theoretical insights..."):
                        app_res = requests.get(f"{BACKEND_URL}/api/documents/{doc['id']}/applications", headers=get_headers())
                        if app_res.status_code == 200:
                            app_data = app_res.json()
                            app_markdown = app_data.get("industry_applications", "")
                            if app_markdown:
                                st.markdown('<div class="glass-card-accent">', unsafe_allow_html=True)
                                st.markdown(app_markdown)
                                st.markdown('</div>', unsafe_allow_html=True)
                            else:
                                st.info("No industry applications generated.")
                        else:
                            st.error("Failed to load industry translation report.")

                # Tab 6: Literature Compare
                elif st.session_state.active_tab == "🔄 Literature Compare":
                    st.subheader("Side-by-Side Paper Comparison")
                    st.write("Select another paper from your library to compare methods, scopes, and results side-by-side:")
                    
                    other_docs = [d for d in all_documents if d["id"] != doc["id"]]
                    if not other_docs:
                        st.info("Please upload at least one other PDF to enable the paper comparison module.")
                    else:
                        compare_doc = st.selectbox(
                            "Choose Comparison Document",
                            other_docs,
                            format_func=lambda x: x["title"]
                        )
                        
                        st.markdown('<div class="btn-primary" style="max-width: 250px;">', unsafe_allow_html=True)
                        compare_btn = st.button("🚀 Compare Selected Papers")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        comp_cache_key = f"compare_{doc['id']}_{compare_doc['id']}"
                        if compare_btn:
                            with st.spinner("Conducting side-by-side academic analysis..."):
                                try:
                                    comp_res = requests.post(
                                        f"{BACKEND_URL}/api/documents/compare",
                                        headers=get_headers(),
                                        json={
                                            "document_id_1": doc["id"],
                                            "document_id_2": compare_doc["id"]
                                        }
                                    )
                                    if comp_res.status_code == 200:
                                        st.session_state[comp_cache_key] = comp_res.json()["comparison"]
                                    else:
                                        st.error("Failed to generate literature comparison.")
                                except Exception as e:
                                    st.error(f"Comparison error: {e}")
                                    
                        if comp_cache_key in st.session_state:
                            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                            st.markdown('<div class="glass-card-accent">', unsafe_allow_html=True)
                            st.subheader("Comparative Analysis Result")
                            st.markdown(st.session_state[comp_cache_key])
                            st.markdown('</div>', unsafe_allow_html=True)
                            
            else:
                st.error("Selected document details could not be retrieved.")
                st.session_state.active_document_id = None
                st.rerun()
        except Exception as e:
            st.error(f"Dashboard load error: {e}")
