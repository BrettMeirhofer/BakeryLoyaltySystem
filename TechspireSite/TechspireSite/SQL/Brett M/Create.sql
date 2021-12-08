CREATE TABLE Employee(
    id int NOT NULL PRIMARY KEY IDENTITY(1,1),
    first_name nvarchar(40) NOT NULL,
    last_name nvarchar(40) NOT NULL,
    email_address nvarchar(254) NOT NULL,
    phone_number nvarchar(15) NOT NULL DEFAULT '+19043335252',
    comments nvarchar(max),
    birthdate date NOT NULL,
    begin_date date NOT NULL DEFAULT GETDATE(),
    end_date date,
);

CREATE TABLE EmployeeJob(
    id int NOT NULL PRIMARY KEY IDENTITY(1,1),
    assign_date date NOT NULL DEFAULT GETDATE(),
);

CREATE TABLE Job(
    id int NOT NULL PRIMARY KEY IDENTITY(1,1),
    job_name nvarchar(40) NOT NULL,
    job_desc nvarchar(200),
);

CREATE TABLE Location(
    id int NOT NULL PRIMARY KEY IDENTITY(1,1),
    zip_code nvarchar(10) NOT NULL DEFAULT 77339,
    city nvarchar(35) NOT NULL DEFAULT 'Houston',
    address nvarchar(100) NOT NULL DEFAULT '3242 StreetName',
);
