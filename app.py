import streamlit as st
import pandas as pd
import time
import sys

# 1. Konfigurasi Halaman Website
st.set_page_config(page_title="Dashboard Banjir BMKG", layout="wide")

st.title("🚨 Pusat Kendali & Monitoring Banjir BMKG")
st.subheader("Stasiun: Kali Babon (Segmen Tembalang) | Koordinat: -7.0512, 110.4578")
st.write("Sistem otomatisasi hulu-ke-hilir untuk memangkas keterlambatan informasi bencana.")
st.markdown("---")

# 2. Inisialisasi Penyimpanan Data di Website (Session State)
if 'histori_air' not in st.session_state:
    st.session_state.histori_air = [90, 95, 110]
    st.session_state.waktu = ["22:00:00", "22:05:00", "22:10:00"]

# 3. Fungsi Simulasi Tren Kenaikan Air Perlahan (Skenario Banjir)
def simulasi_baca_sensor():
    # Mengambil angka terakhir lalu menaikkannya secara logis (5-15 cm)
    tinggi_terakhir = st.session_state.histori_air[-1]

    # Jika sudah terlalu tinggi/banjir, buat fluktuasi surut atau tetap
    if tinggi_terakhir > 250:
        import random
        return tinggi_terakhir + random.randint(-20, 5)
    else:
        import random
        return tinggi_terakhir + random.randint(5, 15)

# 4. Tombol untuk Simulasi Waktu Berjalan (Menerima Data Baru dari Sensor)
if st.button("🔄 Ambil Data Sensor Terbaru (M2M)"):
    tinggi_baru = simulasi_baca_sensor()
    waktu_baru = time.strftime("%H:%M:%S")

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

        # AMPLIFIER AUDIO ENGINE: Menggunakan GainNode untuk mendongkrak volume melebihi batas normal
        st.components.v1.html(
            """
            <audio id="alarm-keras" loop crossOrigin="anonymous">
                <source src="https://www.soundjay.com/buttons/sounds/alarm-clock-01.mp3" type="audio/mp3">
                <source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg" type="audio/ogg">
            </audio>

            <script>
                var audio = document.getElementById("alarm-keras");
                var audioContextStarted = false;

                function kuatkanDanMainkanSuara() {
                    if (audioContextStarted) {
                        audio.play();
                        return;
                    }

                    // 1. Buat sistem Audio Context standar industri
                    var AudioContext = window.AudioContext || window.webkitAudioContext;
                    if (AudioContext) {
                        var context = new AudioContext();
                        
                        // 2. Ambil sumber suara dari tag audio di atas
                        var source = context.createMediaElementSource(audio);
                        
                        // 3. Buat node "Amplifier" (GainNode)
                        var gainNode = context.createGain();
                        
                        # DONGKRAK VOLUME DI SINI: Nilai 3.5 berarti suara dikuatkan 3.5 kali lipat dari aslinya!
                        gainNode.gain.value = 3.5; 
                        
                        # Jalur kabel audio digital: Suara -> Amplifier -> Speaker Laptop
                        source.connect(gainNode);
                        gainNode.connect(context.destination);
                        
                        if (context.state === 'suspended') {
                            context.resume();
                        }
                        audioContextStarted = true;
                    }
                    
                    audio.play();
                }

                # Pemicu Otomatis Langsung
                kuatkanDanMainkanSuara();

                # Pemicu Cadangan Wajib: Klik di area manapun di dalam web akan langsung menggelegarkan suara
                document.addEventListener('click', function() {
                    kuatkanDanMainkanSuara();
                });
                window.parent.document.addEventListener('click', function() {
                    kuatkanDanMainkanSuara();
                });
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
