# app.py
import os
# Baris ini menonaktifkan file watcher bawaan Streamlit.
# Berguna untuk mencegah aplikasi restart berulang kali saat file diubah oleh aplikasi itu sendiri (misalnya saat menyimpan indeks).
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"
import uuid
import shutil
import stat
import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from datetime import datetime

# --- KONFIGURASI DASAR ---
# Mendefinisikan nama folder untuk menyimpan dokumen yang diunggah, indeks vector, dan file riwayat.
UPLOAD_FOLDER = "documents"
INDEX_FOLDER = "index_storage"
HISTORY_FILE = "query_history.txt"

# Membuat folder-folder yang diperlukan jika belum ada.
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(INDEX_FOLDER, exist_ok=True)

# Nama model LLM yang digunakan dari Ollama. Pastikan model ini sudah ada di instalasi Ollama Anda.
MODEL_NAME = "phi4:latest"

# Inisialisasi model embedding lokal menggunakan HuggingFace.
# Model ini digunakan untuk mengubah teks menjadi vektor numerik (embeddings).
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# --- INISIALISASI MODEL BAHASA (LLM) ---
try:
    # Menghubungkan ke model LLM yang berjalan di Ollama.
    llm = Ollama(model=MODEL_NAME, request_timeout=120.0)
    # Mengatur LLM ini sebagai default untuk semua operasi di LlamaIndex.
    Settings.llm = llm
except Exception as e:
    st.error(f"Error initializing LLM: {e}")
    st.stop() # Menghentikan eksekusi aplikasi jika LLM gagal diinisialisasi.

def load_or_create_index():
    try:
        if os.path.exists(os.path.join(INDEX_FOLDER, "docstore.json")):
            storage_context = StorageContext.from_defaults(persist_dir=INDEX_FOLDER)
            index = load_index_from_storage(storage_context, embed_model=embed_model)
        else:
            documents = SimpleDirectoryReader(UPLOAD_FOLDER).load_data()
            index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
            index.storage_context.persist(persist_dir=INDEX_FOLDER)
        return index
    except Exception as e:
        st.error(f"Error loading or creating index: {e}")
        st.stop()

# --- FUNGSI UNTUK RIWAYAT PERTANYAAN ---
def save_query_history(query, response):
    try:
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - Q: {query}\nA: {response}\n\n")
    except Exception as e:
        st.warning(f"Failed to save history: {e}")

def load_query_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Failed to read history: {e}"
    return "There is no question history yet."

# --- PENGATURAN TAMPILAN STREAMLIT ---
st.set_page_config(page_title="Local Document Search AI", layout="wide")
st.title("📄 Local Document Search AI")

# --- SIDEBAR: UNGGAH DOKUMEN & KELOLA INDEKS ---
st.sidebar.header("📤 Upload New Document")
uploaded_files = st.sidebar.file_uploader(
    "Select file (PDF, DOCX, TXT)", 
    type=["pdf", "docx", "txt"], 
    accept_multiple_files=True
)

# Fungsi bantuan untuk mengatasi masalah file read-only saat menghapus folder di Windows.
def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

# Menggunakan `st.session_state` untuk melacak apakah indeks perlu dibangun ulang.
# Ini adalah cara Streamlit untuk menyimpan variabel antar interaksi pengguna.
if "index_rebuilt" not in st.session_state:
    st.session_state.index_rebuilt = True # Diasumsikan indeks sudah sinkron saat aplikasi pertama kali dijalankan.

# Tombol untuk membersihkan semua data (dokumen, indeks, dan riwayat).
if st.sidebar.button("🗑️ Clear All Documents & Indexes"):
    try:
        # Remove all files in the documents folder
        if os.path.exists(UPLOAD_FOLDER):
            shutil.rmtree(UPLOAD_FOLDER, onerror=remove_readonly)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        # Remove all files in the index folder
        if os.path.exists(INDEX_FOLDER):
            shutil.rmtree(INDEX_FOLDER, onerror=remove_readonly)
            os.makedirs(INDEX_FOLDER, exist_ok=True)
        # Optionally clear query history
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        st.sidebar.success("All documents, indexes, and history have been cleared.")
        st.session_state.index_rebuilt = True # Set status kembali ke "sudah dibangun ulang" setelah dibersihkan.
    except Exception as e:
        st.sidebar.error(f"Failed to clear data: {e}")

# Logika untuk menangani file yang diunggah.
if uploaded_files:
    for file in uploaded_files:
        # Prevent overwrite by adding a UUID to the filename
        unique_filename = f"{uuid.uuid4()}_{file.name}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        try:
            with open(file_path, "wb") as f:
                f.write(file.read())
        except Exception as e:
            st.sidebar.error(f"Failed to upload {file.name}: {e}")
    # Setelah file baru diunggah, tandai bahwa indeks perlu dibangun ulang.
    st.session_state.index_rebuilt = False 
    st.sidebar.success(f"{len(uploaded_files)} document(s) uploaded.")

# --- LOGIKA PEMBANGUNAN INDEKS OTOMATIS ---
# Jika ada file baru yang diunggah (`index_rebuilt` adalah False), maka bangun ulang indeks secara otomatis.
if not st.session_state.index_rebuilt:
    st.info("New documents have been uploaded. Rebuilding the index...")
    # Menampilkan spinner saat proses indexing berjalan.
    with st.spinner("Indexing documents... This may take a moment."):
        try:
            documents = SimpleDirectoryReader(UPLOAD_FOLDER).load_data()
            index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
            index.storage_context.persist(persist_dir=INDEX_FOLDER)
            # Setelah selesai, set kembali statusnya menjadi True.
            st.session_state.index_rebuilt = True
            st.success("Index successfully rebuilt.")
        except Exception as e:
            st.error(f"Failed to rebuild index: {e}")

# --- AREA UTAMA APLIKASI: TANYA JAWAB ---

# Muat indeks dari penyimpanan atau buat jika belum ada.
index = load_or_create_index()
# Buat 'query engine' dari indeks. Ini adalah objek yang akan menangani query dari pengguna.
query_engine = index.as_query_engine()

st.subheader("🔍 Ask a Question")
query = st.text_input("Enter your question below:")

# Jika pengguna memasukkan pertanyaan dan menekan Enter.
if query:
    try:
        # Kirim pertanyaan ke query engine untuk mendapatkan jawaban.
        response = query_engine.query(query) 
        st.markdown("### 💬 Answer")
        st.write(response.response)

        st.markdown("### 📚 Relevant Documents")
        # Menampilkan dokumen sumber yang paling relevan yang digunakan LLM untuk menjawab.
        if hasattr(response, "source_nodes") and response.source_nodes:
            for node in response.source_nodes:
                st.markdown(f"**Source:** {node.metadata.get('file_name', 'Tidak diketahui')}")
                st.markdown(f"> {node.node.get_text()[:500]}...")
        else:
            st.markdown("No relevant documents found.")

        # Simpan pertanyaan dan jawaban ke file riwayat.
        save_query_history(query, response.response)
    except Exception as e:
        st.error(f"An error occurred while answering the question: {e}")

# --- TAMPILAN RIWAYAT ---
# Menggunakan `st.expander` untuk membuat bagian yang bisa disembunyikan/ditampilkan.
with st.expander("🕘 View Question History:"):
    st.text(load_query_history())