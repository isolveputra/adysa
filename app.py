import streamlit as st
import sqlite3
import pandas as pd

# ---------------------------------------------------------
# KONFIGURASI HALAMAN
# ---------------------------------------------------------
st.set_page_config(
    page_title="Repositori Materi Kuliah",
    page_icon="📚",
    layout="wide"
)

# ---------------------------------------------------------
# MANAJEMEN DATABASE (SQLite)
# ---------------------------------------------------------
DB_FILE = "materi_kuliah.db"

def init_db():
    """Membuat tabel database jika belum ada."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS materi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matakuliah TEXT NOT NULL,
            topik TEXT NOT NULL,
            judul TEXT NOT NULL,
            konten TEXT NOT NULL,
            link_ref TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_materi(matakuliah, topik, judul, konten, link_ref):
    """Menambah materi baru ke database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO materi (matakuliah, topik, judul, konten, link_ref)
        VALUES (?, ?, ?, ?, ?)
    ''', (matakuliah, topik, judul, konten, link_ref))
    conn.commit()
    conn.close()

def get_all_materi():
    """Mengambil semua materi."""
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM materi ORDER BY id DESC", conn)
    conn.close()
    return df

def delete_materi(materi_id):
    """Menghapus materi berdasarkan ID."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM materi WHERE id = ?", (materi_id,))
    conn.commit()
    conn.close()

# Inisialisasi DB saat aplikasi dijalankan
init_db()

# ---------------------------------------------------------
# ANTARMUKA UTAMA (UI)
# ---------------------------------------------------------
st.title("📚 Platform Repositori Materi Kuliah")
st.caption("Aplikasi manajemen dan penyimpanan materi perkuliahan interaktif.")

# Sidebar Navigation
menu = st.sidebar.radio("Navigasi", ["📖 Baca Materi", "➕ Tambah Materi Baru", "⚙️ Kelola / Hapus Materi"])

# ---------------------------------------------------------
# MENU 1: BACA MATERI
# ---------------------------------------------------------
if menu == "📖 Baca Materi":
    st.header("📖 Daftar Materi Kuliah")
    
    df = get_all_materi()
    
    if df.empty:
        st.info("Belum ada materi yang tersimpan. Silakan tambahkan materi melalui menu **➕ Tambah Materi Baru**.")
    else:
        # Filter berdasarkan Mata Kuliah
        list_mk = ["Semua Mata Kuliah"] + list(df['matakuliah'].unique())
        selected_mk = st.selectbox("Filter berdasarkan Mata Kuliah:", list_mk)
        
        if selected_mk != "Semua Mata Kuliah":
            df_filtered = df[df['matakuliah'] == selected_mk]
        else:
            df_filtered = df

        st.divider()

        # Tampilkan card/expander materi
        for idx, row in df_filtered.iterrows():
            with st.expander(f"📌 [{row['matakuliah']}] {row['judul']} ({row['topik']})"):
                st.markdown(f"**Mata Kuliah:** {row['matakuliah']}")
                st.markdown(f"**Topik / Pertemuan:** {row['topik']}")
                st.markdown("---")
                st.markdown("**Isi Materi:**")
                st.markdown(row['konten'])
                
                if row['link_ref']:
                    st.markdown("---")
                    st.markdown(f"🔗 **Referensi / Link Tambahan:** [{row['link_ref']}]({row['link_ref']})")

# ---------------------------------------------------------
# MENU 2: TAMBAH MATERI BARU
# ---------------------------------------------------------
elif menu == "➕ Tambah Materi Baru":
    st.header("➕ Form Input Materi Kuliah")
    
    with st.form(key="form_tambah_materi", clear_on_submit=True):
        matakuliah = st.text_input("Mata Kuliah (contoh: Digital Forensics, Pemrograman Web, Machine Learning)")
        topik = st.text_input("Topik / Pertemuan (contoh: Pertemuan 3 - Akuisisi Data)")
        judul = st.text_input("Judul Materi")
        konten = st.text_area("Isi Materi (Mendukung format Markdown)", height=250, 
                              placeholder="Tuliskan materi di sini. Anda bisa menggunakan format markdown seperti:\n# Judul Sub\n- Poin 1\n- Poin 2\n\n```python\n# Kodingan contoh\nprint('Hello World')\n```")
        link_ref = st.text_input("Link Referensi / Google Drive / Slide (Opsional)", placeholder="https://...")
        
        submit_button = st.form_submit_button(label="💾 Simpan Materi")

    if submit_button:
        if not matakuliah or not topik or not judul or not konten:
            st.warning("Harap isi semua kolom yang wajib (Mata Kuliah, Topik, Judul, dan Isi Materi).")
        else:
            add_materi(matakuliah, topik, judul, konten, link_ref)
            st.success(f"Materi '{judul}' berhasil disimpan!")

# ---------------------------------------------------------
# MENU 3: KELOLA / HAPUS MATERI
# ---------------------------------------------------------
elif menu == "⚙️ Kelola / Hapus Materi":
    st.header("⚙️ Kelola Data Materi")
    
    df = get_all_materi()
    
    if df.empty:
        st.info("Belum ada materi untuk dikelola.")
    else:
        st.dataframe(df[['id', 'matakuliah', 'topik', 'judul', 'link_ref']], use_container_width=True)
        
        st.divider()
        st.subheader("🗑️ Hapus Materi")
        
        materi_to_delete = st.selectbox("Pilih Materi yang akan dihapus:", 
                                        options=df['id'].tolist(), 
                                        format_func=lambda x: f"ID {x}: {df[df['id']==x]['judul'].values[0]} ({df[df['id']==x]['matakuliah'].values[0]})")
        
        if st.button("❌ Hapus Materi Ini", type="primary"):
            delete_materi(materi_to_delete)
            st.success("Materi berhasil dihapus!")
            st.rerun()
