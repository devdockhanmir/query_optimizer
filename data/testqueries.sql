-- Test Query 1
SELECT FirstName, LastName, SUM(TotalDue) AS TotalSpent
FROM SalesOrderHeader
JOIN Customer ON SalesOrderHeader.CustomerID = Customer.CustomerID
WHERE TotalDue > 10000;
