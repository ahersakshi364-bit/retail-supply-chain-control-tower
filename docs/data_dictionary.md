# Data Dictionary – Retail & Supply Chain Control Tower

## 1. Overview

This document describes the PostgreSQL tables used in the Retail & Supply Chain Control Tower project. The database supports order analysis, inventory monitoring, shipment tracking, supplier performance, anomaly detection, demand forecasting, and alert notifications.

Column names and data types below are based on the database schema inspected in Superset SQL Lab.

## 2. Database Tables

### 2.1 Orders

**Purpose:** Stores order, sales, customer, product category, and delivery information.

| Column | Data type | Description |
|---|---|---|
| product_price | numeric | Price of the product |
| sales | numeric | Sales amount |
| order_item_total | numeric | Total value of the order item |
| order_profit | numeric | Profit associated with the order item |
| order_date | timestamp | Date and time of the order |
| shipping_date | timestamp | Date and time of shipment |
| actual_shipping_days | integer | Actual number of days taken for shipping |
| scheduled_shipping_days | integer | Planned shipping duration |
| delivery_status | varchar | Delivery status |
| late_delivery_risk | integer | Indicator of late delivery risk |
| shipping_mode | varchar | Shipping method |
| order_region | varchar | Region where the order was placed |
| order_country | varchar | Country of the order |
| order_city | varchar | City of the order |
| customer_segment | varchar | Customer segment |
| market | varchar | Market associated with the order |
| category_name | varchar | Product category |
| department_name | varchar | Department associated with the product |

### 2.2 Shipments

**Purpose:** Stores shipment timing, delivery performance, and geographical information.

| Column | Data type | Description |
|---|---|---|
| shipping_date | timestamp | Date and time of shipment |
| actual_shipping_days | integer | Actual shipping duration |
| scheduled_shipping_days | integer | Expected shipping duration |
| delivery_status | varchar | Shipment delivery status |
| late_delivery_risk | integer | Indicator of late delivery risk |
| shipping_mode | varchar | Shipping method |
| order_region | varchar | Region associated with the shipment |
| order_country | varchar | Country associated with the shipment |

### 2.3 Products

**Purpose:** Stores product information and supplier mapping.

| Column | Data type | Description |
|---|---|---|
| product_id | integer | Unique product identifier |
| product_name | varchar | Product name |
| supplier_id | varchar | Identifier of the associated supplier |

### 2.4 Inventory

**Purpose:** Stores current stock levels and inventory planning metrics.

| Column | Data type | Description |
|---|---|---|
| product_id | integer | Product identifier |
| supplier_id | varchar | Supplier identifier |
| average_daily_demand | numeric | Average daily product demand |
| lead_time_days | integer | Expected supplier lead time in days |
| safety_stock | integer | Extra stock maintained to reduce stock-out risk |
| reorder_point | integer | Stock level at which replenishment should be considered |
| current_stock | integer | Current available stock |
| days_of_inventory | numeric | Estimated number of days current stock can cover |

### 2.5 Suppliers

**Purpose:** Stores supplier details and performance-related information.

| Column | Data type | Description |
|---|---|---|
| supplier_id | varchar | Unique supplier identifier |
| supplier_name | varchar | Supplier name |
| lead_time_days | integer | Supplier lead time in days |
| supplier_status | varchar | Current supplier status |

### 2.6 Supply Chain Anomalies

**Purpose:** Stores unusual shipment delays and demand spikes identified by anomaly detection.

| Column | Data type | Description |
|---|---|---|
| anomaly_id | bigint | Unique anomaly record identifier |
| anomaly_type | varchar | Type of anomaly detected |
| shipment_id | bigint | Related shipment identifier, where applicable |
| product_id | integer | Related product identifier, where applicable |
| event_date | date | Date of the detected event |
| observed_value | numeric | Observed measurement associated with the anomaly |
| z_score | numeric | Statistical z-score used to identify unusual observations |
| description | text | Explanation of the detected anomaly |
| detected_at | timestamp | Date and time when the anomaly was detected |

### 2.7 Demand Forecasts

**Purpose:** Stores Prophet-generated product demand forecasts and stock-risk classifications.

| Column | Data type | Description |
|---|---|---|
| forecast_id | bigint | Unique forecast record identifier |
| product_id | integer | Product identifier |
| forecast_date | date | Date for which demand is forecast |
| predicted_demand | numeric | Predicted product demand |
| current_stock | integer | Current stock used for comparison |
| stock_status | varchar | Stock-risk classification |
| forecast_created_at | timestamp | Date and time when the forecast was generated |

### 2.8 Alert Notification History

**Purpose:** Tracks alert keys that have already been processed to help prevent repeated notifications.

| Column | Data type | Description |
|---|---|---|
| alert_key | text | Identifier used to track a previously processed alert |

## 3. Important Relationships

The following logical relationships connect the main project tables:

- `products.product_id` → `inventory.product_id`
- `products.product_id` → `orders.product_id`
- `products.product_id` → `demand_forecasts.product_id`
- `products.product_id` → `supply_chain_anomalies.product_id`
- `suppliers.supplier_id` → `products.supplier_id`
- `suppliers.supplier_id` → `inventory.supplier_id`

Shipment and order records are also used for delivery-performance analysis.

These are logical relationships based on the project data model; they should not be interpreted as confirmed database foreign-key constraints.

## 4. Key Business Metrics

| Metric | Meaning |
|---|---|
| Stock-out rate | Percentage of products or observations with insufficient stock |
| On-time delivery rate | Percentage of shipments delivered on or before the scheduled time |
| Supplier lead time | Time taken by a supplier to provide products |
| Days of inventory | Estimated days that current stock can satisfy demand |
| Shipment delay | Difference between actual and scheduled shipping duration |
| Demand anomaly | Unusually high demand identified using statistical analysis |
| Forecast stock risk | Classification based on comparing current stock with predicted demand |

## 5. Data and Model Notes

- The project uses historical supply-chain data.
- Shipment and demand anomalies are detected using z-scores.
- Shipment anomaly threshold: z-score greater than or equal to 2.
- Demand spike threshold: z-score greater than or equal to 3.
- Prophet is used to generate product-level demand forecasts.
- Forecast records include current stock and a stock-status classification.
- Forecast dates represent historical dataset periods, not live future business dates.
- Alert history supports duplicate-notification prevention.

## 6. Limitations

- Forecasts are based on historical data and may not represent current market conditions.
- Stock-risk classifications are estimates and do not confirm actual stock-outs.
- Anomaly detection identifies statistical outliers and does not establish their business cause.
- The what-if analysis is a scenario simulation, not a guaranteed prediction of future delivery performance.

