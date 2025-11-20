import requests
import pandas as pd
import os
import time

# --- CONFIGURATION ---
OUTPUT_DIR = "data_raw/weather"
START_DATE = "2022-01-01"
END_DATE = "2024-01-01"

# Coordonnées GPS des villes stratégiques
LOCATIONS = {
    "new_york": {"lat": 40.71, "lon": -74.01},
    "houston":  {"lat": 29.76, "lon": -95.36},
    "los_angeles": {"lat": 34.05, "lon": -118.24}
}

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

def get_weather_data():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f"🌤️ Démarrage de l'extraction météo ({START_DATE} au {END_DATE})...")

    for city, coords in LOCATIONS.items():
        print(f"   📍 Traitement de {city}...")
        
        # Paramètres de l'API Open-Meteo
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "start_date": START_DATE,
            "end_date": END_DATE,
            "hourly": "temperature_2m", # On veut la température à 2m du sol
            "timezone": "UTC"           # TRES IMPORTANT : On reste en UTC comme l'EIA
        }
        
        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            # L'API renvoie une structure un peu complexe, on simplifie :
            hourly_data = {
                "time": data["hourly"]["time"],
                "temperature_c": data["hourly"]["temperature_2m"]
            }
            
            df = pd.DataFrame(hourly_data)
            
            # On ajoute une colonne pour se rappeler de quelle ville il s'agit
            df['city'] = city
            
            # Sauvegarde CSV Brut
            filename = f"{OUTPUT_DIR}/weather_{city}.csv"
            df.to_csv(filename, index=False)
            print(f"      ✅ Sauvegardé : {filename} ({len(df)} lignes)")
            
            # Petite pause
            time.sleep(1)
            
        except Exception as e:
            print(f"      ❌ Erreur pour {city}: {e}")

    print("\n🏁 Extraction météo terminée.")

if __name__ == "__main__":
    get_weather_data()