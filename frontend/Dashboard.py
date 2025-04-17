import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Smart AC Controller", layout="centered")

st.title("🏠 Smart AC Controller Dashboard")
st.markdown("Reinforcement Learning in Action ⚡")

# --- Auto-refresh toggle ---
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh every 10s", value=False)
if auto_refresh:
    time.sleep(10)
    st.experimental_rerun()

# --- Fetch data from backend ---
def fetch_data():
    try:
        response = requests.post("http://127.0.0.1:8000/get-action", json={"state": [0, 0, 0]})
        return response.json()
    except Exception as e:
        return {"error": str(e)}

data = fetch_data()

# --- UI ---
if "error" in data:
    st.error(data["error"])
else:
    # Info Cards
    col1, col2 = st.columns(2)
    col1.metric("🌡️ Indoor Temp", f"{data['indoor_temperature']} °C")
    col2.metric("☁️ Outdoor Temp", f"{data['outdoor_temperature']} °C")

    col3, col4 = st.columns(2)
    col3.metric("💧 Humidity", f"{data['humidity']}%")
    col4.metric("💡 Energy Saved", f"{round(data['energy_saved_percentage'], 1)}%")

    # --- Action Box with styled HTML ---
    action = data["action"]
    ac_status = "🟢 <span style='color:green;'>On</span>" if action["ac"] else "🔴 <span style='color:red;'>Off</span>"
    window_status = "🪟 Closed" if action["window"] == 0 else "🪟 Open"

    st.markdown(
        f"""
        <div style="padding: 1em; border-radius: 10px; background-color: #ff4500;">
            <h5>📅 <u>Action Taken</u></h5>
            <ul style="list-style-type: none; padding-left: 1em;">
                <li><strong>AC:</strong> {ac_status}</li>
                <li><strong>AC Temp:</strong> 🌡️ {action['ac_temp']}°C</li>
                <li><strong>Window:</strong> {window_status}</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- In-memory history (no CSV) ---
    if "history_df" not in st.session_state:
        st.session_state.history_df = pd.DataFrame(columns=[
            "timestamp", "indoor_temperature", "outdoor_temperature", "energy_saved_percentage"
        ])

    df = st.session_state.history_df

    # Append new row if not duplicate
    if str(data['timestamp']) not in df["timestamp"].astype(str).values:
        new_row = pd.DataFrame([{
            "timestamp": data["timestamp"],
            "indoor_temperature": data["indoor_temperature"],
            "outdoor_temperature": data["outdoor_temperature"],
            "energy_saved_percentage": data["energy_saved_percentage"]
        }])
        st.session_state.history_df = pd.concat([df, new_row], ignore_index=True)

    # Plot if enough data
    if len(st.session_state.history_df) > 1:
        df = st.session_state.history_df
        df["time"] = pd.to_datetime(df["timestamp"], unit="s")
        fig = px.line(
            df,
            x="time",
            y=["indoor_temperature", "outdoor_temperature", "energy_saved_percentage"],
            labels={"value": "Value", "variable": "Metric"},
            title="📊 Temperature & Energy Over Time"
        )
        st.plotly_chart(fig, use_container_width=True)
