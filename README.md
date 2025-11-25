# End-to-End US Energy Demand Forecasting

## Project Overview
This project is a full-stack data solution designed to predict hourly electricity consumption for the United States (Lower 48 states).
The goal is to simulate a real-world scenario where Grid Operators need accurate forecasts to balance supply and demand using **Data Engineering**, **Machine Learning**, and **Business Intelligence**.

**Key Result:** The XGBoost model achieved a **MAPE (Mean Absolute Percentage Error) of 2.17%** on the test set.

---

## Technical Architecture

The project follows a "Modern Data Stack" approach:

### 1. Data Engineering (ETL)
*   **Data Sources:**
    *   **Electricity Load:** Extracted from the **EIA API v2** (US Energy Information Administration).
    *   **Weather Data:** Historical temperature data for 3 strategic hubs (New York, Houston, Los Angeles) fetched via **Open-Meteo API**.
*   **Processing:**
    *   Data cleaning and type casting using **Pandas**.
    *   Handling time zones (UTC normalization) and missing values.
    *   Storage optimized in **Parquet** format (Partitioned by Year/Month).

### 2. Machine Learning
*   **Feature Engineering:**
    *   Created Lag features (t-24h, t-168h) to capture daily and weekly seasonality.
    *   Rolling window statistics (24h moving average).
    *   Calendar features (Day of week, Hour, Month, Quarter).
*   **Modeling:**
    *   Algorithm: **XGBoost Regressor**.
    *   Validation Strategy: **Time Series Split** (Training on past data, Testing on future unseen data to avoid look-ahead bias).
    *   Performance Metric: **MAPE** (2.17%) and **MAE**.

### 3. Business Intelligence (BI)
*   **Visualization:** Interactive **Power BI Dashboard**.
*   **Insights:**
    *   Real-time comparison of Actual vs. Predicted Load.
    *   Analysis of the non-linear "U-shape" correlation between Temperature and Demand.

---

## Dashboard Preview

![Dashboard Power BI](./dashboard.png)

---
## How to Run
### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/energy-eia-project.git
cd energy-eia-project
```
### 2. Install dependencies
It is recommended to use a virtual environment.

```bash
pip install pandas requests xgboost scikit-learn pyarrow matplotlib seaborn
```
### 3. Set up API Key
Get a free API key from EIA Open Data.
Open pipeline/ingest_load.py and replace the placeholder with your key.
### 4. Run the Pipeline
Execute the scripts in the following order to build the dataset and train the model:

```bash
# Data Ingestion
python pipeline/ingest_load.py       # Step 1: Get Load Data
python pipeline/ingest_weather.py    # Step 2: Get Weather Data

# Data Processing
python pipeline/process_load_data.py # Step 3: Clean Load Data (Parquet)
python pipeline/process_weather.py   # Step 4: Clean Weather Data

# Merging & Feature Engineering
python pipeline/merge_data.py        # Step 5: Merge Datasets into Master Table
python pipeline/feature_engineering.py # Step 6: Create Lags & Rolling Features

# Machine Learning
python pipeline/train_model.py       # Step 7: Train XGBoost & Predict
```
## Future Improvements
Weather Weighting: Implement population-weighted temperature indices (using more cities) instead of using single cities as proxies for the whole region.
Orchestration: Automate the pipeline execution using Airflow or Prefect to run daily updates.
Deep Learning: Experiment with LSTM or Prophet models to compare performance with XGBoost.