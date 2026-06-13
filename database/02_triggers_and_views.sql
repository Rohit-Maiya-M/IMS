-- =============================================================================
-- IMS Triggers & Derived Views
-- =============================================================================

USE ims_db;

-- Derived attribute: Warehouse AvailableSpace = Capacity - occupied units
-- Occupied units approximated as sum of product stock quantities in warehouse.
CREATE OR REPLACE VIEW vw_Warehouse_Availability AS
SELECT
    w.WarehouseID,
    w.Location,
    w.Capacity,
    w.ManagerName,
    COALESCE(SUM(p.StockQuantity), 0) AS OccupiedUnits,
    GREATEST(
        CAST(w.Capacity AS SIGNED) - CAST(COALESCE(SUM(p.StockQuantity), 0) AS SIGNED),
        0
    ) AS AvailableSpace
FROM Warehouse w
LEFT JOIN Product p ON p.WarehouseID = w.WarehouseID
GROUP BY w.WarehouseID, w.Location, w.Capacity, w.ManagerName;

-- Derived attribute: Transaction line detail with computed line totals
CREATE OR REPLACE VIEW vw_Transaction_Summary AS
SELECT
    t.TransactionID,
    t.Type,
    t.TransactionDate,
    t.UserID,
    u.FName,
    u.LName,
    t.ProductID,
    p.Name AS ProductName,
    t.Quantity,
    t.TotalAmount,
    p.Category
FROM `Transaction` t
INNER JOIN User u ON u.UserID = t.UserID
INNER JOIN Product p ON p.ProductID = t.ProductID;

-- Reorder alert view (objective: automated low-stock notifications)
CREATE OR REPLACE VIEW vw_Reorder_Alerts AS
SELECT
    p.ProductID,
    p.Name,
    p.Category,
    p.StockQuantity,
    p.ReorderPoint,
    s.SupplierID,
    s.SupplierName,
    s.Email AS SupplierEmail
FROM Product p
INNER JOIN Supplier s ON s.SupplierID = p.SupplierID
WHERE p.StockQuantity <= p.ReorderPoint;

DELIMITER $$

-- Compute TotalAmount before insert (derived attribute)
CREATE TRIGGER trg_transaction_set_total_amount
BEFORE INSERT ON `Transaction`
FOR EACH ROW
BEGIN
    DECLARE v_price DECIMAL(12, 2);

    SELECT Price INTO v_price
    FROM Product
    WHERE ProductID = NEW.ProductID;

    IF v_price IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Product not found for transaction.';
    END IF;

    SET NEW.TotalAmount = NEW.Quantity * v_price;
END$$

-- Validate stock availability before outward transactions
CREATE TRIGGER trg_transaction_validate_outward
BEFORE INSERT ON `Transaction`
FOR EACH ROW
BEGIN
    DECLARE v_stock INT UNSIGNED;

    IF NEW.Type = 'OUTWARD' THEN
        SELECT StockQuantity INTO v_stock
        FROM Product
        WHERE ProductID = NEW.ProductID
        FOR UPDATE;

        IF v_stock IS NULL THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Product not found for outward transaction.';
        END IF;

        IF v_stock < NEW.Quantity THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Insufficient stock for outward transaction.';
        END IF;
    END IF;
END$$

-- Spec-required trigger: auto-update Product.StockQuantity on Transaction INSERT
CREATE TRIGGER UpdateStockTrigger
AFTER INSERT ON `Transaction`
FOR EACH ROW
BEGIN
    IF NEW.Type = 'INWARD' THEN
        UPDATE Product
        SET StockQuantity = StockQuantity + NEW.Quantity
        WHERE ProductID = NEW.ProductID;
    ELSE
        UPDATE Product
        SET StockQuantity = StockQuantity - NEW.Quantity
        WHERE ProductID = NEW.ProductID;
    END IF;
END$$

-- Keep Product_Transaction bridge in sync when Transaction is recorded
CREATE TRIGGER trg_transaction_sync_product_transaction
AFTER INSERT ON `Transaction`
FOR EACH ROW
BEGIN
    DECLARE v_price DECIMAL(12, 2);

    SELECT Price INTO v_price
    FROM Product
    WHERE ProductID = NEW.ProductID;

    INSERT INTO Product_Transaction (ProductID, TransactionID, Quantity, UnitPrice)
    VALUES (NEW.ProductID, NEW.TransactionID, NEW.Quantity, v_price)
    ON DUPLICATE KEY UPDATE
        Quantity = VALUES(Quantity),
        UnitPrice = VALUES(UnitPrice);
END$$

DELIMITER ;
