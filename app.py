import os
import streamlit as st
import pandas as pd
import time
from urllib.parse import quote
from datetime import datetime

TEMPLATE_FOLDER = "templates"
DEFAULT_PRODUK = "Produk Kami"
DEFAULT_DARI = "Admin"

def load_template(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def generate_pesan(template, data_row):
    pesan = template
    for key, val in data_row.items():
        val = str(val) if val else "-"
        if key == "dari" and not val.strip():
            val = DEFAULT_DARI
        if key == "produk" and not val.strip():
            val = DEFAULT_PRODUK
        pesan = pesan.replace("{" + key + "}", val)
    return pesan

def encode_url(nomor, pesan):
    return f"https://wa.me/{nomor}?text={quote(pesan)}"

def tulis_laporan(nama_file, laporan):
    sukses = [l for l in laporan if l["status"] == "BERHASIL"]
    gagal = [l for l in laporan if l["status"] == "GAGAL"]
    with open(nama_file, "w", encoding="utf-8") as f:
        f.write(f"Jumlah Pesan Sukses: {len(sukses)}\n")
        f.write(f"Jumlah Pesan Gagal: {len(gagal)}\n\n")
        for data in sukses + gagal:
            f.write(f"{data['status']}\t{data['nama']}\t{data['nomor']}\n")

# Streamlit
st.set_page_config(page_title="WA Sender Manual", layout="centered")
st.title("📤 WhatsApp Sender Manual + Delay Visual")

# Step 1: Upload file kontak
uploaded_file = st.file_uploader("📁 Upload file kontak (.xlsx atau .txt)", type=["xlsx", "txt"])

# Step 2: Pilih template dari folder
template_files = [f for f in os.listdir(TEMPLATE_FOLDER) if f.endswith(".txt")]
selected_template_file = st.selectbox("📄 Pilih template pesan", template_files)

# Tampilkan isi template
template_path = os.path.join(TEMPLATE_FOLDER, selected_template_file)
template_content = load_template(template_path)
st.subheader("📝 Pratinjau Template Pesan")
st.code(template_content)

# Load data kontak
if uploaded_file:
    file_ext = os.path.splitext(uploaded_file.name)[-1].lower()
    if file_ext == ".xlsx":
        df = pd.read_excel(uploaded_file)
    elif file_ext == ".txt":
        lines = uploaded_file.read().decode("utf-8").splitlines()
        data = [line.strip().split("\t") for line in lines if "\t" in line]
        df = pd.DataFrame(data, columns=["nama", "nomor"])
    else:
        st.error("Format file tidak didukung.")
        st.stop()

    if st.button("📨 Klik untuk Kirim WhatsApp"):
        st.subheader("⏳ Countdown Mulai...")
        countdown = st.empty()
        for i in range(5, 0, -1):
            countdown.markdown(f"<h3 style='text-align:center;'>Mengirim dalam {i} detik...</h3>", unsafe_allow_html=True)
            time.sleep(1)
        countdown.markdown("<h3 style='text-align:center;'>Memulai pengiriman!</h3>", unsafe_allow_html=True)

        laporan = []
        progress_bar = st.progress(0)
        status_info = st.empty()

        for i, row in df.iterrows():
            nomor = str(row["nomor"]).replace("+", "").replace(" ", "").replace("-", "")
            nama = row["nama"]
            pesan = generate_pesan(template_content, row)
            url = encode_url(nomor, pesan)

            status_info.write(f"📨 Mengirim pesan ke nomor {i+1} / {len(df)}: {nomor}")

            try:
                js = f"window.open('{url}')"  # buka di tab baru
                st.components.v1.html(f"<script>{js}</script>", height=0)
                laporan.append({"status": "BERHASIL", "nama": nama, "nomor": nomor})
            except:
                laporan.append({"status": "GAGAL", "nama": nama, "nomor": nomor})

            time.sleep(3)  # delay antar pesan
            progress_bar.progress((i+1)/len(df))

        st.success("✅ Pengiriman selesai!")

        if st.button("📋 Simpan Laporan"):
            os.makedirs("laporan", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            laporan_file = os.path.join("laporan", f"laporan_{timestamp}.txt")
            tulis_laporan(laporan_file, laporan)
            st.success(f"Laporan disimpan ke: `{laporan_file}`")

