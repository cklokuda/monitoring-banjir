import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Konfigurasi Halaman Website
st.set_page_config(page_title="Dashboard Banjir BMKG Otomatis", layout="wide")

st.title("🚨 Pusat Kendali & Monitoring Banjir BMKG")
st.subheader("Stasiun: Kali Babon (Segmen Tembalang) | Koordinat: -7.0512, 110.4578")
st.write("Sistem otomatisasi hulu-ke-hilir yang berjalan secara REAL-TIME tanpa klik tombol.")
st.markdown("---")

# 2. Inisialisasi Penyimpanan Data di Website (Session State)
if 'histori_air' not in st.session_state:
    st.session_state.histori_air = [90, 95, 110]
    
    # Set 3 waktu awal mundur ke belakang agar grafik terlihat realistis
    waktu_sekarang = datetime.utcnow() + timedelta(hours=7)
    waktu_1 = (waktu_sekarang - timedelta(minutes=10)).strftime("%H:%M:%S")
    waktu_2 = (waktu_sekarang - timedelta(minutes=5)).strftime("%H:%M:%S")
    waktu_3 = waktu_sekarang.strftime("%H:%M:%S")
    st.session_state.waktu = [waktu_1, waktu_2, waktu_3]

# 3. Fungsi Simulasi Sensor (Logika Asli Anda Tetap Dipertahankan)
def simulasi_baca_sensor():
    tinggi_terakhir = st.session_state.histori_air[-1]
    if tinggi_terakhir > 250:
        import random
        return tinggi_terakhir + random.randint(-20, 5)
    else:
        import random
        return tinggi_terakhir + random.randint(5, 15)

# ==================== KUNCI OTOMATISASI (STREAMLIT FRAGMENT) ====================
# Dekorator @st.fragment ini memaksa fungsi di bawahnya untuk berjalan otomatis tiap 3 detik
@st.fragment(run_every=3)
def pembaruan_dashboard_otomatis():
    # A. Jalankan fungsi sensor secara otomatis di latar belakang
    tinggi_baru = simulasi_baca_sensor()
    waktu_baru = (datetime.utcnow() + timedelta(hours=7)).strftime("%H:%M:%S")

    # B. Masukkan data baru ke dalam histori
    st.session_state.histori_air.append(tinggi_baru)
    st.session_state.waktu.append(waktu_baru)

    # C. Ambil data paling terakhir untuk ditampilkan ke layar
    tinggi_sekarang = st.session_state.histori_air[-1]
    waktu_sekarang = st.session_state.waktu[-1]

    # D. Render Layout Metrik dan Grafik secara Live
    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric(label=f"Ketinggian Air Terakhir ({waktu_sekarang})", value=f"{tinggi_sekarang} cm")

        # Logika Penentuan Status & Pemicu Alarm Suara Mandiri GitHub
        if tinggi_sekarang >= 200:
            st.error("🚨 STATUS: AWAS (BAHAYA BANJIR)")
            st.write("**Tindakan Petugas BMKG:** Segera hubungi Tim SAR/BPBD Tembalang!")

            # Memanggil file alarm.mp3 yang sudah Anda upload di repositori Anda
            st.audio(
                "alarm.mp3", 
                format="audio/mp3", 
                autoplay=True, 
                loop=True
            )
        elif 150 <= tinggi_sekarang < 200:
            st.warning("⚠️ STATUS: SIAGA (Waspada Luapan)")
            st.write("**Tindakan Petugas BMKG:** Pantau tren kenaikan grafik secara intensif.")
        else:
            st.success("✅ STATUS: AMAN (Normal)")
            st.write("Aliran sungai terpantau lancar.")

    with col2:
        # Membuat Grafik yang Otomatis Memanjang ke Kanan mengikuti Waktu Nyata
        df = pd.DataFrame({
            'Waktu Pengecekan': st.session_state.waktu,
            'Tinggi Air (cm)': st.session_state.histori_air
        })
        st.line_chart(df.set_index('Waktu Pengecekan'))

# 4. Memanggil Fungsi Otomatis Agar Langsung Berjalan Saat Web Dibuka
pembaruan_dashboard_otomatis()
# ================================================================================
