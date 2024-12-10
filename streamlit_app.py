import streamlit as st
import pydeck as pdk
from geographiclib.geodesic import Geodesic
from geopy.geocoders import Nominatim
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
        path.append({"latitude": pos['lat2'], "longitude": pos['lon2']})
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
st.title("WebGIS Interaktif: Great Circle Distance (GCD) dalam Globe 3D")
st.sidebar.header("Cari Lokasi")

# Pencarian lokasi
geolocator = Nominatim(user_agent="webgis_app")
location = st.sidebar.text_input("Masukkan nama lokasi:")
if location:
    try:
        loc = geolocator.geocode(location)
        if loc:
            st.sidebar.write(f"Lokasi '{location}' ditemukan:")
            st.sidebar.write(f"Lintang: {loc.latitude:.4f}°")
            st.sidebar.write(f"Bujur: {loc.longitude:.4f}°")
        else:
            st.sidebar.error("Lokasi tidak ditemukan. Coba nama lain.")
    except Exception as e:
        st.sidebar.error(f"Kesalahan: {e}")

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
    points = [
        {"latitude": start_lat, "longitude": start_lon, "name": "Titik Awal"},
        {"latitude": end_lat, "longitude": end_lon, "name": "Titik Akhir"}
    ]

    # Layer Titik (Marker)
    point_layer = pdk.Layer(
        "ScatterplotLayer",
        data=points,
        get_position="[longitude, latitude]",
        get_fill_color=[255, 0, 0, 160],
        get_radius=50000,
        pickable=True,
    )

    # Layer Lintasan (Arc)
    arc_layer = pdk.Layer(
        "ArcLayer",
        data=path,
        get_source_position="[longitude, latitude]",
        get_target_position="[longitude, latitude]",
        get_width=5,
        get_source_color=[0, 255, 0],
        get_target_color=[0, 0, 255],
    )

    # Globe Map View
    view_state = pdk.ViewState(latitude=(start_lat + end_lat) / 2, longitude=(start_lon + end_lon) / 2, zoom=0.5, pitch=45)

    # Pydeck Map
    r = pdk.Deck(
        layers=[point_layer, arc_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/satellite-v9",
        tooltip={"text": "{name}"}
    )

    # Tampilkan peta
    st.pydeck_chart(r)
