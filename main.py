import time
import threading
import asyncio
import torch
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from environment import ACWindowEnv, get_outdoor_weather
from model import DQN
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Shared state
latest_action_data = None
clients = set()
data_lock = threading.Lock()
initial_state = None

# Initialize env & model
env = ACWindowEnv()
model = DQN(3, 14)
model.load_state_dict(torch.load("dqn_model.pth"))
model.eval()

# FastAPI app
app = FastAPI()

# CORS (allow frontend to connect to the backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://myrl-hpgxb5gaezembecs.canadacentral-01.azurewebsites.net"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data model for init state
class StateRequest(BaseModel):
    state: list

@app.post("/init")
def init_rl(request: StateRequest):
    global initial_state
    initial_state = request.state

    # Start RL actions in a separate thread
    rl_thread = threading.Thread(target=perform_rl_action, daemon=True)
    rl_thread.start()

    return {"message": "RL started with initial state."}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        logging.info("WebSocket connection established.")
        await websocket.accept()
        clients.add(websocket)
        last_ping = time.time()
        
        while True:
            # Check if we need to send a ping (every 30 seconds)
            if time.time() - last_ping > 30:
                await websocket.send_text("ping")
                last_ping = time.time()
            
            # Send data if available
            with data_lock:
                if latest_action_data:
                    # Convert numpy types to native Python types
                    serializable_data = {
                        k: float(v) if isinstance(v, (np.float32, np.float64)) else 
                           int(v) if isinstance(v, (np.int32, np.int64)) else
                           bool(v) if isinstance(v, np.bool_) else
                           v for k, v in latest_action_data.items()
                    }
                    logging.info(f"Sending data: {serializable_data}")
                    await websocket.send_json(serializable_data)
            
            await asyncio.sleep(1)  # Check every second

    except WebSocketDisconnect:
        logging.info("WebSocket disconnected.")
        clients.remove(websocket)
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        clients.remove(websocket)

def perform_rl_action():
    global latest_action_data

    # If initial state provided, use it, else reset the environment
    if initial_state:
        state = initial_state
    else:
        state = env.reset()[0]

    while True:
        state_tensor = torch.tensor([state], dtype=torch.float32)

        with torch.no_grad():
            q_values = model(state_tensor)
            action_idx = torch.argmax(q_values).item()

        next_state, reward, done, _, _ = env.step(action_idx)

        # Fetch outdoor weather
        weather = get_outdoor_weather(city="Tunis", api_key="94f1097d9a5f5780b3198f97c7f2e3f6")
        env.outdoor_temp, env.outdoor_rain, env.outdoor_humidity = weather

        # Update the shared state with latest action data
        with data_lock:
            latest_action_data = {
                "action": env.actions[action_idx],
                "reward": float(reward),  # Convert to native Python float
                "indoor_temperature": round(float(next_state[0]), 2),
                "outdoor_temperature": round(float(env.outdoor_temp), 2) if env.outdoor_temp else None,
                "rain": bool(env.outdoor_rain),  # Convert to native Python bool
                "humidity": int(env.outdoor_humidity),  # Convert to native Python int
                "energy_saved_percentage": 0 if env.actions[action_idx]["ac"] == 1 else 100,
                "timestamp": float(time.time())  # Convert to native Python float
            }
            logging.info(f"Action: {env.actions[action_idx]}, Reward: {reward}")

        state = next_state
        time.sleep(60)  # Adjust sleep time if faster updates are required for testing

@app.get("/")
def read_root():
    return {"message": "AC Window Controller API with WebSocket is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, ws_ping_interval=30, ws_ping_timeout=30)