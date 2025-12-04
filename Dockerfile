# 1. Image de base Python 3.11
FROM python:3.11-slim

# 2. Installation de uv (On copie le binaire officiel, c'est le plus rapide)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Dossier de travail
WORKDIR /app

# 4. Copie des dépendances
COPY requirements.txt .

# 5. Installation avec uv
# --system : Installe dans le Python global du conteneur (pas besoin de venv dans Docker)
# --no-cache : Garde l'image légère
RUN uv pip install --system --no-cache -r requirements.txt

# 6. Copie du code pipeline
COPY pipeline/ ./pipeline/

# 7. Création des dossiers de données
RUN mkdir -p data_raw data_processed

# 8. Commande par défaut
CMD ["python", "--version"]