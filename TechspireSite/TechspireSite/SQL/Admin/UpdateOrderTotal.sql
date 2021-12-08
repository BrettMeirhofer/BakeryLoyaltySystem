UPDATE "Order"
SET original_total = Totals.Total,
final_total = Totals.Total
FROM "Order"
INNER JOIN (
SELECT 
SUM(OrderLine.total_price) AS Total, OrderLine.order_id
FROM OrderLine 
GROUP BY OrderLine.order_id)
AS Totals ON Totals.order_id = "Order".id
WHERE "Order".id = %s