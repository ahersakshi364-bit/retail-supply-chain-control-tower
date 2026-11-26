\# Retail \& Supply Chain Control Tower

\## Project Test Results



\*\*Project:\*\* Retail \& Supply Chain Control Tower  

\*\*Database:\*\* PostgreSQL  

\*\*Pipeline:\*\* Apache Airflow  

\*\*Analytics:\*\* Python, anomaly detection, Prophet forecasting  

\*\*Dashboard:\*\* Apache Superset  



\---



\## 1. Database Validation



Verified the main PostgreSQL tables and their record counts.



| Table | Records |

|---|---:|

| Inventory | 118 |

| Orders | 180,519 |

| Products | 118 |

| Shipments | 180,519 |

| Suppliers | 10 |

| \*\*Total\*\* | \*\*361,284\*\* |



\### Data quality checks



\- Checked selected important ID and date columns for missing values.

\- No missing values were found in the selected validation columns.

\- Checked uniqueness of inventory product IDs, product IDs, supplier IDs, shipment IDs, and order item IDs.

\- No duplicate values were found in these unique identifiers.

\- Repeated `order\_id` values are expected because one order can contain multiple order items. `order\_item\_id` was used to validate individual order records.



\*\*Result:\*\* Core database validation passed for the selected checks.



\## 2. Airflow Pipeline Validation



\*\*DAG ID:\*\* `retail\_supply\_chain\_pipeline`



The following tasks were executed successfully:



1\. `check\_database`

2\. `detect\_anomalies`

3\. `forecast\_demand`



All three tasks completed successfully in the tested pipeline run.



\*\*Result:\*\* Pipeline execution passed.



\## 3. Anomaly Detection Validation



The anomaly detection process identifies unusual shipment delays and demand spikes.



| Anomaly type | Detection threshold | Detected records |

|---|---:|---:|

| Shipment delay | Z-score >= 2 | 6,983 |

| Demand spike | Z-score >= 3 | 185 |

| \*\*Total\*\* | | \*\*7,168\*\* |



The results were saved in the PostgreSQL table `supply\_chain\_anomalies`.



\*\*Result:\*\* Anomaly detection executed and produced records.



\## 4. Demand Forecasting Validation



The forecasting process uses Prophet to generate product-level demand forecasts.



| Validation | Result |

|---|---:|

| Total forecast records | 3,540 |

| Products covered | 118 |

| Forecast records per product | 30 |

| Missing predicted demand values | 0 |

| Products classified as stock at risk | 108 |

| Products classified as stock sufficient | 10 |



The forecast results are stored in `demand\_forecasts`.



\*\*Result:\*\* Forecast generation and stock-risk classification completed successfully.



\*\*Data limitation:\*\* The source dataset contains historical records from 2015–2018. Therefore, the forecast dates are historical relative to the current date and should not be interpreted as live 2026 forecasts.



\## 5. Dashboard Validation



The Apache Superset dashboard, \*\*Retail \& Supply Chain Control Tower\*\*, was created and saved.



Dashboard visualizations cover areas including:



\- Total orders

\- Current stock by product

\- Current stock by supplier

\- Shipment status distribution

\- Late delivery risk

\- Shipping modes

\- Average shipping days by supplier

\- Top products by order quantity

\- Order trends over time

\- Low-stock products

\- Supplier delay what-if simulation



The what-if analysis includes a fixed seven-day supplier-delay scenario.



\*\*Result:\*\* Dashboard created and saved. Final visual review should be performed before submission.



\## 6. Alert System Validation



A separate Airflow DAG, `supply\_chain\_alerts`, was created to check:



\- Products below their reorder point.

\- Late shipments.



The system uses Gmail SMTP to send notifications and stores notification history in `alert\_notification\_history` to prevent repeated notifications for the same recorded entity.



The SMTP connection was tested, and the alert DAG execution completed successfully.



\*\*Result:\*\* Alert workflow execution passed.



\## 7. Overall Test Summary



| Component | Status |

|---|---|

| PostgreSQL data loading | Passed |

| Selected data quality checks | Passed |

| Main Airflow pipeline | Passed |

| Shipment anomaly detection | Passed |

| Demand spike detection | Passed |

| Prophet forecast generation | Passed |

| Superset dashboard creation | Completed; final review pending |

| Email alert workflow | Passed |



\## 8. Known Limitations



1\. The dataset is historical, so forecasts are based on historical data rather than current live demand.

2\. The dashboard's supplier-delay what-if analysis currently uses a fixed seven-day scenario rather than an interactive slider.

3\. Anomaly counts indicate detected records, not model accuracy.

4\. Stock-at-risk classifications compare current stock with predicted demand; they do not prove that an actual stockout occurred.

5\. Final dashboard review and end-to-end submission checks remain necessary.



\---



\*\*Conclusion:\*\* The major database, pipeline, anomaly detection, forecasting, and alert workflows were executed and tested. The project demonstrates an integrated supply-chain analytics workflow using PostgreSQL, Python, Apache Airflow, Prophet, and Apache Superset.

