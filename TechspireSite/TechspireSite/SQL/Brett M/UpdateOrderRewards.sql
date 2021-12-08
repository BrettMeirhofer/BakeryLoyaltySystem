--
UPDATE OrderReward
SET OrderReward.point_cost = Reward.point_cost,
OrderReward.discount_amount = Reward.discount_amount,
OrderReward.free_product_id = Reward.free_product_id
FROM OrderReward
INNER JOIN Reward ON OrderReward.reward_id = Reward.id
