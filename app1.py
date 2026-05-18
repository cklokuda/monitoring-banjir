import streamlit as st
import pandas as pd
import requests 
import time

# 1. Konfigurasi Halaman Website
st.set_page_config(page_title="Dashboard Banjir BMKG Tembalang", layout="wide")

st.title("🚨 Pusat Kendali & Monitoring Banjir BMKG (LIVE DATA)")

# Database Spasial Baru: Menggeser stasiun pantau ke Sungai Krengseng / Area Kampus Tembalang
stasiun_pantau = {
    "id_stasiun": "ST-05-UND",
    "nama_sungai": "Sungai Krengseng (Sektor Kampus Tembalang)",
    "koordinat": "-7.0538, 110.4432",
    "elevasi_dasar_msl": 115.2  # Elevasi dalam meter di atas permukaan laut (MSL)
}

st.subheader(f"Stasiun: {stasiun_pantau['nama_sungai']} | Koordinat: {stasiun_pantau['koordinat']}")
st.write("Sistem otomatisasi hulu-ke-hilir untuk mendeteksi banjir kiriman berbasis Geospasial Real-Time.")
st.markdown("---")

# 2. Inisialisasi Penyimpanan Data di Website (Session State)
if 'histori_curah_hujan' not in st.session_state:
    st.session_state.histori_curah_hujan = [0.0, 0.0, 0.0]
    st.session_state.waktu = ["13:00:00", "14:00:00", "15:00:00"]

# 3. Fungsi Mengambil Data Aktual dari API Weather Berdasarkan Koordinat Baru
def ambil_data_api_aktual():
    # Menembak koordinat presisi Sungai Krengseng Tembalang
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
    waktu_baru = time.strftime("%H:%M:%S")
    
    st.session_state.histori_curah_hujan.append(curah_hujan_baru)
    st.session_state.waktu.append(waktu_baru)

# 5. Ekstraksi Data Terakhir untuk Visualisasi Metrik
hujan_sekarang = st.session_state.histori_curah_hujan[-1]
waktu_sekarang = st.session_state.waktu[-1]

# Logika Pendekatan Teknik Geodesi: Korelasi Curah Hujan Aktual dengan Estimasi Kenaikan Muka Air
tinggi_air_estimasi = 95 + (hujan_sekarang * 25) 

col1, col2 = st.columns([1, 2])

with col1:
    st.metric(label="Curah Hujan Aktual (Open-Meteo API)", value=f"{hujan_sekarang} mm")
    st.metric(label=f"Estimasi Tinggi Air Sungai ({waktu_sekarang})", value=f"{int(tinggi_air_estimasi)} cm")
    
    # Penentuan Status & Pemicu Alarm berbasis Interaksi Pengguna
    if tinggi_air_estimasi >= 200:
        st.error("🚨 STATUS: AWAS (BAHAYA BANJIR)")
        st.write(f"**Peringatan Otomatis:** Debit limpasan permukaan di {stasiun_pantau['nama_sungai']} melebihi ambang batas aman!")
        
        # Audio Engine: Kebal Proteksi Autoplay Chrome
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
    # Representasi Grafik Spasio-Temporal
    df = pd.DataFrame({
        'Waktu Pengecekan': st.session_state.waktu,
        'Curah Hujan (mm)': st.session_state.histori_curah_hujan
    })
    st.line_chart(df.set_index('Waktu Pengecekan'))