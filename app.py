import streamlit as st
import os
from pathlib import Path
from pptx import Presentation

# ---------------------------------------------------------
# KONFIGURASI HALAMAN
# ---------------------------------------------------------
st.set_page_config(
    page_title="Repositori Materi Kuliah Pro",
    page_icon="📚",
    layout="wide"
)

BASE_DIR = Path("materi_terupload")
BASE_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------
# INISIALISASI SESSION STATE LOGIN
# ---------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = "mahasiswa"

# Sidebar: Login & Navigasi
st.sidebar.title("🔐 Akses Sistem")
if st.session_state.logged_in:
    st.sidebar.success(f"Login sebagai: **{st.session_state.role.upper()}**")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = "mahasiswa"
        st.rerun()
else:
    with st.sidebar.expander("🔑 Login Dosen / Admin"):
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Masuk"):
            # Ganti username & password sesuai keinginan Anda
            if user == "dosen" and pwd == "amikom123":
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.sidebar.success("Login Berhasil!")
                st.rerun()
            else:
                st.sidebar.error("Username atau Password salah!")

st.sidebar.divider()
st.sidebar.title("📌 Menu Navigasi")

if st.session_state.role == "admin":
    menu = st.sidebar.radio("Pilih Menu:", [
        "📖 Baca Materi", 
        "📤 Tambah Materi", 
        "✏️ Edit / Update Materi (CRUD)", 
        "⚙️ Kelola / Hapus"
    ])
else:
    menu = st.sidebar.radio("Pilih Menu:", ["📖 Baca Materi"])
    st.sidebar.info("💡 Mahasiswa memiliki hak akses **Hanya Baca (Read-Only)**.")

# ---------------------------------------------------------
# MENU 1: BACA MATERI & IN-BROWSER VIEWERS (.pptx, .md, .pdf)
# ---------------------------------------------------------
if menu == "📖 Baca Materi":
    st.title("📚 Repositori Materi Kuliah")
    st.caption("Akses materi perkuliahan lengkap untuk mahasiswa.")
    
    daftar_mk = [d.name for d in BASE_DIR.iterdir() if d.is_dir()]

    if not daftar_mk:
        st.info("👋 Belum ada materi yang di-upload oleh dosen.")
    else:
        col1, col2 = st.columns([1, 2])
        with col1:
            pilih_mk = st.selectbox("📌 Pilih Mata Kuliah:", daftar_mk)

        mk_path = BASE_DIR / pilih_mk
        daftar_file = [f.name for f in mk_path.iterdir() if f.is_file()]

        if not daftar_file:
            st.warning(f"Belum ada file di dalam mata kuliah **{pilih_mk}**.")
        else:
            with col2:
                pilih_file = st.selectbox("📄 Pilih File Materi:", daftar_file)

            st.divider()

            file_path = mk_path / pilih_file
            ext = file_path.suffix.lower()

            st.subheader(f"📄 {pilih_file}")

            # 1. Viewer untuk Markdown / Text (.md / .txt)
            if ext in [".md", ".txt"]:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    st.markdown(f.read())

            # 2. Viewer untuk PowerPoint (.pptx) Langsung di Browser
            elif ext == ".pptx":
                st.success("📊 PowerPoint Presentation Viewer (Tampil Langsung di Browser)")
                try:
                    prs = Presentation(file_path)
                    st.caption(f"Total Slide: {len(prs.slides)}")
                    
                    # Tampilkan slide menggunakan tab interaktif
                    slide_tabs = st.tabs([f"Slide {i+1}" for i in range(len(prs.slides))])
                    for i, slide in enumerate(prs.slides):
                        with slide_tabs[i]:
                            st.markdown(f"#### Slide {i+1}")
                            slide_texts = []
                            for shape in slide.shapes:
                                if shape.has_text_frame:
                                    for p in shape.text_frame.paragraphs:
                                        if p.text.strip():
                                            slide_texts.append(p.text)
                            
                            if slide_texts:
                                for t in slide_texts:
                                    st.markdown(f"- {t}")
                            else:
                                st.info("*(Slide ini berisi gambar / bentuk grafis tanpa teks teks terdeteksi)*")
                except Exception as e:
                    st.error(f"Gagal memuat file PowerPoint: {e}")

                st.divider()
                with open(file_path, "rb") as f:
                    st.download_button("⬇️ Download File PowerPoint (.pptx)", f, file_name=pilih_file)

            # 3. Viewer untuk PDF & File Lainnya
            elif ext == ".pdf":
                st.info("File PDF Materi Kuliah")
                with open(file_path, "rb") as f:
                    st.download_button("⬇️ Download / Buka PDF", f, file_name=pilih_file, mime="application/pdf")
            else:
                with open(file_path, "rb") as f:
                    st.download_button(f"⬇️ Download File ({pilih_file})", f, file_name=pilih_file)

# ---------------------------------------------------------
# MENU 2: TAMBAH MATERI (CREATE)
# ---------------------------------------------------------
elif menu == "📤 Tambah Materi" and st.session_state.role == "admin":
    st.title("📤 Tambah Materi Kuliah Baru")
    
    with st.form("form_tambah", clear_on_submit=True):
        mk_input = st.text_input("Nama Mata Kuliah (contoh: Digital Forensics)")
        tipe_input = st.radio("Metode Input:", ["Upload File (PDF/PPTX/MD/DOCX)", "Tulis Catatan / Markdown Langsung"])
        
        uploaded_file = None
        judul_md = ""
        isi_md = ""
        
        if "Upload" in tipe_input:
            uploaded_file = st.file_uploader("Pilih File Materi", type=["pdf", "pptx", "md", "txt", "docx"])
        else:
            judul_md = st.text_input("Nama File Materi (contoh: Pertemuan_3_Akuisisi.md)")
            isi_md = st.text_area("Tulis Isi Materi (Mendukung format Markdown & Kodingan)", height=250)
            
        submit = st.form_submit_button("💾 Simpan Materi", type="primary")
        
        if submit:
            if not mk_input.strip():
                st.warning("Nama Mata Kuliah wajib diisi!")
            else:
                mk_dir = BASE_DIR / mk_input.strip().replace("/", "_")
                mk_dir.mkdir(exist_ok=True)
                
                if uploaded_file is not None:
                    save_path = mk_dir / uploaded_file.name
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.success(f"File **{uploaded_file.name}** berhasil di-upload!")
                elif judul_md and isi_md:
                    if not judul_md.endswith(".md"):
                        judul_md += ".md"
                    save_path = mk_dir / judul_md
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(isi_md)
                    st.success(f"Catatan **{judul_md}** berhasil dibuat!")
                else:
                    st.warning("Harap lengkapi data file atau catatan!")

# ---------------------------------------------------------
# MENU 3: EDIT / UPDATE MATERI (UPDATE CRUD)
# ---------------------------------------------------------
elif menu == "✏️ Edit / Update Materi (CRUD)" and st.session_state.role == "admin":
    st.title("✏️ Edit & Update Materi Kuliah")
    st.caption("Ubah isi materi teks/markdown secara langsung di browser.")
    
    daftar_mk = [d.name for d in BASE_DIR.iterdir() if d.is_dir()]
    if not daftar_mk:
        st.info("Belum ada materi yang tersimpan.")
    else:
        pilih_mk = st.selectbox("Pilih Mata Kuliah:", daftar_mk)
        mk_path = BASE_DIR / pilih_mk
        daftar_file = [f.name for f in mk_path.iterdir() if f.is_file() and f.suffix.lower() in [".md", ".txt"]]
        
        if not daftar_file:
            st.warning("Tidak ada file teks/markdown (.md / .txt) yang dapat diedit di mata kuliah ini.")
        else:
            pilih_file = st.selectbox("Pilih File untuk Diedit:", daftar_file)
            file_path = mk_path / pilih_file
            
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                current_content = f.read()
            
            with st.form("form_edit"):
                new_filename = st.text_input("Ganti Nama File:", value=pilih_file)
                new_content = st.text_area("Edit Isi Materi:", value=current_content, height=350)
                update_btn = st.form_submit_button("💾 Perbarui Materi", type="primary")
                
                if update_btn:
                    # Jika nama file berubah, hapus yang lama
                    new_path = mk_path / new_filename
                    if pilih_file != new_filename and file_path.exists():
                        file_path.unlink()
                    
                    with open(new_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    st.success(f"Materi **{new_filename}** berhasil diperbarui!")
                    st.rerun()

# ---------------------------------------------------------
# MENU 4: KELOLA / HAPUS MATERI (DELETE)
# ---------------------------------------------------------
elif menu == "⚙️ Kelola / Hapus" and st.session_state.role == "admin":
    st.title("⚙️ Hapus Materi Kuliah")
    
    daftar_mk = [d.name for d in BASE_DIR.iterdir() if d.is_dir()]
    if not daftar_mk:
        st.info("Belum ada materi.")
    else:
        pilih_mk = st.selectbox("Pilih Mata Kuliah:", daftar_mk)
        mk_path = BASE_DIR / pilih_mk
        daftar_file = [f.name for f in mk_path.iterdir() if f.is_file()]
        
        if not daftar_file:
            st.warning("Tidak ada file.")
        else:
            pilih_file = st.selectbox("Pilih File yang akan dihapus:", daftar_file)
            file_path = mk_path / pilih_file
            
            st.divider()
            if st.button("🗑️ Hapus File Ini", type="primary"):
                file_path.unlink()
                if not list(mk_path.iterdir()):
                    mk_path.rmdir()
                st.success(f"File **{pilih_file}** berhasil dihapus!")
                st.rerun()
