--Brett Meirhofer
--Cashier Transaction Performance Active
--The client can use this report as one metric to access cashier performance. Cashiers with high customer spending may have skills that could be transferred to lower performing Cashiers increasing the overall revenue of the business.
--Displays all the active cashiers and the total amount of customer spending with them acting as the cashier.
--Row Number,Employee Name,Email,Type,Orders,Total Spending,Avg Spending
--,,,,right,right,right

SELECT ROW_NUMBER() OVER(ORDER BY Totals.total) AS "Row",
CONCAT(Employee.first_name, ' ', Employee.last_name)AS "Employee Name",
Employee.email_address AS Email,
EmployeeType.type_name AS "Type", 
Actions.total AS Orders, 
CONCAT('$', CAST(Totals.total as decimal(18,2)))AS "Total Sales", 
CONCAT('$', CAST(Totals.total/Actions.total as decimal(18,2))) AS "Avg Sales Per Order"
FROM
(SELECT
SUM ("ORDER".final_total) AS total, "Order".employee_id
FROM "ORDER"
GROUP BY "Order".employee_id)
AS Totals
INNER JOIN Employee on Employee.id = Totals.employee_id
INNER JOIN EmployeeType on Employee.employee_type_id = EmployeeType.id
INNER JOIN EmployeeStatus on Employee.employee_status_id = EmployeeStatus.id
INNER JOIN (SELECT
COUNT (*) AS total, "Order".employee_id
FROM "ORDER"
GROUP BY "Order".employee_id)
as Actions ON Employee.id = Actions.employee_id
WHERE EmployeeStatus.is_active = 1
