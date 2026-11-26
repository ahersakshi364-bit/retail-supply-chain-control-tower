\# Retail \& Supply Chain Control Tower



A data analytics and automation project designed to monitor retail inventory, shipment performance, supplier delays, and product demand. It combines data engineering, anomaly detection, forecasting, dashboards, and automated email alerts to help identify potential supply-chain problems.



\## Project Overview



The Retail \& Supply Chain Control Tower provides a centralized view of supply-chain operations. It processes historical retail and shipment data, stores structured information in PostgreSQL, runs automated workflows using Apache Airflow, detects unusual patterns, forecasts product demand, and displays operational insights through Apache Superset.



\## Objectives



\- Monitor inventory levels and identify products at risk of stockouts.

\- Analyze shipment delays and delivery performance.

\- Evaluate supplier performance.

\- Detect unusual shipment delays and demand spikes.

\- Forecast product demand using Prophet.

\- Compare predicted demand with available inventory.

\- Notify stakeholders about selected supply-chain risks through email alerts.



\## Technology Stack



| Technology | Purpose |

|---|---|

| Python | Data processing and analytics |

| PostgreSQL | Relational database |

| Apache Airflow | Workflow orchestration and scheduling |

| Apache Superset | Interactive analytics dashboards |

| Prophet | Time-series demand forecasting |

| Pandas and NumPy | Data manipulation and numerical analysis |

| Docker Compose | Local application environment |

| Gmail SMTP | Email notifications |

| SQL | Data queries and KPI calculations |



\## Architecture



```mermaid

flowchart TD

&#x20;   A\[Historical Supply Chain Dataset] --> B\[Python Data Processing]

&#x20;   B --> C\[PostgreSQL Database]

&#x20;   C --> D\[Apache Airflow]

&#x20;   D --> E\[Data Validation]

&#x20;   D --> F\[Anomaly Detection]

&#x20;   D --> G\[Prophet Demand Forecasting]

&#x20;   C --> H\[Apache Superset]

&#x20;   F --> I\[Anomaly Results]

&#x20;   G --> J\[Demand Forecast Results]

&#x20;   I --> C

&#x20;   J --> C

&#x20;   C --> H

&#x20;   D --> K\[Alert Workflow]

&#x20;   K --> L\[Gmail SMTP Notifications]

```



\## Main Features



\### 1. Data Collection and Database



\- Loaded and structured supply-chain data in PostgreSQL.

\- Created core tables for orders, shipments, products, inventory, and suppliers.

\- Used SQL to query and validate records.



\### 2. Automated Data Pipeline



Apache Airflow orchestrates the main workflow through the `retail\_supply\_chain\_pipeline` DAG.



The pipeline includes:

\- Database connectivity checks.

\- Shipment and demand anomaly detection.

\- Product demand forecasting.



\### 3. Supply Chain Analytics



The project analyzes:

\- Inventory availability.

\- Shipment and delivery performance.

\- Late delivery risk.

\- Supplier shipping performance.

\- Product demand and order trends.



\### 4. Anomaly Detection



Z-score-based detection is used to identify unusual patterns.



\- Shipment delay threshold: Z-score >= 2.

\- Demand spike threshold: Z-score >= 3.



Detected records are stored in the PostgreSQL table `supply\_chain\_anomalies`.



\### 5. Demand Forecasting



Prophet is used to generate product-level demand forecasts.



Forecast results are stored in `demand\_forecasts` and compared with current inventory to classify products as:



\- `STOCK\_AT\_RISK`

\- `STOCK\_SUFFICIENT`



\### 6. Interactive Dashboard



Apache Superset provides a dashboard named \*\*Retail \& Supply Chain Control Tower\*\*.



It includes visualizations for:

\- Total orders.

\- Current stock by product and supplier.

\- Shipment status distribution.

\- Late delivery risk.

\- Shipping modes.

\- Average shipping days by supplier.

\- Top products by order quantity.

\- Order trends over time.

\- Low-stock products.

\- Supplier-delay what-if analysis.



\### 7. Automated Email Alerts



A separate Airflow DAG, `supply\_chain\_alerts`, checks for low-stock products and late shipments.



Email notifications are sent through Gmail SMTP. Notification history is stored in PostgreSQL to help avoid repeated notifications for the same recorded entity.



\## Project Validation Results



| Test | Result |

|---|---:|

| Inventory records | 118 |

| Order records | 180,519 |

| Product records | 118 |

| Shipment records | 180,519 |

| Supplier records | 10 |

| Shipment-delay anomalies | 6,983 |

| Demand-spike anomalies | 185 |

| Forecast records | 3,540 |

| Products covered by forecasts | 118 |

| Products classified as stock at risk | 108 |

| Products classified as stock sufficient | 10 |



The main Airflow pipeline completed successfully in the tested run, and the alert workflow also completed successfully.



For detailed validation results, see \[`tests/test\_results.md`](tests/test\_results.md).



\## Project Structure



```text

retail-supply-chain-control-tower/

│

├── dags/

│   ├── supply\_chain\_pipeline.py

│   └── supply\_chain\_alerts.py

│

├── data/

│   ├── raw/

│   └── processed/

│

├── docs/

│

├── sql/

│

├── tests/

│   └── test\_results.md

│

├── Dockerfile

├── docker-compose.yaml

├── requirements.txt

├── .gitignore

├── README.md

└── 01\_data\_exploration.ipynb

```



\## Running the Project



\### Prerequisites



\- Python

\- Docker Desktop

\- Docker Compose

\- Git



\### Setup



1\. Clone the repository:



&#x20;  ```bash

&#x20;  git clone YOUR\_GITHUB\_REPOSITORY\_URL

&#x20;  cd retail-supply-chain-control-tower

&#x20;  ```



2\. Create a local `.env` file containing the configuration required by the project. Use your own credentials and database settings. Never commit this file.



3\. Start the Docker Compose environment:



&#x20;  ```bash

&#x20;  docker compose up -d --build

&#x20;  ```



4\. Open the Airflow interface:



&#x20;  `http://localhost:8080`



5\. Open the Apache Superset interface using the port configured in `docker-compose.yaml`.



6\. Run the Airflow pipeline and view the resulting database tables and dashboard.



\*\*Note:\*\* Exact environment variables, database initialization steps, and service configuration depend on the local setup. Do not publish passwords or application secrets.



\## Limitations and Future Improvements



\- The source dataset contains historical data from 2015–2018; forecasts are not live 2026 predictions.

\- The supplier-delay what-if analysis currently uses a fixed seven-day scenario.

\- Anomaly counts represent detected records, not model accuracy.

\- Stock-risk classifications are based on forecast-versus-stock comparisons and do not prove actual stockouts.

\- Future improvements could include live data ingestion, interactive what-if controls, model evaluation, and more advanced anomaly detection.



\## Author



Developed as a hands-on data engineering and analytics project demonstrating Python, SQL, PostgreSQL, Apache Airflow, Prophet, Docker, and Apache Superset.



\---


## System Architecture

The following diagram illustrates the architecture of the Retail & Supply Chain Control Tower, including PostgreSQL data storage, Apache Airflow workflows, anomaly detection, demand forecasting, email alerts, and the Apache Superset dashboard.

![Retail Supply Chain Control Tower Architecture](docs/architecture.png)



\*\*Project:\*\* Retail \& Supply Chain Control Tower

