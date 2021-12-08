SELECT TOP 5
CONCAT(first_name, ' ', last_name) AS "label", Totals.Earnings AS y
FROM Employee
INNER JOIN 
(SELECT "Order".employee_id, SUM(final_total) AS Earnings FROM "Order"
WHERE DATEDIFF(day, "Order".order_date, GETDATE()) < 30
GROUP BY employee_id) AS Totals
ON Totals.employee_id = Employee.id
ORDER BY Earnings DESC