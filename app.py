import streamlit as st
import pandas as pd
import time
import sys
from datetime import datetime, timedelta # TAMBAHAN: Untuk mengunci waktu riil WIB

# 1. Konfigurasi Halaman Website
st.set_page_config(page_title="Dashboard Banjir BMKG", layout="wide")

st.title("🚨 Pusat Kendali & Monitoring Banjir BMKG")
st.subheader("Stasiun: Kali Babon (Segmen Tembalang) | Koordinat: -7.0512, 110.4578")
st.write("Sistem otomatisasi hulu-ke-hilir untuk memangkas keterlambatan informasi bencana.")
st.markdown("---")

# 2. Inisialisasi Penyimpanan Data di Website (Session State)
if 'histori_air' not in st.session_state:
    st.session_state.histori_air = [90, 95, 110]
    
    # PERBAIKAN: Set waktu awal agar langsung menyesuaikan WIB nyata (UTC server + 7 jam)
    waktu_sekarang_init = (datetime.utcnow() + timedelta(hours=7)).strftime("%H:%M:%S")
    st.session_state.waktu = [waktu_sekarang_init, waktu_sekarang_init, waktu_sekarang_init]

# 3. Fungsi Simulasi Tren Kenaikan Air Perlahan (Skenario Banjir)
def simulasi_baca_sensor():
    tinggi_terakhir = st.session_state.histori_air[-1]
    if tinggi_terakhir > 250:
        import random
        return tinggi_terakhir + random.randint(-20, 5)
    else:
        import random
        return tinggi_terakhir + random.randint(5, 15)

# 4. Tombol untuk Simulasi Waktu Berjalan (Menerima Data Baru dari Sensor)
if st.button("🔄 Ambil Data Sensor Terbaru (M2M)"):
    tinggi_baru = simulasi_baca_sensor()
    
    # KUNCI PERBAIKAN WAKTU NYATA: Memaksa server mencatat waktu WIB saat tombol diklik
    waktu_baru = (datetime.utcnow() + timedelta(hours=7)).strftime("%H:%M:%S")

    # Masukkan data baru ke dalam histori website
    st.session_state.histori_air.append(tinggi_baru)
    st.session_state.waktu.append(waktu_baru)

# 5. Tampilan Komponen Website (Metrik & Alarm)
tinggi_sekarang = st.session_state.histori_air[-1]
waktu_sekarang = st.session_state.waktu[-1]

col1, col2 = st.columns([1, 2])

with col1:
    st.metric(label=f"Ketinggian Air Terakhir ({waktu_sekarang})", value=f"{tinggi_sekarang} cm")

    # Logika Penentuan Status & Pemicu Alarm Suara di Website
    if tinggi_sekarang >= 200:
        st.error("🚨 STATUS: AWAS (BAHAYA BANJIR)")
        st.write("**Tindakan Petugas BMKG:** Segera nyalakan sirine desa dan hubungi Tim SAR/BPBD Tembalang!")

        # Memicu bunyi alarm otomatis menggunakan link alternatif Google yang lebih aman dari blokir internet
        st.components.v1.html(
            """
            <audio id="alarm-keras" loop>
                <source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg" type="audio/ogg">
                <source src="https://www.soundjay.com/buttons/sounds/alarm-clock-01.mp3" type="audio/mp3">
            </audio>
            <script>
                var audio = document.getElementById("alarm-keras");
                audio.volume = 1.0; // Volume maksimal
                
                // Memicu paksa suara melalui interaksi klik pengguna
                document.addEventListener('click', function() {
                    audio.play();
                });
                audio.play();
            </script>
            """,
            height=0
        )
    elif 150 <= tinggi_sekarang < 200:
        st.warning("⚠️ STATUS: SIAGA (Waspada Luapan)")
        st.write("**Tindakan Petugas BMKG:** Pantau tren kenaikan grafik secara intensif.")
    else:
        st.success("✅ STATUS: AMAN (Normal)")
        st.write("Aliran sungai terpantau lancar.")

with col2:
    # Membuat Grafik Tren Elevasi Air secara Otomatis di Website
    df = pd.DataFrame({
        'Waktu Pengecekan': st.session_state.waktu,
        'Tinggi Air (cm)': st.session_state.histori_air
    })
    st.line_chart(df.set_index('Waktu Pengecekan'))
