# 📄 AI Pencari Dokumen Lokal

Aplikasi web sederhana yang dibangun dengan Streamlit dan LlamaIndex untuk memungkinkan Anda melakukan pencarian dan tanya jawab pada dokumen Anda sendiri secara lokal. Aplikasi ini menggunakan model LLM dari Ollama dan model embedding lokal, memastikan semua data tetap berada di mesin Anda.

<img width="1920" height="1032" alt="image" src="https://github.com/user-attachments/assets/50149468-7a9d-40d1-8159-2fe086310a85" />

## ✨ Fitur

-   **Unggah Dokumen**: Mendukung file PDF, DOCX, dan TXT.
-   **Tanya Jawab**: Ajukan pertanyaan dalam bahasa alami tentang konten dokumen Anda.
-   **Jawaban Berbasis Sumber**: Dapatkan jawaban yang dihasilkan oleh LLM beserta kutipan dari dokumen sumber yang relevan.
-   **100% Lokal**: Menggunakan [Ollama](https://ollama.com/) untuk menjalankan LLM secara lokal dan [HuggingFace Embeddings](https://huggingface.co/BAAI/bge-small-en-v1.5) untuk pembuatan vektor. Tidak ada data yang dikirim ke cloud.
-   **Indeks Persisten**: Indeks vektor dari dokumen Anda disimpan secara lokal untuk mempercepat pemuatan di sesi berikutnya.
-   **Indexing Otomatis**: Secara otomatis membangun ulang indeks ketika dokumen baru diunggah.
-   **Manajemen Data**: Fitur untuk membersihkan semua dokumen, indeks, dan riwayat yang tersimpan.
-   **Riwayat Pertanyaan**: Menyimpan catatan semua pertanyaan dan jawaban Anda.

## ⚙️ Prasyarat

Sebelum Anda memulai, pastikan Anda telah menginstal perangkat lunak berikut:

1.  **Python 3.8+**
2.  **Ollama**: Ikuti petunjuk instalasi di [situs web Ollama](https://ollama.com/).
3.  **Model LLM untuk Ollama**: Aplikasi ini dikonfigurasi untuk menggunakan `phi4:latest`. Tarik model ini dengan menjalankan perintah berikut di terminal Anda:
    ```bash
    ollama pull phi4:latest
    ```
    Pastikan Ollama sedang berjalan di latar belakang sebelum menjalankan aplikasi Streamlit.

## 🚀 Instalasi & Penggunaan

1.  **Clone Repositori**
    ```bash
    git clone <URL_REPOSITORI_ANDA>
    cd <NAMA_FOLDER_REPOSITORI>
    ```

2.  **Buat Lingkungan Virtual (Direkomendasikan)**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Di Windows, gunakan: venv\Scripts\activate
    ```

3.  **Instal Dependensi**
    Aplikasi ini memerlukan beberapa pustaka Python. Instal semuanya dengan satu perintah menggunakan file `requirements.txt` yang disediakan.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Jalankan Aplikasi**
    Pastikan Ollama sudah berjalan. Kemudian, jalankan aplikasi Streamlit dengan perintah:
    ```bash
    streamlit run app.py
    ```

5.  **Gunakan Aplikasi**
    -   Buka browser Anda dan navigasikan ke URL lokal yang ditampilkan oleh Streamlit (biasanya `http://localhost:8501`).
    -   Gunakan sidebar untuk mengunggah dokumen Anda.
    -   Tunggu aplikasi selesai mengindeks dokumen baru (Anda akan melihat statusnya).
    -   Ketik pertanyaan Anda di kotak input utama dan tekan Enter.
    -   Jawaban dan dokumen sumber yang relevan akan ditampilkan.

## 🔧 Konfigurasi

Anda dapat mengubah beberapa pengaturan langsung di bagian atas file `app.py`:

-   `MODEL_NAME`: Ganti `"phi4:latest"` dengan model Ollama lain yang telah Anda unduh (misalnya, `"llama3:latest"`).
-   `UPLOAD_FOLDER`: Nama folder untuk menyimpan dokumen yang diunggah.
-   `INDEX_FOLDER`: Nama folder untuk menyimpan data indeks vektor.
-   `HISTORY_FILE`: Nama file untuk menyimpan riwayat percakapan.

## 📁 Struktur File

```
.
├── documents/         # Folder untuk menyimpan file yang diunggah (dibuat otomatis)
├── index_storage/     # Folder untuk menyimpan indeks vektor (dibuat otomatis)
├── app.py             # Kode utama aplikasi Streamlit
├── query_history.txt  # File riwayat pertanyaan (dibuat otomatis)
├── requirements.txt   # Daftar dependensi Python
└── README.md          # File ini
```
