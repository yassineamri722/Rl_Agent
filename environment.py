import gymnasium as gym
import numpy as np
from gymnasium import spaces
import requests

def get_outdoor_weather(city="Tunis", api_key="YOUR_API_KEY"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()

        # Debug: Print the raw response data from the API
        print(f"API Response: {data}")

        outdoor_temp = data.get("main", {}).get("temp", 24.0)
        rain = data.get("weather", [{}])[0].get("main", "").lower() == "rain"
        humidity = data.get("main", {}).get("humidity", 50)

        # Debug: Print the parsed weather information
        print(f"Parsed Weather Data - Temp: {outdoor_temp}, Rain: {rain}, Humidity: {humidity}")

        return outdoor_temp, rain, humidity
    except Exception as e:
        print(f"Erreur récupération météo: {e}")
        return 24.0, False, 50  # Valeurs par défaut : temp=24°C, pas de pluie, humidité à 50%

class ACWindowEnv(gym.Env):
    def __init__(self):
        super(ACWindowEnv, self).__init__()

        self.actions = self._generate_actions()
        self.observation_space = spaces.Box(low=np.array([0.0, 0, 0]),
                                            high=np.array([40.0, 1, 1]), dtype=np.float32)
        self.action_space = spaces.Discrete(len(self.actions))

        self.api_key = "94f1097d9a5f5780b3198f97c7f2e3f6"
        self.outdoor_temp = None
        self.outdoor_rain = False
        self.outdoor_humidity = None
        self.last_action = None
        self.last_temp = None
        self.energy_used = 0  # Initialize energy used counter
        self.total_steps = 0  # Total number of steps

        self.reset()

    def _generate_actions(self):
        actions = [{"ac": 0, "ac_temp": None, "window": 0},
                   {"ac": 0, "ac_temp": None, "window": 1}]
        for t in range(19, 31):
            actions.append({"ac": 1, "ac_temp": t, "window": 0})
        return actions

    def reset(self, seed=None, options=None):
        self.state = np.array([np.random.uniform(0, 45), 0, 0], dtype=np.float32)
        self.steps = 0
        self.outdoor_temp = None
        self.outdoor_rain = False
        self.outdoor_humidity = None
        self.last_action = None
        self.last_temp = self.state[0]
        self.energy_used = 0  # Reset energy used
        self.total_steps = 0  # Reset total steps
        return self.state, {}

    def step(self, action_idx):
        action = self.actions[action_idx]
        temp, _, _ = self.state

        self.last_action = action
        self.last_temp = temp

        # Initialisation du pénalité de pluie à une valeur par défaut (0)
        rain_penalty = 0

        if action["ac"] == 1:
            temp += -0.5 * (temp - action["ac_temp"])
            energy_cost = 1
            self.energy_used += 1  # Increment energy used if AC is ON
        elif action["window"] == 1:
            self.outdoor_temp, self.outdoor_rain, self.outdoor_humidity = get_outdoor_weather("Tunis", self.api_key)
            # Debug: Check if weather data is retrieved correctly
            print(f"Weather Data - Temp: {self.outdoor_temp}, Rain: {self.outdoor_rain}, Humidity: {self.outdoor_humidity}")

            if self.outdoor_rain:
                rain_penalty = -1.0  # Pénalité si il pleut
            temp += 0.1 * (self.outdoor_temp - temp)
            energy_cost = 0
        else:
            temp += np.random.uniform(-0.1, 0.1)
            energy_cost = 0

        temp_reward = -abs(temp - 24)
        energy_penalty = -0.1 * energy_cost
        reward = temp_reward + energy_penalty + rain_penalty  # Assurez-vous que rain_penalty est toujours inclus

        self.state = np.array([temp, action["ac"], action["window"]], dtype=np.float32)
        self.steps += 1
        self.total_steps += 1  # Increment total steps at each step
        done = self.steps >= 50

        # After each step, calculate energy saved as percentage
        energy_saved = self.total_steps - self.energy_used
        percent_saved = (energy_saved / self.total_steps) * 100 if self.total_steps > 0 else 0

        print(f"Energy Used: {self.energy_used}")
        print(f"Energy Saved: {energy_saved} ({percent_saved:.2f}% saved)")

        self.render()  # ← Affichage automatique à chaque étape

        return self.state, reward, done, False, {}

    def render(self):
        temp_now = self.state[0]
        temp_diff = temp_now - self.last_temp

        # Action effectuée
        if self.last_action:
            if self.last_action["ac"] == 1:
                action_str = f"🧊 AC ON ({self.last_action['ac_temp']}°C)"
            elif self.last_action["window"] == 1:
                action_str = "🌬 Fenêtre ouverte"
            else:
                action_str = "⛔️ AC et fenêtre OFF"
        else:
            action_str = "⏳ Pas encore d'action"

        # Affichage des données météo pour s'assurer que l'API fonctionne
        print(f"\n--- État actuel ---")
        print(f"Température intérieure : {temp_now:.2f}°C")
        print(f"Température extérieure : {self.outdoor_temp:.2f}°C" if self.outdoor_temp is not None else "Température extérieure : Non disponible")
        print(f"Pluie extérieure : {'Oui' if self.outdoor_rain else 'Non'}")
        print(f"Humidité extérieure : {self.outdoor_humidity}%")

        print(f"Action choisie : {action_str}")
        print(f"Différence de température : {temp_diff:.2f}°C")
        print(f"Energy Used: {self.energy_used}")
        print(f"Energy Saved: {self.total_steps - self.energy_used} ({(self.total_steps - self.energy_used) / self.total_steps * 100:.2f}% saved)")
