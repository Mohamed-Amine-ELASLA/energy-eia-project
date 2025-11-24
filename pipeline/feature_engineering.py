import pandas as pd
import numpy as np

# --- CONFIGURATION ---
INPUT_FILE = "data_processed/energy_dataset_master.parquet"
OUTPUT_FILE = "data_processed/energy_dataset_features.parquet"

def create_features():
    print("🛠️ Création des Features (Indices pour le ML)...")
    
    df = pd.read_parquet(INPUT_FILE)
    
    # 1. Features Temporelles (Cycliques)
    # Le modèle doit savoir si on est lundi ou dimanche, matin ou soir.
    df['hour'] = df['datetime_utc'].dt.hour
    df['day_of_week'] = df['datetime_utc'].dt.dayofweek # 0=Lundi, 6=Dimanche
    df['month'] = df['datetime_utc'].dt.month
    df['quarter'] = df['datetime_utc'].dt.quarter
    
    # Indicateur Week-end (Samedi ou Dimanche)
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # 2. Features de "Lag" (Décalage temporel)
    # L'info la plus puissante : la consommation d'il y a 24h (J-1) et 7 jours (J-7)
    print("   Calcul des lags (J-1, J-7)...")
    
    # Lag 24h : La conso à la même heure hier
    df['lag_24h'] = df['demand_mwh'].shift(24)
    
    # Lag 168h : La conso à la même heure la semaine dernière
    df['lag_168h'] = df['demand_mwh'].shift(168)
    
    # 3. Moyennes Mobiles (Rolling Windows)
    # La tendance des dernières 24h (pour lisser le bruit)
    # Note: On exclut la valeur actuelle pour éviter la fuite de données (closed='left' n'existe pas partout, donc on shift d'abord)
    print("   Calcul des moyennes mobiles...")
    df['rolling_mean_24h'] = df['demand_mwh'].shift(1).rolling(window=24).mean()
    
    # 4. Nettoyage des NaNs créés par le décalage
    # Les 7 premiers jours auront des valeurs vides à cause du lag_168h. On les supprime.
    original_len = len(df)
    df = df.dropna()
    lost_rows = original_len - len(df)
    print(f"   Lignes supprimées (démarrage) : {lost_rows}")
    
    # 5. Sauvegarde
    df.to_parquet(OUTPUT_FILE, index=False)
    print(f"✅ Dataset Enrichi sauvegardé : {OUTPUT_FILE}")
    print(f"   Nouvelles dimensions : {df.shape}")
    print("   Colonnes :", list(df.columns))

if __name__ == "__main__":
    create_features()