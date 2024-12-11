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
        path.append([pos['lon2'], pos['lat2']])
    return path

@st.cache_data
def calculate_great_circle_distance(lat1, lon1, lat2, lon2):
    geod = Geodesic.WGS84
    g = geod.Inverse(lat1, lon1, lat2, lon2)
    return g['s12'] / 1000  # dalam kilometer

@st.cache_data
def calculate_angle_between_points(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    delta_lon = lon2 - lon1
    x = math.cos(lat2) * math.sin(delta_lon)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    angle = math.degrees(math.atan2(x, y))
    return angle % 360

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
    # Menghitung lintasan, jarak, dan sudut
    path = calculate_great_circle_path(start_lat, start_lon, end_lat, end_lon)
    distance = calculate_great_circle_distance(start_lat, start_lon, end_lat, end_lon)
    angle = calculate_angle_between_points(start_lat, start_lon, end_lat, end_lon)

    st.write(f"Jarak antara titik awal dan akhir adalah: **{distance:.2f} km**")
    st.write(f"Sudut yang dibentuk antara kedua titik: **{angle:.2f}°**")

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

    # Menambahkan simbol pin untuk titik awal dan akhir
    pin_layer = pdk.Layer(
        "IconLayer",
        data=points,
        get_position="[longitude, latitude]",
        get_icon_size=5,
        get_icon_anchor=[0.5, 1],
        icon_data={"url": "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-location.svg"},
        pickable=True
    )

    # Layer Lintasan (Path)
    path_layer = pdk.Layer(
        "PathLayer",
        data=[{"path": path}],
        get_path="path",
        get_width=3,
        get_color=[0, 255, 0],
        width_min_pixels=2,
    )

    # Globe Map View dengan efek Elevasi 3D
    view_state = pdk.ViewState(latitude=(start_lat + end_lat) / 2, longitude=(start_lon + end_lon) / 2, zoom=2, pitch=60)

    # Pydeck Map
    r = pdk.Deck(
        layers=[point_layer, pin_layer, path_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/satellite-v9",
        tooltip={"text": "{name}"}
    )

    # Tampilkan peta
    st.pydeck_chart(r)
