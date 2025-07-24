import streamlit as st
import time
import webbrowser
import os
from io import StringIO
from datetime import datetime

# Inisialisasi session state
if "status_list" not in st.session_state:
    st.session_state.status_list = []

st.title("📤 Kirim Pesan WhatsApp Massal")

uploaded_file = st.file_uploader("📄 Upload file TXT daftar nomor (format: nama - nomor)", type=["txt"])

if uploaded_file:
    # Membaca isi file dan parsing nomor
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    lines = stringio.readlines()
    data_nomor = []
    for line in lines:
        parts = line.strip().split(" - ")
        if len(parts) == 2:
            nama, nomor = parts
            data_nomor.append({"nama": nama.strip(), "nomor": nomor.strip()})

    pesan_template = st.text_area("✏️ Tulis pesan yang ingin dikirim (gunakan {{nama}} untuk nama)", "Halo {{nama}}, ini adalah pesan percobaan.")

    if st.button("🚀 Klik untuk Kirim WA"):
        st.session_state.status_list = []  # Reset status sebelumnya
        progress_bar = st.progress(0)
        total = len(data_nomor)

        for i, data in enumerate(data_nomor):
            nama = data["nama"]
            nomor = data["nomor"]
            pesan = pesan_template.replace("{{nama}}", nama)

            encoded_pesan = pesan.replace(" ", "%20").replace("\n", "%0A")
            url = f"https://wa.me/{nomor}?text={encoded_pesan}"

            with st.container():
                st.markdown(f"### 📲 Mengirim ke: {nama} - {nomor}")
                with st.empty():
                    for detik in range(7, 0, -1):
                        st.markdown(f"<h2 style='text-align:center; color:#4CAF50;'>⏳ Kirim dalam {detik} detik...</h2>", unsafe_allow_html=True)
                        time.sleep(1)

            webbrowser.open_new_tab(url)

            st.session_state.status_list.append({"nama": nama, "nomor": nomor, "status": None})
            progress_bar.progress((i + 1) / total)

        st.success("✅ Semua link WA telah dibuka. Setelah mengirim semua pesan, kembali dan tandai statusnya di bawah.")

    if st.session_state.status_list:
        st.markdown("---")
        st.header("📋 Laporan Status Pengiriman")
        for i, data in enumerate(st.session_state.status_list):
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.text(f"{data['nama']} - {data['nomor']}")
            with col2:
                if st.button(f"✅ Berhasil", key=f"sukses_{i}"):
                    st.session_state.status_list[i]["status"] = "BERHASIL"
            with col3:
                if st.button(f"❌ Gagal", key=f"gagal_{i}"):
                    st.session_state.status_list[i]["status"] = "GAGAL"

        if st.button("📥 Unduh Laporan TXT"):
            sukses = [x for x in st.session_state.status_list if x["status"] == "BERHASIL"]
            gagal = [x for x in st.session_state.status_list if x["status"] == "GAGAL"]

            laporan = []
            laporan.append(f"Jumlah pesan sukses = {len(sukses)}")
            laporan.append(f"Jumlah pesan gagal = {len(gagal)}")
            laporan.append("")
            for x in sukses:
                laporan.append(f"{x['nomor']} - {x['nama']} - BERHASIL")
            for x in gagal:
                laporan.append(f"{x['nomor']} - {x['nama']} - GAGAL")

            nama_file = uploaded_file.name.replace(".txt", "")
            final_text = "\n".join(laporan)
            st.download_button("⬇️ Download Laporan", data=final_text, file_name=f"laporan_{nama_file}.txt", mime="text/plain")
