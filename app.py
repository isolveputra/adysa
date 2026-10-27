import streamlit as st
import os

# ---------------------------------------------------------
# KONFIGURASI HALAMAN
# ---------------------------------------------------------
st.set_page_config(
    page_title="Repositori Materi Kuliah Terproteksi",
    page_icon="📚",
    layout="wide"
)

BASE_DIR = "materi_terupload"
os.makedirs(BASE_DIR, exist_ok=True)

# ---------------------------------------------------------
# INISIALISASI SESSION STATE UNTUK LOGIN
# ---------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = "mahasiswa"  # Default role untuk pengunjung umum

# ---------------------------------------------------------
# SIDEBAR: AUTENTIKASI & NAVIGASI
# ---------------------------------------------------------
st.sidebar.title("🔐 Akses Sistem")

# Status Login di Sidebar
if st.session_state.logged_in:
    st.sidebar.success(f"Login sebagai: **{st.session_state.role.upper()}**")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = "mahasiswa"
        st.rerun()
else:
    with st.sidebar.expander("🔑 Login khusus Dosen / Admin"):
        # Anda bisa mengubah username & password di sini
        input_user = st.text_input("Username")
        input_pass = st.text_input("Password", type="password")
        
        if st.button("Masuk"):
            # Contoh kredensial sederhana (bisa diganti sesuai keinginan)
            if input_user == "dosen" and input_pass == "amikom123":
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.sidebar.success("Login Berhasil!")
                st.rerun()
            else:
                st.sidebar.error("Username atau Password salah!")

st.sidebar.divider()
st.sidebar.title("📌 Menu Navigasi")

# Daftar menu berdasarkan hak akses (Role)
if st.session_state.role == "admin":
    menu = st.sidebar.radio("Pilih Menu:", ["📖 Baca Materi", "📤 Upload Materi Baru", "⚙️ Kelola / Hapus Materi"])
else:
    menu = st.sidebar.radio("Pilih Menu:", ["📖 Baca Materi"])
    st.sidebar.info("💡 Mahasiswa memiliki hak akses **Hanya Baca (Read-Only)**.")

# ---------------------------------------------------------
# HALAMAN 1: BACA MATERI (Bisa diakses semua orang)
# ---------------------------------------------------------
if menu == "📖 Baca Materi":
    st.title("📚 Repositori Materi Kuliah")
    st.caption("Akses materi perkuliahan lengkap untuk mahasiswa.")
    
    daftar_mk = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]

    if not daftar_mk:
        st.info("👋 Belum ada materi yang di-upload oleh dosen.")
    else:
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

            file_path = os.path.join(mk_path, pilih_file)
            file_ext = os.path.splitext(pilih_file)[1].lower()

            st.subheader(f"📖 {pilih_file}")

            if file_ext in [".md", ".txt"]:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    isi_teks = f.read()
                st.markdown(isi_teks)

            elif file_ext == ".pdf":
                st.info("File dalam format PDF.")
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download / Baca PDF",
                        data=f,
                        file_name=pilih_file,
                        mime="application/pdf"
                    )
            else:
                with open(file_path, "rb") as f:
                    st.download_button(
                        label=f"⬇️ Download File ({pilih_file})",
                        data=f,
                        file_name=pilih_file
                    )

# ---------------------------------------------------------
# HALAMAN 2: UPLOAD MATERI BARU (Hanya untuk Admin / Dosen)
# ---------------------------------------------------------
elif menu == "📤 Upload Materi Baru" and st.session_state.role == "admin":
    st.title("📤 Form Upload Materi Kuliah")
    st.caption("Menu khusus Dosen untuk menambahkan modul baru.")
    
    with st.form("form_upload", clear_on_submit=True):
        mk_input = st.text_input("Nama Mata Kuliah", placeholder="Contoh: Digital Forensics")
        uploaded_file = st.file_uploader("Pilih File Materi", type=["pdf", "md", "txt", "docx", "pptx"])
        
        submit_btn = st.form_submit_button("💾 Simpan Materi", type="primary")
        
        if submit_btn:
            if not mk_input.strip() or uploaded_file is None:
                st.warning("Harap isi Nama Mata Kuliah dan pilih file terlebih dahulu!")
            else:
                clean_mk_name = mk_input.strip().replace("/", "_").replace("\\", "_")
                target_dir = os.path.join(BASE_DIR, clean_mk_name)
                os.makedirs(target_dir, exist_ok=True)

                save_path = os.path.join(target_dir, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                st.success(f"File **{uploaded_file.name}** berhasil di-upload ke mata kuliah **{clean_mk_name}**!")

# ---------------------------------------------------------
# HALAMAN 3: KELOLA / HAPUS MATERI (Hanya untuk Admin / Dosen)
# ---------------------------------------------------------
elif menu == "⚙️ Kelola / Hapus Materi" and st.session_state.role == "admin":
    st.title("⚙️ Kelola & Hapus Materi")
    st.caption("Hapus materi yang sudah kedaluwarsa atau salah upload.")
    
    daftar_mk = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    
    if not daftar_mk:
        st.info("Belum ada materi yang tersimpan.")
    else:
        pilih_mk_hapus = st.selectbox("Pilih Mata Kuliah:", daftar_mk)
        mk_path_hapus = os.path.join(BASE_DIR, pilih_mk_hapus)
        daftar_file_hapus = os.listdir(mk_path_hapus)
        
        if not daftar_file_hapus:
            st.warning("Tidak ada file di mata kuliah ini.")
        else:
            pilih_file_hapus = st.selectbox("Pilih File yang akan dihapus:", daftar_file_hapus)
            file_path_hapus = os.path.join(mk_path_hapus, pilih_file_hapus)
            
            st.divider()
            if st.button("🗑️ Hapus File Ini", type="primary"):
                os.remove(file_path_hapus)
                # Jika folder kosong, hapus foldernya juga
                if not os.listdir(mk_path_hapus):
                    os.rmdir(mk_path_hapus)
                st.success(f"File **{pilih_file_hapus}** berhasil dihapus!")
                st.rerun()
