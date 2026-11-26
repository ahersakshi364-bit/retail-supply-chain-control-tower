# Retail & Supply Chain Control Tower

A data analytics and automation project that monitors retail inventory, shipments, suppliers, and orders. It uses Apache Airflow to automate analytics workflows, statistical anomaly detection to identify unusual patterns, Prophet to generate demand forecasts, and Apache Superset to visualize supply chain performance.

## Project Objectives

- Monitor inventory levels and identify products at risk of low stock.
- Analyze shipment delays and delivery performance.
- Monitor supplier performance.
- Detect unusual shipment delays and demand patterns.
- Generate 30-day demand forecasts.
- Send email alerts for low-stock products and late shipments.
- Present key supply chain metrics through an interactive dashboard.

## Technology Stack

| Component | Technology |
|---|---|
| Programming | Python |
| Database | PostgreSQL |
| Workflow orchestration | Apache Airflow |
| Dashboard | Apache Superset |
| Data processing | Pandas |
| Anomaly detection | Statistical Z-score analysis |
| Demand forecasting | Prophet |
| Containerization | Docker and Docker Compose |
| Version control | Git and GitHub |

## System Architecture

The architecture diagram illustrates the data flow, database, automated workflows, analytics, forecasting, alerts, and dashboard.

![Retail Supply Chain Control Tower Architecture](docs/architecture.png)

Architecture source: `docs/architecture.mmd`

## Main Features

### 1. Data Preparation and Storage
- Loads the supply chain dataset into PostgreSQL.
- Stores products, inventory, suppliers, shipments, and orders in separate tables.
- Uses Python and Pandas for data preparation.

### 2. Automated Data Pipeline
Apache Airflow runs the `retail_supply_chain_pipeline` DAG hourly.

The workflow:
- Checks database connectivity and table records.
- Calculates supply chain performance metrics.
- Identifies unusual shipment delays and demand patterns.
- Generates demand forecasts for the next 30 days.
- Saves analytical results in PostgreSQL.

### 3. Anomaly Detection
Uses statistical Z-score analysis to identify unusual shipment-delay and demand patterns.

Results are stored in:

`public.supply_chain_anomalies`

### 4. Demand Forecasting
Uses Facebook Prophet to generate 30-day demand forecasts.

Results are stored in:

`public.demand_forecasts`

### 5. Automated Email Alerts
The `supply_chain_alerts` Airflow DAG checks for:
- Products with stock below their reorder point.
- Late shipments and shipments identified as having late-delivery risk.

Email notifications are sent for qualifying records. Notification history is stored in PostgreSQL to help prevent repeated alerts for the same records.

### 6. Interactive Dashboard
Apache Superset provides visualizations for:
- Total orders.
- Current stock by product and supplier.
- Low-stock products.
- Shipment status distribution.
- Late-delivery risk.
- Shipping-mode distribution.
- Average shipping days by supplier.
- Top products by order quantity.
- Order trends over time.
- Supplier delay what-if simulation.

## Project Validation Results

The following results were obtained from the project database and analytical tables.

| Metric | Result |
|---|---:|
| Products | 118 |
| Inventory records | 118 |
| Suppliers | 10 |
| Orders | 180,519 |
| Shipments | 180,519 |
| Shipment-delay anomaly records | 6,983 |
| Demand anomaly records | 185 |
| Total anomaly records | 7,168 |
| Demand forecast records | 3,540 |
| Products covered by forecasts | 118 |
| Products classified as stock at risk | 108 |
| Products classified as stock sufficient | 10 |

**Note:** Anomaly counts represent detected records, not model accuracy. Forecast records represent generated predictions, not verified forecast accuracy.
## Documentation

The following documents describe the system architecture, database structure, KPIs, and automated workflows.

- [System Architecture Diagram](docs/architecture.png)
- [Architecture Source File](docs/architecture.mmd)
- [Database Data Dictionary](docs/data_dictionary.md)
- [KPI Documentation](docs/KPI_Documentation.txt)
- [Airflow Workflow Documentation](docs/workflow_documentation.md)


## Project Structure


Generated data, runtime logs, local configuration, and secrets are excluded from Git.

## Setup and Installation

### Prerequisites
retail-supply-chain-control-tower/
│
├── dags/
│   ├── supply_chain_pipeline.py
│   └── supply_chain_alerts.py
│
├── docs/
│   ├── architecture.mmd
│   ├── architecture.png
│   ├── data_dictionary.md
│   ├── KPI_Documentation.txt
│   └── workflow_documentation.md
│
├── sql/
│
├── tests/
│   └── test_results.md
│
├── data/
│   ├── raw/
│   └── processed/
│
├── 01_data_exploration.ipynb
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
- Windows, Linux, or macOS
- Python environment
- Docker Desktop and Docker Compose
- PostgreSQL
- Git
- Apache Superset (configured separately)

### 1. Clone the repository

```bash
git clone https://github.com/ahersakshi364-bit/retail-supply-chain-control-tower.git
cd retail-supply-chain-control-tower
```

### 2. Configure environment variables

Copy the example environment file:

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

Edit `.env` and replace the example values with your own configuration.

Required variables:

- `AIRFLOW_UID`
- `FERNET_KEY`
- `GMAIL_SENDER`
- `GMAIL_APP_PASSWORD`
- `GMAIL_RECEIVER`

Keep `.env` private. Never commit passwords, application passwords, or other secrets.

### 3. Prepare PostgreSQL

Install and start PostgreSQL. Create a database named:

```text
retail_supply_chain
```

Create a PostgreSQL user with the necessary permissions for the project database.

Use `01_data_exploration.ipynb` to prepare the dataset and load the project tables into PostgreSQL. The notebook requests the database password interactively.

### 4. Configure the Airflow PostgreSQL connection

Start Airflow first, then open the Airflow web interface.

Create a connection with these settings:

| Field | Value |
|---|---|
| Connection ID | `retail_postgres` |
| Connection Type | PostgreSQL |
| Host | `host.docker.internal` |
| Database | `retail_supply_chain` |
| Login | Your PostgreSQL project username |
| Port | `5432` |
| Password | Your PostgreSQL project password |

`host.docker.internal` allows Docker containers to reach PostgreSQL running on the host machine. If PostgreSQL is hosted elsewhere, use the appropriate database hostname.

### 5. Start Apache Airflow

Build and start the Airflow services:

```bash
docker compose up -d --build
```

Check the running services:

```bash
docker compose ps
```

Open Airflow:

http://localhost:8080

Log in using the Airflow credentials configured for your local environment.

### 6. Run the workflows

In Airflow, enable and run:

- `retail_supply_chain_pipeline`
- `supply_chain_alerts`

The main pipeline performs database checks, analytics, anomaly detection, and demand forecasting. The alert workflow checks qualifying low-stock products and late shipments and sends email notifications.

### 7. Configure Apache Superset

Apache Superset is configured separately and is not started by this project's Docker Compose file.

Install or start Superset separately, then configure a PostgreSQL database connection to the `retail_supply_chain` database.

Open the dashboard at:

http://localhost:8088

The Superset database connection must use a hostname and credentials accessible from the Superset environment.

## Limitations

- The project uses historical supply chain data rather than live operational feeds.
- The dataset represents historical records from 2015â€“2018; forecasts are not live 2026 demand predictions.
- The supplier-delay what-if simulation uses a fixed seven-day scenario.
- Anomaly counts indicate flagged records and do not establish detection accuracy.
- Stock-risk classifications are based on forecast-versus-stock comparisons and do not prove actual stockouts.
- Forecast accuracy requires evaluation against actual future demand.

## Future Improvements

- Integrate live data ingestion.
- Add interactive what-if controls.
- Evaluate forecasting performance using suitable accuracy metrics.
- Improve anomaly detection with additional statistical and machine-learning methods.
- Extend alerting and monitoring capabilities.

## Author

Developed as a Retail & Supply Chain Control Tower project to demonstrate data engineering, analytics, workflow automation, forecasting, and dashboard development.

**GitHub Repository:**
https://github.com/ahersakshi364-bit/retail-supply-chain-control-tower
