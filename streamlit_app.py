import streamlit as st
from geographiclib.geodesic import Geodesic
from geopy.geocoders import Nominatim
import math  # Import the math module

# Fungsi untuk menghitung lintasan besar
@st.cache_data
def calculate_great_circle_path(lat1, lon1, lat2, lon2):
    path = []
    geod = Geodesic.WGS84
    g = geod.InverseLine(lat1, lon1, lat2, lon2)
    ds = 1000e3  # Segment size: 1000 km
    n = int(g.s13 / ds) + 1
    for i in range(n + 1):
        s = min(ds * i, g.s13)
        point = g.Position(s)
        path.append((point['lat2'], point['lon2']))
    return path

@st.cache_data
def calculate_great_circle_distance(lat1, lon1, lat2, lon2):
    geod = Geodesic.WGS84
    g = geod.Inverse(lat1, lon1, lat2, lon2)
    return g['s12'] / 1000  # dalam kilometer

# Tampilan aplikasi Streamlit
st.title("WebGIS Interaktif: Great Circle Distance (GCD)")
st.markdown("Masukkan koordinat dalam format desimal untuk melihat jarak dan lintasan di peta.")

# Input pencarian lokasi
st.sidebar.header("Cari Lokasi")
location = st.sidebar.text_input("Masukkan lokasi:", value="")  # Set a default empty string

# Inisialisasi geolocator
geolocator = Nominatim(user_agent="webgis_app")  # Buat user agent unik

if location:
    try:
        loc = geolocator.geocode(location)
        if loc:
            st.sidebar.write(f"Koordinat untuk '{location}':")
            lat_decimal = loc.latitude
            lon_decimal = loc.longitude
            st.sidebar.write(f"Lintang: {lat_decimal:.4f}°")
            st.sidebar.write(f"Bujur: {lon_decimal:.4f}°")
        else:
            st.sidebar.error("Lokasi tidak ditemukan. Coba periksa ejaan atau gunakan nama tempat yang lebih spesifik.")
    except Exception as e:
        st.sidebar.error(f"Terjadi kesalahan saat mencari lokasi: {e}")

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

# Button untuk menghitung
if st.sidebar.button("Hitung"):
    # Menghitung lintasan besar dan jarak
    path = calculate_great_circle_path(start_lat, start_lon, end_lat, end_lon)
    distance = calculate_great_circle_distance(start_lat, start_lon, end_lat, end_lon)

    # Menghitung azimuth berangkat dan pulang
    d_lon = math.radians(end_lon - start_lon)

    start_lat, start_lon, end_lat, end_lon = map(math.radians, [start_lat, start_lon, end_lat, end_lon])

    y_depart = math.sin(d_lon) * math.cos(end_lat)
    x_depart = math.cos(start_lat) * math.sin(end_lat) - math.sin(start_lat) * math.cos(end_lat) * math.cos(d_lon)
    azimuth_depart = math.degrees(math.atan2(y_depart, x_depart))

    y_return = math.sin(-d_lon) * math.cos(start_lat)
    x_return = math.cos(end_lat) * math.sin(start_lat) - math.sin(end_lat) * math.cos(start_lat) * math.cos(-d_lon)
    azimuth_return = math.degrees(math.atan2(y_return, x_return))

    # Konversi sudut negatif ke rentang 0–360°
    azimuth_depart = (azimuth_depart + 360) % 360
    azimuth_return = (azimuth_return + 360) % 360

    # Menampilkan hasil
    st.write(f"Jarak antara titik awal dan akhir adalah: {distance:.5f} km")
    st.write(f"Sudut berangkat: {azimuth_depart:.5f}°")
    st.write(f"Sudut pulang: {azimuth_return:.5f}°")

    # Membuat peta
    m = folium.Map(location=[(start_lat + end_lat) / 2, (start_lon + end_lon) / 2], zoom_start=3)

    # Menambahkan marker untuk titik awal dan akhir dengan simbol yang berbeda
    folium.Marker(
        [start_lat, start_lon],
        popup=f'Titik Awal\nLintang: {start_lat:.5f}°, Bujur: {start_lon:.5f}°',
        icon=folium.Icon(color='green', icon='info-sign')
    ).add_to(m)

    folium.Marker(
        [end_lat, end_lon],
        popup=f'Titik Akhir\nLintang: {end_lat:.5f}°, Bujur: {end_lon:.5f}°',
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

    # Menambahkan lintasan ke peta
    folium.PolyLine(path, color='red', weight=2.5, opacity=1).add_to(m)

    # Menampilkan peta di Streamlit
    st_folium(m, width=800, height=500)
