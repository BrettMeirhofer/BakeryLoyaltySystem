--Brett Meirhofer
--Active Cashiers at HotBreads Store
--The client can use this report to contact Cashiers that currently work at the Hotbreads Location. Understaffing or overstaffing of Cashiers could be identified and corrected using this document in conjunction with other documents such as the store schedule.
--Displays all Cashiers that currently work at the Hotbreads location.
--Row Number,Type,Employee Name,Phone Number,Email Address
--,,,phone,

SELECT ROW_NUMBER() 
OVER(ORDER BY EmployeeType.id,Employee.first_name) AS num_row, 
EmployeeType.type_name, 
CONCAT(Employee.first_name,' ', Employee.last_name) AS 'Name', 
Employee.phone_number,
Employee.email_address
FROM EmployeeJob
INNER JOIN Employee ON Employee.id = EmployeeJob.employee_id
INNER JOIN EmployeeType ON Employee.employee_type_id = EmployeeType.id
INNER JOIN Job ON EmployeeJob.job_id = Job.id
INNER JOIN EmployeeStatus ON Employee.employee_status_id = EmployeeStatus.id
WHERE EmployeeJob.store_id = 1 
AND EmployeeJob.job_id = 2 
AND EmployeeStatus.is_active = 1



