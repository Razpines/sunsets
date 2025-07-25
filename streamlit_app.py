import streamlit as st
import sunset_prediction as sp
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Sunset Score", page_icon="☀️", layout="wide")

st.title("Sunset Score Explorer")

POPULAR = {
    "Tel Aviv": (32.0853, 34.7818),
    "New York": (40.7128, -74.0060),
    "London": (51.5074, -0.1278),
    "Tokyo": (35.6895, 139.6917),
    "Sydney": (-33.8688, 151.2093),
}

location = st.selectbox("Select a popular location", list(POPULAR.keys()))
lat, lon = POPULAR[location]

st.write("Or pick a custom location by clicking on the map below:")

m = folium.Map(location=[lat, lon], zoom_start=4)
folium.Marker([lat, lon], tooltip=location).add_to(m)
click_data = st_folium(m, width=700, height=500)
if click_data.get("last_clicked"):
    lat = click_data["last_clicked"]["lat"]
    lon = click_data["last_clicked"]["lng"]

st.write(f"Current coordinates: {lat:.4f}, {lon:.4f}")

if st.button("Get Sunset Score"):
    with st.spinner("Fetching data..."):
        sunset_time = sp.fetch_sunset_time(lat, lon)
        weather = sp.fetch_weather(lat, lon)
        air = sp.fetch_air_quality(lat, lon)
        target_hour = sunset_time.replace(minute=0, second=0, microsecond=0)
        score, variables = sp.compute_score(weather, air, target_hour)
        st.subheader("Results")
        st.write("Sunset time (UTC)", sunset_time)
        st.json(variables)
        st.metric("Sunset score", f"{score:.2f}")

