import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Logika Fuzzy Suhu Ruangan",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ Studi Kasus Logika Fuzzy")
st.subheader("Penentuan Tingkat Kepanasan Suhu Ruangan")

st.markdown("""
Sistem Smart Room menentukan kondisi suhu menggunakan Logika Fuzzy.
Satu suhu dapat memiliki lebih dari satu derajat keanggotaan.
""")

# ==========================
# Fungsi Keanggotaan
# ==========================

def dingin(x):
    if x <= 15:
        return 1
    elif 15 < x < 25:
        return (25 - x) / (25 - 15)
    else:
        return 0

def hangat(x):
    if x <= 15 or x >= 35:
        return 0
    elif 15 < x <= 25:
        return (x - 15) / (25 - 15)
    elif 25 < x < 35:
        return (35 - x) / (35 - 25)
    else:
        return 1

def panas(x):
    if x <= 25:
        return 0
    elif 25 < x < 35:
        return (x - 25) / (35 - 25)
    else:
        return 1

# ==========================
# Input Suhu
# ==========================

st.sidebar.header("Input")

suhu = st.sidebar.slider(
    "Masukkan Suhu (°C)",
    min_value=0,
    max_value=40,
    value=30
)

# ==========================
# Hitung Derajat Keanggotaan
# ==========================

mu_dingin = dingin(suhu)
mu_hangat = hangat(suhu)
mu_panas = panas(suhu)

# ==========================
# Hasil
# ==========================

col1, col2 = st.columns([1,1])

with col1:

    st.markdown("## Hasil Fuzzifikasi")

    st.metric(
        "❄️ Dingin",
        f"{mu_dingin:.2f}"
    )

    st.metric(
        "😊 Hangat",
        f"{mu_hangat:.2f}"
    )

    st.metric(
        "🔥 Panas",
        f"{mu_panas:.2f}"
    )

with col2:

    st.markdown("## Interpretasi")

    kategori = {
        "Dingin": mu_dingin,
        "Hangat": mu_hangat,
        "Panas": mu_panas
    }

    dominan = max(kategori, key=kategori.get)

    st.success(
        f"Suhu {suhu}°C lebih dominan pada kategori **{dominan}** "
        f"dengan derajat keanggotaan {kategori[dominan]:.2f}"
    )

# ==========================
# Tabel Hasil
# ==========================

st.markdown("## Tabel Derajat Keanggotaan")

st.table({
    "Kategori": ["Dingin", "Hangat", "Panas"],
    "Derajat Keanggotaan": [
        round(mu_dingin,2),
        round(mu_hangat,2),
        round(mu_panas,2)
    ]
})

# ==========================
# Grafik
# ==========================

st.markdown("## Grafik Fungsi Keanggotaan")

x = np.arange(0, 41, 1)

y_dingin = [dingin(i) for i in x]
y_hangat = [hangat(i) for i in x]
y_panas = [panas(i) for i in x]

fig, ax = plt.subplots(figsize=(10,5))

ax.plot(x, y_dingin, linewidth=3, label="Dingin (Linear Turun)")
ax.plot(x, y_hangat, linewidth=3, label="Hangat (Segitiga)")
ax.plot(x, y_panas, linewidth=3, label="Panas (Linear Naik)")

# posisi suhu yang dipilih
ax.axvline(
    suhu,
    linestyle='--',
    linewidth=2,
    label=f'Suhu = {suhu}°C'
)

ax.scatter(
    [suhu],
    [mu_dingin],
    s=100
)

ax.scatter(
    [suhu],
    [mu_hangat],
    s=100
)

ax.scatter(
    [suhu],
    [mu_panas],
    s=100
)

ax.set_title("Grafik Himpunan Fuzzy Suhu")
ax.set_xlabel("Suhu (°C)")
ax.set_ylabel("Derajat Keanggotaan μ(x)")
ax.set_xlim(0,40)
ax.set_ylim(0,1.1)
ax.grid(True)
ax.legend()

st.pyplot(fig)

# ==========================
# Perhitungan Manual
# ==========================

st.markdown("## Contoh Perhitungan")

st.write(f"Input Suhu = **{suhu}°C**")

st.latex(
    rf"\mu_{{dingin}}({suhu})={mu_dingin:.2f}"
)

st.latex(
    rf"\mu_{{hangat}}({suhu})={mu_hangat:.2f}"
)

st.latex(
    rf"\mu_{{panas}}({suhu})={mu_panas:.2f}"
)

# ==========================
# Kesimpulan
# ==========================

st.markdown("## Kesimpulan")

st.info(
    f"""
    Pada suhu {suhu}°C diperoleh:

    - Dingin = {mu_dingin:.2f}
    - Hangat = {mu_hangat:.2f}
    - Panas = {mu_panas:.2f}

    Kategori dominan adalah **{dominan}**.
    """
)