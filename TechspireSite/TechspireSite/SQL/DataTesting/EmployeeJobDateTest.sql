SELECT Employee.id, EMployee.begin_date, EmployeeJob.assign_date FROM Employee
INNER JOIN EmployeeJob ON Employee.id = EmployeeJob.employee_id
WHERE Employee.begin_date <> EmployeeJob.assign_date