import statistics
from collections import defaultdict
from datetime import datetime, timedelta

import pandas as pd
from prophet import Prophet
from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook


@dag(
    dag_id="retail_supply_chain_pipeline",
    description="Hourly Retail and Supply Chain Control Tower pipeline",
    start_date=datetime(2026, 11, 23),
    schedule="@hourly",
    catchup=False,
    tags=["retail", "supply-chain"],
)
def supply_chain_pipeline():

    @task
    def check_database():
        hook = PostgresHook(
            postgres_conn_id="retail_postgres"
        )

        tables = [
            "products",
            "inventory",
            "suppliers",
            "shipments",
            "orders",
        ]

        print("Retail Supply Chain Pipeline Started!")

        for table in tables:
            result = hook.get_first(
                f"SELECT COUNT(*) FROM public.{table}"
            )
            print(f"{table}: {result[0]} records")

        print("Database check completed successfully!")

        # Inspect columns for all five tables
        print("\n===== TABLE COLUMN DETAILS =====")

        query = """
        SELECT
            table_schema,
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name IN (
            'products',
            'inventory',
            'suppliers',
            'shipments',
            'orders'
        )
        ORDER BY table_name, ordinal_position;
        """

        columns = hook.get_records(query)

        for column in columns:
            print(column)

        print("Column inspection completed!")
        # Inspect sample records
        print("\n===== INVENTORY SAMPLE =====")
        inventory_rows = hook.get_records(
            "SELECT * FROM public.inventory LIMIT 5"
        )
        for row in inventory_rows:
            print(row)

        print("\n===== SHIPMENTS SAMPLE =====")
        shipment_rows = hook.get_records(
            "SELECT * FROM public.shipments LIMIT 5"
        )
        for row in shipment_rows:
            print(row)

        print("\n===== SUPPLIERS SAMPLE =====")
        supplier_rows = hook.get_records(
            "SELECT * FROM public.suppliers LIMIT 5"
        )
        for row in supplier_rows:
            print(row)
        # Calculate Supply Chain KPIs
        print("\n===== SUPPLY CHAIN KPI RESULTS =====")

        # Inventory KPIs
        inventory_kpis = hook.get_first("""
            SELECT
                COUNT(*) AS total_products,
                COUNT(*) FILTER (WHERE current_stock <= 0) AS out_of_stock,
                COUNT(*) FILTER (WHERE current_stock <= reorder_point) AS products_at_reorder_level,
                ROUND(AVG(days_of_inventory), 2) AS average_days_of_inventory
            FROM public.inventory;
        """)

        print("Total Products:", inventory_kpis[0])
        print("Out of Stock Products:", inventory_kpis[1])
        print("Products At or Below Reorder Point:", inventory_kpis[2])
        print("Average Days of Inventory:", inventory_kpis[3])

        # Delivery KPIs
        delivery_kpis = hook.get_first("""
            SELECT
                COUNT(*) AS total_shipments,
                COUNT(*) FILTER (
                    WHERE delivery_status IN ('Advance shipping', 'Shipping on time')
                ) AS on_time_shipments,
                COUNT(*) FILTER (
                    WHERE delivery_status = 'Late delivery'
                ) AS late_shipments
            FROM public.shipments;
        """)

        total_shipments = delivery_kpis[0]
        on_time_shipments = delivery_kpis[1]
        late_shipments = delivery_kpis[2]

        on_time_rate = (
            round((on_time_shipments / total_shipments) * 100, 2)
            if total_shipments else 0
        )

        print("Total Shipments:", total_shipments)
        print("On-Time Shipments:", on_time_shipments)
        print("Late Shipments:", late_shipments)
        print("On-Time Delivery Rate:", str(on_time_rate) + "%")

        # Supplier KPI
        supplier_kpi = hook.get_first("""
            SELECT ROUND(AVG(lead_time_days)::numeric, 2)
            FROM public.suppliers;
        """)

        print("Average Supplier Lead Time:", supplier_kpi[0], "days")

        print("===== KPI CALCULATIONS COMPLETED =====")
        
    
    @task
    def detect_anomalies():
        hook = PostgresHook(postgres_conn_id="retail_postgres")

        print("===== ANOMALY DETECTION STARTED =====")

        # Create a table to store detected anomalies
        hook.run("""
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
        """)

        # Keep only the latest detection results
        hook.run("TRUNCATE TABLE public.supply_chain_anomalies;")

        anomalies = []

        # 1. Detect unusually long shipment delays
        shipment_rows = hook.get_records("""
            SELECT
                shipment_id,
                product_id,
                shipping_date::date,
                GREATEST(actual_shipping_days - scheduled_shipping_days, 0)
            FROM public.shipments
            WHERE actual_shipping_days IS NOT NULL
              AND scheduled_shipping_days IS NOT NULL;
        """)

        delays = [float(row[3]) for row in shipment_rows]

        if len(delays) >= 5:
            average_delay = statistics.mean(delays)
            std_delay = statistics.pstdev(delays)

            if std_delay > 0:
                for row in shipment_rows:
                    shipment_id, product_id, event_date, delay = row
                    z_score = (float(delay) - average_delay) / std_delay

                    if z_score >= 2:
                        anomalies.append((
                            "SHIPMENT_DELAY",
                            shipment_id,
                            product_id,
                            event_date,
                            float(delay),
                            round(z_score, 2),
                            "Unusually long shipment delay detected"
                        ))

        # 2. Calculate daily demand for each product
        demand_rows = hook.get_records("""
            SELECT
                product_id,
                order_date::date,
                SUM(quantity)
            FROM public.orders
            WHERE order_date IS NOT NULL
            GROUP BY product_id, order_date::date
            ORDER BY product_id, order_date::date;
        """)

        product_demand = defaultdict(list)

        for product_id, event_date, daily_demand in demand_rows:
            product_demand[product_id].append(
                (event_date, float(daily_demand))
            )

        # Detect unusually high daily demand for each product
        for product_id, observations in product_demand.items():
            values = [value for _, value in observations]

            if len(values) < 5:
                continue

            average_demand = statistics.mean(values)
            std_demand = statistics.pstdev(values)

            if std_demand == 0:
                continue

            for event_date, demand in observations:
                z_score = (demand - average_demand) / std_demand

                if z_score >= 3:
                    anomalies.append((
                        "DEMAND_SPIKE",
                        None,
                        product_id,
                        event_date,
                        demand,
                        round(z_score, 2),
                        "Unusually high daily product demand detected"
                    ))

        # 3. Save anomalies in PostgreSQL
        if anomalies:
            connection = hook.get_conn()
            try:
                cursor = connection.cursor()
                cursor.executemany("""
                    INSERT INTO public.supply_chain_anomalies (
                        anomaly_type,
                        shipment_id,
                        product_id,
                        event_date,
                        observed_value,
                        z_score,
                        description
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, anomalies)
                connection.commit()
                cursor.close()
            finally:
                connection.close()

        print("Total anomalies detected:", len(anomalies))
        print("Shipment delay anomalies:", sum(
            1 for item in anomalies if item[0] == "SHIPMENT_DELAY"
        ))
        print("Demand spike anomalies:", sum(
            1 for item in anomalies if item[0] == "DEMAND_SPIKE"
        ))
        print("===== ANOMALY DETECTION COMPLETED =====")

    @task
    def forecast_demand():
        hook = PostgresHook(
            postgres_conn_id="retail_postgres"
        )
        print("===== PROPHET DEMAND FORECAST STARTED =====")

        # Create forecast results table
        hook.run("""
            CREATE TABLE IF NOT EXISTS public.demand_forecasts (
                forecast_id BIGSERIAL PRIMARY KEY,
                product_id INTEGER,
                forecast_date DATE,
                predicted_demand NUMERIC,
                current_stock INTEGER,
                stock_status VARCHAR(50),
                forecast_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Keep the latest forecast results
        hook.run("TRUNCATE TABLE public.demand_forecasts RESTART IDENTITY;")

        # Read historical daily demand
        demand_rows = hook.get_records("""
            SELECT
                product_id,
                order_date::date AS ds,
                SUM(quantity) AS y
            FROM public.orders
            WHERE order_date IS NOT NULL
            GROUP BY product_id, order_date::date
            ORDER BY product_id, ds;
        """)

        # Group demand by product
        product_data = defaultdict(list)

        for product_id, ds, quantity in demand_rows:
            product_data[product_id].append({
                "ds": ds,
                "y": float(quantity)
            })

        # Read current inventory
        inventory_rows = hook.get_records("""
            SELECT product_id, current_stock
            FROM public.inventory;
        """)

        stock_lookup = {
            product_id: current_stock
            for product_id, current_stock in inventory_rows
        }

        forecast_results = []

        # Forecast each product separately
        for product_id, observations in product_data.items():

            # Prophet needs at least 2 observations
            if len(observations) < 2:
                print(
                    f"Skipping product {product_id}: "
                    "not enough historical data"
                )
                continue
            df = pd.DataFrame(observations)

            # Convert dates to consistent daily timestamps
            df["ds"] = pd.to_datetime(df["ds"]).dt.normalize()

            # Convert demand to numeric values
            df["y"] = pd.to_numeric(df["y"], errors="coerce")

            # Remove invalid rows
            df = df.dropna(subset=["ds", "y"])

            # Combine all orders for the same product and date
            df = (
                df.groupby("ds", as_index=False)
                .agg({"y": "sum"})
                .sort_values("ds")
                .drop_duplicates(subset=["ds"])
                .reset_index(drop=True)
            )
           

            try:
                model = Prophet(
                    yearly_seasonality=False,
                    weekly_seasonality=True,
                    daily_seasonality=False
                )

                model.fit(df)

                future = model.make_future_dataframe(
                    periods=30,
                    freq="D"
                )

                prediction = model.predict(future)

                # Keep only the next 30 days
                future_forecast = prediction.tail(30)

                total_forecast = max(
                    0,
                    float(future_forecast["yhat"].sum())
                )

                current_stock = stock_lookup.get(product_id)

                if current_stock is None:
                    print(
                        f"Skipping product {product_id}: "
                        "inventory not found"
                    )
                    continue

                # Compare forecast demand with current stock
                if current_stock < total_forecast:
                    stock_status = "STOCK_AT_RISK"
                else:
                    stock_status = "STOCK_SUFFICIENT"

                for _, row in future_forecast.iterrows():
                    predicted_demand = max(
                        0,
                        float(row["yhat"])
                    )

                    forecast_results.append((
                        product_id,
                        row["ds"].date(),
                        round(predicted_demand, 2),
                        int(current_stock),
                        stock_status
                    ))

                print(
                    f"Product {product_id}: "
                    f"Forecast demand = {round(total_forecast, 2)}, "
                    f"Current stock = {current_stock}, "
                    f"Status = {stock_status}"
                )

            except Exception as error:
                import traceback

                print(
                    f"Forecast failed for product {product_id}: {error}"
                )
                traceback.print_exc()
        # Save all forecasts to PostgreSQL
        if forecast_results:
            connection = hook.get_conn()

            try:
                cursor = connection.cursor()

                cursor.executemany("""
                    INSERT INTO public.demand_forecasts (
                        product_id,
                        forecast_date,
                        predicted_demand,
                        current_stock,
                        stock_status
                    )
                    VALUES (%s, %s, %s, %s, %s);
                """, forecast_results)

                connection.commit()
                cursor.close()

            finally:
                connection.close()

        print("Forecast records saved:", len(forecast_results))
        print("===== PROPHET DEMAND FORECAST COMPLETED =====")

    database_check = check_database()
    anomaly_check = detect_anomalies()
    forecast_check = forecast_demand()

    database_check >> anomaly_check >> forecast_check

supply_chain_pipeline()
