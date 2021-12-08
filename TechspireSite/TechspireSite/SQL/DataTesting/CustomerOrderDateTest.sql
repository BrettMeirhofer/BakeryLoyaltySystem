SELECT cust_orders.id, date_diff 
FROM
(
SELECT Customer.id, DATEDIFF(day, begin_date, order_date) AS date_diff FROM Customer
INNER JOIN "Order" ON "Order".customer_id = Customer.id
) AS cust_orders
WHERE date_diff < 0