import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime

st.set_page_config(page_title="Pengirim Pesan WA", layout="wide")

st.title("📲 Pengirim Pesan WhatsApp Otomatis")
st.markdown("Upload file `.txt` dengan format: `NAMA<TAB>NOMOR`")

# ========== Upload File ==========

uploaded_file = st.file_uploader("Upload File TXT Nomor Penerima", type=["txt"])
if uploaded_file is None:
    st.stop()

# Baca File TXT
try:
    lines = uploaded_file.read().decode("utf-8").splitlines()
    data = [line.strip().split("\t") for line in lines if "\t" in line]
    df = pd.DataFrame(data, columns=["nama", "nomor"])
except Exception as e:
    st.error(f"Gagal membaca file TXT: {e}")
    st.stop()

# ========== Pilih Template Pesan ==========

template_folder = "template"
template_files = [f for f in os.listdir(template_folder) if f.endswith(".txt")]

if not template_files:
    st.warning("Tidak ada file template di folder `template`.")
    st.stop()

template_name = st.selectbox("Pilih Template Pesan", template_files)
with open(os.path.join(template_folder, template_name), "r", encoding="utf-8") as f:
    template_text = f.read()

st.markdown("---")

# ========== Tombol Kirim ==========

if st.button("🚀 Mulai Kirim Pesan"):
    # Siapkan elemen UI
    progress_bar = st.progress(0)
    status_text = st.empty()
    timer_text = st.empty()
    hasil_log = []

    total = len(df)
    counter = 0
    start_time = time.time()
    waktu_berjalan = 0

    # Hitung waktu dengan teks berjalan
    placeholder_timer = st.empty()

    for index, row in df.iterrows():
        nama = row["nama"]
        nomor = row["nomor"]

        # Ganti [[fullname]] dalam template
        pesan = template_text.replace("[[fullname]]", nama)

        # Simulasi pengiriman (gunakan perintah kirim WA di sini)
        time.sleep(1)  # Delay per pesan
        counter += 1

        # Update progress bar dan teks berjalan
        progress_bar.progress(counter / total)
        status_text.text(f"Mengirim ke: {nama} ({nomor})")

        waktu_berjalan = int(time.time() - start_time)
        placeholder_timer.text(f"⏱️ Waktu berjalan: {waktu_berjalan} detik")

        hasil_log.append({"nama": nama, "nomor": nomor, "status": "Terkirim"})

    # Total waktu habis
    waktu_habis = int(time.time() - start_time)
    menit, detik = divmod(waktu_habis, 60)

    st.success(f"✅ Semua pesan berhasil dikirim dalam {menit} menit {detik} detik.")
    st.markdown("---")

    # ========== Buat Laporan ==========

    df_laporan = pd.DataFrame(hasil_log)
    df_laporan["waktu_kirim"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    df_laporan["durasi_pengiriman"] = f"{menit} menit {detik} detik"

    laporan_file = "laporan_pengiriman.csv"
    df_laporan.to_csv(laporan_file, index=False)

    with open(laporan_file, "rb") as f:
        st.download_button(
            label="📥 Download Laporan Pengiriman",
            data=f,
            file_name=laporan_file,
            mime="text/csv"
        )
