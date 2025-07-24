import streamlit as st
import time
import webbrowser
from datetime import datetime
import random
import os

st.set_page_config(layout="centered", page_title="Kirim Pesan WhatsApp")

# Penyimpanan status
if 'data_nomor' not in st.session_state:
    st.session_state.data_nomor = []
if 'index_nomor' not in st.session_state:
    st.session_state.index_nomor = 0
if 'status_kirim' not in st.session_state:
    st.session_state.status_kirim = {}
if 'namafile' not in st.session_state:
    st.session_state.namafile = ''

# Upload file
st.title("📤 Kirim Pesan WhatsApp Massal")
uploaded_file = st.file_uploader("Unggah file .txt berisi daftar nomor WhatsApp (tanpa +)", type=["txt"])

# Pesan yang akan dikirim
pesan_default = "Halo, ini adalah pesan otomatis. Semoga harimu menyenangkan! 😊"
pesan = st.text_area("✉️ Pesan yang akan dikirim", value=pesan_default, height=150)

def countdown_ui(delay_seconds):
    for remaining in range(delay_seconds, 0, -1):
        st.markdown(
            f"""
            <div style="font-size:50px; text-align:center; padding:20px;">
                ⏳ Tunggu {remaining} detik...
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(1)
    st.markdown(
        """
        <div style="font-size:50px; text-align:center; color:green; padding:20px;">
            ✅ Kirim pesan sekarang!
        </div>
        """,
        unsafe_allow_html=True
    )

# Mulai kirim
if uploaded_file:
    st.success("✅ File berhasil diunggah!")

    if not st.session_state.data_nomor:
        st.session_state.data_nomor = [line.strip() for line in uploaded_file.readlines() if line.strip()]
        st.session_state.namafile = uploaded_file.name.replace('.txt', '')

    if st.session_state.index_nomor < len(st.session_state.data_nomor):
        nomor = st.session_state.data_nomor[st.session_state.index_nomor]
        st.subheader(f"📲 Kirim ke nomor: {nomor}")

        # Kirim pesan WA
        if st.button("🌐 Buka WhatsApp"):
            url = f"https://wa.me/{nomor}?text={pesan.replace(' ', '%20')}"
            webbrowser.open_new_tab(url)

        # Tombol status
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Berhasil"):
                st.session_state.status_kirim[nomor] = 'Berhasil'
                st.session_state.index_nomor += 1
                st.experimental_rerun()
        with col2:
            if st.button("❌ Gagal"):
                st.session_state.status_kirim[nomor] = 'Gagal'
                st.session_state.index_nomor += 1
                st.experimental_rerun()

        # Delay
        delay = random.randint(6, 10)
        countdown_ui(delay)

    else:
        st.success("✅ Semua pesan telah diproses.")
        waktu = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Simpan hasil kirim
        status_lines = []
        gagal_lines = []
        for no, status in st.session_state.status_kirim.items():
            status_lines.append(f"{no}: {status}")
            if status == "Gagal":
                gagal_lines.append(no)

        status_txt = "\n".join(status_lines)
        gagal_txt = "\n".join(gagal_lines)

        # Simpan ke file
        status_file_name = f"status_pengiriman_{st.session_state.namafile}_{waktu}.txt"
        gagal_file_name = f"nomorgagal_{st.session_state.namafile}_{waktu}.txt"

        with open(status_file_name, "w", encoding="utf-8") as f:
            f.write(status_txt)

        with open(gagal_file_name, "w", encoding="utf-8") as f:
            f.write(gagal_txt)

        # Unduhan
        with open(status_file_name, "rb") as f:
            st.download_button("📥 Unduh Hasil Pengiriman", f, file_name=status_file_name)

        with open(gagal_file_name, "rb") as f:
            st.download_button("📥 Unduh Nomor Gagal", f, file_name=gagal_file_name)

        # Reset opsi
        if st.button("🔄 Kirim ulang dari awal"):
            for key in ['data_nomor', 'index_nomor', 'status_kirim', 'namafile']:
                del st.session_state[key]
            st.experimental_rerun()
