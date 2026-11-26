# Data Dictionary – Retail & Supply Chain Control Tower

## 1. Overview

This document describes the PostgreSQL database schema used by the Retail & Supply Chain Control Tower.

The database supports:
- Order and sales analysis
- Inventory monitoring
- Shipment tracking
- Supplier performance analysis
- Statistical anomaly detection
- Demand forecasting
- Automated alert notification tracking

The schema information was verified using PostgreSQL `information_schema.columns` and `information_schema.table_constraints`.

**Database schema:** `public`

## 2. Database Tables

The project uses eight documented tables.

### 2.1 Orders

**Purpose:** Stores order, sales, customer, product category, and delivery information.

| Column | PostgreSQL data type | Nullable |
|---|---|---|
| product_price | numeric | YES |
| sales | numeric | YES |
| order_item_total | numeric | YES |
| order_profit | numeric | YES |
| order_date | timestamp without time zone | YES |
| shipping_date | timestamp without time zone | YES |
| actual_shipping_days | integer | YES |
| scheduled_shipping_days | integer | YES |
| delivery_status | character varying | YES |
| late_delivery_risk | integer | YES |
| shipping_mode | character varying | YES |
| order_region | character varying | YES |
| order_country | character varying | YES |
| order_city | character varying | YES |
| customer_segment | character varying | YES |
| market | character varying | YES |
| category_name | character varying | YES |
| department_name | character varying | YES |

### 2.2 Shipments

**Purpose:** Stores shipment timing, delivery performance, and geographical information.

| Column | PostgreSQL data type | Nullable |
|---|---|---|
| shipping_date | timestamp without time zone | YES |
| actual_shipping_days | integer | YES |
| scheduled_shipping_days | integer | YES |
| delivery_status | character varying | YES |
| late_delivery_risk | integer | YES |
| shipping_mode | character varying | YES |
| order_region | character varying | YES |
| order_country | character varying | YES |

### 2.3 Products

**Purpose:** Stores product information and supplier mapping.

| Column | PostgreSQL data type | Nullable |
|---|---|---|
| product_id | integer | NO |
| product_name | character varying | NO |
| supplier_id | character varying | YES |

### 2.4 Inventory

**Purpose:** Stores current stock levels and inventory planning metrics.

| Column | PostgreSQL data type | Nullable |
|---|---|---|
| product_id | integer | NO |
| supplier_id | character varying | YES |
| average_daily_demand | numeric | YES |
| lead_time_days | integer | YES |
| safety_stock | integer | YES |
| reorder_point | integer | YES |
| current_stock | integer | YES |
| days_of_inventory | numeric | YES |

### 2.5 Suppliers

**Purpose:** Stores supplier details and performance-related information.

| Column | PostgreSQL data type | Nullable |
|---|---|---|
| supplier_id | character varying | NO |
| supplier_name | character varying | NO |
| lead_time_days | integer | NO |
| supplier_status | character varying | NO |

### 2.6 Supply Chain Anomalies

**Purpose:** Stores unusual shipment delays and demand patterns identified through statistical anomaly detection.

**Primary key:** `anomaly_id`

| Column | PostgreSQL data type | Nullable |
|---|---|---|
| anomaly_id | bigint | NO |
| anomaly_type | character varying | YES |
| shipment_id | bigint | YES |
| product_id | integer | YES |
| event_date | date | YES |
| observed_value | numeric | YES |
| z_score | numeric | YES |
| description | text | YES |
| detected_at | timestamp without time zone | YES |

### 2.7 Demand Forecasts

**Purpose:** Stores Prophet-generated product demand forecasts and stock-risk classifications.

**Primary key:** `forecast_id`

| Column | PostgreSQL data type | Nullable |
|---|---|---|
| forecast_id | bigint | NO |
| product_id | integer | YES |
| forecast_date | date | YES |
| predicted_demand | numeric | YES |
| current_stock | integer | YES |
| stock_status | character varying | YES |
| forecast_created_at | timestamp without time zone | YES |

### 2.8 Alert Notification History

**Purpose:** Tracks previously processed alerts to help prevent duplicate notifications.

**Primary key:** `alert_key`

| Column | PostgreSQL data type | Nullable |
|---|---|---|
| alert_key | text | NO |

## 3. Primary Keys

The following primary keys were confirmed using PostgreSQL database metadata.

| Table | Primary key |
|---|---|
| supply_chain_anomalies | anomaly_id |
| demand_forecasts | forecast_id |
| alert_notification_history | alert_key |

No declared primary keys were returned for the other five tables in the metadata query.

## 4. Logical Table Relationships

The following logical relationships are used for analysis:

| Parent table | Parent column | Related table | Related column |
|---|---|---|---|
| products | product_id | inventory | product_id |
| products | product_id | orders | product_id |
| products | product_id | demand_forecasts | product_id |
| products | product_id | supply_chain_anomalies | product_id |
| suppliers | supplier_id | products | supplier_id |
| suppliers | supplier_id | inventory | supplier_id |

Shipment and order information is used for delivery-performance analysis.

**Important:** These relationships describe the logical data model. They are not confirmed foreign-key constraints.

## 5. Key Business Metrics

| Metric | Meaning |
|---|---|
| Stock-out risk | Indicates products whose available stock may be insufficient |
| On-time delivery rate | Percentage of shipments delivered on or before the scheduled time |
| Supplier lead time | Time taken by a supplier to provide products |
| Days of inventory | Estimated number of days current stock can cover demand |
| Shipment delay | Difference between actual and scheduled shipping duration |
| Demand anomaly | Unusual demand pattern identified using statistical analysis |
| Forecast stock risk | Classification based on comparing available stock with predicted demand |

## 6. Data Processing and Model Notes

### Anomaly Detection
- Uses statistical Z-score analysis.
- Shipment-delay anomaly threshold: Z-score greater than or equal to 2.
- Demand-spike anomaly threshold: Z-score greater than or equal to 3.
- Results are stored in `public.supply_chain_anomalies`.

### Demand Forecasting
- Uses Prophet for product-level demand forecasting.
- Generates a 30-day forecast horizon.
- Stores predicted demand, forecast date, current stock, and stock status.
- Results are stored in `public.demand_forecasts`.

### Alert Processing
- Monitors low-stock products and late shipments.
- Uses `public.alert_notification_history` to track processed alert keys.
- Sends email notifications for qualifying records.

## 7. Data Validation Results

The following record counts were verified during project validation:

| Table | Records |
|---|---:|
| products | 118 |
| inventory | 118 |
| suppliers | 10 |
| orders | 180,519 |
| shipments | 180,519 |
| supply_chain_anomalies | 7,168 |
| demand_forecasts | 3,540 |

Alert notification history is maintained separately as alerts are processed.

## 8. Limitations

- The project uses historical supply chain data rather than live operational feeds.
- Historical data may not represent current market conditions.
- Stock-risk classifications are estimates and do not confirm actual stock-outs.
- Anomaly detection identifies statistical outliers but does not establish their business cause.
- Forecast accuracy must be evaluated against actual future demand.
- Logical relationships do not necessarily represent enforced database constraints.

