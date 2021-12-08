--The same as UpdateCustomerPoints but instead a variable is used to determine which customer is updated
DECLARE @CustID INT;
SET @CustID = %s

UPDATE Customer
SET Customer.points_earned = Points.points_produced
FROM Customer
INNER JOIN
(SELECT SUM(PointLog.points_amount) as points_produced,PointLog.customer_id FROM PointLog
WHERE PointLog.points_amount >= 0
AND PointLog.customer_id = @CustID
GROUP BY PointLog.customer_id) AS Points ON Points.customer_id = Customer.id
WHERE Customer.id = @CustID

UPDATE Customer
SET Customer.points_spent = -Points.points_produced
FROM Customer
INNER JOIN
(SELECT SUM(PointLog.points_amount) as points_produced,PointLog.customer_id FROM PointLog
WHERE PointLog.points_amount < 0
AND PointLog.customer_id = @CustID
GROUP BY PointLog.customer_id) AS Points ON Points.customer_id = Customer.id
WHERE Customer.id = @CustID

UPDATE Customer
SET Customer.point_total = Customer.points_earned - Customer.points_spent
WHERE Customer.id = @CustID

UPDATE Customer
SET Customer.tier_id = T.tier
FROM Customer
INNER JOIN
(SELECT Customer.id AS cust_id, Max(Tier.id) AS tier, MIN(points_earned - min_points) AS calc FROM Tier
CROSS JOIN Customer
WHERE (points_earned - min_points) >= 0 AND
Customer.id = @CustID
GROUP BY Customer.id) AS T ON Customer.id = T.cust_id
WHERE Customer.id = @CustID