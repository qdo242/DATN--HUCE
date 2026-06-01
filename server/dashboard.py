import streamlit as st
import sqlite3
import pandas as pd
import folium
from streamlit_folium import st_folium
import time

st.set_page_config(page_title="Hệ thống giám sát Xi-Y", layout="wide")
DB_NAME = 'iot_security.db'

st.title("Hệ thống giám sát truyền tin bảo mật IoT (Xi -> Y)")

tabs = st.tabs(["Dữ liệu cảm biến khí", "Bản đồ Web (Leaflet)", "Nhật ký hệ thống"])

# --- TAB 1: TELEMETRY (Cảm biến khí) ---
with tabs[0]:
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 100", conn)
    conn.close()
    
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        latest = df.iloc[0]
        
        co2_val = (latest.get('heart_rate') or 0) * 10
        temp_val = latest.get('temperature') or 0.0
        humi_val = latest.get('humidity') or 0.0
        
        col1.metric("Khí CO2 (ppm)", f"{co2_val:.0f}") # Giả lập CO2
        col2.metric("Nhiệt độ (C)", f"{temp_val:.1f}")
        col3.metric("Độ ẩm (%)", f"{humi_val:.1f}")
        
        st.line_chart(df[['temperature', 'humidity']])
    else:
        st.info("Đang chờ dữ liệu từ thiết bị Y...")

# --- TAB 2: WEB MAP (LEAFLET + OSM) ---
with tabs[1]:
    st.write("### Bản đồ vị trí thiết bị Xi và Y")
    # Tọa độ mặc định (Hà Nội)
    m = folium.Map(location=[21.0045, 105.8433], zoom_start=15)
    
    # Thêm các Marker từ Database
    conn = sqlite3.connect(DB_NAME)
    devices = pd.read_sql_query("SELECT * FROM devices", conn)
    conn.close()
    
    for _, row in devices.iterrows():
        color = 'blue' if 'IOT_NODE' in row['device_id'] else 'red'
        icon = 'cloud' if color == 'blue' else 'user'
        folium.Marker(
            [row['latitude'], row['longitude']],
            popup=f"ID: {row['device_id']}<br>Desc: {row['description']}",
            tooltip=row['device_id'],
            icon=folium.Icon(color=color, icon=icon)
        ).add_to(m)
    
    st_folium(m, width=1200, height=500)

# --- TAB 3: LOGS ---
with tabs[2]:
    st.write("### Nhật ký truyền nhận dữ liệu")
    st.dataframe(df[['timestamp', 'device_id', 'status', 'error_msg']])

time.sleep(5)
st.rerun()
