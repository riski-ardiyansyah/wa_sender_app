import streamlit as st
import time
import webbrowser
import os

st.set_page_config(page_title="Pengirim WA", layout="centered")

# === Fungsi countdown dengan animasi UI keren ===
def countdown(seconds):
    for i in range(seconds, 0, -1):
        st.markdown(f"""
        <h2 style='text-align: center; color: #39FF14; font-size: 36px;'>
            Mengirim pesan dalam {i} detik...
        </h2>""", unsafe_allow_html=True)
        time.sleep(1)
        st.empty()

# === Fungsi buat laporan ===
def buat_laporan(daftar_berhasil, daftar_gagal, nama_file):
    semua = []
    header = f"""LAPORAN PENGIRIMAN PESAN WA

Jumlah pesan sukses = {len(daftar_berhasil)}
Jumlah pesan gagal  = {len(daftar_gagal)}

==============================\n"""

    for nomor, nama in daftar_berhasil:
        semua.append(f"[SUKSES] {nomor} - {nama}")

    for nomor, nama in daftar_gagal:
        semua.append(f"[GAGAL]  {nomor} - {nama}")

    isi_laporan = header + "\n".join(semua)

    # File gabungan
    file_laporan = f"laporan_{nama_file}.txt"
    with open(file_laporan, "w", encoding="utf-8") as f:
        f.write(isi_laporan)

    # File khusus gagal
    file_gagal = f"nomorgagal_{nama_file}.txt"
    with open(file_gagal, "w", encoding="utf-8") as f:
        for nomor, nama in daftar_gagal:
            f.write(f"{nomor} - {nama}\n")

    return file_laporan, file_gagal

# === Upload dan ambil data nomor ===
st.title("📤 Kirim Pesan WA Masal dengan Countdown dan Laporan")

uploaded_file = st.file_uploader("Upload file TXT berisi daftar nomor (format: 628xx|Nama)", type="txt")
template_list = os.listdir("template") if os.path.exists("template") else []

template_selected = st.selectbox("Pilih Template Pesan", template_list)

if uploaded_file and template_selected:
    nama_file_txt = uploaded_file.name.replace(".txt", "")
    data = uploaded_file.read().decode("utf-8").splitlines()
    daftar_nomor = [baris.split("|") for baris in data if "|" in baris]

    with open(f"template/{template_selected}", "r", encoding="utf-8") as f:
        template = f.read()

    if st.button("Klik untuk Kirim WA"):
        st.markdown("---")
        berhasil, gagal = [], []

        progress_text = "📤 Mengirim pesan ke semua nomor..."
        my_bar = st.progress(0, text=progress_text)

        for i, (nomor, nama) in enumerate(daftar_nomor):
            persen = (i + 1) / len(daftar_nomor)
            my_bar.progress(persen, text=f"📨 Mengirim ke {nama} ({nomor}) ({i+1}/{len(daftar_nomor)})")

            pesan = template.replace("[[nama]]", nama)
            url = f"https://wa.me/{nomor}?text={pesan}"
            countdown(7)
            webbrowser.open(url)

            status = st.radio(
                f"Apakah pesan ke {nama} ({nomor}) terkirim?",
                ["Belum Dipilih", "Berhasil", "Gagal"],
                key=f"status_{i}"
            )

            if status == "Berhasil":
                berhasil.append((nomor, nama))
            elif status == "Gagal":
                gagal.append((nomor, nama))

            st.markdown("---")

        st.success("✅ Pengiriman selesai!")

        # Buat laporan
        file_laporan, file_gagal = buat_laporan(berhasil, gagal, nama_file_txt)

        with open(file_laporan, "rb") as f:
            st.download_button("📥 Download Laporan Semua", f, file_name=file_laporan)

        with open(file_gagal, "rb") as f:
            st.download_button("📥 Download Nomor Gagal", f, file_name=file_gagal)
