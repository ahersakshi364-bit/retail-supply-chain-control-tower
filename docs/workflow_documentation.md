# Airflow Workflow Documentation

## 1. Overview

The Retail & Supply Chain Control Tower uses Apache Airflow to automate supply-chain data validation, anomaly detection, demand forecasting, and email alerts.

Two scheduled DAGs are implemented:

1. `supply_chain_pipeline`
2. `supply_chain_alerts`

Both DAGs run hourly and connect to the project PostgreSQL database using the Airflow connection ID `retail_postgres`.

## 2. Main Supply Chain Pipeline

**DAG name:** `retail_supply_chain_pipeline`  
**Schedule:** Hourly (`@hourly`)  
**Database:** PostgreSQL  
**Connection ID:** `retail_postgres`

### Task execution sequence

The pipeline executes three tasks in this order:

`check_database → detect_anomalies → forecast_demand`

### Task 1: Database validation

The `check_database` task checks the PostgreSQL connection and validates the availability of the source tables required by the pipeline.

Main tables include:

- `products`
- `inventory`
- `suppliers`
- `shipments`
- `orders`

### Task 2: Anomaly detection

The `detect_anomalies` task identifies unusual supply-chain patterns using statistical Z-score analysis.

It checks:

- Unusual shipment delays.
- Unusual demand patterns.

The configured detection thresholds are:

- Shipment-delay anomalies: absolute Z-score threshold of 2.
- Demand anomalies: absolute Z-score threshold of 3.

Detected results are stored in:

`public.supply_chain_anomalies`

The output includes the anomaly type, related shipment or product identifier, event date, observed value, Z-score, description, and detection timestamp.

### Task 3: Demand forecasting

The `forecast_demand` task uses Facebook Prophet to generate product-level demand forecasts.

The model:

- Uses historical demand observations.
- Requires at least two observations to build a forecast.
- Generates forecasts for the next 30 days.
- Saves forecast dates and predicted demand values.

Results are stored in:

`public.demand_forecasts`

The output includes product ID, forecast date, predicted demand, current stock, stock status, and forecast creation timestamp.

## 3. Supply Chain Alert Workflow

**DAG name:** `supply_chain_alerts`  
**Schedule:** Hourly (`@hourly`)  
**Main task:** `check_and_send_alerts`  
**Database connection:** `retail_postgres`

This workflow checks for new supply-chain problems and sends email notifications.

### Alert type 1: Low-stock products

A low-stock alert is generated when:

`current_stock < reorder_point`

The workflow retrieves the product ID, current stock, and reorder point from:

`public.inventory`

### Alert type 2: Late shipments

A late-shipment alert is generated when either condition is true:

- `delivery_status = 'Late delivery'`
- `late_delivery_risk = 1`

The workflow retrieves shipment, order, supplier, delivery-status, actual-shipping-days, and scheduled-shipping-days information from:

`public.shipments`

A maximum of 100 new late-shipment records are processed in one run.

### Email notifications

The workflow prepares an HTML email containing the newly detected low-stock products and late shipments.

It sends notifications using Airflow's `send_email()` function.

The recipient is configured through the `GMAIL_RECEIVER` environment variable. Email credentials and sender configuration are maintained in environment variables and are not stored in this documentation.

### Duplicate notification prevention

The workflow uses:

`public.alert_notification_history`

Each alert receives a unique alert key:

- `LOW_STOCK:<product_id>`
- `LATE_SHIPMENT:<shipment_id>`

Previously notified records are excluded from subsequent alert queries.

Importantly, notification history is updated only after the email has been sent successfully. This prevents failed email attempts from being incorrectly marked as completed notifications.

## 4. Database and Application Integration

| Component | Purpose |
|---|---|
| PostgreSQL | Stores source data, anomaly results, forecasts, and notification history |
| Apache Airflow | Schedules and executes automated workflows |
| PostgreSQL Airflow connection | Connects DAG tasks to the project database |
| Prophet | Generates demand forecasts |
| Z-score analysis | Detects unusual shipment and demand patterns |
| Email notification | Sends low-stock and late-shipment alerts |
| Apache Superset | Reads PostgreSQL data to display dashboard charts and KPIs |

The initial dataset preparation and database loading are performed separately using the Jupyter Notebook `01_data_exploration.ipynb`. The Airflow pipeline processes the data already stored in PostgreSQL.

## 5. Monitoring and Execution

Airflow provides a web interface for monitoring DAG execution:

`http://localhost:8080`

Users can monitor:

- DAG scheduling and execution status.
- Individual task success or failure.
- Task logs and error messages.
- Historical DAG runs.

The Superset dashboard is available separately:

`http://localhost:8088`

It presents supply-chain KPIs, inventory information, shipment performance, and supplier analysis.

## 6. API Scope

The current implementation is a database-driven analytics and automation project. It does not expose a custom REST API endpoint.

Data exchange between the workflows and analytics layer is performed through PostgreSQL. Airflow provides workflow scheduling and monitoring, while Superset provides dashboard access.

## 7. Current Implementation Scope

The implemented workflows provide:

- Hourly database validation and processing.
- Statistical anomaly detection.
- 30-day product-level demand forecasting.
- Low-stock and late-shipment detection.
- Email-based supply-chain alerts.
- Duplicate notification prevention.
- Dashboard-based monitoring and analysis.

Future improvements could include REST API integration, real-time event ingestion, and additional notification channels.