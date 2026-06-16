import streamlit as st
import pandas as pd
import requests 
import time
from datetime import datetime, timedelta

# 1. Konfigurasi Halaman Website
st.set_page_config(page_title="Dashboard Banjir BMKG Tembalang", layout="wide")

# ==================== SENTUHAN DESAIN VISUAL (CSS) ====================
# Menyisipkan gambar background keren bertema teknologi/satelit cuaca
background_image_url = "https://img.piri.net/piri/upload/3/2026/2/18/beda5ea5-87aoshytvtcpclgr0izw1e.webp" # Gambar bumi/teknologi dari Unsplash

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.65)), url("{background_image_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: white;
    }}
    /* Membuat teks judul dan subheader agar lebih kontras di atas background */
    h1, h2, h3, p, .stMetric {{
        color: white !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)
# ======================================================================

st.title("🚨 Pusat Kendali & Monitoring Banjir BMKG (LIVE DATA)")

stasiun_pantau = {
    "id_stasiun": "ST-05-UND",
    "nama_sungai": "Sungai Krengseng (Sektor Kampus Tembalang)",
    "koordinat": "-7.0538, 110.4432",
    "elevasi_dasar_msl": 115.2  
}

st.subheader(f"Stasiun: {stasiun_pantau['nama_sungai']} | Koordinat: {stasiun_pantau['koordinat']}")
st.write("Sistem otomatisasi hulu-ke-hilir untuk mendeteksi banjir kiriman berbasis Geospasial Real-Time.")
st.markdown("---")

# 2. Inisialisasi Penyimpanan Data di Website (Session State)
if 'histori_curah_hujan' not in st.session_state:
    st.session_state.histori_curah_hujan = [0.0, 0.0, 0.0]
    waktu_sekarang_init = (datetime.utcnow() + timedelta(hours=7)).strftime("%H:%M:%S")
    st.session_state.waktu = [waktu_sekarang_init, waktu_sekarang_init, waktu_sekarang_init]

# 3. Fungsi Mengambil Data Aktual dari API Weather
def ambil_data_api_aktual():
    url = f"https://api.open-meteo.com/v1/forecast?latitude=-7.0538&longitude=110.4432&current=rain"
    try:
        respon = requests.get(url).json()
        curah_hujan_sekarang = respon['current']['rain'] 
        return float(curah_hujan_sekarang)
    except Exception:
        return 0.0

# 4. Tombol Akses Sinkronisasi Sensor Lapangan
if st.button("📡 Tarik Data Satelit & Sensor Cuaca Aktual"):
    curah_hujan_baru = ambil_data_api_aktual()
    waktu_baru = (datetime.utcnow() + timedelta(hours=7)).strftime("%H:%M:%S")
    
    st.session_state.histori_curah_hujan.append(curah_hujan_baru)
    st.session_state.waktu.append(waktu_baru)

# 5. Ekstraksi Data Terakhir untuk Visualisasi Metrik
hujan_sekarang = st.session_state.histori_curah_hujan[-1]
waktu_sekarang = st.session_state.waktu[-1]

tinggi_air_estimasi = 95 + (hujan_sekarang * 25) 

# SUSUNAN LAYOUT TAMPILAN WEBSITE
col1, col2 = st.columns([1, 2])

with col1:
    st.metric(label="Curah Hujan Aktual (Open-Meteo API)", value=f"{hujan_sekarang} mm")
    st.metric(label=f"Estimasi Tinggi Air Sungai ({waktu_sekarang})", value=f"{int(tinggi_air_estimasi)} cm")
    
    if tinggi_air_estimasi >= 200:
        st.error("🚨 STATUS: AWAS (BAHAYA BANJIR)")
        st.write(f"**Peringatan Otomatis:** Debit limpasan permukaan di {stasiun_pantau['nama_sungai']} melebihi ambang batas aman!")
        
        st.components.v1.html(
            """
            <audio id="alarm-keras" loop><source src="https://www.soundjay.com/buttons/sounds/alarm-clock-01.mp3" type="audio/mp3"></audio>
            <script>
                var audio = document.getElementById("alarm-keras"); audio.volume = 1.0;
                document.addEventListener('click', function() { audio.play(); });
                audio.play();
            </script>
            """, height=0
        )
    elif 150 <= tinggi_air_estimasi < 200:
        st.warning("⚠️ STATUS: SIAGA (Waspada Luapan)")
        st.write("Anomali cuaca terdeteksi. Petugas BMKG harap melakukan pemantauan visual pada pintu air.")
    else:
        st.success("✅ STATUS: AMAN (Normal)")
        st.write("Aliran hidrologi sekitar Tembalang terpantau lancar dan stabil.")

with col2:
    # Grafik Tren Curah Hujan
    df = pd.DataFrame({
        'Waktu Pengecekan': st.session_state.waktu,
        'Curah Hujan (mm)': st.session_state.histori_curah_hujan
    })
    st.line_chart(df.set_index('Waktu Pengecekan'))

# ==================== MENYISIPKAN VIDEO MURNI TANPA ELEMEN YOUTUBE ====================
st.markdown("---")
video_col1, video_col2 = st.columns(2)

# ID Video dari link asli Anda
id_video_anda = "EJiMR9bIcRU"
id_video_dua = "M99b2qWJ1m0"

with video_col1:
    # Menggunakan parameter kontrok tambahan (?controls=0&modestbranding=1&rel=0)
    # Dan gaya CSS overflow hidden + pointer-events agar board YouTube tidak bisa diinteraksi
    st.components.v1.html(
        f"""
        <div style="position: relative; width: 100%; height: 315px; overflow: hidden; border-radius: 8px;">
            <iframe width="100%" height="100%" 
                src="https://www.youtube.com/embed/EJiMR9bIcRU?autoplay=1&mute=1&loop=1&playlist={id_video_anda}&controls=0&modestbranding=1&rel=0&showinfo=0" 
                title="Video Player 1" frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;"
                allowfullscreen>
            </iframe>
        </div>
        """,
        height=320,
    )

with video_col2:
    st.components.v1.html(
        f"""
        <div style="position: relative; width: 100%; height: 315px; overflow: hidden; border-radius: 8px;">
            <iframe width="100%" height="100%" 
                src="https://www.youtube.com/embed/EJiMR9bIcRU?autoplay=1&mute=1&loop=1&playlist={id_video_dua}&controls=0&modestbranding=1&rel=0&showinfo=0" 
                title="Video Player 2" frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;"
                allowfullscreen>
            </iframe>
        </div>
        """,
        height=320,
    )
# =====================================================================
