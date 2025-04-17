from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import json
import time
from environment import ACWindowEnv
from model import DQN
from fastapi.middleware.cors import CORSMiddleware
from rl import perform_rl_action  # Import the RL function
import torch
import threading
from contextlib import asynccontextmanager

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run RL logic in a separate thread when the app starts
    rl_thread = threading.Thread(target=perform_rl_action)
    rl_thread.daemon = True
    rl_thread.start()
    
    yield  # The app is running
    
    # No teardown actions needed (if needed, add them after yield)

app = FastAPI(lifespan=lifespan)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment and model (optional if not used in this file)
env = ACWindowEnv()
model = DQN(3, 14)
model.load_state_dict(torch.load("dqn_model.pth"))
model.eval()

# Request model
class StateRequest(BaseModel):
    state: list

@app.get("/")
def read_root():
    return {"message": "AC Window Controller API is running!"}

@app.post("/get-action")
def get_action(request: StateRequest):
    try:
        with open("latest_action.json", "r") as f:
            data = json.load(f)

        # Check freshness
        timestamp = data.get("timestamp", 0)
        if time.time() - timestamp > 60:
            return {"error": "The action data is outdated, please wait for the RL model to update it."}
        
        return data

    except FileNotFoundError:
        return {"error": "RL model has not generated an action yet."}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

# For running locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
