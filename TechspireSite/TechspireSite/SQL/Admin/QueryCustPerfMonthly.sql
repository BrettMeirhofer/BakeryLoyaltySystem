SELECT TOP 5
CONCAT(first_name, ' ', last_name) AS "label", Totals.Earnings AS y
FROM Customer
INNER JOIN 
(SELECT "Order".customer_id, SUM(final_total) AS Earnings FROM "Order"
WHERE DATEDIFF(day, "Order".order_date, GETDATE()) < 30
GROUP BY customer_id) AS Totals
ON Totals.customer_id = Customer.id
ORDER BY Earnings DESC