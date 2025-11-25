import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Energy Forecasting Dashboard", layout="wide")

st.title("⚡ US Energy Consumption & Forecasting")
st.markdown("Ce dashboard visualise la consommation électrique des USA (US48) et compare les prédictions du modèle XGBoost avec la réalité.")

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data # Garde les données en cache pour que ça aille vite
def load_data():
    # Chargement des prédictions (Test set)
    df_pred = pd.read_csv("data_processed/test_predictions.csv")
    df_pred['datetime_utc'] = pd.to_datetime(df_pred['datetime_utc'])
    
    # Chargement de l'historique complet (pour le contexte)
    df_master = pd.read_parquet("data_processed/energy_dataset_master.parquet")
    
    return df_pred, df_master

try:
    df_pred, df_master = load_data()
except FileNotFoundError:
    st.error("❌ Les fichiers de données sont introuvables. Vérifie que tu es bien à la racine du projet.")
    st.stop()

# --- SIDEBAR (FILTRES) ---
st.sidebar.header("Filtres")
# Sélection de la plage de dates pour le zoom
min_date = df_pred['datetime_utc'].min()
max_date = df_pred['datetime_utc'].max()

start_date = st.sidebar.date_input("Date de début", min_date)
end_date = st.sidebar.date_input("Date de fin", max_date)

# Filtrage du dataframe
mask = (df_pred['datetime_utc'].dt.date >= start_date) & (df_pred['datetime_utc'].dt.date <= end_date)
filtered_df = df_pred.loc[mask]

# --- KPIS (CHIFFRES CLÉS) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_demand = filtered_df['demand_mwh'].mean()
    st.metric("Consommation Moyenne", f"{avg_demand:,.0f} MWh")

with col2:
    peak_demand = filtered_df['demand_mwh'].max()
    st.metric("Pic de Consommation", f"{peak_demand:,.0f} MWh")

with col3:
    # Calcul du MAPE sur la sélection
    mape = abs((filtered_df['demand_mwh'] - filtered_df['prediction']) / filtered_df['demand_mwh']).mean() * 100
    st.metric("Précision du Modèle (MAPE)", f"{mape:.2f} %", delta_color="inverse") # Vert si bas

with col4:
    total_hours = len(filtered_df)
    st.metric("Heures Analysées", f"{total_hours} h")

# --- GRAPHIQUE PRINCIPAL ---
st.subheader("📈 Comparaison Réel vs Prédiction")

fig = go.Figure()

# Courbe Réelle
fig.add_trace(go.Scatter(
    x=filtered_df['datetime_utc'], 
    y=filtered_df['demand_mwh'],
    mode='lines',
    name='Réel',
    line=dict(color='black', width=2)
))

# Courbe Prédiction
fig.add_trace(go.Scatter(
    x=filtered_df['datetime_utc'], 
    y=filtered_df['prediction'],
    mode='lines',
    name='Prédiction XGBoost',
    line=dict(color='#FFA500', width=2, dash='dash') # Orange en pointillés
))

fig.update_layout(
    height=500,
    xaxis_title="Date (UTC)",
    yaxis_title="Consommation (MWh)",
    template="plotly_white",
    hovermode="x unified" # Affiche les deux valeurs quand on passe la souris
)

st.plotly_chart(fig, use_container_width=True)

# --- ANALYSE DES ERREURS ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🌡️ Corrélation Température vs Conso")
    # Scatter plot interactif
    fig_scatter = px.scatter(
        filtered_df, 
        x="temp_houston", 
        y="demand_mwh", 
        color="hour",
        title="Impact de la Température (Houston)",
        template="plotly_white"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_right:
    st.subheader("📉 Distribution des Erreurs")
    # Histogramme des erreurs
    filtered_df['error'] = filtered_df['demand_mwh'] - filtered_df['prediction']
    fig_hist = px.histogram(
        filtered_df, 
        x="error", 
        nbins=50,
        title="Répartition des erreurs (MWh)",
        color_discrete_sequence=['indianred'],
        template="plotly_white"
    )
    st.plotly_chart(fig_hist, use_container_width=True)