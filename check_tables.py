
from airflow.providers.postgres.hooks.postgres import PostgresHook

hook = PostgresHook(postgres_conn_id="retail_postgres")

query = """
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
ORDER BY table_schema, table_name;
"""

results = hook.get_records(query)

for row in results:
    if row[1] in ["products", "inventory", "suppliers", "shipments", "orders"]:
        print(row)
