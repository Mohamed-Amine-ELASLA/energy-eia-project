from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# 1. Configuration par défaut
# Si une tâche échoue, on réessaie 1 fois après 5 minutes
default_args = {
    'owner': 'amine',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 2. Définition du DAG
with DAG(
    'energy_forecast_production',        # Le nom que tu verras dans l'interface
    default_args=default_args,
    description='Pipeline ETL + ML quotidien pour la consommation US',
    schedule_interval='0 8 * * *',       # Cron : Tous les jours à 08h00 du matin
    start_date=datetime(2023, 11, 1),    # Date de début (fictive pour l'instant)
    catchup=False,                       # False = Ne pas relancer les jours passés manqués
    tags=['energy', 'xgboost', 'etl'],
) as dag:

    # --- TÂCHE 1 : Ingestion (En parallèle) ---
    # On utilise BashOperator car tes scripts sont déjà faits pour être lancés en ligne de commande.
    # Note le chemin : /opt/airflow/pipeline/... c'est le chemin DANS le conteneur Docker.
    
    t1_weather = BashOperator(
        task_id='ingest_weather',
        bash_command='cd /opt/airflow && python pipeline/ingest_weather.py'
    )

    t2_load = BashOperator(
        task_id='ingest_load',
        bash_command='cd /opt/airflow && python pipeline/ingest_load_data.py'
    )

    # --- TÂCHE 2 : Nettoyage (Processing) ---
    t3_process_load = BashOperator(
        task_id='process_load',
        bash_command='cd /opt/airflow && python pipeline/process_load_data.py'
    )
    
    t3_process_weather = BashOperator(
        task_id='process_weather',
        bash_command='cd /opt/airflow && python pipeline/process_weather.py'
    )

    # --- TÂCHE 3 : Fusion & Features ---
    # On enchaîne merge puis feature engineering
    t4_merge_features = BashOperator(
        task_id='merge_and_features',
        bash_command='cd /opt/airflow && python pipeline/merge_data.py && python /opt/airflow/pipeline/feature_engineering.py'
    )

    # --- TÂCHE 4 : Machine Learning ---
    t5_train_predict = BashOperator(
        task_id='train_xgboost',
        bash_command='cd /opt/airflow && python pipeline/train_model.py'
    )

    # --- 3. Définition de l'ordre (Dépendances) ---
    # Load et Weather se lancent en même temps
    # Une fois Load fini -> Process Load
    # Une fois Weather fini -> Process Weather
    # Une fois les deux Process finis -> Merge -> Train
    
    t2_load >> t3_process_load
    t1_weather >> t3_process_weather
    
    [t3_process_load, t3_process_weather] >> t4_merge_features >> t5_train_predict