import streamlit as st
import sqlite3
import pandas as pd
import folium
from streamlit_folium import st_folium
import time
import os

st.set_page_config(page_title="Dashboard Giam sat Xi-Y", layout="wide")
DB_NAME = os.path.join(os.path.dirname(__file__), '..', 'iot_security.db')

st.title("He thong quan ly va giam sat IoT (Xi_01 + Xi_02 -> Y -> Server)")

tabs = st.tabs(["Bieu do cam bien", "Ban do Web (Leaflet)", "Du lieu thiet bi", "Hieu nang"])

def load_data(query):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

with tabs[0]:
    df_telemetry = load_data("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 50")
    if not df_telemetry.empty:
        latest = df_telemetry.iloc[0]
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

        col1.metric("Nhiet do (C)", f"{latest.get('temperature') or 0:.1f}")
        col2.metric("Do am (%)", f"{latest.get('humidity') or 0:.1f}")
        col3.metric("Ap suat (hPa)", f"{latest.get('pressure') or 0:.0f}")
        col4.metric("Nhip tim (bpm)", f"{latest.get('heart_rate') or 0:.0f}")
        col5.metric("SpO2 (%)", f"{latest.get('spo2') or 0:.0f}")
        col6.metric("CO2 (ppm)", f"{latest.get('co2') or 0:.0f}")
        col7.metric("CO/NH3", f"{latest.get('co') or 0:.1f}/{latest.get('nh3') or 0:.1f}")

        st.write("### Dien bien cac chi so moi truong")
        avail = [c for c in ['temperature', 'humidity', 'pressure', 'heart_rate', 'spo2', 'co2', 'co', 'nh3'] if c in df_telemetry.columns]
        if avail:
            chart_data = df_telemetry.set_index('timestamp')[avail]
            st.line_chart(chart_data)
        else:
            st.warning("Khong tim thay du lieu")
    else:
        st.info("Dang cho du lieu tu cac thiet bi Xi...")

with tabs[1]:
    st.write("### Vi tri thuc te cua thiet bi Xi va Y tren ban do")
    m = folium.Map(location=[21.8449, 104.0975], zoom_start=15)

    df_map = load_data("""
        SELECT t.device_id, t.latitude, t.longitude, d.description
        FROM telemetry t
        JOIN devices d ON t.device_id = d.device_id
        WHERE t.timestamp = (SELECT MAX(t2.timestamp) FROM telemetry t2 WHERE t2.device_id = t.device_id)
    """)

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
    df_devices = load_data("SELECT DISTINCT t.device_id, d.description, t.latitude, t.longitude FROM telemetry t LEFT JOIN devices d ON t.device_id = d.device_id ORDER BY t.timestamp DESC")
    st.table(df_devices)

    st.write("### Du lieu telemetry moi nhat")
    df_latest = load_data("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 10")
    st.dataframe(df_latest)

    st.write("### GPS tracking (toa do moi nhat)")
    df_gps = load_data("SELECT device_id, latitude, longitude, altitude, satellites, timestamp FROM telemetry WHERE latitude != 0 ORDER BY timestamp DESC LIMIT 5")
    if not df_gps.empty:
        st.dataframe(df_gps)

with tabs[3]:
    st.write("### Hieu nang xu ly (benchmark)")
    df_bench = load_data("SELECT * FROM benchmark ORDER BY id DESC LIMIT 50")
    if not df_bench.empty:
        st.dataframe(df_bench[['device_id', 'decrypt_ms', 'seq_ms', 'log_ms', 'total_ms', 'status', 'timestamp']])

        st.write("#### Thong ke hieu nang theo thiet bi")
        stats = df_bench.groupby('device_id').agg(
            tong_so_lan=('id', 'count'),
            decrypt_tb=('decrypt_ms', 'mean'),
            seq_tb=('seq_ms', 'mean'),
            log_tb=('log_ms', 'mean'),
            total_tb=('total_ms', 'mean'),
            total_max=('total_ms', 'max')
        ).round(1)
        st.dataframe(stats)

        st.write("#### Bieu do thoi gian xu ly (30 request gan nhat)")
        chart = df_bench.head(30).set_index('id')[['decrypt_ms', 'seq_ms', 'log_ms', 'total_ms']]
        st.line_chart(chart)

        st.write("#### Ti le thanh cong / that bai")
        suc_rate = df_bench['status'].value_counts()
        st.bar_chart(suc_rate)
    else:
        st.info("Dang cho du lieu benchmark tu server...")

time.sleep(10)
st.rerun()
