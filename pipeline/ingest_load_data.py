import requests
import pandas as pd
import time
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
START_DATE = "2020-01-01T00" 
END_DATE = datetime.now().strftime("%Y-%m-%dT%H") 
OUTPUT_DIR = "data_raw"
OUTPUT_FILE = "us_load_latest.csv"
BASE_URL = "https://api.eia.gov/v2/electricity/rto/region-data/data/"

def get_eia_data(api_key, start, end):
    """
    Récupère les données de consommation US48 page par page.
    """
    all_data = []
    offset = 0
    length = 5000 # Max autorisé par appel
    
    print(f" Démarrage de l'extraction de {start} à {end}...")

    while True:
        params = {
            "api_key": api_key,
            "frequency": "hourly",
            "data[0]": "value",
            "facets[respondent][]": "US48",
            "facets[type][]": "D",
            "start": start,
            "end": end,
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "offset": offset,
            "length": length
        }

        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status() # Lève une erreur si le code n'est pas 200
            
            data = response.json()
            records = data['response']['data']
            
            if not records:
                print(" Fin des données reçues.")
                break
            
            all_data.extend(records)
            print(f" Récupéré {len(records)} lignes (Total: {len(all_data)})...")
            
            # Préparation pour la page suivante
            offset += length
            
            # Pause courte pour être gentil avec l'API (éviter le blocage)
            time.sleep(0.5)
            
        except Exception as e:
            print(f" Erreur lors de la requête : {e}")
            break

    return pd.DataFrame(all_data)

# --- MAIN ---
if __name__ == "__main__":
    # 1. Création du dossier si inexistant
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    # 2. Extraction
    df = get_eia_data(API_KEY, START_DATE, END_DATE)
    
    if not df.empty:
        # 3. Sauvegarde CSV Brut
        full_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
        df.to_csv(full_path, index=False)
        print(f"\n Succès ! Données sauvegardées dans : {full_path}")
        print(f" Dimension du dataset : {df.shape}")
        print("Aperçu :")
        print(df[['period', 'value']].head())
        print(df[['period', 'value']].tail())
    else:
        print(" Aucune donnée récupérée.")