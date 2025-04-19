# Utilise une image Python
FROM python:3.10-slim

# Créer un répertoire de travail
WORKDIR /app

# Copier les fichiers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Commande d'exécution (à adapter)
CMD ["python", "main.py"]
