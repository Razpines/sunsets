import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import folium

from sunset_prediction import (
    fetch_sunset_time,
    fetch_weather,
    fetch_air_quality,
    build_dataframe,
    compute_score,
)

st.set_page_config(page_title="Sunset Score", layout="centered")

st.title("Sunset Predictor")

POPULAR_LOCATIONS = {
    "Tel Aviv, Israel": (32.07, 34.78),
    "New York, USA": (40.7128, -74.0060),
    "London, UK": (51.5074, -0.1278),
    "Tokyo, Japan": (35.6895, 139.6917),
    "Sydney, Australia": (-33.8688, 151.2093),
}

location_name = st.selectbox("Choose a location", options=list(POPULAR_LOCATIONS.keys()))
lat_default, lon_default = POPULAR_LOCATIONS[location_name]

if "selected_location" not in st.session_state:
    st.session_state.selected_location = location_name
    st.session_state.lat = lat_default
    st.session_state.lon = lon_default

if location_name != st.session_state.selected_location:
    st.session_state.selected_location = location_name
    st.session_state.lat = lat_default
    st.session_state.lon = lon_default

st.number_input("Latitude", key="lat")
st.number_input("Longitude", key="lon")

m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=5)
folium.Marker([st.session_state.lat, st.session_state.lon]).add_to(m)

st.write("Click on the map to select coordinates:")
map_data = st_folium(m, key="map", height=400, width=700)

if map_data.get("last_clicked"):
    st.session_state.lat = map_data["last_clicked"]["lat"]
    st.session_state.lon = map_data["last_clicked"]["lng"]

if st.button("Get Sunset Score"):
    with st.spinner("Fetching data..."):
        sunset_time = fetch_sunset_time(
            st.session_state.lat, st.session_state.lon
        )
        weather = fetch_weather(
            st.session_state.lat, st.session_state.lon, date=sunset_time.date()
        )
        air_quality = fetch_air_quality(
            st.session_state.lat, st.session_state.lon, date=sunset_time.date()
        )
        df = build_dataframe(weather, air_quality)
        target_hour = sunset_time.replace(minute=0, second=0, microsecond=0)
        if target_hour in df.index:
            row = df.loc[target_hour]
        else:
            nearest_idx = df.index.get_indexer([target_hour], method="nearest")[0]
            row = df.iloc[nearest_idx]
        score = compute_score(row)
    st.success(f"Sunset time (local): {sunset_time}")
    st.write("Variables at sunset:")
    st.dataframe(row.to_frame().T)
    st.metric("Sunset Score", f"{score:.2f}")
