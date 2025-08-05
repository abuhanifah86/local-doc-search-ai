# app.py

import os
import uuid
import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from datetime import datetime

# === Configuration and Setup ===

UPLOAD_FOLDER = "documents"
INDEX_FOLDER = "index_storage"
HISTORY_FILE = "query_history.txt"

# Ensure necessary folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(INDEX_FOLDER, exist_ok=True)

# Name of the Ollama model to use
MODEL_NAME = "phi4:latest"

# Initialize local embedding model (HuggingFace)
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# === LLM Initialization ===

try:
    # Initialize Ollama LLM and set it globally for LlamaIndex
    llm = Ollama(model=MODEL_NAME, request_timeout=120.0)
    Settings.llm = llm
except Exception as e:
    st.error(f"Error initializing LLM: {e}")
    st.stop()

# === Index Loading/Creation ===

def load_or_create_index():
    """
    Loads the index from disk if it exists, otherwise creates a new one from uploaded documents.
    """
    try:
        if os.path.exists(os.path.join(INDEX_FOLDER, "docstore.json")):
            # Load existing index from storage
            storage_context = StorageContext.from_defaults(persist_dir=INDEX_FOLDER)
            index = load_index_from_storage(storage_context, embed_model=embed_model)
        else:
            # Create a new index from documents
            documents = SimpleDirectoryReader(UPLOAD_FOLDER).load_data()
            index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
            index.storage_context.persist(persist_dir=INDEX_FOLDER)
        return index
    except Exception as e:
        st.error(f"Error loading or creating index: {e}")
        st.stop()

# === Query History Utilities ===

def save_query_history(query, response):
    """
    Appends the user's query and the AI's response to the history file.
    """
    try:
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - Q: {query}\nA: {response}\n\n")
    except Exception as e:
        st.warning(f"Gagal menyimpan riwayat: {e}")

def load_query_history():
    """
    Loads the query history from the history file.
    """
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Gagal membaca riwayat: {e}"
    return "Belum ada riwayat pertanyaan."

# === Streamlit UI Setup ===

st.set_page_config(page_title="AI Pencari Dokumen Lokal", layout="wide")
st.title("📄 AI Pencari Dokumen Lokal")

# --- Sidebar: Document Upload ---
st.sidebar.header("📤 Upload Dokumen Baru")
uploaded_files = st.sidebar.file_uploader(
    "Pilih file (PDF, DOCX, TXT)", 
    type=["pdf", "docx", "txt"], 
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        # Prevent overwrite by adding a UUID to the filename
        unique_filename = f"{uuid.uuid4()}_{file.name}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        try:
            with open(file_path, "wb") as f:
                f.write(file.read())
        except Exception as e:
            st.sidebar.error(f"Gagal mengunggah {file.name}: {e}")
    st.sidebar.success("Dokumen berhasil diunggah. Silakan refresh untuk mengindeks ulang.")

# --- Sidebar: Re-index Button ---
if st.sidebar.button("🔄 Bangun Ulang Indeks"):
    try:
        documents = SimpleDirectoryReader(UPLOAD_FOLDER).load_data()
        index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
        index.storage_context.persist(persist_dir=INDEX_FOLDER)
        st.sidebar.success("Indeks berhasil dibangun ulang.")
    except Exception as e:
        st.sidebar.error(f"Gagal membangun ulang indeks: {e}")

# === Main App: Query and Display ===

# Load or create the index
index = load_or_create_index()
query_engine = index.as_query_engine()

st.subheader("🔍 Ajukan Pertanyaan")
query = st.text_input("Masukkan pertanyaan Anda di bawah ini:")

if query:
    try:
        # Query the index
        response = query_engine.query(query)
        st.markdown("### 💬 Jawaban")
        st.write(response.response)

        # Show relevant documents
        st.markdown("### 📚 Dokumen Relevan")
        if hasattr(response, "source_nodes") and response.source_nodes:
            for node in response.source_nodes:
                st.markdown(f"**Sumber:** {node.metadata.get('file_name', 'Tidak diketahui')}")
                st.markdown(f"> {node.node.get_text()[:500]}...")
        else:
            st.markdown("Tidak ada dokumen relevan ditemukan.")

        # Save the query and response to history
        save_query_history(query, response.response)
    except Exception as e:
        st.error(f"Terjadi kesalahan saat menjawab pertanyaan: {e}")

# --- Expandable: Query History ---
with st.expander("🕘 Lihat Riwayat Pertanyaan"):
    st.text(load_query_history())