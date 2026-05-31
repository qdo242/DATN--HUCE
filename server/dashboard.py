import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import time

st.set_page_config(page_title="Giam sat An ninh IoT - LilyGO", layout="wide")
DB_NAME = 'iot_security.db'

def load_data(table):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(f"SELECT * FROM {table} ORDER BY timestamp DESC", conn)
    conn.close()
    return df

st.title("He thong Quan tri An ninh IoT - 3 Thiet bi LilyGO")

tabs = st.tabs(["Real-time Telemetry", "Security Logs", "Device Map", "Device Management"])

# --- TAB 1: TELEMETRY ---
with tabs[0]:
    df = load_data("telemetry")
    safe_df = df[df['status'] == 'An toan'].copy()
    
    col1, col2, col3 = st.columns(3)
    if not safe_df.empty:
        # Ep kieu du lieu sang dang so de tranh loi Plotly
        numeric_cols = ['heart_rate', 'temperature', 'humidity', 'pressure', 'spo2', 'latency']
        for col in numeric_cols:
            if col in safe_df.columns:
                safe_df[col] = pd.to_numeric(safe_df[col], errors='coerce')

        latest = safe_df.iloc[0]
        col1.metric("Latest Heart Rate", f"{latest['heart_rate'] or 0} bpm")
        col2.metric("Latest Temp", f"{latest['temperature'] or 0} C")
        col3.metric("Latest Pressure", f"{latest['pressure'] or 0} hPa")
        
        st.write("### Dien bien chi so sinh trac hoc & Moi truong")
        # Chi ve bieu do neu co du lieu hop le
        fig_cols = [c for c in ['heart_rate', 'temperature', 'humidity', 'spo2'] if c in safe_df.columns and not safe_df[c].isnull().all()]
        if fig_cols:
            fig = px.line(safe_df.head(50), x='timestamp', y=fig_cols, 
                          title="Data History (Safe Packets Only)")
            st.plotly_chart(fig, key="sensor_line_chart", width='stretch')
        else:
            st.info("Dang cho du lieu cam bien hop le...")
    else:
        st.info("Chua co du lieu an toan.")

# --- TAB 2: SECURITY ---
with tabs[1]:
    df_attacks = load_data("attack_logs")
    st.write("### Nhat ky tan cong he thong")
    st.dataframe(df_attacks, use_container_width=True)
    
    if not df_attacks.empty:
        fig_pie = px.pie(df_attacks, names='attack_type', title="Phan loai cac kieu tan cong")
        st.plotly_chart(fig_pie)

# --- TAB 3: MAP ---
with tabs[2]:
    st.write("### Ban do vi tri thiet bi")
    df_devs = load_data("devices")
    if not df_devs.empty:
        map_df = df_devs[['latitude', 'longitude', 'device_id', 'status']]
        map_df.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
        st.map(map_df)

# --- TAB 4: MANAGEMENT ---
with tabs[3]:
    st.write("### Danh sach thiet bi he thong")
    st.table(df_devs[['device_id', 'status', 'description']])

time.sleep(2)
st.rerun()
