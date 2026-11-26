-- ============================================================
-- Retail & Supply Chain Control Tower
-- SQL table definitions used by the Airflow pipeline
-- Database: PostgreSQL
-- ============================================================

-- 1. Supply Chain Anomalies
-- Stores shipment delay and demand spike detection results.

CREATE TABLE IF NOT EXISTS public.supply_chain_anomalies (
    anomaly_id BIGSERIAL PRIMARY KEY,
    anomaly_type VARCHAR(50),
    shipment_id BIGINT,
    product_id INTEGER,
    event_date DATE,
    observed_value NUMERIC,
    z_score NUMERIC,
    description TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Demand Forecasts
-- Stores Prophet demand predictions and stock-risk classifications.

CREATE TABLE IF NOT EXISTS public.demand_forecasts (
    forecast_id BIGSERIAL PRIMARY KEY,
    product_id INTEGER,
    forecast_date DATE,
    predicted_demand NUMERIC,
    current_stock INTEGER,
    stock_status VARCHAR(50),
    forecast_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Alert Notification History
-- Tracks notifications already processed by the alert pipeline.

CREATE TABLE IF NOT EXISTS public.alert_notification_history (
    alert_key TEXT PRIMARY KEY,
    alert_type TEXT,
    entity_id TEXT,
    notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Note:
-- Orders, shipments, products, inventory and suppliers
-- are populated through the project's data-loading process.
-- Their table definitions are not recreated in this file.
