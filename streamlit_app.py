import streamlit as st
import pydeck as pdk
import math
from geopy.geocoders import Nominatim

# Fungsi untuk mencari lokasi dengan geopy
def get_coordinates(location):
    geolocator = Nominatim(user_agent="webgis_app")
    loc = geolocator.geocode(location)
    if loc:
        return loc.latitude, loc.longitude
    return None, None

# Judul aplikasi
st.title("Globe 3D Interaktif dengan Pydeck dan Mapbox")

# Kolom untuk mencari lokasi
st.sidebar.header("Cari Lokasi")
location = st.sidebar.text_input("Masukkan nama lokasi", value="Semarang")  # Default: Semarang

# Mengambil koordinat lokasi yang dicari
if location:
    lat, lon = get_coordinates(location)
    if lat is not None and lon is not None:
        st.sidebar.write(f"Lokasi '{location}' ditemukan!")
        st.sidebar.write(f"Latitude: {lat:.4f}°")
        st.sidebar.write(f"Longitude: {lon:.4f}°")
    else:
        st.sidebar.write(f"Lokasi '{location}' tidak ditemukan.")

# Koordinat titik awal dan akhir
st.sidebar.header("Masukkan Koordinat Titik Awal dan Akhir")

start_lat = st.sidebar.number_input("Latitude Titik Awal", min_value=-90.0, max_value=90.0, value=6.20889)
start_lon = st.sidebar.number_input("Longitude Titik Awal", min_value=-180.0, max_value=180.0, value=106.82750)
end_lat = st.sidebar.number_input("Latitude Titik Akhir", min_value=-90.0, max_value=90.0, value=35.50000)
end_lon = st.sidebar.number_input("Longitude Titik Akhir", min_value=-180.0, max_value=180.0, value=100.00000)

# Sudut berangkat dan pulang
st.sidebar.subheader("Sudut Berangkat dan Pulang")
azimuth_depart = st.sidebar.number_input("Sudut Berangkat (°)", min_value=-180.0, max_value=180.0, value=89.75)
azimuth_return = st.sidebar.number_input("Sudut Pulang (°)", min_value=-180.0, max_value=180.0, value=131.33)

# Menampilkan Globe 3D
view_state = pdk.ViewState(
    latitude=0,   # Titik tengah globe
    longitude=0,
    zoom=1,       # Level zoom untuk globe
    pitch=45,     # Tilt untuk efek 3D
    bearing=0     # Putar globe
)

# Menambahkan Globe 3D dengan Pydeck
deck = pdk.Deck(
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/satellite-v9",  # Style mapbox
    layers=[]
)

# Menampilkan globe 3D di Streamlit
st.pydeck_chart(deck)

# Menampilkan informasi tentang titik awal dan akhir
st.write(f"**Koordinat Titik Awal**: Latitude {start_lat:.4f}°, Longitude {start_lon:.4f}°")
st.write(f"**Koordinat Titik Akhir**: Latitude {end_lat:.4f}°, Longitude {end_lon:.4f}°")

st.write(f"**Sudut Berangkat**: {azimuth_depart:.2f}°")
st.write(f"**Sudut Pulang**: {azimuth_return:.2f}°")

# Menambahkan Pin untuk Titik Awal dan Titik Akhir ke Globe
marker_layer = pdk.Layer(
    "ScatterplotLayer",
    data=[{"position": [start_lon, start_lat], "color": [0, 255, 0], "radius": 1000},  # Titik Awal (hijau)
          {"position": [end_lon, end_lat], "color": [255, 0, 0], "radius": 1000}],  # Titik Akhir (merah)
    get_position="position",
    get_color="color",
    get_radius="radius",
    pickable=True
)

# Menambahkan layer untuk garis lintasan
path_layer = pdk.Layer(
    "PathLayer",
    data=[{"coordinates": [[start_lon, start_lat], [end_lon, end_lat]], "color": [0, 255, 0], "width": 3}],
    get_color="color",
    get_width="width",
    width_scale=1,
    pickable=True
)

# Memasukkan layer ke dalam deck dan menampilkan
deck.layers = [marker_layer, path_layer]
st.pydeck_chart(deck)

# Menambahkan deskripsi peta
st.markdown("""
Peta ini menampilkan globe 3D dengan dua titik (titik awal dan akhir), serta lintasan antara kedua titik tersebut.
""")
