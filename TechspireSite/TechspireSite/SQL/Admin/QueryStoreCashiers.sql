SELECT * 
FROM Employee
INNER JOIN EmployeeJob ON EmployeeJob.employee_id = Employee.id
INNER JOIN EmployeeStatus ON EmployeeStatus.id = Employee.employee_status_id
WHERE EmployeeJob.store_id = %s AND
EmployeeJob.job_id = 2 AND
EmployeeStatus.is_active = 1	