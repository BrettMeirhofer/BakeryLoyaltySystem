BULK INSERT Job
FROM "D:\Dev\Python\TechspireProject\TechspireSite\TechspireSite\SQL\Data\JobList.tsv"
WITH
	(
	CHECK_CONSTRAINTS,
	FIELDTERMINATOR = '\t',
	ROWTERMINATOR = '\n',
	KEEPIDENTITY 
	)
GO