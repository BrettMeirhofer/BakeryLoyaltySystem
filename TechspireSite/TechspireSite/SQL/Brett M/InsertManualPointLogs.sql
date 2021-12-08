--Randomly selects 10% of orders to generate instances of employees manually adding points to the associated customer
INSERT INTO PointLog(points_amount, created_date, customer_id, employee_id, order_id, reason_id)
SELECT TOP 10 PERCENT
abs(checksum(NewId()) % 100) as points, order_date, customer_id, employee_id, id, 1 as reason
  FROM "Order"
  ORDER BY NEWID()

INSERT INTO PointLog(points_amount, created_date, customer_id, employee_id, order_id, reason_id)
SELECT TOP 10 PERCENT
abs(checksum(NewId()) % 100) as points, order_date, customer_id, employee_id, id, 2 as reason
  FROM "Order"
  ORDER BY NEWID()
