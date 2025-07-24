import streamlit as st
import pandas as pd
import time
from urllib.parse import quote
from datetime import datetime
import os
from io import BytesIO
import random

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

# Session state
if "dataframe" not in st.session_state:
    st.session_state.dataframe = None
if "template" not in st.session_state:
    st.session_state.template = ""
if "index_kirim" not in st.session_state:
    st.session_state.index_kirim = 0
if "laporan" not in st.session_state:
    st.session_state.laporan = []

st.set_page_config(page_title="WA Sender Manual", layout="centered")
st.title("📤 WhatsApp Sender Manual + Delay Visual")

uploaded_file = st.file_uploader("📁 Upload file kontak (.xlsx atau .txt)", type=["xlsx", "txt"])
uploaded_template = st.file_uploader("📄 Upload template pesan (.txt)", type=["txt"])
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

    st.session_state.dataframe = df
    st.success(f"📄 Berhasil membaca {len(df)} kontak dari file.")

    if uploaded_template:
        st.session_state.template = uploaded_template.read().decode("utf-8")
    else:
        st.session_state.template = load_template(DEFAULT_TEMPLATE_PATH)

    st.subheader("📝 Pratinjau Template Pesan")
    st.code(st.session_state.template)

if st.session_state.dataframe is not None and st.session_state.template:

    df = st.session_state.dataframe
    index = st.session_state.index_kirim

    if index < len(df):
        row = df.iloc[index]
        nomor = str(row.get("nomor", "")).strip()
        data_row = {k.lower(): v for k, v in row.items()}
        pesan = generate_pesan(st.session_state.template, data_row)
        url = encode_url(nomor, pesan)

        st.markdown(f"📨 [{index+1}/{len(df)}] **Kirim ke {nomor}**")
        st.text_area("📋 Isi Pesan", value=pesan, height=200)

        if st.button("🚀 KIRIM PESAN INI"):
            waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            media_file = str(row.get("media", "")).strip() if "media" in row else ""
            st.session_state.laporan.append([
                index+1, nomor, data_row.get("nama", ""), pesan, media_file, waktu, "Tautan Dibuka"
            ])
            
            # Tampilkan tombol & jalankan JavaScript untuk buka tautan
            js = f"<script>window.open('{url}', '_blank');</script>"
            st.components.v1.html(js)

            # Tampilkan jeda waktu visual
            jeda = random.randint(7, 9)
            st.subheader(f"⏳ Tunggu {jeda} detik untuk kontak berikutnya...")
            progress_bar = st.progress(0)
            status_text = st.empty()

            for detik in range(jeda):
                percent = int((detik + 1) / jeda * 100)
                status_text.info(f"🕐 Menunggu... {jeda - detik} detik lagi")
                progress_bar.progress((detik + 1) / jeda)
                time.sleep(1)

            st.session_state.index_kirim += 1
            st.experimental_rerun()

    else:
        st.success("✅ Semua pesan telah ditampilkan.")
        df_laporan = pd.DataFrame(
            st.session_state.laporan,
            columns=["No", "Nomor", "Nama", "Pesan", "Media", "Waktu", "Status"]
        )
        st.dataframe(df_laporan)

        output = BytesIO()
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_laporan.to_excel(writer, index=False, sheet_name="Laporan")
        st.download_button("⬇️ Download Laporan Excel", data=output.getvalue(), file_name=f"laporan_wa_{now}.xlsx")
