SELECT emp_orders.id, date_diff 
FROM
(
SELECT Employee.id, DATEDIFF(day, begin_date, order_date) AS date_diff FROM Employee
INNER JOIN "Order" ON "Order".employee_id = Employee.id
) AS emp_orders
WHERE date_diff < 0