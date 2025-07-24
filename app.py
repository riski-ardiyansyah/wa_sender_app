import streamlit as st
import pandas as pd
import time
import os
from urllib.parse import quote
from datetime import datetime

DEFAULT_TEMPLATE_PATH = "templates/pesan.txt"
DEFAULT_DARI = "Admin"
DEFAULT_PRODUK = "Produk Kami"

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

def tampilkan_countdown(seconds, timer_placeholder, progress_bar):
    for i in range(seconds):
        percent = int((i + 1) / seconds * 100)
        timer_placeholder.markdown(
            f"<div style='text-align:center;'><h4>⏳ Menunggu {seconds - i} detik...</h4></div>",
            unsafe_allow_html=True
        )
        progress_bar.progress((i + 1) / seconds)
        time.sleep(1)
    timer_placeholder.empty()
    progress_bar.empty()

# Inisialisasi state
if "dataframe" not in st.session_state:
    st.session_state.dataframe = None
if "template" not in st.session_state:
    st.session_state.template = ""
if "index_kirim" not in st.session_state:
    st.session_state.index_kirim = 0
if "laporan" not in st.session_state:
    st.session_state.laporan = []
if "start_time" not in st.session_state:
    st.session_state.start_time = None

st.set_page_config(page_title="WA Sender Manual", layout="centered")
st.title("📤 WhatsApp Sender Manual + Countdown Visual")

uploaded_file = st.file_uploader("📁 Upload file kontak (.txt)", type=["txt"])

# Pilih template dari folder + upload manual
template_files = [f for f in os.listdir("templates") if f.endswith(".txt")]
selected_template_file = st.selectbox("📂 Pilih Template Pesan dari Folder 'templates/'", template_files)

uploaded_template = st.file_uploader("📄 Atau Upload Template Pesan (.txt)", type=["txt"])
st.info("Gunakan placeholder seperti `{nama}`, `{dari}`, `{produk}` di template.")

if uploaded_file:
    # Pakai hanya txt
    lines = uploaded_file.read().decode("utf-8").splitlines()
    data = [line.strip().split("\t") for line in lines if "\t" in line]
    df = pd.DataFrame(data, columns=["nama", "nomor"])

    st.session_state.dataframe = df
    st.success(f"📄 Berhasil membaca {len(df)} kontak dari file.")

    # Template dari upload/manual
    if uploaded_template:
        st.session_state.template = uploaded_template.read().decode("utf-8")
    else:
        template_path = os.path.join("templates", selected_template_file)
        st.session_state.template = load_template(template_path)

    st.subheader("📝 Pratinjau Template Pesan")
    st.code(st.session_state.template)

    if st.button("🚀 Mulai Kirim Manual"):
        st.session_state.index_kirim = 0
        st.session_state.laporan = []
        st.session_state.start_time = time.time()

    if st.session_state.index_kirim < len(df):
        i = st.session_state.index_kirim
        current = df.iloc[i]
        pesan = generate_pesan(st.session_state.template, current)
        url = encode_url(current["nomor"], pesan)

        st.markdown(f"### ✅ Kirim ke: {current['nama']} ({current['nomor']})")
        st.text_area("📨 Isi Pesan", pesan, height=150)
        st.markdown(f"[🌐 Klik untuk kirim WA]({url})")

        st.markdown(f"#### ⏱️ Progres Pengiriman: {i+1}/{len(df)}")
        st.progress((i + 1) / len(df))

        timer_placeholder = st.empty()
        countdown_progress = st.progress(0)

        if st.button("✅ Sudah Terkirim, Lanjutkan"):
            st.session_state.laporan.append({
                "nama": current["nama"],
                "nomor": current["nomor"],
                "status": "sukses",
                "pesan": pesan
            })
            st.session_state.index_kirim += 1
            tampilkan_countdown(7, timer_placeholder, countdown_progress)

        if st.button("❌ Gagal Terkirim"):
            st.session_state.laporan.append({
                "nama": current["nama"],
                "nomor": current["nomor"],
                "status": "gagal",
                "pesan": pesan
            })
            st.session_state.index_kirim += 1
            tampilkan_countdown(7, timer_placeholder, countdown_progress)

        # Tampilkan waktu berjalan
        if st.session_state.start_time:
            elapsed_seconds = int(time.time() - st.session_state.start_time)
            st.info(f"⏱️ Waktu berjalan: {time.strftime('%M:%S', time.gmtime(elapsed_seconds))}")

    else:
        st.success("🎉 Semua pesan telah selesai dikirim!")
        df_lap = pd.DataFrame(st.session_state.laporan)
        df_sukses = df_lap[df_lap["status"] == "sukses"]
        df_gagal = df_lap[df_lap["status"] == "gagal"]
        df_final = pd.concat([df_sukses, df_gagal])

        jumlah_sukses = len(df_sukses)
        jumlah_gagal = len(df_gagal)

        elapsed_total = int(time.time() - st.session_state.start_time) if st.session_state.start_time else 0
        elapsed_str = time.strftime('%M:%S', time.gmtime(elapsed_total))

        header = f"Jumlah pesan sukses = {jumlah_sukses}\nJumlah pesan gagal = {jumlah_gagal}\nTotal waktu = {elapsed_str}\n\n"
        isi = "\n".join([f"{r['nomor']} - {r['nama']} - {r['status']}" for _, r in df_final.iterrows()])
        laporan_txt = header + isi

        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(uploaded_file.name)[0]

        st.download_button(
            "📥 Unduh Laporan Akhir (TXT)",
            laporan_txt,
            file_name=f"laporan_{base_name}_{now}.txt",
            mime="text/plain"
        )
