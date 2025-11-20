import pandas as pd
import os

# --- CONFIGURATION ---
INPUT_FILE = "data_raw/us_load_2022_2023.csv"
OUTPUT_DIR = "data_processed/load"  # On sépare par "sujet" (ici load)

def process_data():
    print("⚙️ Début du nettoyage...")
    
    # 1. Lecture du CSV Brut
    # dtype={'value': float} force la colonne value à être numérique dès la lecture
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier {INPUT_FILE} n'existe pas.")
        return

    print(f"   Lecture de {len(df)} lignes.")

    # 2. Conversion des Types (Typing)
    # On transforme la string "2022-01-01T00" en vrai objet datetime
    df['period'] = pd.to_datetime(df['period'])
    
    # 3. Renommage et Sélection
    # On garde uniquement ce qui nous intéresse et on donne des noms clairs
    df = df.rename(columns={
        'period': 'datetime_utc',
        'value': 'demand_mwh'
    })
    
    # On sélectionne juste les colonnes utiles (on vire respondent-name, etc.)
    keep_cols = ['datetime_utc', 'demand_mwh']
    df = df[keep_cols]

    # 4. Gestion des valeurs manquantes
    # Si l'API a envoyé des trous, on peut décider de les supprimer ou de les remplir
    missing = df['demand_mwh'].isnull().sum()
    if missing > 0:
        print(f"⚠️ Attention : {missing} valeurs manquantes détectées.")
        # Pour l'instant, on supprime les lignes vides (on verra l'imputation plus tard)
        df = df.dropna(subset=['demand_mwh'])

    # 5. Création des colonnes de Partitionnement
    # Pour ranger les fichiers comme dans une bibliothèque
    df['year'] = df['datetime_utc'].dt.year
    df['month'] = df['datetime_utc'].dt.month

    # 6. Sauvegarde en Parquet Partitionné
    # Cela va créer une structure de dossiers : data_processed/load/year=2022/month=1/
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"💾 Sauvegarde en Parquet dans {OUTPUT_DIR}...")
    
    df.to_parquet(
        OUTPUT_DIR,
        engine='pyarrow',
        compression='snappy',  # Compresse le fichier pour gagner de la place
        partition_cols=['year', 'month'], # La magie opère ici
        index=False
    )
    
    print("✅ Terminé ! Structure de fichiers créée.")

if __name__ == "__main__":
    process_data()