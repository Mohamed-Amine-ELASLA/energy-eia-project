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
