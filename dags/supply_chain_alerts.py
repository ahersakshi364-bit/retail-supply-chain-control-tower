
from datetime import datetime
import os
from html import escape

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.email import send_email


@dag(
    dag_id="supply_chain_alerts",
    schedule="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["supply-chain", "alerts"],
)
def supply_chain_alerts():

    @task
    def check_and_send_alerts():

        hook = PostgresHook(
            postgres_conn_id="retail_postgres"
        )

        # Create a table to remember alerts already sent
        hook.run("""
            CREATE TABLE IF NOT EXISTS public.alert_notification_history (
                alert_key TEXT PRIMARY KEY,
                alert_type TEXT,
                entity_id TEXT,
                notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Find products with newly detected low stock
        low_stock = hook.get_records("""
            SELECT
                i.product_id,
                i.current_stock,
                i.reorder_point
            FROM public.inventory i
            WHERE i.current_stock < i.reorder_point
              AND NOT EXISTS (
                  SELECT 1
                  FROM public.alert_notification_history a
                  WHERE a.alert_key =
                      'LOW_STOCK:' || i.product_id::text
              )
            ORDER BY i.current_stock ASC;
        """)

        # Find newly detected late shipments
        late_shipments = hook.get_records("""
            SELECT
                sh.shipment_id,
                sh.order_id,
                sh.supplier_id,
                sh.delivery_status,
                sh.actual_shipping_days,
                sh.scheduled_shipping_days
            FROM public.shipments sh
            WHERE (
                sh.delivery_status = 'Late delivery'
                OR sh.late_delivery_risk = 1
            )
            AND NOT EXISTS (
                SELECT 1
                FROM public.alert_notification_history a
                WHERE a.alert_key =
                    'LATE_SHIPMENT:' || sh.shipment_id::text
            )
            ORDER BY
                sh.actual_shipping_days -
                sh.scheduled_shipping_days DESC NULLS LAST
            LIMIT 100;
        """)

        # Stop if there are no new alerts
        if not low_stock and not late_shipments:
            print("No new supply-chain alerts.")
            return

        receiver = os.environ.get("GMAIL_RECEIVER")

        if not receiver:
            raise ValueError(
                "GMAIL_RECEIVER environment variable is missing."
            )

        # Prepare the email
        email_body = """
        <h2>Retail & Supply Chain Control Tower</h2>
        <p>New supply-chain alerts were detected.</p>
        """

        if low_stock:
            email_body += "<h3>Low Stock Products</h3><ul>"

            for product_id, stock, reorder_point in low_stock:
                email_body += (
                    f"<li>Product {escape(str(product_id))}: "
                    f"Stock = {stock}, "
                    f"Reorder Point = {reorder_point}</li>"
                )

            email_body += "</ul>"

        if late_shipments:
            email_body += "<h3>Late Shipments</h3><ul>"

            for shipment_id, order_id, supplier_id, status, actual, scheduled in late_shipments:
                email_body += (
                    f"<li>Shipment {escape(str(shipment_id))}, "
                    f"Order {escape(str(order_id))}, "
                    f"Supplier {escape(str(supplier_id))}: "
                    f"{escape(str(status))}; "
                    f"Actual days = {actual}, "
                    f"Scheduled days = {scheduled}</li>"
                )

            email_body += "</ul>"

        # Send the email
        send_email(
            to=receiver,
            subject="Supply Chain Alert - Action Required",
            html_content=email_body,
        )

        # Record alerts only after the email is sent successfully
        for product_id, stock, reorder_point in low_stock:
            hook.run(
                """
                INSERT INTO public.alert_notification_history
                    (alert_key, alert_type, entity_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (alert_key) DO NOTHING;
                """,
                parameters=(
                    f"LOW_STOCK:{product_id}",
                    "LOW_STOCK",
                    str(product_id),
                ),
            )

        for shipment in late_shipments:
            shipment_id = shipment[0]

            hook.run(
                """
                INSERT INTO public.alert_notification_history
                    (alert_key, alert_type, entity_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (alert_key) DO NOTHING;
                """,
                parameters=(
                    f"LATE_SHIPMENT:{shipment_id}",
                    "LATE_SHIPMENT",
                    str(shipment_id),
                ),
            )

        print(
            f"Email sent. Low-stock alerts: {len(low_stock)}; "
            f"late-shipment alerts: {len(late_shipments)}"
        )

    check_and_send_alerts()


supply_chain_alerts()
