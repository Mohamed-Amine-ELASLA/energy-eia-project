import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import joblib 
from datetime import timedelta


# --- CONFIGURATION ---
INPUT_FILE = "data_processed/energy_dataset_features.parquet"
MODEL_PATH = "pipeline/model_xgboost.pkl"


def train_forecasting_model():
    print("Chargement des données...")
    df = pd.read_parquet(INPUT_FILE)

    # Conversion date si nécessaire
    df['datetime_utc'] = pd.to_datetime(df['datetime_utc'])

    # --- SPLIT DYNAMIQUE ---
    # On définit la date de coupure : "La date max des données MOINS 3 mois"
    max_date = df['datetime_utc'].max()
    cutoff_date = max_date - pd.DateOffset(months=3)
    
    print(f"Données disponibles jusqu'au : {max_date}")
    print(f"Découpage Train/Test automatique à la date : {cutoff_date}")
    
    # On définit nos variables
    target = 'demand_mwh' # Ce qu'on veut prédire
    
    # On enlève la target et les colonnes de dates (la machine ne comprend pas "2023-01-01")
    # On garde toutes les features numériques créées
    features = [col for col in df.columns if col not in ['datetime_utc', 'demand_mwh']]
    
    print(f"Features utilisées ({len(features)}) : {features}")
    
    # 1. SPLIT TRAIN / TEST (Chronologique)
    train = df[df['datetime_utc'] < cutoff_date].copy()
    test = df[df['datetime_utc'] >= cutoff_date].copy()

    
    print(f"Train set : {train.shape[0]} heures")
    print(f"Test set  : {test.shape[0]} heures")
    
    X_train, y_train = train[features], train[target]
    X_test, y_test = test[features], test[target]
    
    # 2. ENTRAINEMENT (XGBoost)
    print(" Entraînement du modèle XGBoost...")
    model = xgb.XGBRegressor(
        n_estimators=1000,    # Nombre d'arbres
        learning_rate=0.05,   # Vitesse d'apprentissage (plus petit = plus précis mais plus lent)
        max_depth=5,          # Profondeur des arbres
        early_stopping_rounds=50, # Arrête si ça ne s'améliore plus
        n_jobs=-1             # Utilise tous les coeurs du processeur
    )
    
    # On lui donne le test set pour qu'il surveille la qualité pendant l'entraînement (eval_set)
    model.fit(
        X_train, y_train,
        eval_set=[(X_train, y_train), (X_test, y_test)],
        verbose=100 # Affiche le progrès toutes les 100 itérations
    )
    
    # 3. PREDICTION & EVALUATION
    print(" Prédictions sur le Test Set...")
    predictions = model.predict(X_test)
    
    # Métriques
    mae = mean_absolute_error(y_test, predictions)
    mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100
    
    print("\n" + "="*30)
    print(" RÉSULTATS DU MODÈLE")
    print("="*30)
    print(f"   MAE (Erreur Moyenne Absolue) : {mae:.2f} MWh")
    print(f"   MAPE (Erreur Pourcentage)    : {mape:.2f} %")
    print("="*30)
    
    if mape < 5:
        print(" EXCELLENT RÉSULTAT (< 5%) !")
    elif mape < 10:
        print(" Bon résultat (< 10%).")
    else:
        print("Résultat moyen.")

    # 4. Feature Importance (Qu'est-ce qui a le plus compté ?)
    importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n Top 5 Features les plus importantes :")
    print(importance.head(5))
    
    # 5. Sauvegarde
    joblib.dump(model, MODEL_PATH)
    print(f"\n Modèle sauvegardé sous : {MODEL_PATH}")

    # Petit bonus : Ajout des prédictions dans le DataFrame test pour analyse future
    test['prediction'] = predictions
    test.to_csv("data_processed/test_predictions.csv", index=False)

if __name__ == "__main__":
    train_forecasting_model()