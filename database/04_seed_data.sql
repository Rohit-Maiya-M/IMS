-- =============================================================================
-- IMS Seed Data (development / demo)
-- Default password for all demo users: password123
-- SHA2('password123', 256) = 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74bcf41
-- =============================================================================

USE ims_db;

INSERT INTO Supplier (SupplierName, Email, Street, City, Zip) VALUES
('Acme Supplies Ltd', 'contact@acme-supplies.example', '42 Industrial Ave', 'Bangalore', '560001'),
('Global Parts Co', 'sales@globalparts.example', '15 Market Road', 'Bangalore', '560002');

INSERT INTO Supplier_Phone (SupplierID, Phone) VALUES
(1, '+91-9876543210'),
(1, '+91-9876543211'),
(2, '+91-9123456780');

INSERT INTO Warehouse (Location, Capacity, ManagerName) VALUES
('Central Warehouse - Whitefield', 10000, 'Rajesh Kumar'),
('South Hub - Electronic City', 5000, 'Priya Sharma');

INSERT INTO Product (Name, Category, StockQuantity, Price, ReorderPoint, SupplierID, WarehouseID) VALUES
('Wireless Mouse', 'Electronics', 150, 599.00, 20, 1, 1),
('USB-C Cable 2m', 'Electronics', 300, 299.00, 50, 1, 1),
('Office Chair', 'Furniture', 45, 8500.00, 5, 2, 2),
('A4 Paper Ream', 'Stationery', 200, 250.00, 30, 2, 1);

INSERT INTO User (FName, LName, Email, PasswordHash, Role, Street, City, Zip, SupplierID) VALUES
('Admin', 'User', 'admin@ims.local',
 '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74bcf41',
 'ADMIN', '1 Admin Block', 'Bangalore', '560001', NULL),
('John', 'Customer', 'customer@ims.local',
 '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74bcf41',
 'CUSTOMER', '10 Customer Lane', 'Bangalore', '560003', NULL),
('Sam', 'Supplier', 'supplier@ims.local',
 '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74bcf41',
 'SUPPLIER', '5 Vendor Street', 'Bangalore', '560004', 1);

INSERT INTO User_Phone (UserID, Phone) VALUES
(1, '+91-9000000001'),
(2, '+91-9000000002'),
(3, '+91-9000000003');
