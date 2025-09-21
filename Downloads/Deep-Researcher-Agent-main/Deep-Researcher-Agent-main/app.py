import streamlit as st
import os
import pickle
from typing import List, Dict, Any
import time
from datetime import datetime

# Import our custom modules
from utils.vector_db import VectorDatabase
from utils.reasoning_engine import ReasoningEngine
from utils.ingest import load_pdfs, load_texts, docs_to_chunks, save_chunks
from utils.embedder import generate_embeddings

# Page configuration
st.set_page_config(
    page_title="Deep Researcher Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean CSS without problematic selectors
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f4e79;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border: 2px solid;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #5a67d8;
        margin-left: 20%;
    }
    .assistant-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-color: #e53e3e;
        margin-right: 20%;
    }
    .status-success {
        color: #38a169;
        font-weight: bold;
        background-color: #f0fff4;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #38a169;
    }
    .status-error {
        color: #e53e3e;
        font-weight: bold;
        background-color: #fed7d7;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #e53e3e;
    }
    .status-warning {
        color: #d69e2e;
        font-weight: bold;
        background-color: #fefcbf;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #d69e2e;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .stTextInput input {
        border-radius: 10px;
        border: 2px solid #667eea;
    }
    .stFileUploader > div {
        border-radius: 10px;
        border: 2px dashed #667eea;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
    }
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 1rem;
    }
    .stFileUploader label {
        color: white !important;
        font-weight: bold;
    }
    .stFileUploader .uploadedFile {
        background: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border-radius: 5px;
        padding: 0.5rem;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .sidebar .sidebar-content .block-container {
        padding-top: 2rem;
    }
    .main .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'vector_db' not in st.session_state:
    st.session_state.vector_db = None
if 'reasoning_engine' not in st.session_state:
    st.session_state.reasoning_engine = None
if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

def initialize_system():
    """Initialize the AI system components."""
    try:
        with st.spinner("🤖 Initializing AI system..."):
            vector_db = VectorDatabase()
            st.session_state.vector_db = vector_db
            st.session_state.reasoning_engine = ReasoningEngine(vector_db)
            
            # Load existing data if available
            if vector_db.load():
                st.session_state.documents_loaded = True
                st.info("📚 Loaded existing documents from previous session")
            else:
                st.session_state.documents_loaded = False
                st.info("📝 Ready for new document uploads")
            
            return True
    except Exception as e:
        st.error(f"❌ Error initializing system: {e}")
        return False

def process_documents(uploaded_files):
    """Process uploaded documents and add to vector database."""
    if not uploaded_files:
        return False
    
    try:
        with st.spinner("📄 Processing documents..."):
            # Clear existing data for new uploads
            if st.session_state.vector_db:
                st.session_state.vector_db.clear()
            
            # Create temporary directory for uploaded files
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Save uploaded files temporarily
            saved_files = []
            for uploaded_file in uploaded_files:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_files.append(file_path)
            
            # Process documents
            docs = []
            for file_path in saved_files:
                if file_path.lower().endswith('.pdf'):
                    pdf_docs = load_pdfs(os.path.dirname(file_path))
                    docs.extend(pdf_docs)
                elif file_path.lower().endswith('.txt'):
                    txt_docs = load_texts(os.path.dirname(file_path))
                    docs.extend(txt_docs)
            
            if not docs:
                st.error("❌ No valid documents found in uploaded files.")
                return False
            
            # Convert to chunks and add to vector database
            chunks = docs_to_chunks(docs, chunk_size=300, overlap=50)
            
            if st.session_state.vector_db:
                st.session_state.vector_db.add_embeddings(chunks)
                st.session_state.vector_db.save()
                st.session_state.documents_loaded = True
                
                # Clean up temporary files
                for file_path in saved_files:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                
                return True
            else:
                st.error("❌ Vector database not initialized.")
                return False
                
    except Exception as e:
        st.error(f"❌ Error processing documents: {e}")
        return False

def display_chat_message(role: str, content: str, reasoning_steps: List[Dict] = None):
    """Display a chat message with proper styling."""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 You:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 Deep Researcher:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
        
        # Show reasoning steps if available
        if reasoning_steps:
            with st.expander("🧠 Reasoning Steps"):
                for i, step in enumerate(reasoning_steps, 1):
                    st.write(f"**Step {i}:** {step['description']}")
                    st.write(f"Sub-queries: {len(step.get('sub_queries', []))}")

def main():
    """Main application function."""
    # Header
    st.markdown('<h1 class="main-header">🔍 Deep Researcher Agent</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize system
    if st.session_state.vector_db is None:
        if not initialize_system():
            st.error("❌ Failed to initialize the system. Please refresh the page.")
            return
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Document Management")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload Documents",
            type=['pdf', 'txt'],
            accept_multiple_files=True,
            help="Upload PDF or TXT files to analyze"
        )
        
        if uploaded_files:
            st.session_state.uploaded_files = [f.name for f in uploaded_files]
        
        # Process documents
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Process Documents", type="primary", use_container_width=True):
                if uploaded_files:
                    with st.spinner("🔄 Processing documents... This may take a moment."):
                        if process_documents(uploaded_files):
                            st.success(f"✅ Successfully processed {len(uploaded_files)} document(s)!")
                            st.balloons()  # Celebration animation
                            st.rerun()
                        else:
                            st.error("❌ Failed to process documents.")
                else:
                    st.warning("⚠️ Please upload at least one document.")
        
        with col2:
            if st.button("🗑️ Clear Database", use_container_width=True):
                if st.session_state.vector_db:
                    st.session_state.vector_db.clear()
                    st.session_state.documents_loaded = False
                    st.session_state.chat_history = []
                    st.session_state.uploaded_files = []
                    st.success("✅ Database cleared!")
                    st.rerun()
        
        # System status
        st.header("📊 System Status")
        if st.session_state.documents_loaded:
            stats = st.session_state.vector_db.get_stats()
            st.success("✅ System Ready")
            st.write(f"📚 **Chunks:** {stats['total_vectors']}")
            st.write(f"🤖 **Model:** {stats['model_name']}")
            
            # Show uploaded files with better styling
            if st.session_state.uploaded_files:
                st.markdown("### 📄 Uploaded Files:")
                for file_name in st.session_state.uploaded_files:
                    st.markdown(f"• **{file_name}**")
            
            # Quick actions
            st.markdown("### 🔧 Quick Actions")
            
            # Sample content preview
            if st.button("📝 Sample Content", use_container_width=True):
                try:
                    sample_text = st.session_state.vector_db.metadata[0]['text'][:200]
                    st.markdown("**📝 Sample Content:**")
                    st.markdown(f"*{sample_text}...*")
                except:
                    st.warning("No content available")
            
            # Debug database
            if st.button("🔍 Debug Database", use_container_width=True):
                try:
                    stats = st.session_state.vector_db.get_stats()
                    st.markdown("**Database Stats:**")
                    st.json(stats)
                    
                    if st.session_state.vector_db.metadata:
                        st.markdown("**Sample Metadata:**")
                        st.json(st.session_state.vector_db.metadata[0])
                except Exception as e:
                    st.error(f"Debug error: {e}")
        else:
            st.warning("⚠️ No documents loaded")
            st.info("📚 Upload documents to start researching!")
            
            # Show what happens when documents are loaded
            st.markdown("""
            ### 🎯 What happens when you upload documents?
            
            1. **📄 Document Processing** - Files are read and converted to text
            2. **✂️ Text Chunking** - Content is split into manageable pieces
            3. **🧠 AI Embedding** - Each chunk gets a semantic representation
            4. **💾 Vector Storage** - Embeddings are stored for fast retrieval
            5. **🔍 Ready for Queries** - You can now ask questions!
            """)
        
        # Settings
        st.header("⚙️ Settings")
        top_k = st.slider("Number of results to retrieve", 1, 10, 5)
        chunk_size = st.slider("Chunk size", 100, 500, 300)
    
    # Main interface
    if not st.session_state.documents_loaded:
        # Welcome screen with detailed explanation
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 20px; color: white; margin: 2rem 0;">
            <h1 style="font-size: 3rem; margin-bottom: 1rem;">🔍 Deep Researcher Agent</h1>
            <h2 style="font-size: 1.5rem; margin-bottom: 2rem; opacity: 0.9;">Your AI-Powered Research Assistant</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ## 🚀 What is Deep Researcher Agent?
        
        **Deep Researcher Agent** is an advanced AI-powered system that can analyze and answer questions about your documents using cutting-edge artificial intelligence. Here's what makes it special:
        
        ### ✨ Key Features:
        
        **🧠 Multi-Step Reasoning**
        - Breaks down complex questions into smaller, manageable parts
        - Uses advanced AI models to understand context and relationships
        - Provides detailed reasoning steps for transparency
        
        **📚 Local AI Processing**
        - No external API calls - everything runs on your computer
        - Uses state-of-the-art language models (BART, DistilBERT)
        - Fast, secure, and private document analysis
        
        **🔍 Intelligent Search**
        - Semantic search that understands meaning, not just keywords
        - Finds relevant information even with different wording
        - Ranks results by relevance and confidence
        
        **💬 Natural Conversations**
        - Ask questions in plain English
        - Get detailed, well-structured answers
        - Follow-up questions and clarifications supported
        
        ### 📋 Supported Document Types:
        - **PDF files** - Research papers, reports, articles
        - **Text files** - Notes, transcripts, documentation
        - **Multiple files** - Analyze multiple documents together
        
        ### 🎯 How to Get Started:
        
        1. **📁 Upload Documents** - Use the sidebar to upload your PDF or TXT files
        2. **⚙️ Process Documents** - Click "Process Documents" to analyze and index them
        3. **💬 Start Chatting** - Ask questions about your documents in natural language
        4. **🔍 Explore** - Use the reasoning steps to understand how the AI thinks
        
        ### 💡 Example Questions You Can Ask:
        - "What is this document about?"
        - "Summarize the main points"
        - "What are the key findings?"
        - "Compare the different sections"
        - "What are the recommendations?"
        - "Explain the methodology used"
        
        ---
        
        **Ready to start? Upload your documents using the sidebar! 📚**
        """)
        
        # Show some example interactions
        with st.expander("🔍 See Example Interactions", expanded=False):
            st.markdown("""
            **Example 1: Research Paper Analysis**
            - Upload: "AI_in_Healthcare_2024.pdf"
            - Ask: "What are the main findings about AI in healthcare?"
            - Get: Detailed summary with key findings, statistics, and conclusions
            
            **Example 2: Multiple Document Comparison**
            - Upload: "Company_Report_2023.pdf" and "Market_Analysis.txt"
            - Ask: "Compare the market trends mentioned in both documents"
            - Get: Side-by-side comparison with insights and differences
            
            **Example 3: Technical Documentation**
            - Upload: "API_Documentation.pdf"
            - Ask: "How do I authenticate with the API?"
            - Get: Step-by-step instructions with code examples
            """)
    
    else:
        # Chat interface when documents are loaded
        st.header("💬 Chat with Deep Researcher")
        
        # Display chat history
        for message in st.session_state.chat_history:
            display_chat_message(
                message['role'], 
                message['content'], 
                message.get('reasoning_steps')
            )
    
    # Chat input using form to avoid session state issues
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Ask a question about your documents:",
            placeholder="e.g., What is this document about? Summarize the main points.",
            key="user_input"
        )
        
        submitted = st.form_submit_button("🔍 Search", type="primary")
        
        if submitted:
            if user_input and st.session_state.documents_loaded:
                # Process query
                with st.spinner("🧠 Thinking..."):
                    try:
                        response = st.session_state.reasoning_engine.process_query(user_input, top_k=top_k)
                        
                        # Add to chat history
                        st.session_state.chat_history.append({
                            'role': 'user',
                            'content': user_input,
                            'timestamp': datetime.now()
                        })
                        
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': response['synthesis'],
                            'reasoning_steps': response['reasoning_steps'],
                            'timestamp': datetime.now()
                        })
                        
                        # Rerun to show new messages
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error processing query: {e}")
            
            elif user_input and not st.session_state.documents_loaded:
                st.warning("⚠️ Please upload and process documents first!")
            elif not user_input:
                st.info("💡 Enter a question to get started!")

if __name__ == "__main__":
    main()
