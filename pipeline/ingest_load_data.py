import requests
import pandas as pd
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

# On définit les années qu'on veut récupérer
START_YEAR = 2020
CURRENT_YEAR = datetime.now().year

OUTPUT_DIR = "data_raw"
OUTPUT_FILE = "us_load_latest.csv"
BASE_URL = "https://api.eia.gov/v2/electricity/rto/region-data/data/"

def get_data_by_year(api_key, year):
    """
    Récupère une année complète de données.
    """
    all_year_data = []
    offset = 0
    length = 5000
    
    # Définition du début et fin de l'année demandée
    start_date = f"{year}-01-01T00"
    # Si c'est l'année en cours, on s'arrête à "maintenant", sinon fin d'année
    if year == CURRENT_YEAR:
        end_date = datetime.now().strftime("%Y-%m-%dT%H")
    else:
        end_date = f"{year}-12-31T23"

    print(f"Traitement de l'année {year} ({start_date} -> {end_date})...")

    while True:
        params = {
            "api_key": api_key,
            "frequency": "hourly",
            "data[0]": "value",
            "facets[respondent][]": "US48",
            "facets[type][]": "D",
            "start": start_date,
            "end": end_date,
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "offset": offset,
            "length": length
        }

        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            records = data.get('response', {}).get('data', [])
            
            if not records:
                break
            
            all_year_data.extend(records)
            
            # Si on a reçu moins que le max, c'est que c'est la dernière page de l'année
            if len(records) < length:
                break
                
            offset += length
            time.sleep(0.2) # Petite pause
            
        except Exception as e:
            print(f"Erreur pour l'année {year}: {e}")
            break
            
    return pd.DataFrame(all_year_data)

# --- MAIN ---
if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    full_df_list = []
    
    print(f"Démarrage de l'extraction par morceaux (Chunking)...")

    # BOUCLE SUR LES ANNÉES (2020 -> 2026)
    for year in range(START_YEAR, CURRENT_YEAR + 1):
        df_year = get_data_by_year(API_KEY, year)
        
        if not df_year.empty:
            full_df_list.append(df_year)
            print(f"Année {year} terminée : {len(df_year)} lignes récupérées.")
        else:
            print(f"Pas de données trouvées pour {year}.")

    # Fusion finale
    if full_df_list:
        final_df = pd.concat(full_df_list, ignore_index=True)
        
        # Nettoyage doublons éventuels
        final_df = final_df.drop_duplicates(subset=['period'])
        final_df = final_df.sort_values('period')

        full_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
        final_df.to_csv(full_path, index=False)
        
        print(f"\nExtraction terminée avec succès !")
        print(f"Fichier : {full_path}")
        print(f"Total lignes : {len(final_df)}")
        print("Dernières données :")
        print(final_df[['period', 'value']].tail())
    else:
        print("Aucune donnée au total.")