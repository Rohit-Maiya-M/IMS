-- =============================================================================
-- IMS Stored Procedures (Business Logic Layer)
-- =============================================================================

USE ims_db;

DELIMITER $$

-- 1. Authentication
DROP PROCEDURE IF EXISTS sp_authenticate$$
CREATE PROCEDURE sp_authenticate(
    IN p_email VARCHAR(255),
    IN p_password VARCHAR(255)
)
BEGIN
    DECLARE v_hash VARCHAR(64);
    SET v_hash = SHA2(p_password, 256);

    SELECT UserID, FName, LName, Email, Role, SupplierID, IsActive
    FROM User
    WHERE Email = p_email AND PasswordHash = v_hash AND IsActive = 1;
END$$

-- 2. Product Catalog
DROP PROCEDURE IF EXISTS sp_get_products$$
CREATE PROCEDURE sp_get_products(IN p_user_id INT UNSIGNED)
BEGIN
    DECLARE v_role VARCHAR(20);
    DECLARE v_supplier_id INT UNSIGNED;
    
    SELECT Role, SupplierID INTO v_role, v_supplier_id 
    FROM User 
    WHERE UserID = p_user_id;

    IF v_role = 'SUPPLIER' THEN
        SELECT p.ProductID, p.Name, p.Category, p.StockQuantity, p.Price, p.ReorderPoint, 
               s.SupplierName, w.Location AS WarehouseLocation
        FROM Product p
        INNER JOIN Supplier s ON s.SupplierID = p.SupplierID
        INNER JOIN Warehouse w ON w.WarehouseID = p.WarehouseID
        WHERE p.SupplierID = v_supplier_id
        ORDER BY p.Name;
    ELSE
        SELECT p.ProductID, p.Name, p.Category, p.StockQuantity, p.Price, p.ReorderPoint, 
               s.SupplierName, w.Location AS WarehouseLocation
        FROM Product p
        INNER JOIN Supplier s ON s.SupplierID = p.SupplierID
        INNER JOIN Warehouse w ON w.WarehouseID = p.WarehouseID
        ORDER BY p.Name;
    END IF;
END$$

DROP PROCEDURE IF EXISTS sp_get_products_by_category$$
CREATE PROCEDURE sp_get_products_by_category(IN p_category VARCHAR(80))
BEGIN
    SELECT p.ProductID, p.Name, p.Category, p.StockQuantity, p.Price, s.SupplierName
    FROM Product p
    INNER JOIN Supplier s ON s.SupplierID = p.SupplierID
    WHERE p.Category = p_category
    ORDER BY p.Name;
END$$

DROP PROCEDURE IF EXISTS sp_search_products$$
CREATE PROCEDURE sp_search_products(IN p_search_term VARCHAR(150))
BEGIN
    SELECT p.ProductID, p.Name, p.Category, p.StockQuantity, p.Price
    FROM Product p
    WHERE p.Name LIKE CONCAT('%', p_search_term, '%')
       OR p.Category LIKE CONCAT('%', p_search_term, '%')
    ORDER BY p.Name;
END$$

-- 3. Transactions
DROP PROCEDURE IF EXISTS sp_create_outward_transaction$$
CREATE PROCEDURE sp_create_outward_transaction(
    IN p_user_id INT UNSIGNED,
    IN p_product_id INT UNSIGNED,
    IN p_quantity INT UNSIGNED,
    OUT p_transaction_id INT UNSIGNED
)
BEGIN
    INSERT INTO `Transaction` (Type, Quantity, UserID, ProductID)
    VALUES ('OUTWARD', p_quantity, p_user_id, p_product_id);
    SET p_transaction_id = LAST_INSERT_ID();
END$$

DROP PROCEDURE IF EXISTS sp_create_inward_transaction$$
CREATE PROCEDURE sp_create_inward_transaction(
    IN p_user_id INT UNSIGNED,
    IN p_product_id INT UNSIGNED,
    IN p_quantity INT UNSIGNED,
    OUT p_transaction_id INT UNSIGNED
)
BEGIN
    DECLARE v_user_role VARCHAR(20);
    DECLARE v_user_supplier_id INT UNSIGNED;
    DECLARE v_product_supplier_id INT UNSIGNED;

    -- 1. Grab the role and linked supplier ID of the user trying to make the transaction
    SELECT Role, SupplierID INTO v_user_role, v_user_supplier_id 
    FROM User 
    WHERE UserID = p_user_id;

    -- 2. Grab the actual supplier ID who owns the targeted product
    SELECT SupplierID INTO v_product_supplier_id 
    FROM Product 
    WHERE ProductID = p_product_id;

    -- 3. Security Guard Check: If they are a SUPPLIER, ensure they own this product
    IF v_user_role = 'SUPPLIER' AND v_user_supplier_id <> v_product_supplier_id THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Security Violation: Suppliers may only restock their own registered products.';
    END IF;

    -- 4. If validation passes (or user is an ADMIN), execute the inward transaction safely
    INSERT INTO `Transaction` (Type, Quantity, UserID, ProductID)
    VALUES ('INWARD', p_quantity, p_user_id, p_product_id);
    
    SET p_transaction_id = LAST_INSERT_ID();
END$$

-- 4. Supplier & Product Management
DROP PROCEDURE IF EXISTS sp_register_product$$
CREATE PROCEDURE sp_register_product(
    IN p_user_id INT UNSIGNED, 
    IN p_name VARCHAR(150), 
    IN p_category VARCHAR(80),
    IN p_price DECIMAL(12, 2), 
    IN p_reorder_point INT UNSIGNED,
    IN p_warehouse_id INT UNSIGNED, 
    IN p_supplier_id INT UNSIGNED,
    IN p_initial_quantity INT UNSIGNED
)
BEGIN
    DECLARE v_effective_supplier_id INT UNSIGNED;
    DECLARE v_product_id INT UNSIGNED;
    DECLARE v_role VARCHAR(20);

    -- Look up the session creator's account profile details
    SELECT Role, SupplierID INTO v_role, v_effective_supplier_id 
    FROM User 
    WHERE UserID = p_user_id;

    -- If administrative manager overrides, adapt the targeted supplier record
    IF v_role = 'ADMIN' THEN
        SET v_effective_supplier_id = p_supplier_id;
    END IF;

    INSERT INTO Product (Name, Category, StockQuantity, Price, ReorderPoint, SupplierID, WarehouseID)
    VALUES (p_name, p_category, 0, p_price, COALESCE(p_reorder_point, 10), v_effective_supplier_id, p_warehouse_id);
    SET v_product_id = LAST_INSERT_ID();

    IF p_initial_quantity > 0 THEN
        CALL sp_create_inward_transaction(p_user_id, v_product_id, p_initial_quantity, @txn_id);
    END IF;
    SELECT v_product_id AS ProductID;
END$$

DROP PROCEDURE IF EXISTS sp_get_suppliers$$
CREATE PROCEDURE sp_get_suppliers()
BEGIN
    -- Rewritten safely using a subquery to guarantee compatibility under strict ONLY_FULL_GROUP_BY modes
    SELECT 
        s.SupplierID, 
        s.SupplierName, 
        s.Email, 
        s.City, 
        COALESCE(
            (SELECT GROUP_CONCAT(sp.Phone SEPARATOR ', ') 
             FROM Supplier_Phone sp 
             WHERE sp.SupplierID = s.SupplierID), 
            'No Phone Registered'
        ) AS PhoneNumbers
    FROM Supplier s
    ORDER BY s.SupplierID ASC;
END$$

-- 5. Warehouse Management
DROP PROCEDURE IF EXISTS sp_get_warehouses$$
CREATE PROCEDURE sp_get_warehouses()
BEGIN
    SELECT * FROM vw_warehouse_availability ORDER BY Location;
END$$

-- 6. Admin Reporting
DROP PROCEDURE IF EXISTS sp_get_transactions$$
CREATE PROCEDURE sp_get_transactions(IN p_limit INT UNSIGNED)
BEGIN
    SELECT * FROM vw_Transaction_Summary ORDER BY TransactionDate DESC LIMIT 100;
END$$

DROP PROCEDURE IF EXISTS sp_get_reorder_alerts$$
CREATE PROCEDURE sp_get_reorder_alerts()
BEGIN
    SELECT * FROM vw_Reorder_Alerts ORDER BY StockQuantity ASC;
END$$

-- 7. User Management
DROP PROCEDURE IF EXISTS sp_create_user$$
CREATE PROCEDURE sp_create_user(
    IN p_admin_id INT UNSIGNED, IN p_fname VARCHAR(80), IN p_lname VARCHAR(80),
    IN p_email VARCHAR(255), IN p_password VARCHAR(255),
    IN p_role ENUM('CUSTOMER', 'SUPPLIER', 'ADMIN'),
    IN p_street VARCHAR(200), IN p_city VARCHAR(100), IN p_zip VARCHAR(20),
    IN p_supplier_id INT UNSIGNED, IN p_phone VARCHAR(20)
)
BEGIN
    INSERT INTO User (FName, LName, Email, PasswordHash, Role, Street, City, Zip, SupplierID)
    VALUES (p_fname, p_lname, p_email, SHA2(p_password, 256), p_role, p_street, p_city, p_zip, p_supplier_id);
    SELECT LAST_INSERT_ID() AS UserID;
END$$

DELIMITER ;