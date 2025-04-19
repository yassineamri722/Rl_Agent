# 🧠 RL_Agent

Ce projet implémente un agent d’apprentissage par renforcement (RL) avec une API FastAPI et une interface Streamlit pour tester et visualiser les performances du modèle.

---

## 🚀 1ère Approche — Utiliser l'API déployée sur Azure

L’API FastAPI est automatiquement déployée sur Azure via GitHub Actions (CI/CD).

🔗 **Lien public Azure (API uniquement)** :  
👉 [https://myrl-hpgxb5gaezembecs.canadacentral-01.azurewebsites.net](https://myrl-hpgxb5gaezembecs.canadacentral-01.azurewebsites.net)

### 📘 Interface Swagger :
[https://myrl-hpgxb5gaezembecs.canadacentral-01.azurewebsites.net/docs](https://myrl-hpgxb5gaezembecs.canadacentral-01.azurewebsites.net/docs)

✅ **Dashboard Streamlit disponible localement** :  
Même si le frontend n’est pas déployé sur Azure, vous pouvez le lancer **en local** avec :

```bash
streamlit run Dashboard.py
```

📁 Le fichier `Dashboard.py` est déjà inclus dans le dépôt `RL_Agent`, vous n'avez rien à télécharger de plus.

> Le dashboard communique directement avec l'API Azure ou locale selon la configuration.

---

## 💻 2ème Approche — Exécuter localement (API + Dashboard)

Vous pouvez cloner le projet et lancer à la fois l’API FastAPI **et** le dashboard en local.

### 🔧 Étapes d’installation

```bash
git clone https://github.com/yassineamr1/RL_Agent.git
cd RL_Agent
pip install -r requirements.txt
python main.py
```

L’API sera disponible à : [http://localhost:8000/docs](http://localhost:8000/docs)

### ▶️ Lancer le Dashboard Streamlit

```bash
streamlit run Dashboard.py
```

> Le dashboard accède à l'API locale disponible sur `localhost:8000`.

---

## 🐳 3ème Approche — Utiliser Docker

Vous pouvez utiliser Docker pour exécuter l’API sans avoir à installer les dépendances Python.

### 📥 Option 1 : Utiliser l’image DockerHub

```bash
docker pull yassineamri/rl_agent
docker run -p 8000:8000 yassineamri/rl_agent
```

### 📥 Option 2 : Construire l’image depuis le repo GitHub

```bash
git clone https://github.com/yassineamr1/RL_Agent.git
cd RL_Agent
docker build -t rl_agent .
docker run -p 8000:8000 rl_agent
```

L’API FastAPI sera accessible ici : [http://localhost:8000/docs](http://localhost:8000/docs)

### ▶️ Lancer le Dashboard (toujours localement)

```bash
streamlit run Dashboard.py
```

> Le Dashboard reste exécuté en local mais peut pointer vers l'API en local (Docker) ou en ligne (Azure).

---

## 📂 Structure du projet

```
RL_Agent/
├── Dashboard.py           ← Interface utilisateur Streamlit
├── training/           ← Entraînement de l’agent RL
├── main.py             ← Backend API (FastAPI)
├── requirements.txt
├── Dockerfile
└── README.md
```
