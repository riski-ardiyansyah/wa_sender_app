import streamlit as st
import time
import webbrowser
import os
from datetime import datetime
import random

st.set_page_config(layout="centered")

# --- Fungsi utilitas ---
def load_template_files():
    folder = 'templates'
    return [f for f in os.listdir(folder) if f.endswith('.txt')]

def read_template(file_name):
    with open(os.path.join("template", file_name), "r", encoding="utf-8") as f:
        return f.read()

def read_numbers(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def show_countdown(seconds):
    countdown_placeholder = st.empty()
    for i in range(seconds, 0, -1):
        countdown_placeholder.markdown(
            f"""
            <div style="text-align: center; font-size: 28px; padding: 20px; color: green;">
                ⏳ Mengirim dalam <b>{i}</b> detik...
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(1)
    countdown_placeholder.empty()

# --- Upload daftar nomor ---
st.title("📲 Kirim Pesan WhatsApp Otomatis")
file_uploaded = st.file_uploader("📄 Upload File Nomor (format: nama|nomor)", type=["txt"])

# --- Pilih template ---
template_files = load_template_files()
template_choice = st.selectbox("📋 Pilih Template Pesan", template_files)

# Tombol kirim WA
if st.button("🚀 Klik untuk Kirim WA"):
    if not file_uploaded or not template_choice:
        st.error("Harap upload file nomor dan pilih template pesan.")
        st.stop()

    # Proses
    numbers_data = file_uploaded.getvalue().decode("utf-8").splitlines()
    message_template = read_template(template_choice)
    total = len(numbers_data)
    nomor_sukses, nomor_gagal = [], []

    start_time = time.time()
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, line in enumerate(numbers_data, start=1):
        try:
            nama, nomor = line.split("|")
        except ValueError:
            nomor_gagal.append(("Format Salah", line))
            continue

        pesan = message_template.replace("[[fullname]]", nama.strip())

        # Encode untuk URL
        link = f"https://wa.me/{nomor.strip()}?text={pesan.strip().replace(' ', '%20')}"
        webbrowser.open(link)

        status_text.markdown(f"📤 Mengirim pesan ke **{nama}** ({nomor})... ({i}/{total})")
        show_countdown(7)

        # Tambahkan ke daftar sukses (sementara diasumsikan berhasil)
        nomor_sukses.append((nama, nomor))

        progress_bar.progress(i / total)

    end_time = time.time()
    waktu_total = round(end_time - start_time, 2)

    # --- Input status laporan ---
    st.subheader("📝 Tambahkan Status Laporan")
    laporan_status = {}
    for nama, nomor in nomor_sukses:
        kol = st.radio(f"{nama} ({nomor})", ["✅ Berhasil", "❌ Gagal"], horizontal=True)
        laporan_status[nomor] = kol

    # --- Simpan laporan ---
    if st.button("📥 Unduh Laporan"):
        nama_file = os.path.splitext(file_uploaded.name)[0]
        sukses_final, gagal_final = [], []

        for nama, nomor in nomor_sukses:
            status = laporan_status.get(nomor)
            if status == "✅ Berhasil":
                sukses_final.append(f"{nama}|{nomor}")
            else:
                gagal_final.append(f"{nama}|{nomor}")

        jumlah_sukses = len(sukses_final)
        jumlah_gagal = len(gagal_final)

        laporan_isi = [
            f"📊 Laporan Pengiriman Pesan WA\n",
            f"Total sukses: {jumlah_sukses}",
            f"Total gagal: {jumlah_gagal}",
            f"Total waktu: {waktu_total:.2f} detik\n",
            "== Daftar Sukses ==",
            *sukses_final,
            "\n== Daftar Gagal ==",
            *gagal_final,
        ]

        # Simpan laporan lengkap
        laporan_path = f"laporan_{nama_file}.txt"
        with open(laporan_path, "w", encoding="utf-8") as f:
            f.write("\n".join(laporan_isi))
        st.success("✅ Laporan berhasil dibuat!")

        # Simpan file gagal khusus
        gagal_path = f"nomorgagal_{nama_file}.txt"
        with open(gagal_path, "w", encoding="utf-8") as f:
            f.write("\n".join(gagal_final))

        with open(laporan_path, "rb") as f:
            st.download_button("⬇️ Unduh Laporan Lengkap", data=f, file_name=laporan_path)

        with open(gagal_path, "rb") as f:
            st.download_button("⬇️ Unduh Nomor Gagal", data=f, file_name=gagal_path)
