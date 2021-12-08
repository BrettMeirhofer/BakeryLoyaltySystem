--Brett Meirhofer
--Hotbreads Store Cashier Points Given
--Points can be exchanged for products using rewards making it an actual currency. This report will allow the client to pay close attention to how many points and thus money the cashiers at the Hotbreads locations are distributing to customers. Cashiers giving away excessive points can then be identified and their behavior corrected.
--Displays Cashiers at the Hotbreads locations and their individual totals for point transactions and total points given.
--Row Num,Employee Name,Email,Phone,Point Transactions,Points Given
--,,,phone,right,right

SELECT ROW_NUMBER() 
OVER(ORDER BY PSum desc) AS num_row, 
CONCAT(Employee.first_name,' ', Employee.last_name) AS 'Name',
Employee.email_address,
Employee.phone_number,
Points.PCount,
Points.PSum
FROM Employee
INNER JOIN EmployeeStatus ON Employee.employee_status_id = EmployeeStatus.id
INNER JOIN EmployeeJob ON Employee.id = EmployeeJob.employee_id
INNER JOIN
(SELECT employee_id, SUM(points_amount) AS PSum, COUNT(*) AS PCount FROM PointLog
WHERE (reason_id = 1 
OR reason_id = 2 
OR reason_id = 33)
AND points_amount > 0
GROUP BY employee_id) AS Points
ON Employee.id = Points.employee_id
WHERE EmployeeStatus.is_active = 1
AND EmployeeJob.store_id = 1
AND EmployeeJob.job_id = 2
