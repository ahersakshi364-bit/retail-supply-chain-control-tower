-- ============================================================
-- Retail & Supply Chain Control Tower
-- Business KPI SQL Queries
-- Database: PostgreSQL
-- ============================================================

-- 1. Total Orders
SELECT COUNT(*) AS total_order_items
FROM public.orders;


-- 2. Total Sales
SELECT ROUND(SUM(sales)::numeric, 2) AS total_sales
FROM public.orders;


-- 3. On-Time Delivery Rate
-- Advance shipping and Shipping on time are counted as on-time.
-- Canceled shipments are excluded from the denominator.

SELECT
    COUNT(*) FILTER (
        WHERE delivery_status <> 'Shipping canceled'
    ) AS eligible_shipments,

    COUNT(*) FILTER (
        WHERE delivery_status IN (
            'Advance shipping',
            'Shipping on time'
        )
    ) AS on_time_shipments,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE delivery_status IN (
                'Advance shipping',
                'Shipping on time'
            )
        ) / NULLIF(
            COUNT(*) FILTER (
                WHERE delivery_status <> 'Shipping canceled'
            ),
            0
        ),
        2
    ) AS on_time_delivery_percentage
FROM public.shipments;

-- 4. Average Supplier Lead Time
SELECT
    ROUND(AVG(lead_time_days)::numeric, 2)
        AS average_supplier_lead_time_days
FROM public.suppliers;


-- 5. Average Days of Inventory
SELECT
    ROUND(AVG(days_of_inventory), 2)
        AS average_days_of_inventory
FROM public.inventory;


-- 6. Products at Reorder Level
SELECT
    COUNT(*) AS products_at_reorder_level
FROM public.inventory
WHERE current_stock <= reorder_point;


-- 7. Low-Stock Products
-- Uses the same strict comparison as the alert DAG.
SELECT
    product_id,
    current_stock,
    reorder_point
FROM public.inventory
WHERE current_stock < reorder_point
ORDER BY current_stock ASC;


-- 8. Average Shipment Delay
SELECT
    ROUND(
        AVG(
            GREATEST(
                actual_shipping_days - scheduled_shipping_days,
                0
            )
        )::numeric,
        2
    ) AS average_shipment_delay_days
FROM public.shipments
WHERE actual_shipping_days IS NOT NULL
  AND scheduled_shipping_days IS NOT NULL;


-- 9. Late Delivery Risk
SELECT
    COUNT(*) AS total_shipments,
    COUNT(*) FILTER (
        WHERE delivery_status = 'Late delivery'
           OR late_delivery_risk = 1
    ) AS late_risk_shipments
FROM public.shipments;


-- 10. Supplier Performance
SELECT
    s.supplier_id,
    s.supplier_name,
    s.lead_time_days,
    s.supplier_status
FROM public.suppliers s
ORDER BY s.lead_time_days ASC;


-- 11. Inventory Status by Product
SELECT
    product_id,
    current_stock,
    reorder_point,
    safety_stock,
    days_of_inventory,
    CASE
        WHEN current_stock < reorder_point THEN 'LOW STOCK'
        WHEN current_stock <= reorder_point THEN 'AT REORDER LEVEL'
        ELSE 'SUFFICIENT STOCK'
    END AS inventory_status
FROM public.inventory
ORDER BY days_of_inventory ASC;


-- 12. Shipment Delay by Supplier
SELECT
    s.supplier_id,
    s.supplier_name,
    ROUND(
        AVG(
            GREATEST(
                sh.actual_shipping_days - sh.scheduled_shipping_days,
                0
            )
        )::numeric,
        2
    ) AS average_delay_days
FROM public.shipments sh
JOIN public.suppliers s
    ON sh.supplier_id = s.supplier_id
WHERE sh.actual_shipping_days IS NOT NULL
  AND sh.scheduled_shipping_days IS NOT NULL
GROUP BY s.supplier_id, s.supplier_name
ORDER BY average_delay_days DESC;

