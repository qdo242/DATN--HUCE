import streamlit as st
import sqlite3
import pandas as pd
import folium
from streamlit_folium import st_folium
import time
import os

st.set_page_config(page_title="Dashboard Giam sat Xi-Y", layout="wide")
DB_NAME = os.path.join(os.path.dirname(__file__), '..', 'iot_security.db')

st.title("He thong quan ly va giam sat IoT (Mo hinh Xi -> Y -> Server)")

tabs = st.tabs(["Bieu do cam bien", "Ban do Web (Leaflet)", "Du lieu thiet bi"])

def load_data(query):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

with tabs[0]:
    df_telemetry = load_data("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 50")
    if not df_telemetry.empty:
        latest = df_telemetry.iloc[0]
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Nhiet do (C)", f"{latest.get('temperature') or 0:.1f}")
        col2.metric("Do am (%)", f"{latest.get('humidity') or 0:.1f}")
        col3.metric("CO2 (ppm)", f"{latest.get('co2') or 0:.0f}")
        col4.metric("CO (ppm)", f"{latest.get('co') or 0:.1f}")
        col5.metric("NH3 (ppm)", f"{latest.get('nh3') or 0:.1f}")

        st.write("### Dien bien cac chi so moi truong")
        avail = [c for c in ['temperature', 'humidity', 'co2', 'co', 'nh3'] if c in df_telemetry.columns]
        if avail:
            chart_data = df_telemetry.set_index('timestamp')[avail]
            st.line_chart(chart_data)
        else:
            st.warning("Khong tim thay du lieu")
    else:
        st.info("Dang cho du lieu tu cac thiet bi Xi...")

with tabs[1]:
    st.write("### Vi tri thuc te cua thiet bi Xi va Y tren ban do")
    m = folium.Map(location=[21.0045, 105.8433], zoom_start=16)

    map_query = """
        SELECT t.device_id, t.latitude, t.longitude, d.description
        FROM telemetry t
        JOIN (SELECT device_id, MAX(timestamp) as max_ts FROM telemetry GROUP BY device_id) tm
        ON t.device_id = tm.device_id AND t.timestamp = tm.max_ts
        JOIN devices d ON t.device_id = d.device_id
    """
    df_map = load_data(map_query)

    if not df_map.empty:
        for _, row in df_map.iterrows():
            if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
                color = 'blue' if 'Xi' in row['device_id'] else 'red'
                folium.Marker(
                    [float(row['latitude']), float(row['longitude'])],
                    popup=f"ID: {row['device_id']}<br>{row['description']}",
                    tooltip=row['device_id'],
                    icon=folium.Icon(color=color, icon='info-sign')
                ).add_to(m)

    st_folium(m, width=1100, height=500)

with tabs[2]:
    st.write("### Danh sach cac thiet bi trong mang")
    df_devices = load_data("SELECT device_id, description, latitude, longitude FROM devices")
    st.table(df_devices)

    st.write("### Du lieu telemetry moi nhat")
    df_latest = load_data("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 10")
    st.dataframe(df_latest)

time.sleep(10)
st.rerun()
