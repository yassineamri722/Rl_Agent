import streamlit as st
import pandas as pd
import plotly.express as px
import asyncio
import websockets
import json
import threading
from queue import Queue
import requests
import time

st.set_page_config(page_title="Smart AC Controller", layout="centered")
st.title("🏠 Smart AC Controller Dashboard")
st.markdown("Real-time Reinforcement Learning Control ⚡")

# Configuration
INIT_API_URL = "https://myrl-hpgxb5gaezembecs.canadacentral-01.azurewebsites.net/init"
WEBSOCKET_URI = "wss://myrl-hpgxb5gaezembecs.canadacentral-01.azurewebsites.net/ws"

# Default initial state (customize as needed)
DEFAULT_STATE = [25.0, 0, 1]  # [temp, ac_status, window_status]

# Data queue for WebSocket messages
data_queue = Queue()

# --- Initialization ---
def initialize_rl_agent():
    try:
        response = requests.post(
            INIT_API_URL,
            json={"state": DEFAULT_STATE},
            timeout=5
        )
        if response.status_code == 200:
            st.success("RL Agent initialized successfully!")
            return True
        else:
            st.error(f"Initialization failed: {response.text}")
            return False
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return False

# --- WebSocket Client Thread ---
def websocket_listener():
    async def listen():
        try:
            async with websockets.connect(WEBSOCKET_URI) as websocket:
                while True:
                    message = await websocket.recv()
                    if message != "ping":  # Filter out keep-alive pings
                        try:
                            data = json.loads(message)
                            data_queue.put(data)
                        except json.JSONDecodeError:
                            pass
        except Exception as e:
            data_queue.put({"error": f"WebSocket error: {str(e)}"})
    
    asyncio.new_event_loop().run_until_complete(listen())

# --- Dashboard UI Components ---
def display_control_panel():
    with st.sidebar:
        st.subheader("Control Panel")
        global DEFAULT_STATE
        DEFAULT_STATE = [
            st.slider("Initial Temperature", 15.0, 35.0, 25.0, 0.5),
            st.selectbox("Initial AC State", [0, 1], format_func=lambda x: "OFF" if x == 0 else "ON"),
            st.selectbox("Initial Window State", [0, 1], format_func=lambda x: "CLOSED" if x == 0 else "OPEN")
        ]
        
        if st.button("🔄 Initialize RL Agent"):
            if initialize_rl_agent():
                if 'ws_thread' not in st.session_state:
                    st.session_state.ws_thread = threading.Thread(target=websocket_listener, daemon=True)
                    st.session_state.ws_thread.start()

def update_dashboard(data):
    if "error" in data:
        st.error(data["error"])
        return

    # Info Cards
    col1, col2 = st.columns(2)
    col1.metric("🌡️ Indoor Temp", f"{data['indoor_temperature']:.1f}°C", 
               delta=f"{data['indoor_temperature'] - data.get('prev_temp', data['indoor_temperature']):.1f}°C")
    col2.metric("☁️ Outdoor Temp", f"{data['outdoor_temperature']:.1f}°C")

    col3, col4 = st.columns(2)
    col3.metric("💧 Humidity", f"{data['humidity']}%")
    energy_color = "normal" if data['energy_saved_percentage'] < 50 else "inverse"
    col4.metric("💡 Energy Saved", f"{data['energy_saved_percentage']:.1f}%", 
               delta_color=energy_color)

    # Action Visualization
    action = data["action"]
    ac_status = (f"🟢 <span style='color:green;font-weight:bold;'>ON @ {action['ac_temp']}°C</span>" 
                 if action["ac"] else "🔴 <span style='color:red;'>OFF</span>")
    window_status = ("🪟 <span style='color:red;'>CLOSED</span>" 
                    if action["window"] == 0 else "🪟 <span style='color:green;'>OPEN</span>")
    reward_color = "green" if data["reward"] >= -0.1 else "orange" if data["reward"] >= -0.5 else "red"

    st.markdown(
        f"""
        <div style="padding: 1em; border-radius: 10px; background-color: #0000FF; margin: 1em 0;">
            <h5>🤖 <u>Agent Decision</u> (Reward: <span style='color:{reward_color};font-weight:bold;'>{data['reward']:.2f}</span>)</h5>
            <ul style="list-style-type: none; padding-left: 1em;">
                <li><strong>AC Status:</strong> {ac_status}</li>
                <li><strong>Window:</strong> {window_status}</li>
                <li><strong>Last Update:</strong> {pd.to_datetime(data['timestamp'], unit='s').strftime('%H:%M:%S')}</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    # History Tracking
    if "history" not in st.session_state:
        st.session_state.history = pd.DataFrame(columns=[
            "timestamp", "indoor_temp", "outdoor_temp", "energy_saved", "action", "reward"
        ])

    new_row = {
        "timestamp": pd.to_datetime(data["timestamp"], unit="s"),
        "indoor_temp": data["indoor_temperature"],
        "outdoor_temp": data["outdoor_temperature"],
        "energy_saved": data["energy_saved_percentage"],
        "action": f"AC{action['ac']}_WIN{action['window']}",
        "reward": data["reward"]
    }
    st.session_state.history = pd.concat([
        st.session_state.history, 
        pd.DataFrame([new_row])
    ], ignore_index=True)

    # Visualizations
    if len(st.session_state.history) > 1:
        tab1, tab2, tab3 = st.tabs(["📈 Temperature", "🔋 Energy", "📊 Rewards"])
        
        with tab1:
            fig_temp = px.line(
                st.session_state.history,
                x="timestamp",
                y=["indoor_temp", "outdoor_temp"],
                labels={"value": "Temperature (°C)", "variable": "Metric"},
                title="Temperature Trends"
            )
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with tab2:
            fig_energy = px.area(
                st.session_state.history,
                x="timestamp",
                y="energy_saved",
                labels={"energy_saved": "Energy Saved (%)"},
                title="Energy Efficiency"
            )
            st.plotly_chart(fig_energy, use_container_width=True)
            
        with tab3:
            fig_rewards = px.bar(
                st.session_state.history,
                x="timestamp",
                y="reward",
                color="reward",
                color_continuous_scale="RdYlGn",
                labels={"reward": "Reward Value"},
                title="Action Rewards Over Time"
            )
            st.plotly_chart(fig_rewards, use_container_width=True)

# --- Main Application ---
def main():
    display_control_panel()
    
    if 'ws_thread' not in st.session_state:
        st.info("Click 'Initialize RL Agent' to start")
    else:
        placeholder = st.empty()
        
        while True:
            if not data_queue.empty():
                latest_data = data_queue.get()
                
                # Store previous temp for delta calculation
                if "history" in st.session_state and not st.session_state.history.empty:
                    latest_data["prev_temp"] = st.session_state.history["indoor_temp"].iloc[-1]
                
                with placeholder.container():
                    update_dashboard(latest_data)
            
            time.sleep(0.5)  # Smooth refresh rate

if __name__ == "__main__":
    main()