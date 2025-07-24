import streamlit as st
import time
import os
from urllib.parse import quote

# Folder template
TEMPLATE_FOLDER = "template"

# Pilih file template
template_files = os.listdir(TEMPLATE_FOLDER)
selected_template = st.selectbox("📄 Pilih Template Pesan", template_files)

# Ambil isi template
with open(os.path.join(TEMPLATE_FOLDER, selected_template), "r", encoding="utf-8") as f:
    pesan_template = f.read()

# Upload file nomor
uploaded_file = st.file_uploader("📤 Upload File Nomor", type=["txt"])

# Inisialisasi session
if "nomor_list" not in st.session_state:
    st.session_state.nomor_list = []
if "laporan" not in st.session_state:
    st.session_state.laporan = {"sukses": [], "gagal": []}
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "mulai_kirim" not in st.session_state:
    st.session_state.mulai_kirim = False

# Jika file diupload
if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
    st.session_state.nomor_list = [line.strip() for line in content.splitlines() if line.strip()]
    st.success(f"{len(st.session_state.nomor_list)} nomor berhasil dimuat.")

# Tombol kirim WA
if st.button("📨 Klik untuk Kirim WA") and st.session_state.nomor_list:
    st.session_state.mulai_kirim = True
    st.session_state.laporan = {"sukses": [], "gagal": []}
    st.session_state.current_index = 0

# Mulai proses pengiriman
if st.session_state.mulai_kirim:
    nomor_list = st.session_state.nomor_list
    with st.container():
        progress = st.progress(0)
        for idx in range(st.session_state.current_index, len(nomor_list)):
            nomor = nomor_list[idx]
            pesan = pesan_template.replace("[[fullname]]", f"User{idx+1}")
            encoded_pesan = quote(pesan)
            wa_link = f"https://wa.me/{nomor}?text={encoded_pesan}"
            
            st.subheader(f"📱 Mengirim pesan ke nomor {idx+1}/{len(nomor_list)}")
            with st.empty():
                for sisa in range(7, 0, -1):
                    st.markdown(f"<h2 style='text-align:center;color:green;'>⏳ Mengalihkan ke WhatsApp dalam {sisa} detik...</h2>", unsafe_allow_html=True)
                    time.sleep(1)

            js = f"window.open('{wa_link}')"
            st.components.v1.html(f"<script>{js}</script>", height=0)

            st.session_state.current_index = idx + 1
            progress.progress((idx + 1) / len(nomor_list))
            st.stop()  # Tunggu hingga user kembali

# Setelah kembali dari WhatsApp
if st.session_state.mulai_kirim and st.session_state.current_index > 0:
    nomor_terakhir = st.session_state.nomor_list[st.session_state.current_index - 1]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Berhasil Terkirim"):
            st.session_state.laporan["sukses"].append(nomor_terakhir)
            st.rerun()
    with col2:
        if st.button("❌ Gagal Terkirim"):
            st.session_state.laporan["gagal"].append(nomor_terakhir)
            st.rerun()

# Tombol unduh laporan
if st.session_state.current_index == len(st.session_state.nomor_list):
    total_sukses = len(st.session_state.laporan["sukses"])
    total_gagal = len(st.session_state.laporan["gagal"])
    semua_data = st.session_state.laporan["sukses"] + st.session_state.laporan["gagal"]
    keterangan = f"Total sukses: {total_sukses}\nTotal gagal: {total_gagal}\n\n"

    isi_laporan = keterangan
    for nomor in st.session_state.laporan["sukses"]:
        isi_laporan += f"{nomor} - SUKSES\n"
    for nomor in st.session_state.laporan["gagal"]:
        isi_laporan += f"{nomor} - GAGAL\n"

    # Buat file laporan
    base_name = os.path.splitext(uploaded_file.name)[0]
    laporan_name = f"laporan_{base_name}.txt"
    gagal_name = f"nomorgagal_{base_name}.txt"

    with open(laporan_name, "w", encoding="utf-8") as f:
        f.write(isi_laporan)
    with open(gagal_name, "w", encoding="utf-8") as f:
        for nomor in st.session_state.laporan["gagal"]:
            f.write(f"{nomor}\n")

    with open(laporan_name, "rb") as f:
        st.download_button("⬇️ Unduh Laporan", f, file_name=laporan_name)

    with open(gagal_name, "rb") as f:
        st.download_button("⬇️ Unduh Nomor Gagal", f, file_name=gagal_name)
