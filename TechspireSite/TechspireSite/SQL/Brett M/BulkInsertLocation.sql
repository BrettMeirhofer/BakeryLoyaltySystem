BULK INSERT "Location"
FROM "D:\Dev\Python\TechspireProject\TechspireSite\TechspireSite\SQL\Data\LocationList.tsv"
WITH
	(
	CHECK_CONSTRAINTS,
	FIELDTERMINATOR = '\t',
	ROWTERMINATOR = '\n',
	KEEPIDENTITY
	)
GO