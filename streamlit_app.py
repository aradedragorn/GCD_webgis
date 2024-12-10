import streamlit as st
import pydeck as pdk
from geographiclib.geodesic import Geodesic
import math

# Fungsi untuk menghitung lintasan besar
@st.cache_data
def calculate_great_circle_path(lat1, lon1, lat2, lon2, segments=100):
    path = []
    geod = Geodesic.WGS84
    g = geod.InverseLine(lat1, lon1, lat2, lon2)
    for i in range(segments + 1):
        s = g.s13 * i / segments
        pos = g.Position(s)
        path.append([pos['lon2'], pos['lat2']])
    return path

@st.cache_data
def calculate_great_circle_distance(lat1, lon1, lat2, lon2):
    geod = Geodesic.WGS84
    g = geod.Inverse(lat1, lon1, lat2, lon2)
    return g['s12'] / 1000  # dalam kilometer

@st.cache_data
def calculate_azimuth(lat1, lon1, lat2, lon2):
    geod = Geodesic.WGS84
    g = geod.Inverse(lat1, lon1, lat2, lon2)
    return g['azi1'], g['azi2']  # Azimuth berangkat dan pulang

# Tampilan aplikasi Streamlit
st.title("WebGIS Interaktif: Great Circle Distance (GCD) dalam 3D")
st.sidebar.header("Masukkan Koordinat")

# Koordinat Titik Awal
st.sidebar.subheader("Koordinat Titik Awal")
start_lat = st.sidebar.number_input("Latitude Awal (°)", min_value=-90.0, max_value=90.0, value=6.20889)
start_lon = st.sidebar.number_input("Longitude Awal (°)", min_value=-180.0, max_value=180.0, value=106.82750)

# Koordinat Titik Akhir
st.sidebar.subheader("Koordinat Titik Akhir")
end_lat = st.sidebar.number_input("Latitude Akhir (°)", min_value=-90.0, max_value=90.0, value=35.50000)
end_lon = st.sidebar.number_input("Longitude Akhir (°)", min_value=-180.0, max_value=180.0, value=100.00000)

# Tombol Hitung
if st.sidebar.button("Hitung"):
    # Menghitung lintasan, jarak, dan azimuth
    path = calculate_great_circle_path(start_lat, start_lon, end_lat, end_lon)
    distance = calculate_great_circle_distance(start_lat, start_lon, end_lat, end_lon)
    azimuth_depart, azimuth_return = calculate_azimuth(start_lat, start_lon, end_lat, end_lon)
    
    # Pastikan azimuth positif
    azimuth_depart = azimuth_depart % 360
    azimuth_return = azimuth_return % 360

    st.write(f"Jarak antara titik awal dan akhir adalah: **{distance:.2f} km**")
    st.write(f"Sudut berangkat: **{azimuth_depart:.2f}°**")
    st.write(f"Sudut pulang: **{azimuth_return:.2f}°**")

    # Data untuk Pydeck
    arc_data = [{
        "from": {"latitude": start_lat, "longitude": start_lon},
        "to": {"latitude": end_lat, "longitude": end_lon},
        "name": "Great Circle Path"
    }]
    
    # Layer Arc
    arc_layer = pdk.Layer(
        "ArcLayer",
        data=arc_data,
        get_source_position="['from.longitude', 'from.latitude']",
        get_target_position="['to.longitude', 'to.latitude']",
        get_width=2,
        get_source_color=[255, 0, 0],
        get_target_color=[0, 0, 255],
    )
    
    # Globe Map View
    view_state = pdk.ViewState(latitude=(start_lat + end_lat) / 2, longitude=(start_lon + end_lon) / 2, zoom=0.5, pitch=0)

    # Pydeck Map
    r = pdk.Deck(
        layers=[arc_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10"
    )

    # Tampilkan peta
    st.pydeck_chart(r)
