import streamlit as st
import pandas as pd
import time
import datetime
from io import StringIO

st.set_page_config(page_title="Pengirim WA Massal", layout="centered")

st.title("📤 Kirim Pesan WhatsApp Massal (1 per 1)")

# Upload file
uploaded_file = st.file_uploader("📄 Upload file TXT (format: Nama,Nomor)", type=["txt"])

# Template pesan
template = st.text_area(
    "💬 Template Pesan (gunakan [[fullname]] untuk nama):",
    "Halo [[fullname]],\nSemoga sehat selalu.\nIni adalah pesan dari kami.",
    height=150
)

# Tombol kirim
start_kirim = st.button("🚀 Kirim Pesan Sekarang")

if start_kirim:
    if uploaded_file is not None:
        try:
            # Baca isi file
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            lines = stringio.readlines()

            data = []
            for line in lines:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    nama, nomor = parts
                    data.append({"nama": nama.strip(), "nomor": nomor.strip()})
                else:
                    st.warning(f"⚠️ Format salah di baris: {line.strip()} (dilewati)")

            if not data:
                st.error("❌ Tidak ada data valid ditemukan.")
            else:
                total_pesan = len(data)
                st.success(f"✅ {total_pesan} nomor berhasil dimuat.")

                # Inisialisasi progress dan waktu
                progress_bar = st.progress(0)
                status_text = st.empty()
                elapsed_placeholder = st.empty()

                start_time = time.time()

                for i, row in enumerate(data):
                    nama = row["nama"]
                    nomor = row["nomor"]

                    # Ganti [[fullname]] dengan nama
                    pesan_personal = template.replace("[[fullname]]", nama)

                    # Tampilkan waktu berjalan
                    elapsed_seconds = int(time.time() - start_time)
                    elapsed_str = str(datetime.timedelta(seconds=elapsed_seconds))
                    elapsed_placeholder.markdown(f"⏱️ **Waktu berjalan:** {elapsed_str}")

                    # Kirim pesan (simulasi, Anda bisa ganti dengan fungsi asli)
                    st.write(f"📨 Mengirim ke {nama} ({nomor}):")
                    st.code(pesan_personal)

                    # Simulasi delay pengiriman
                    time.sleep(1.5)

                    progress_bar.progress((i + 1) / total_pesan)

                end_time = time.time()
                total_seconds = int(end_time - start_time)
                total_str = str(datetime.timedelta(seconds=total_seconds))

                # Buat laporan
                laporan_txt = f"Total pesan: {total_pesan}\nWaktu yang digunakan: {total_str}"
                st.success("✅ Semua pesan berhasil dikirim.")
                st.markdown(f"📋 **Ringkasan:**\n\n- Total pesan: {total_pesan}\n- Waktu: {total_str}")

                st.download_button(
                    label="📥 Download Laporan",
                    data=laporan_txt,
                    file_name="laporan.txt",
                    mime="text/plain"
                )

        except Exception as e:
            st.error(f"❌ Gagal membaca file TXT: {e}")
    else:
        st.warning("⚠️ Silakan upload file terlebih dahulu.")
