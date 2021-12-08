SELECT * 
FROM Reward
INNER JOIN StoreReward ON StoreReward.reward_id = Reward.id
INNER JOIN RewardStatus ON RewardStatus.id = Reward.reward_status_id
WHERE StoreReward.store_id = %s AND
RewardStatus.is_active = 1 
