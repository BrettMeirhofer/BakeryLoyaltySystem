UPDATE Customer
SET points_spent = Points.Consumed,
	points_earned = Points.Produced,
	point_total = Points.Produced - Points.Consumed
	FROM
	(
	SELECT
		Customer.id,
		(IFNULL(LPlus.points, 0) + IFNULL(OrderPoints.produce, 0)) AS Produced,
		(IFNULL(-LRemove.points, 0) + IFNULL(OrderPoints.consume, 0)) AS Consumed
	FROM
		Customer
		LEFT JOIN (
				SELECT 
				SUM(PointLog.points_amount) AS points, PointLog.customer_id
				FROM PointLog 
				WHERE points_amount > 0
				GROUP BY customer_id
				)
			AS LPlus ON LPlus.customer_id = Customer.id
		LEFT JOIN (
				SELECT 
				SUM(PointLog.points_amount) AS points, PointLog.customer_id
				FROM PointLog 
				WHERE points_amount < 0
				GROUP BY customer_id
				)
			AS LRemove ON LRemove.customer_id = Customer.id
		LEFT JOIN (
				SELECT 
				SUM(points_produced) AS produce, 
				SUM(points_consumed) AS consume, 
				customer_id
				FROM "Order"
				GROUP BY customer_id
				)
			AS OrderPoints ON OrderPoints.customer_id = Customer.id
		) AS Points
		WHERE Points.id = Customer.id
