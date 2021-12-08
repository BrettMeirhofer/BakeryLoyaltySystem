SELECT product_name AS "label", Totals.Sold AS y
FROM Product
INNER JOIN
(SELECT TOP 5
SUM(quantity) AS Sold, product_id
FROM OrderLine
INNER JOIN 
(SELECT "Order".id FROM "Order"
WHERE DATEDIFF(day, "Order".order_date, GETDATE()) < 30
) AS Totals
ON Totals.id = OrderLine.order_id
GROUP BY product_id) AS Totals
ON Totals.product_id = Product.id
Order BY Totals.Sold DESC