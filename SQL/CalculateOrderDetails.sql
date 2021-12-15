UPDATE "Order" 
SET original_total = Details.total_price,
	discount_amount = Details.discount,
	final_total = Details.total_price - Details.discount, 
	eligible_for_points = Details.total_eligible, 
	points_produced = (Floor(Details.total_eligible)/10), 
	points_consumed = Details.point_cost,
	points_total = (Floor(Details.total_eligible)/10) - Details.point_cost

	FROM
	(
	SELECT 
	StoreOrder.id,
	IFNULL(Eligible.total_price, 0) AS total_eligible,
	NotEligible.total_price AS total_price,
	IFNULL(Rewards.point_cost, 0) as point_cost,
	IFNULL(Rewards.discount, 0) as discount
	FROM "Order" AS StoreOrder

	LEFT JOIN (
		SELECT 
		SUM(OrderLine.total_price) AS total_price, OrderLine.order_id
		FROM OrderLine 
		WHERE points_eligible = 1
		GROUP BY order_id
		)
	AS Eligible ON Eligible.order_id = StoreOrder.id
	LEFT JOIN (
		SELECT 
		SUM(OrderLine.total_price) AS total_price, OrderLine.order_id
		FROM OrderLine 
		GROUP BY order_id)
	AS NotEligible ON NotEligible.order_id = StoreOrder.id
	LEFT JOIN (
		SELECT 
		SUM(OrderReward.point_cost) AS point_cost, 
		SUM(OrderReward.discount_amount) AS discount,
		OrderReward.order_id
		FROM OrderReward 
		GROUP BY order_id)
	AS Rewards ON Rewards.order_id = StoreOrder.id
	) AS Details
	WHERE Details.id = "Order".id