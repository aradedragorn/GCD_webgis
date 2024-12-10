import streamlit as st
from geographiclib.geodesic import Geodesic
from geopy.geocoders import Nominatim
import pandas as pd

# Fungsi untuk menghitung lintasan besar
@st.cache_data
def calculate_great_circle_path(lat1, lon1, lat2, lon2, num_points=100):
    path = []
    geod = Geodesic.WGS84
    g = geod.InverseLine(lat1, lon1, lat2, lon2)
    ds = g.s13 / num_points  # Segment size
    for i in range(num_points + 1):
        s = ds * i
        point = g.Position(s)
        path.append({"latitude": point['lat2'], "longitude": point['lon2']})
    return pd.DataFrame(path)

@st.cache_data
def calculate_great_circle_distance(lat1, lon1, lat2, lon2):
    geod = Geodesic.WGS84
    g = geod.Inverse(lat1, lon1, lat2, lon2)
    return g['s12'] / 1000  # dalam kilometer

# Tampilan aplikasi Streamlit
st.title("WebGIS Interaktif: Great Circle Distance (GCD)")
st.markdown("Masukkan koordinat dalam format desimal untuk melihat lintasan besar dan jarak di peta.")

# Input pencarian lokasi
st.sidebar.header("Cari Lokasi")
location = st.sidebar.text_input("Masukkan lokasi:", value="")

# Inisialisasi geolocator
geolocator = Nominatim(user_agent="webgis_app")  # Buat user agent unik

if location:
    try:
        loc = geolocator.geocode(location)
        if loc:
            st.sidebar.write(f"Koordinat untuk '{location}':")
            st.sidebar.write(f"Lintang: {loc.latitude:.4f}°")
            st.sidebar.write(f"Bujur: {loc.longitude:.4f}°")
        else:
            st.sidebar.error("Lokasi tidak ditemukan. Coba gunakan nama tempat yang lebih spesifik.")
    except Exception as e:
        st.sidebar.error(f"Kesalahan saat mencari lokasi: {e}")

# Input koordinat dalam format desimal
st.sidebar.header("Masukkan Koordinat dalam Desimal")

# Koordinat Titik Awal
st.sidebar.subheader("Koordinat Titik Awal")
start_lat = st.sidebar.number_input("Latitude (°)", min_value=-90.0, max_value=90.0, value=6.20889)
start_lon = st.sidebar.number_input("Longitude (°)", min_value=-180.0, max_value=180.0, value=106.82750)

# Koordinat Titik Akhir
st.sidebar.subheader("Koordinat Titik Akhir")
end_lat = st.sidebar.number_input("Latitude (°)", min_value=-90.0, max_value=90.0, value=35.50000)
end_lon = st.sidebar.number_input("Longitude (°)", min_value=-180.0, max_value=180.0, value=100.00000)

# Tombol untuk memulai kalkulasi
if st.sidebar.button("Hitung"):
    # Menghitung lintasan besar dan jarak
    path_df = calculate_great_circle_path(start_lat, start_lon, end_lat, end_lon)
    distance = calculate_great_circle_distance(start_lat, start_lon, end_lat, end_lon)

    # Menampilkan hasil
    st.write(f"Jarak antara titik awal dan akhir adalah: {distance:.5f} km")

    # Menampilkan lintasan di peta menggunakan Streamlit Maps
    st.map(path_df)
