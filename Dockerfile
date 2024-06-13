# Utiliser une image de base officielle Python avec une version spécifique
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier des dépendances et installer les dépendances
COPY requirements.txt .
# Supprimer la mise à jour de pip pour éviter les problèmes liés aux threads
# RUN pip install --upgrade pip
# Installer les dépendances sans utiliser la barre de progression pour minimiser l'utilisation des ressources
RUN pip install --no-cache-dir --progress-bar off -r requirements.txt

# Copier les fichiers du script et de configuration dans le conteneur
COPY clotheapp.py .
COPY config.json .

# Définir la commande pour exécuter l'application
CMD ["python", "./clotheapp.py"]
