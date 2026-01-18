import pandas as pd


# --- CONFIGURATION ---
LOAD_DIR = "data_processed/load"
WEATHER_DIR = "data_processed/weather"
OUTPUT_FILE = "data_processed/energy_dataset_master.parquet"

def merge_datasets():
    print("Démarrage de la fusion (Merge)...")
    
    # 1. Chargement des données Load (Parquet lit tous les dossiers d'un coup !)
    print("Chargement Consommation...")
    df_load = pd.read_parquet(LOAD_DIR)
    # On s'assure qu'on n'a pas de doublons temporels
    df_load = df_load.drop_duplicates(subset=['datetime_utc'])
    
    # 2. Chargement des données Météo
    print("Chargement Météo...")
    df_weather = pd.read_parquet(WEATHER_DIR)

    # --- FIX ANTI-DOUBLONS (AJOUTE CECI) ---
    # On s'assure qu'il n'y a pas deux fois la même ville à la même heure
    print("Suppression des doublons Météo...")
    df_weather = df_weather.drop_duplicates(subset=['datetime_utc', 'city'])
    # ---------------------------------------

    
    # 3. PIVOT de la météo (Transformation cruciale)
    # On passe de lignes (City) à des colonnes (temp_new_york, temp_houston...)
    print("   Pivot de la météo...")
    df_weather_pivot = df_weather.pivot(
        index='datetime_utc', 
        columns='city', 
        values='temperature_c'
    )
    
    # Renommer les colonnes pour faire propre (ex: new_york -> temp_new_york)
    df_weather_pivot.columns = [f"temp_{col}" for col in df_weather_pivot.columns]
    df_weather_pivot = df_weather_pivot.reset_index()
    
    # 4. MERGE (Jointure Gauche)
    # On garde toutes les dates de conso (Left), et on ajoute la météo en face
    print("Assemblage Load + Météo...")
    df_master = pd.merge(
        df_load, 
        df_weather_pivot, 
        on='datetime_utc', 
        how='left'
    )
    
    # 5. Nettoyage final
    # Tri par date
    df_master = df_master.sort_values('datetime_utc')
    
    # Vérification des trous (Nulls)
    missing_weather = df_master['temp_new_york'].isnull().sum()
    if missing_weather > 0:
        print(f"  Attention : Il manque la météo pour {missing_weather} heures.")
        # Interpolation linéaire (bouche les petits trous par la moyenne des voisins)
        numeric_cols = df_master.select_dtypes(include=['number']).columns
        df_master[numeric_cols] = df_master[numeric_cols].interpolate(method='linear')
        
    print(f"Dataset Final : {df_master.shape} (Lignes, Colonnes)")
    print(df_master.head())
    
    # 6. Sauvegarde Finale (Fichier unique pour le ML)
    df_master.to_parquet(OUTPUT_FILE, index=False)
    print(f"Fichier MAÎTRE sauvegardé : {OUTPUT_FILE}")

    csv_path = OUTPUT_FILE.replace(".parquet", ".csv")
    df_master.to_csv(csv_path, index=False)
    print(f" CSV Master généré pour Power BI : {csv_path}")


if __name__ == "__main__":
    merge_datasets()