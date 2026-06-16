import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime, timedelta

# 1. Konfigurasi Halaman Website
st.set_page_config(page_title="Dashboard Banjir BMKG Live API", layout="wide")

st.title("🚨 Pusat Kendali & Monitoring Banjir BMKG (LIVE API)")
st.subheader("Stasiun: Kali Babon (Segmen Tembalang) | Koordinat: -7.0512, 110.4578")
st.write("Sistem monitoring otomatis berbasis data satelit cuaca riil yang diperbarui tiap 3 detik.")
st.markdown("---")

# 2. Inisialisasi Penyimpanan Data di Website (Session State)
if 'histori_air' not in st.session_state:
    st.session_state.histori_air = [90, 95, 100]
    
    waktu_sekarang = datetime.utcnow() + timedelta(hours=7)
    waktu_1 = (waktu_sekarang - timedelta(minutes=10)).strftime("%H:%M:%S")
    waktu_2 = (waktu_sekarang - timedelta(minutes=5)).strftime("%H:%M:%S")
    waktu_3 = waktu_sekarang.strftime("%H:%M:%S")
    st.session_state.waktu = [waktu_1, waktu_2, waktu_3]

# 3. Fungsi Ambil Data Curah Hujan Aktual dari API Open-Meteo
def ambil_data_api_aktual():
    url = "https://api.open-meteo.com/v1/forecast?latitude=-7.0512&longitude=110.4578&current=rain"
    try:
        respon = requests.get(url).json()
        return float(respon['current']['rain']) # Data curah hujan dalam mm
    except Exception:
        return 0.0 # Jika gagal/rto, kembalikan nilai 0.0

# ==================== INTERVAL OTOMATIS RUN ====================
@st.fragment(run_every=3)
def jalankan_dashboard_live():
    # A. Ambil curah hujan riil saat ini dari satelit
    hujan_riil = ambil_data_api_aktual()
    
    # B. Logika Hidrologi Simulasi: Konversi hujan riil ke fluktuasi tinggi air sungai
    import random
    tinggi_terakhir = st.session_state.histori_air[-1]
    
    # Base height dipengaruhi hujan riil (jika hujan > 0, air otomatis melonjak naik)
    if hujan_riil > 0:
        tinggi_baru = tinggi_terakhir + (hujan_riil * 15) + random.randint(2, 8)
    else:
        # Jika cuaca cerah (0.0 mm), air berfluktuasi normal atau naik turun tipis (skenario simulasi air mengalir)
        if tinggi_terakhir > 240:
            tinggi_baru = tinggi_terakhir + random.randint(-15, 5)
        else:
            tinggi_baru = tinggi_terakhir + random.randint(3, 12)
            
    waktu_baru = (datetime.utcnow() + timedelta(hours=7)).strftime("%H:%M:%S")

    # C. Simpan ke histori program
    st.session_state.histori_air.append(tinggi_baru)
    st.session_state.waktu.append(waktu_baru)

    tinggi_sekarang = st.session_state.histori_air[-1]
    waktu_sekarang = st.session_state.waktu[-1]

    # D. Tampilan Hasil Analisis Spasial
    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric(label="Live Curah Hujan Satelit (API)", value=f"{hujan_riil} mm")
        st.metric(label=f"Ketinggian Air Kali Babon ({waktu_sekarang})", value=f"{int(tinggi_sekarang)} cm")

        # Pemicu Alarm Suara Mandiri Berbasis File alarm.mp3 Anda (Edisi Visual Kebal Blokir)
        if tinggi_sekarang >= 200:
            st.error("🚨 STATUS: AWAS (BAHAYA BANJIR)")
            st.write("**Tindakan Petugas BMKG:** Segera bunyikan sirine evakuasi warga!")
            
            # Membuat kotak visual khusus tempat bernaungnya audio agar tidak diblokir Chrome
            with st.container(border=True):
                st.markdown("<p style='text-align: center; color: #ff4b4b; font-weight: bold;'>🔊 SISTEM SIRINE ELEKTRONIK PUSAT (LIVE)</p>", unsafe_allow_html=True)
                
                # Memanggil audio lokal via Streamlit Native (Autoplay diaktifkan)
                st.audio(
                    "alarm.mp3", 
                    format="audio/mp3", 
                    autoplay=True, 
                    loop=True
                )
                
                st.markdown("<p style='text-align: center; font-size: 12px; color: #aaaaaa;'>NB: Jika suara belum keluar akibat proteksi browser, silakan klik tombol PLAY (segitiga) di atas sekali.</p>", unsafe_allow_html=True)
        elif 150 <= tinggi_sekarang < 200:
            st.warning("⚠️ STATUS: SIAGA (Waspada Luapan)")
            st.write("**Tindakan Petugas BMKG:** Siagakan logistik penanganan bencana.")
        else:
            st.success("✅ STATUS: AMAN (Normal)")
            st.write("Kondisi aliran sungai Tembalang aman terkendali.")

    with col2:
        df = pd.DataFrame({
            'Waktu Pengecekan': st.session_state.waktu,
            'Tinggi Air (cm)': st.session_state.histori_air
        })
        st.line_chart(df.set_index('Waktu Pengecekan'))

# Panggil fungsi agar langsung mengeksekusi saat website diakses
jalankan_dashboard_live()
