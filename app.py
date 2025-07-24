import streamlit as st
import time
import urllib.parse
import os

st.set_page_config(page_title="WA Sender", layout="centered")

st.title("📤 Pengirim Pesan WA + Laporan")

uploaded_file = st.file_uploader("📄 Upload file .txt berisi daftar nomor (1 nomor/line):", type=["txt"])

pesan_template = st.text_area("✏️ Masukkan isi pesan yang ingin dikirim:", height=150)
delay = st.slider("⏱️ Delay antar pesan (detik)", 3, 15, 7)

if uploaded_file is not None and pesan_template.strip() != "":
    nomor_list = uploaded_file.read().decode("utf-8").splitlines()
    filename_base = uploaded_file.name.replace(".txt", "")
    
    st.success(f"📱 Jumlah nomor yang akan dikirimi pesan: {len(nomor_list)}")

    if st.button("🚀 Mulai Kirim"):
        sukses = []
        gagal = []
        for i, nomor in enumerate(nomor_list, 1):
            st.markdown("---")
            st.subheader(f"📨 Mengirim pesan ke nomor {i} / {len(nomor_list)}")

            # Encode pesan
            pesan_encoded = urllib.parse.quote(pesan_template)
            link_wa = f"https://wa.me/{nomor}?text={pesan_encoded}"
            st.markdown(f"[Klik untuk kirim ke WhatsApp](%s)" % link_wa)
            st.info("👈 Silakan klik link di atas untuk mengirim pesan. Setelah kembali, beri status pengiriman:")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Berhasil [{nomor}]", key=f"sukses_{i}"):
                    sukses.append(nomor)
            with col2:
                if st.button(f"❌ Gagal [{nomor}]", key=f"gagal_{i}"):
                    gagal.append(nomor)

            # UI Countdown Keren dengan Progress Bar
            with st.empty():
                for sisa in range(delay, 0, -1):
                    progress = (delay - sisa) / delay
                    st.progress(progress, f"⏳ Menunggu {sisa} detik sebelum lanjut...")
                    time.sleep(1)
                st.success("✅ Lanjut ke nomor berikutnya!")

        # Simpan hasil laporan
        laporan_path = f"laporan_{filename_base}.txt"
        gagal_path = f"nomorgagal_{filename_base}.txt"

        with open(laporan_path, "w") as f:
            f.write("=== Nomor Sukses ===\n")
            f.write("\n".join(sukses) + "\n\n")
            f.write("=== Nomor Gagal ===\n")
            f.write("\n".join(gagal))

        with open(gagal_path, "w") as f:
            f.write("\n".join(gagal))

        st.success("📥 Pengiriman selesai! Berikut file laporan:")

        with open(laporan_path, "rb") as f:
            st.download_button("⬇️ Unduh Laporan Lengkap", f, file_name=laporan_path)

        if gagal:
            with open(gagal_path, "rb") as f:
                st.download_button("⬇️ Unduh Nomor Gagal", f, file_name=gagal_path)
        else:
            st.info("🎉 Tidak ada nomor yang gagal.")
