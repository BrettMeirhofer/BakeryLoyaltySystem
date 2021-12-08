ALTER TABLE EmployeeJob ADD
    employee_id int NOT NULL FOREIGN KEY REFERENCES Employee(id),
    job_id int NOT NULL FOREIGN KEY REFERENCES Job(id),
    store_id int NOT NULL FOREIGN KEY REFERENCES Store(id);

ALTER TABLE Employee ADD
    location_id int NOT NULL FOREIGN KEY REFERENCES Location(id),
    employee_status_id int NOT NULL FOREIGN KEY REFERENCES EmployeeStatus(id),
    employee_type_id int NOT NULL FOREIGN KEY REFERENCES EmployeeType(id);

ALTER TABLE Location ADD
     state_id int NOT NULL FOREIGN KEY REFERENCES StateProvince(id) DEFAULT 1407,
     country_id int NOT NULL FOREIGN KEY REFERENCES Country(id) DEFAULT 233;
