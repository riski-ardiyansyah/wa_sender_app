import streamlit as st
import pandas as pd
import time
import urllib.parse
import os
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Kirim WhatsApp Massal", layout="wide")
st.title("📤 Kirim WhatsApp Massal")

# Step 1: Pilih file data
uploaded_file = st.file_uploader("Upload file TXT (format: nama[TAB]nomor)", type=["txt"])

# Step 2: Pilih template pesan
template_folder = "templates"
template_files = [f for f in os.listdir(template_folder) if f.endswith(".txt")]
template_choice = st.selectbox("Pilih Template Pesan", template_files)

# Step 3: Baca pesan template
template_path = os.path.join(template_folder, template_choice)
with open(template_path, "r", encoding="utf-8") as f:
    template_pesan = f.read()

# Step 4: Baca data dari file TXT
if uploaded_file and template_choice:
    try:
        df = pd.read_csv(uploaded_file, sep="\t", header=None, names=["nama", "nomor"], encoding="utf-8")
        df = df.dropna(subset=["nama", "nomor"])
        df = df[df["nomor"].astype(str).str.match(r'^62\d{8,}$')].reset_index(drop=True)
    except Exception as e:
        st.error(f"Gagal membaca file TXT: {e}")
        st.stop()

    st.success(f"✅ Berhasil memuat {len(df)} data")

    if st.button("🚀 Klik untuk Kirim WA"):
        start_time = time.time()
        progress_text = "Mengirim pesan..."
        bar = st.progress(0, text=progress_text)

        laporan = []
        for idx, row in df.iterrows():
            nama = row["nama"]
            nomor = str(row["nomor"])
            pesan = template_pesan.replace("[[fullname]]", nama)

            # Encode pesan untuk URL
            encoded_pesan = urllib.parse.quote(pesan)
            url = f"https://wa.me/{nomor}?text={encoded_pesan}"

            # Tampilkan info dan tombol kirim WA dengan countdown
            with st.container():
                st.markdown(f"**{idx+1}. {nama} - {nomor}**")
                link_html = f'<a href="{url}" target="_blank"><button style="background-color:#25D366;color:white;padding:6px 16px;border:none;border-radius:6px;">Kirim WA</button></a>'
                st.markdown(link_html, unsafe_allow_html=True)
                countdown_placeholder = st.empty()

                for i in range(5, 0, -1):
                    countdown_placeholder.markdown(f"<span style='color:gray;'>⌛ Tunggu {i} detik sebelum kirim berikutnya...</span>", unsafe_allow_html=True)
                    time.sleep(1)

                countdown_placeholder.empty()

            laporan.append({
                "Nama": nama,
                "Nomor": nomor,
                "Pesan": pesan,
                "Link": url
            })

            bar.progress((idx + 1) / len(df), text=f"Mengirim {idx + 1} dari {len(df)}...")

        end_time = time.time()
        waktu_total = end_time - start_time
        waktu_durasi = time.strftime("%M menit %S detik", time.gmtime(waktu_total))

        # Simpan ke Excel
        df_laporan = pd.DataFrame(laporan)
        excel_output = BytesIO()
        df_laporan.to_excel(excel_output, index=False)
        excel_output.seek(0)

        # Simpan waktu ke TXT
        waktu_log = f"Waktu yang dihabiskan: {waktu_durasi}\nJumlah kontak: {len(df)}\n"
        txt_output = BytesIO()
        txt_output.write(waktu_log.encode("utf-8"))
        txt_output.seek(0)

        st.success("✅ Semua pesan berhasil diproses!")
        st.markdown(f"🕒 **Waktu total:** {waktu_durasi}")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 Unduh Laporan Excel", data=excel_output, file_name="laporan_wa.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with col2:
            st.download_button("📥 Unduh Log Waktu", data=txt_output, file_name="waktu_pengiriman.txt", mime="text/plain")
