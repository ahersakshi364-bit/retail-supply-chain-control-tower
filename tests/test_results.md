# Retail & Supply Chain Control Tower

## Project Test Results

**Project:** Retail & Supply Chain Control Tower
**Database:** PostgreSQL
**Pipeline:** Apache Airflow
**Analytics:** Python, Z-score anomaly detection, Prophet forecasting
**Dashboard:** Apache Superset

**Testing approach:** Manual workflow validation, SQL data checks, and dashboard verification. This report records observed execution results; it is not an automated pytest test suite.
---
## 1. Database Validation

Verified the main PostgreSQL tables and their record counts.

| Table | Records |
|---|---:|
| Inventory | 118 |
| Orders | 180,519 |
| Products | 118 |
| Shipments | 180,519 |
| Suppliers | 10 |
| **Total** | **361,284** |

### Data quality checks

- Checked selected important ID and date columns for missing values.
- No missing values were found in the selected validation columns.
- Checked uniqueness of inventory product IDs, product IDs, supplier IDs, shipment IDs, and order item IDs.
- No duplicate values were found in these unique identifiers.
- Repeated `order_id` values are expected because one order can contain multiple order items. `order_item_id` was used to validate individual order records.

**Result:** Core database validation passed for the selected checks.

## 2. Airflow Pipeline Validation

**DAG ID:** `retail_supply_chain_pipeline`

The following tasks executed successfully:

1. `check_database`
2. `detect_anomalies`
3. `forecast_demand`

All three tasks completed successfully in the tested pipeline run.

**Result:** Pipeline execution passed.

## 3. Anomaly Detection Validation

The anomaly detection process identifies unusual shipment delays and demand patterns using statistical Z-score analysis.

| Anomaly type | Detection threshold | Detected records |
|---|---:|---:|
| Shipment delay | Z-score >= 2 | 6,983 |
| Demand spike | Z-score >= 3 | 185 |
| **Total** | | **7,168** |

The results were saved in PostgreSQL table `public.supply_chain_anomalies`.

**Result:** Anomaly detection executed and produced records.

**Important:** These counts represent detected records, not precision, recall, or model accuracy.

## 4. Demand Forecasting Validation

The forecasting process uses Prophet to generate product-level demand forecasts.

| Validation | Result |
|---|---:|
| Total forecast records | 3,540 |
| Products covered | 118 |
| Forecast records per product | 30 |
| Missing predicted demand values | 0 |
| Products classified as stock at risk | 108 |
| Products classified as stock sufficient | 10 |

The forecast results are stored in `public.demand_forecasts`.

**Result:** Forecast generation and stock-risk classification completed successfully.

**Data limitation:** The source dataset contains historical records from 2015â€“2018. Therefore, the forecast dates are historical relative to the current date and should not be interpreted as live 2026 forecasts.

**Accuracy limitation:** Forecast generation alone does not establish predictive accuracy. See the historical forecast backtesting results below for the measured error metrics and their limitations.


### Historical Forecast Backtesting

A separate historical backtest was conducted using Prophet and PostgreSQL data.

**Testing methodology:**
- Selected 54 products with at least 90 daily demand observations.
- Used all but the final 30 observed demand records for training.
- Tested predictions against the final 30 observed demand records per product.
- Evaluated 1,620 actual demand observations across 54 products.
- Compared Prophet with a naive baseline that repeats the last training observation.

**Backtest results:**

| Metric | Prophet | Naive Baseline |
|---|---:|---:|
| MAE | 2.7105 | 3.8025 |

Additional Prophet metrics:

| Metric | Result |
|---|---:|
| RMSE | 5.0975 |
| MAPE | 66.44% |
| WAPE | 30.66% |
| sMAPE | 44.41% |

Prophet achieved approximately 28.7% lower MAE than the naive baseline in this backtest.

**Interpretation:** The results indicate that Prophet performed better than the selected baseline on this historical test. MAPE is relatively high and can be sensitive to small actual demand values. These results represent one historical holdout evaluation, not a guarantee of future forecasting performance.

**Note:** The final 30 observations are the final 30 recorded demand dates for each product, not necessarily 30 consecutive calendar days.

## 5. Dashboard Validation

The Apache Superset dashboard, **Retail & Supply Chain Control Tower**, was created, saved, and visually reviewed.

The dashboard contains 12 visualizations covering:

- Total orders KPI
- Current stock by product
- Current stock by supplier
- Low-stock products
- Shipment status distribution
- Late delivery risk analysis
- Shipment distribution by shipping mode
- Average shipping days by supplier
- Top products by order quantity
- Order trends over time
- Current stock by supplier
- Supplier delay what-if simulation

The what-if analysis includes a fixed seven-day supplier-delay scenario.

Dashboard charts, displayed data, filters, and simulation results were checked.

**Result:** Dashboard validation passed.

## 6. Alert System Validation

A separate Airflow DAG, `supply_chain_alerts`, checks:

- Products below their reorder point.
- Late shipments.

The system uses Gmail SMTP to send notifications and stores notification history in `public.alert_notification_history` to prevent repeated notifications for the same recorded entity.

The SMTP connection was tested, an alert email was received, and the alert DAG execution completed successfully.

Notification history is recorded only after successful email sending.

**Result:** Alert workflow execution passed.

## 7. Overall Test Summary

| Component | Status |
|---|---|
| PostgreSQL data loading | Passed |
| Selected data quality checks | Passed |
| Main Airflow pipeline | Passed |
| Shipment anomaly detection | Passed |
| Demand spike detection | Passed |
| Prophet forecast generation | Passed |
| Superset dashboard and filters | Passed |
| Email alert workflow | Passed |
| Duplicate notification prevention | Implemented and executed |

## 8. Known Limitations

1. The dataset is historical, so forecasts are based on historical data rather than current live demand.
2. The dashboard's supplier-delay what-if analysis uses a fixed seven-day scenario rather than an interactive slider.
3. Anomaly counts indicate detected records, not model accuracy.
4. Stock-at-risk classifications compare current stock with predicted demand; they do not prove that an actual stockout occurred.
5. Forecast accuracy was evaluated using one historical holdout backtest; additional rolling-window validation is recommended.
6. The current implementation does not expose a custom REST API.

## Conclusion

The major database, pipeline, anomaly detection, forecasting, dashboard, and alert workflows were executed and tested.

The project demonstrates an integrated supply-chain analytics workflow using PostgreSQL, Python, Apache Airflow, Prophet, and Apache Superset.
