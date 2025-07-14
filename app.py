import streamlit as st
import pandas as pd
import time
import webbrowser
from urllib.parse import quote
from datetime import datetime
import os
import random
from io import BytesIO

DEFAULT_TEMPLATE_PATH = "templates/pesan.txt"
DEFAULT_DARI = "tim kami"
DEFAULT_PRODUK = "produk terbaik kami"
FOLDER_MEDIA = "media"

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

st.set_page_config(page_title="WA Sender", layout="centered")
st.title("\U0001F4E4 WhatsApp Mass Sender dengan Delay Aman")

uploaded_file = st.file_uploader("\U0001F4C2 Upload file kontak (.xlsx atau .txt)", type=["xlsx", "txt"])
uploaded_template = st.file_uploader("\U0001F4DD Upload template pesan (.txt)", type=["txt"])
st.info("Gunakan placeholder seperti `{nama}`, `{dari}`, `{produk}`, `{media}` di template.")

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

    st.success(f"\U0001F4C4 Berhasil membaca {len(df)} kontak dari file.")

    template = uploaded_template.read().decode("utf-8") if uploaded_template else load_template(DEFAULT_TEMPLATE_PATH)

    st.subheader("\U0001F4DD Pratinjau Template Pesan")
    st.code(template)

    if st.button("\U0001F680 Mulai Kirim"):
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        laporan = []
        progress = st.progress(0)
        total = len(df)

        for i, row in df.iterrows():
            nomor = str(row.get("nomor", "")).strip()
            data_row = {k.lower(): v for k, v in row.items()}
            pesan = generate_pesan(template, data_row)
            media_file = str(row.get("media", "")).strip() if "media" in row else ""
            media_note = ""
            if media_file:
                if os.path.exists(os.path.join(FOLDER_MEDIA, media_file)):
                    media_note = f"[Media: {media_file}]"
                else:
                    media_note = f"[Media tidak ditemukan: {media_file}]"

            url = encode_url(nomor, pesan)
            webbrowser.open(url)

            waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            laporan.append([i+1, nomor, data_row.get("nama", ""), pesan, media_file, waktu, "Dibuka"])

            st.write(f"✅ [{i+1}/{total}] Kirim ke {nomor} - tunggu sebelum lanjut...")
            jeda = random.randint(7, 9)
            with st.empty():
                for detik in range(jeda, 0, -1):
                    st.info(f"⏳ Menunggu {detik} detik...")
                    time.sleep(1)

            progress.progress((i+1) / total)

        df_laporan = pd.DataFrame(laporan, columns=["No", "Nomor", "Nama", "Pesan", "Media", "Waktu", "Status"])
        st.success("✅ Semua link wa.me sudah dibuka.")
        st.dataframe(df_laporan)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_laporan.to_excel(writer, index=False, sheet_name="Laporan")
        st.download_button("⬇️ Download Laporan Excel", data=output.getvalue(), file_name=f"laporan_wa_{now}.xlsx")
