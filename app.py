import streamlit as st
import os
import shutil

# ---------------------------------------------------------
# KONFIGURASI HALAMAN
# ---------------------------------------------------------
st.set_page_config(
    page_title="Platform Upload Materi Kuliah",
    page_icon="📚",
    layout="wide"
)

# Folder utama tempat menyimpan file upload di server Streamlit
BASE_DIR = "materi_terupload"
os.makedirs(BASE_DIR, exist_ok=True)

st.title("📚 Repositori Materi Kuliah Interaktif")
st.caption("Upload dan akses modul/materi kuliah langsung dari browser.")

# ---------------------------------------------------------
# SIDEBAR: PANEL UPLOAD MATERI
# ---------------------------------------------------------
st.sidebar.header("📤 Form Upload Materi")

# Input Nama Mata Kuliah & File
mk_input = st.sidebar.text_input("Nama Mata Kuliah", placeholder="Contoh: Digital Forensics")
uploaded_file = st.sidebar.file_uploader(
    "Pilih File Materi", 
    type=["pdf", "md", "txt", "docx", "pptx"]
)

# Tombol Simpan
if st.sidebar.button("💾 Simpan Materi", type="primary"):
    if not mk_input.strip():
        st.sidebar.error("Harap isi Nama Mata Kuliah terlebih dahulu!")
    elif uploaded_file is None:
        st.sidebar.error("Pilih file materi yang ingin di-upload!")
    else:
        # Bersihkan nama folder dari karakter aneh
        clean_mk_name = mk_input.strip().replace("/", "_").replace("\\", "_")
        target_dir = os.path.join(BASE_DIR, clean_mk_name)
        os.makedirs(target_dir, exist_ok=True)

        # Simpan file ke direktori tujuan
        save_path = os.path.join(target_dir, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.sidebar.success(f"File **{uploaded_file.name}** berhasil disimpan di mata kuliah **{clean_mk_name}**!")
        st.rerun()

# ---------------------------------------------------------
# HALAMAN UTAMA: BACA & KELOLA MATERI
# ---------------------------------------------------------
# Ambil daftar folder mata kuliah
daftar_mk = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]

if not daftar_mk:
    st.info("👋 Belum ada materi yang di-upload. Silakan gunakan menu **Form Upload Materi** di sidebar sebelah kiri.")
else:
    # Filter Mata Kuliah
    col1, col2 = st.columns([1, 2])
    with col1:
        pilih_mk = st.selectbox("📌 Pilih Mata Kuliah:", daftar_mk)

    mk_path = os.path.join(BASE_DIR, pilih_mk)
    daftar_file = os.listdir(mk_path)

    if not daftar_file:
        st.warning(f"Belum ada file di dalam mata kuliah **{pilih_mk}**.")
    else:
        with col2:
            pilih_file = st.selectbox("📄 Pilih File Materi:", daftar_file)

        st.divider()

        # Path file yang dipilih
        file_path = os.path.join(mk_path, pilih_file)
        file_ext = os.path.splitext(pilih_file)[1].lower()

        st.subheader(f"📖 {pilih_file}")

        # Tampilkan atau Sediakan Tombol Download berdasarkan Ekstensi File
        if file_ext in [".md", ".txt"]:
            # Jika teks / markdown, tampilkan isinya langsung di layar
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                isi_teks = f.read()
            st.markdown(isi_teks)

        elif file_ext == ".pdf":
            st.info("File dalam format PDF. Anda dapat mengunduh atau membukanya langsung.")
            with open(file_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download PDF Materi",
                    data=f,
                    file_name=pilih_file,
                    mime="application/pdf"
                )

        else:
            # File dokumen seperti DOCX / PPTX
            st.info(f"File format {file_ext.upper()}. Klik tombol di bawah untuk mengunduh.")
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"⬇️ Download File ({pilih_file})",
                    data=f,
                    file_name=pilih_file
                )

        # ---------------------------------------------------------
        # FITUR HAPUS FILE (OPSIONAL)
        # ---------------------------------------------------------
        with st.expander("⚙️ Opsi Pengelola File"):
            if st.button("🗑️ Hapus File Ini", type="secondary"):
                os.remove(file_path)
                st.success(f"File {pilih_file} berhasil dihapus.")
                st.rerun()
