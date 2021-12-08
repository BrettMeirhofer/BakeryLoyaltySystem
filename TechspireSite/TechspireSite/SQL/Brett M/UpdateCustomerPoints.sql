--Updates the calculated points for every customer based off their point-logs
UPDATE Customer
SET Customer.points_earned = IsNull(Prod.points_produced, 0), 
Customer.points_spent = IsNull(-Cons.points_produced, 0),
Customer.point_total = IsNull(Prod.points_produced, 0) - IsNull(-Cons.points_produced, 0)
FROM Customer
FULL JOIN
(SELECT SUM(PointLog.points_amount) as points_produced,PointLog.customer_id FROM PointLog
WHERE PointLog.points_amount >= 0
GROUP BY PointLog.customer_id) AS Prod ON Prod.customer_id = Customer.id
FULL JOIN
(SELECT SUM(PointLog.points_amount) as points_produced,PointLog.customer_id FROM PointLog
WHERE PointLog.points_amount < 0
GROUP BY PointLog.customer_id) AS Cons ON Cons.customer_id = Customer.id
