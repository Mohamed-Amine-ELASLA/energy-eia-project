import pandas as pd
import os
import glob # Permet de lister des fichiers avec des wildcards (*)

# --- CONFIGURATION ---
INPUT_PATTERN = "data_raw/weather/weather_*.csv" # Prend tous les fichiers weather
OUTPUT_DIR = "data_processed/weather"

def process_weather():
    print("⚙️ Début du nettoyage Météo...")
    
    # 1. Lister tous les fichiers CSV météo
    files = glob.glob(INPUT_PATTERN)
    print(f"   Fichiers trouvés : {files}")
    
    all_data = []
    
    # 2. Boucle sur chaque ville
    for file in files:
        df_city = pd.read_csv(file)
        
        # Conversion Date (Crucial !)
        df_city['time'] = pd.to_datetime(df_city['time'])
        
        # Renommage pour uniformiser
        df_city = df_city.rename(columns={'time': 'datetime_utc'})
        
        all_data.append(df_city)
    
    # 3. Fusion verticale (On empile New York, Houston, LA l'un sous l'autre)
    df_final = pd.concat(all_data, ignore_index=True)
    
    print(f"   Total lignes fusionnées : {len(df_final)}")
    
    # 4. Partitionnement
    df_final['year'] = df_final['datetime_utc'].dt.year
    df_final['month'] = df_final['datetime_utc'].dt.month
    
    # 5. Sauvegarde Parquet
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f"💾 Sauvegarde dans {OUTPUT_DIR}...")
    df_final.to_parquet(
        OUTPUT_DIR,
        engine='pyarrow',
        compression='snappy',
        partition_cols=['year', 'month'],
        index=False
    )
    print("✅ Météo nettoyée et sauvegardée.")

if __name__ == "__main__":
    process_weather()