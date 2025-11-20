import requests
import json
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

BASE_URL = "https://api.eia.gov/v2/electricity/rto/region-data/data/"

# 2. Paramètres de la requête (Ce qu'on demande au serveur)
params = {
    "api_key": API_KEY,
    "frequency": "hourly",           # Données heure par heure
    "data[0]": "value",              # On veut la colonne "value" (la consommation en MWh)
    "facets[respondent][]": "US48",  # On filtre sur les USA (Lower 48 states)
    "facets[type][]": "D",           # D = Demand (Consommation)
    "start": "2024-01-01T00",        # Juste pour tester, on commence début 2024
    "end": "2024-01-02T00",          # On prend juste 24h de données pour le test
    "sort[0][column]": "period",     # Trier par date
    "sort[0][direction]": "asc",     # Croissant
    "offset": 0,
    "length": 5000                   # Limite max par page
}

# 3. Envoi de la demande
print("📡 Connexion à l'API EIA...")
response = requests.get(BASE_URL, params=params)

# 4. Vérification
if response.status_code == 200:
    print("✅ Succès ! Connexion établie.")
    
    # Conversion de la réponse (JSON) en dictionnaire Python
    data_json = response.json()
    
    # Extraction des données utiles
    records = data_json['response']['data']
    
    # Affichage brut des 3 premiers résultats pour comprendre la structure
    print("\n🔍 Voici à quoi ressemble la donnée brute (JSON) :")
    print(json.dumps(records[:3], indent=4))
    
    # Petit bonus : mettre ça dans un DataFrame Pandas pour que ce soit lisible
    df = pd.DataFrame(records)
    print("\n📊 Aperçu sous forme de tableau :")
    print(df[['period', 'value', 'respondent-name', 'type-name']].head())
    
else:
    print(f"❌ Erreur {response.status_code}")
    print(response.text)
