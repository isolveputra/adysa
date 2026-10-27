import streamlit as st
import os
import subprocess
import re
from pathlib import Path
import fitz  # PyMuPDF untuk render PDF ke Gambar

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
# FUNGSI HELPER: PENGURUTAN ALFANUMERIK (NATURAL SORT)
# ---------------------------------------------------------
def natural_sort_key(s):
    """Fungsi pengurutan agar Pertemuan 1, Pertemuan 2, ..., Pertemuan 10 urut secara logis."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]

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
# FUNGSI KONVERSI PPTX KE GAMBAR SLIDE
# ---------------------------------------------------------
def render_pptx_slides(pptx_path):
    pptx_path = Path(pptx_path)
    pdf_path = pptx_path.with_suffix(".pdf")
    
    # 1. Konversi PPTX ke PDF menggunakan LibreOffice (jika belum ada PDF-nya)
    if not pdf_path.exists():
        try:
            subprocess.run(
                ["soffice", "--headless", "--convert-to", "pdf", str(pptx_path), "--outdir", str(pptx_path.parent)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except Exception as e:
            return None, f"LibreOffice error: {e}"
            
    # 2. Render setiap halaman PDF menjadi gambar menggunakan PyMuPDF
    if pdf_path.exists():
        try:
            doc = fitz.open(str(pdf_path))
            slide_images = []
            for page in doc:
                pix = page.get_pixmap(dpi=150)
                slide_images.append(pix.tobytes("png"))
            return slide_images, None
        except Exception as e:
            return None, f"PDF rendering error: {e}"
            
    return None, "Gagal memproses file PowerPoint."

# ---------------------------------------------------------
# MENU 1: BACA MATERI & VISUAL VIEWER (.pptx, .md, .pdf)
# ---------------------------------------------------------
if menu == "📖 Baca Materi":
    st.title("📚 Repositori Materi Kuliah")
    st.caption("Akses materi perkuliahan lengkap untuk mahasiswa (terurut berdasarkan Pertemuan).")
    
    daftar_mk = sorted([d.name for d in BASE_DIR.iterdir() if d.is_dir()], key=natural_sort_key)

    if not daftar_mk:
        st.info("👋 Belum ada materi yang di-upload oleh dosen.")
    else:
        col1, col2 = st.columns([1, 2])
        with col1:
            pilih_mk = st.selectbox("📌 Pilih Mata Kuliah:", daftar_mk)

        mk_path = BASE_DIR / pilih_mk
        
        # Ambil daftar file & urutkan secara natural (P01, P02, dst.)
        raw_files = [f.name for f in mk_path.iterdir() if f.is_file() and not f.name.endswith(".pdf_temp") and not f.name.endswith(".pdf")]
        daftar_file = sorted(raw_files, key=natural_sort_key)

        if not daftar_file:
            st.warning(f"Belum ada file di dalam mata kuliah **{pilih_mk}**.")
        else:
            with col2:
                pilih_file = st.selectbox("📄 Pilih Pertemuan / File Materi:", daftar_file)

            st.divider()

            file_path = mk_path / pilih_file
            ext = file_path.suffix.lower()

            st.subheader(f"📖 {pilih_file}")

            # 1. Viewer untuk Markdown / Text (.md / .txt)
            if ext in [".md", ".txt"]:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    st.markdown(f.read())

            # 2. Viewer Visual untuk PowerPoint (.pptx) Slide Asli
            elif ext == ".pptx":
                st.success("📊 PowerPoint Slide Deck Viewer (Tampilan Visual Asli)")
                
                with st.spinner("Sedang merender slide PowerPoint..."):
                    images, err = render_pptx_slides(file_path)
                
                if err:
                    st.warning("⚠️ Fitur preview visual memerlukan komponen server LibreOffice. Menampilkan opsi download file.")
                    st.error(err)
                elif images:
                    st.info(f"Total Slide: **{len(images)}** slide. Gunakan tombol navigasi di bawah untuk melihat slide.")
                    
                    if "slide_idx" not in st.session_state:
                        st.session_state.slide_idx = 0
                    
                    if st.session_state.slide_idx >= len(images):
                        st.session_state.slide_idx = 0

                    st.image(images[st.session_state.slide_idx], use_container_width=True, caption=f"Slide {st.session_state.slide_idx + 1} dari {len(images)}")
                    
                    col_prev, col_info, col_next = st.columns([1, 2, 1])
                    with col_prev:
                        if st.button("⬅️ Slide Sebelumnya") and st.session_state.slide_idx > 0:
                            st.session_state.slide_idx -= 1
                            st.rerun()
                    with col_info:
                        st.markdown(f"<p style='text-align: center; font-weight: bold;'>Slide {st.session_state.slide_idx + 1} / {len(images)}</p>", unsafe_allow_html=True)
                    with col_next:
                        if st.button("Slide Berikutnya ➡️") and st.session_state.slide_idx < len(images) - 1:
                            st.session_state.slide_idx += 1
                            st.rerun()

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
# MENU 2: TAMBAH MATERI (CREATE) WITH PERTEMUAN
# ---------------------------------------------------------
elif menu == "📤 Tambah Materi" and st.session_state.role == "admin":
    st.title("📤 Tambah Materi Kuliah Baru")
    
    with st.form("form_tambah", clear_on_submit=True):
        col_mk, col_pert = st.columns([2, 1])
        with col_mk:
            mk_input = st.text_input("Nama Mata Kuliah", placeholder="Contoh: Digital Forensics")
        with col_pert:
            pertemuan_ke = st.number_input("Pertemuan Ke-", min_value=1, max_value=30, value=1, step=1)
            
        tipe_input = st.radio("Metode Input:", ["Upload File (PDF/PPTX/MD/DOCX)", "Tulis Catatan / Markdown Langsung"])
        
        uploaded_file = None
        judul_md = ""
        isi_md = ""
        
        if "Upload" in tipe_input:
            uploaded_file = st.file_uploader("Pilih File Materi", type=["pdf", "pptx", "md", "txt", "docx"])
        else:
            judul_md = st.text_input("Judul Materi", placeholder="Contoh: Akuisisi Data Forensik")
            isi_md = st.text_area("Tulis Isi Materi (Mendukung format Markdown & Kodingan)", height=250)
            
        submit = st.form_submit_button("💾 Simpan Materi", type="primary")
        
        if submit:
            if not mk_input.strip():
                st.warning("Nama Mata Kuliah wajib diisi!")
            else:
                mk_dir = BASE_DIR / mk_input.strip().replace("/", "_")
                mk_dir.mkdir(exist_ok=True)
                
                prefix = f"[P{pertemuan_ke:02d}] "
                
                if uploaded_file is not None:
                    # Tambahkan prefix [P01] jika belum ada
                    filename = uploaded_file.name
                    if not filename.startswith("[P"):
                        filename = f"{prefix}{filename}"
                    
                    save_path = mk_dir / filename
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.success(f"File **{filename}** berhasil disimpan di Pertemuan {pertemuan_ke}!")
                elif judul_md and isi_md:
                    clean_title = judul_md.strip().replace(" ", "_")
                    if not clean_title.endswith(".md"):
                        clean_title += ".md"
                    if not clean_title.startswith("[P"):
                        clean_title = f"{prefix}{clean_title}"
                        
                    save_path = mk_dir / clean_title
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(isi_md)
                    st.success(f"Catatan **{clean_title}** berhasil dibuat di Pertemuan {pertemuan_ke}!")
                else:
                    st.warning("Harap lengkapi data file atau catatan!")

# ---------------------------------------------------------
# MENU 3: EDIT / UPDATE MATERI (UPDATE CRUD)
# ---------------------------------------------------------
elif menu == "✏️ Edit / Update Materi (CRUD)" and st.session_state.role == "admin":
    st.title("✏️ Edit & Update Materi Kuliah")
    st.caption("Ubah nama file, urutan pertemuan, atau ganti isi file materi.")
    
    daftar_mk = sorted([d.name for d in BASE_DIR.iterdir() if d.is_dir()], key=natural_sort_key)
    if not daftar_mk:
        st.info("Belum ada materi yang tersimpan.")
    else:
        pilih_mk = st.selectbox("Pilih Mata Kuliah:", daftar_mk)
        mk_path = BASE_DIR / pilih_mk
        
        raw_files = [f.name for f in mk_path.iterdir() if f.is_file() and not f.name.endswith(".pdf_temp") and not f.name.endswith(".pdf")]
        daftar_file = sorted(raw_files, key=natural_sort_key)
        
        if not daftar_file:
            st.warning("Tidak ada file di mata kuliah ini.")
        else:
            pilih_file = st.selectbox("Pilih File untuk Diedit:", daftar_file)
            file_path = mk_path / pilih_file
            ext = file_path.suffix.lower()
            
            with st.form("form_edit"):
                new_filename = st.text_input("Nama File / Judul:", value=pilih_file)
                
                new_content = ""
                new_file_upload = None
                
                if ext in [".md", ".txt"]:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        current_content = f.read()
                    new_content = st.text_area("Edit Isi Materi (Markdown):", value=current_content, height=300)
                else:
                    st.info(f"File terpilih berformat **{ext.upper()}**. Upload file baru di bawah ini jika ingin menggantinya.")
                    new_file_upload = st.file_uploader("Upload File Pengganti (Opsional)", type=["pptx", "pdf", "docx", "md", "txt"])
                
                update_btn = st.form_submit_button("💾 Perbarui Materi", type="primary")
                
                if update_btn:
                    target_path = mk_path / new_filename
                    
                    if pilih_file != new_filename:
                        if file_path.exists():
                            file_path.rename(target_path)
                        file_path = target_path
                        old_pdf = mk_path / Path(pilih_file).with_suffix(".pdf")
                        if old_pdf.exists():
                            old_pdf.unlink()

                    if ext in [".md", ".txt"] and new_content:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        st.success(f"Materi **{new_filename}** berhasil diperbarui!")
                    
                    elif new_file_upload is not None:
                        if file_path.exists():
                            file_path.unlink()
                        old_pdf = file_path.with_suffix(".pdf")
                        if old_pdf.exists():
                            old_pdf.unlink()
                            
                        new_save_path = mk_path / new_file_upload.name
                        with open(new_save_path, "wb") as f:
                            f.write(new_file_upload.getbuffer())
                        st.success(f"File berhasil diganti dengan **{new_file_upload.name}**!")
                    else:
                        st.success(f"Nama file/materi berhasil diperbarui!")
                    
                    st.rerun()

# ---------------------------------------------------------
# MENU 4: KELOLA / HAPUS MATERI (DELETE)
# ---------------------------------------------------------
elif menu == "⚙️ Kelola / Hapus" and st.session_state.role == "admin":
    st.title("⚙️ Hapus Materi Kuliah")
    
    daftar_mk = sorted([d.name for d in BASE_DIR.iterdir() if d.is_dir()], key=natural_sort_key)
    if not daftar_mk:
        st.info("Belum ada materi.")
    else:
        pilih_mk = st.selectbox("Pilih Mata Kuliah:", daftar_mk)
        mk_path = BASE_DIR / pilih_mk
        
        raw_files = [f.name for f in mk_path.iterdir() if f.is_file() and not f.name.endswith(".pdf_temp") and not f.name.endswith(".pdf")]
        daftar_file = sorted(raw_files, key=natural_sort_key)
        
        if not daftar_file:
            st.warning("Tidak ada file.")
        else:
            pilih_file = st.selectbox("Pilih File yang akan dihapus:", daftar_file)
            file_path = mk_path / pilih_file
            
            st.divider()
            if st.button("🗑️ Hapus File Ini", type="primary"):
                pdf_temp = file_path.with_suffix(".pdf")
                if pdf_temp.exists():
                    pdf_temp.unlink()
                file_path.unlink()
                
                if not list(mk_path.iterdir()):
                    mk_path.rmdir()
                st.success(f"File **{pilih_file}** berhasil dihapus!")
                st.rerun()
