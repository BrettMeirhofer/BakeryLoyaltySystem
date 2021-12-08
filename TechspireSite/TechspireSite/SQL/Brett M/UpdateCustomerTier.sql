UPDATE Customer
SET Customer.tier_id = T.tier
FROM Customer
INNER JOIN
(SELECT Customer.id AS cust_id, Max(Tier.id) AS tier, MIN(points_earned - min_points) AS calc FROM Tier
CROSS JOIN Customer
WHERE (points_earned - min_points) >= 0
GROUP BY Customer.id) AS T ON Customer.id = T.cust_id
