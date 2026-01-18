import pandas as pd
import requests
import joblib
from datetime import datetime, timedelta
import numpy as np

# --- CONFIG ---
MODEL_PATH = "pipeline/model_xgboost.pkl"
HISTORY_FILE = "data_processed/energy_dataset_master.parquet"
OUTPUT_FILE = "data_processed/future_predictions.csv"

# Coordonnées (les mêmes que d'habitude)
LOCATIONS = {
    "new_york": {"lat": 40.71, "lon": -74.01},
    "houston":  {"lat": 29.76, "lon": -95.36},
    "los_angeles": {"lat": 34.05, "lon": -118.24}
}

def get_future_weather():
    """Récupère les 7 jours de prévision météo"""
    print("Récupération des prévisions météo J+7...")
    future_weather = []
    
    for city, coords in LOCATIONS.items():
        # API Forecast (différente de Archive)
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "hourly": "temperature_2m",
            "timezone": "UTC",
            "forecast_days": 7
        }
        r = requests.get(url, params=params)
        data = r.json()
        
        df = pd.DataFrame({
            "datetime_utc": pd.to_datetime(data["hourly"]["time"]),
            "temp": data["hourly"]["temperature_2m"],
            "city": city
        })
        future_weather.append(df)
    
    # Fusion et Pivot
    df_concat = pd.concat(future_weather)
    df_pivot = df_concat.pivot(index="datetime_utc", columns="city", values="temp").reset_index()
    df_pivot.columns = ["datetime_utc", "temp_houston", "temp_los_angeles", "temp_new_york"]
    return df_pivot

def make_future_predictions():
    # 1. Charger le modèle
    print("Chargement du modèle...")
    model = joblib.load(MODEL_PATH)
    
    # 2. Préparer le futur (Dates + Météo)
    df_future = get_future_weather()
    
    # 3. Récupérer l'historique pour simuler les Lags
    # On va chercher les données d'il y a 7 jours exactement pour remplir les colonnes manquantes
    print("Récupération de l'historique récent...")
    df_history = pd.read_parquet(HISTORY_FILE)
    df_history['datetime_utc'] = pd.to_datetime(df_history['datetime_utc'])
    
    # On crée une colonne de jointure : "Date Future" - 7 jours = "Date Passée"
    df_future['join_date'] = df_future['datetime_utc'] - timedelta(days=7)
    
    # On joint pour récupérer la consommation de la semaine dernière
    df_merged = pd.merge(
        df_future,
        df_history[['datetime_utc', 'demand_mwh']],
        left_on='join_date',
        right_on='datetime_utc',
        how='left',
        suffixes=('', '_past')
    )
    
    # 4. Feature Engineering (Le même que pour l'entraînement)
    print("Création des features...")
    df = df_merged.copy()
    
    # Dates
    df['hour'] = df['datetime_utc'].dt.hour
    df['day_of_week'] = df['datetime_utc'].dt.dayofweek
    df['month'] = df['datetime_utc'].dt.month
    df['quarter'] = df['datetime_utc'].dt.quarter
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['year'] = df['datetime_utc'].dt.year # Nécessaire si le modèle l'utilise
    
    # Lags (Astuce : On utilise la conso de la semaine dernière comme proxy)
    # Pour le futur, on suppose que lag_24h (hier) ressemble à lag_168h (semaine dernière)
    # C'est une approximation nécessaire pour éviter une boucle récursive complexe
    df['lag_24h'] = df['demand_mwh'] 
    df['lag_168h'] = df['demand_mwh']
    df['rolling_mean_24h'] = df['demand_mwh'] # Approximation
    
    # Sélection des colonnes dans le bon ordre pour le modèle
    # (Attention : Il faut exclure les colonnes qui ne sont pas des features)
    features_needed = model.get_booster().feature_names
    
    # Vérification et remplissage des NaNs (au cas où il manque de l'historique)
    X_future = df[features_needed].fillna(method='ffill').fillna(0)
    
    # 5. Prédiction
    print("Prédiction J+7...")
    predictions = model.predict(X_future)
    
    # 6. Sauvegarde
    result = df[['datetime_utc']].copy()
    result['prediction'] = predictions
    result['type'] = 'Forecast J+7' # Pour Power BI
    
    result.to_csv(OUTPUT_FILE, index=False)
    print(f"Prévisions sauvegardées : {OUTPUT_FILE}")

if __name__ == "__main__":
    make_future_predictions()