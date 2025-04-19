# 🧠 RL_Agent

This project implements a Reinforcement Learning (RL) agent with a FastAPI backend and a Streamlit-based dashboard for testing and visualization.

The agent simulates smart energy management in a house by selecting from **13 possible actions** to maintain comfortable temperature while optimizing energy cost.

## 🧠 About the RL Agent

The RL agent is designed to intelligently control the environment with actions like:

- Turn **ON/OFF Air Conditioner**
- Open/Close **windows**
- Adjust the **AC temperature** from 19°C to 31°C

It learns to take optimal actions based on the internal and external temperature states.

---

## 🚀 Approach 1 — Use the Deployed API on Azure (CI/CD)

The FastAPI backend is automatically deployed to **Azure Web Services** using GitHub Actions (CI/CD).

🔗 **Public Azure Link (API only)**:  
👉 [https://myrl-hpgxb5gaezembecs.canadacentral-01.azurewebsites.net](https://myrl-hpgxb5gaezembecs.canadacentral-01.azurewebsites.net)

📘 **Swagger Interface**:  
[https://myrl-hpgxb5gaezembecs.canadacentral-01.azurewebsites.net/docs](https://myrl-hpgxb5gaezembecs.canadacentral-01.azurewebsites.net/docs)

✅ **Dashboard (Streamlit) locally**:  
You can run the dashboard locally to interact with the deployed API:

```bash
streamlit run Dashboard.py
```

> `Dashboard.py` is already in the repo and communicates directly with the deployed API.

---

## 💻 Approach 2 — Run Everything Locally (API + Dashboard)

Clone the repo and run both the backend and the dashboard on your local machine.

### 🛠️ Setup

```bash
git clone https://github.com/yassineamr1/RL_Agent.git
cd RL_Agent
pip install -r requirements.txt
python main.py
```

API available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### ▶️ Run the Streamlit Dashboard

```bash
streamlit run Dashboard.py
```

---

## 🐳 Approach 3 — Use Docker

### 📦 Option 1: Pull from DockerHub

```bash
docker pull yassineamri/rl_agent
docker run -p 8000:8000 yassineamri/rl_agent
```

### 🛠️ Option 2: Build the Image from GitHub

```bash
git clone https://github.com/yassineamr1/RL_Agent.git
cd RL_Agent
docker build -t rl_agent .
docker run -p 8000:8000 rl_agent
```

Then run the dashboard locally as before:

```bash
streamlit run Dashboard.py
```

> The dashboard can talk to the API running inside the Docker container.

---

## 📁 Project Structure

```
RL_Agent/
├── Dashboard.py           ← Streamlit UI
├── training/              ← RL agent logic and training
├── main.py                ← FastAPI backend
├── requirements.txt
├── Dockerfile
└── README.md
```

