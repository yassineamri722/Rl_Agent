from fastapi import FastAPI
from pydantic import BaseModel
import torch
import threading
from contextlib import asynccontextmanager
from environment import ACWindowEnv
from model import DQN
from rl import perform_rl_action
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run RL logic in a separate thread when the app starts
    rl_thread = threading.Thread(target=perform_rl_action)
    rl_thread.daemon = True
    rl_thread.start()
    yield  # App is running

app = FastAPI(lifespan=lifespan)

# CORS config (adjust allowed origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment and model
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
        state_tensor = torch.FloatTensor(np.array([request.state]))
        with torch.no_grad():
            q_values = model(state_tensor)
            action_index = torch.argmax(q_values).item()

        # Get action description from action index
        action = env.actions[action_index]

        return {
            "action": action,
            "message": "Action computed successfully."
        }

    except Exception as e:
        return {"error": f"Failed to compute action: {str(e)}"}

# Entry point for Azure
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
