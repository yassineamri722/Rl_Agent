import time
import torch
from environment import ACWindowEnv
from environment import get_outdoor_weather
from model import DQN

# Initialize environment and model
env = ACWindowEnv()
model = DQN(3, 14)
model.load_state_dict(torch.load("dqn_model.pth"))
model.eval()

# Define a function to perform RL actions
def perform_rl_action():
    # Initialize state
    state = env.reset()[0]

    while True:
        # Convert the state to a tensor
        state_tensor = torch.tensor([state], dtype=torch.float32)

        # Use the model to predict the action to take
        with torch.no_grad():
            q_values = model(state_tensor)
            action_idx = torch.argmax(q_values).item()

        # Perform the action in the environment
        next_state, reward, done, _, _ = env.step(action_idx)

        # Print chosen action
        print(f"\n--- Chosen Action ---")
        print(f"Action: {env.actions[action_idx]}")

        # Print the reward obtained
        print(f"Reward obtained: {reward}")

        # Fetch outdoor weather data
        env.outdoor_temp, env.outdoor_rain, env.outdoor_humidity = get_outdoor_weather(city="Tunis", api_key="94f1097d9a5f5780b3198f97c7f2e3f6")
        print(f"Outdoor temperature fetched: {env.outdoor_temp:.2f}°C")
        print(f"Outdoor rain: {'Yes' if env.outdoor_rain else 'No'}")
        print(f"Outdoor humidity: {env.outdoor_humidity}%")

        # Print current state
        temp_now = next_state[0]
        outdoor_temp = env.outdoor_temp
        outdoor_rain = env.outdoor_rain

        print(f"\n--- Current State ---")
        print(f"Indoor temperature: {temp_now:.2f}°C")
        print(f"Outdoor temperature: {outdoor_temp:.2f}°C" if outdoor_temp is not None else "Outdoor temperature: Not available")
        print(f"Outdoor rain: {'Yes' if outdoor_rain else 'No'}")

        # Update the state
        state = next_state

        # Wait for 1 minute before repeating the action
        time.sleep(60)
