-- -- =============================================================================
-- -- IMS Database Schema (3NF)
-- -- Inventory Management System - Phase 1 Foundation
-- -- =============================================================================

-- DROP DATABASE IF EXISTS ims_db;
-- CREATE DATABASE ims_db
--   CHARACTER SET utf8mb4
--   COLLATE utf8mb4_unicode_ci;

-- USE ims_db;

-- -- -----------------------------------------------------------------------------
-- -- Core entity: Supplier
-- -- Composite Address flattened; multi-valued Phone -> Supplier_Phone
-- -- -----------------------------------------------------------------------------
-- CREATE TABLE Supplier (
--     SupplierID   INT UNSIGNED     NOT NULL AUTO_INCREMENT,
--     SupplierName VARCHAR(120)     NOT NULL,
--     Email        VARCHAR(255)     NOT NULL,
--     Street       VARCHAR(200)     NOT NULL,
--     City         VARCHAR(100)     NOT NULL,
--     Zip          VARCHAR(20)      NOT NULL,
--     CreatedAt    DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     PRIMARY KEY (SupplierID),
--     UNIQUE KEY uq_supplier_email (Email),
--     CONSTRAINT chk_supplier_email CHECK (Email LIKE '%@%')
-- ) ENGINE=InnoDB;

-- CREATE TABLE Supplier_Phone (
--     SupplierID INT UNSIGNED NOT NULL,
--     Phone      VARCHAR(20)  NOT NULL,
--     PRIMARY KEY (SupplierID, Phone),
--     CONSTRAINT fk_supplier_phone_supplier
--         FOREIGN KEY (SupplierID) REFERENCES Supplier (SupplierID)
--         ON UPDATE CASCADE ON DELETE CASCADE
-- ) ENGINE=InnoDB;

-- -- -----------------------------------------------------------------------------
-- -- Core entity: Warehouse
-- -- AvailableSpace is derived via view (see 02_views.sql)
-- -- -----------------------------------------------------------------------------
-- CREATE TABLE Warehouse (
--     WarehouseID INT UNSIGNED  NOT NULL AUTO_INCREMENT,
--     Location    VARCHAR(200)  NOT NULL,
--     Capacity    INT UNSIGNED  NOT NULL,
--     ManagerName VARCHAR(120)  NOT NULL,
--     CreatedAt   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     PRIMARY KEY (WarehouseID),
--     CONSTRAINT chk_warehouse_capacity CHECK (Capacity > 0)
-- ) ENGINE=InnoDB;

-- -- -----------------------------------------------------------------------------
-- -- Core entity: Product
-- -- Supplies (Supplier 1:M Product), Stored In (Product M:1 Warehouse)
-- -- -----------------------------------------------------------------------------
-- CREATE TABLE Product (
--     ProductID        INT UNSIGNED   NOT NULL AUTO_INCREMENT,
--     Name             VARCHAR(150)   NOT NULL,
--     Category         VARCHAR(80)    NOT NULL,
--     StockQuantity    INT UNSIGNED   NOT NULL DEFAULT 0,
--     Price            DECIMAL(12, 2) NOT NULL,
--     ReorderPoint     INT UNSIGNED   NOT NULL DEFAULT 10,
--     SupplierID       INT UNSIGNED   NOT NULL,
--     WarehouseID      INT UNSIGNED   NOT NULL,
--     CreatedAt        DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     UpdatedAt        DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP
--                                       ON UPDATE CURRENT_TIMESTAMP,
--     PRIMARY KEY (ProductID),
--     UNIQUE KEY uq_product_name (Name),
--     CONSTRAINT fk_product_supplier
--         FOREIGN KEY (SupplierID) REFERENCES Supplier (SupplierID)
--         ON UPDATE CASCADE ON DELETE RESTRICT,
--     CONSTRAINT fk_product_warehouse
--         FOREIGN KEY (WarehouseID) REFERENCES Warehouse (WarehouseID)
--         ON UPDATE CASCADE ON DELETE RESTRICT,
--     CONSTRAINT chk_product_price CHECK (Price >= 0),
--     CONSTRAINT chk_product_stock CHECK (StockQuantity >= 0),
--     CONSTRAINT chk_product_reorder CHECK (ReorderPoint >= 0)
-- ) ENGINE=InnoDB;

-- -- -----------------------------------------------------------------------------
-- -- Core entity: User
-- -- Role supports RBAC; SupplierID links supplier-role accounts to vendor records
-- -- -----------------------------------------------------------------------------
-- CREATE TABLE User (
--     UserID       INT UNSIGNED NOT NULL AUTO_INCREMENT,
--     FName        VARCHAR(80)  NOT NULL,
--     LName        VARCHAR(80)  NOT NULL,
--     Email        VARCHAR(255) NOT NULL,
--     PasswordHash VARCHAR(64)  NOT NULL,
--     Role         ENUM('CUSTOMER', 'SUPPLIER', 'ADMIN') NOT NULL DEFAULT 'CUSTOMER',
--     Street       VARCHAR(200) NOT NULL,
--     City         VARCHAR(100) NOT NULL,
--     Zip          VARCHAR(20)  NOT NULL,
--     SupplierID   INT UNSIGNED NULL,
--     IsActive     TINYINT(1)   NOT NULL DEFAULT 1,
--     CreatedAt    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     PRIMARY KEY (UserID),
--     UNIQUE KEY uq_user_email (Email),
--     CONSTRAINT fk_user_supplier
--         FOREIGN KEY (SupplierID) REFERENCES Supplier (SupplierID)
--         ON UPDATE CASCADE ON DELETE SET NULL,
--     CONSTRAINT chk_user_email CHECK (Email LIKE '%@%'),
--     CONSTRAINT chk_supplier_role_link CHECK (
--         (Role = 'SUPPLIER' AND SupplierID IS NOT NULL)
--         OR (Role <> 'SUPPLIER')
--     )
-- ) ENGINE=InnoDB;

-- CREATE TABLE User_Phone (
--     UserID INT UNSIGNED NOT NULL,
--     Phone  VARCHAR(20)  NOT NULL,
--     PRIMARY KEY (UserID, Phone),
--     CONSTRAINT fk_user_phone_user
--         FOREIGN KEY (UserID) REFERENCES User (UserID)
--         ON UPDATE CASCADE ON DELETE CASCADE
-- ) ENGINE=InnoDB;

-- -- -----------------------------------------------------------------------------
-- -- Core entity: Transaction
-- -- ProductID on Transaction enables UpdateStockTrigger on INSERT (per spec).
-- -- Product_Transaction bridge supports M:N Involved relationship.
-- -- TotalAmount is derived from Quantity * unit price at transaction time.
-- -- -----------------------------------------------------------------------------
-- CREATE TABLE `Transaction` (
--     TransactionID   INT UNSIGNED   NOT NULL AUTO_INCREMENT,
--     Type            ENUM('INWARD', 'OUTWARD') NOT NULL,
--     Quantity        INT UNSIGNED   NOT NULL,
--     TransactionDate DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     TotalAmount     DECIMAL(14, 2) NOT NULL DEFAULT 0.00,
--     UserID          INT UNSIGNED   NOT NULL,
--     ProductID       INT UNSIGNED   NOT NULL,
--     PRIMARY KEY (TransactionID),
--     CONSTRAINT fk_transaction_user
--         FOREIGN KEY (UserID) REFERENCES User (UserID)
--         ON UPDATE CASCADE ON DELETE RESTRICT,
--     CONSTRAINT fk_transaction_product
--         FOREIGN KEY (ProductID) REFERENCES Product (ProductID)
--         ON UPDATE CASCADE ON DELETE RESTRICT,
--     CONSTRAINT chk_transaction_quantity CHECK (Quantity > 0),
--     CONSTRAINT chk_transaction_amount CHECK (TotalAmount >= 0)
-- ) ENGINE=InnoDB;

-- -- Bridge: Product M:N Transaction (Involved)
-- CREATE TABLE Product_Transaction (
--     ProductID     INT UNSIGNED NOT NULL,
--     TransactionID INT UNSIGNED NOT NULL,
--     Quantity      INT UNSIGNED NOT NULL,
--     UnitPrice     DECIMAL(12, 2) NOT NULL,
--     PRIMARY KEY (ProductID, TransactionID),
--     CONSTRAINT fk_pt_product
--         FOREIGN KEY (ProductID) REFERENCES Product (ProductID)
--         ON UPDATE CASCADE ON DELETE RESTRICT,
--     CONSTRAINT fk_pt_transaction
--         FOREIGN KEY (TransactionID) REFERENCES `Transaction` (TransactionID)
--         ON UPDATE CASCADE ON DELETE CASCADE,
--     CONSTRAINT chk_pt_quantity CHECK (Quantity > 0),
--     CONSTRAINT chk_pt_unit_price CHECK (UnitPrice >= 0)
-- ) ENGINE=InnoDB;

-- -- Indexes for common access patterns
-- CREATE INDEX idx_product_category ON Product (Category);
-- CREATE INDEX idx_product_supplier ON Product (SupplierID);
-- CREATE INDEX idx_product_warehouse ON Product (WarehouseID);
-- CREATE INDEX idx_transaction_date ON `Transaction` (TransactionDate);
-- CREATE INDEX idx_transaction_user ON `Transaction` (UserID);
-- CREATE INDEX idx_transaction_product ON `Transaction` (ProductID);
-- CREATE INDEX idx_transaction_type ON `Transaction` (Type);


-- =============================================================================
-- IMS Database Schema (3NF) - Optimized for MySQL
-- =============================================================================

DROP DATABASE IF EXISTS ims_db;
CREATE DATABASE ims_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ims_db;

-- 1. PARENT TABLES (No Foreign Keys)
CREATE TABLE Supplier (
    SupplierID   INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    SupplierName VARCHAR(120)    NOT NULL,
    Email        VARCHAR(255)    NOT NULL,
    Street       VARCHAR(200)    NOT NULL,
    City         VARCHAR(100)    NOT NULL,
    Zip          VARCHAR(20)     NOT NULL,
    CreatedAt    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (SupplierID),
    UNIQUE KEY uq_supplier_email (Email),
    CONSTRAINT chk_supplier_email CHECK (Email LIKE '%@%')
) ENGINE=InnoDB;

CREATE TABLE Warehouse (
    WarehouseID INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    Location    VARCHAR(200)  NOT NULL,
    Capacity    INT UNSIGNED  NOT NULL,
    ManagerName VARCHAR(120)  NOT NULL,
    CreatedAt   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (WarehouseID),
    CONSTRAINT chk_warehouse_capacity CHECK (Capacity > 0)
) ENGINE=InnoDB;

-- 2. DEPENDENT TABLES (FKs to Parent Tables)
CREATE TABLE Product (
    ProductID      INT UNSIGNED   NOT NULL AUTO_INCREMENT,
    Name           VARCHAR(150)   NOT NULL,
    Category       VARCHAR(80)    NOT NULL,
    StockQuantity  INT UNSIGNED   NOT NULL DEFAULT 0,
    Price          DECIMAL(12, 2) NOT NULL,
    ReorderPoint   INT UNSIGNED   NOT NULL DEFAULT 10,
    SupplierID     INT UNSIGNED   NOT NULL,
    WarehouseID    INT UNSIGNED   NOT NULL,
    CreatedAt      DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt      DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (ProductID),
    UNIQUE KEY uq_product_name (Name),
    CONSTRAINT fk_product_supplier
        FOREIGN KEY (SupplierID) REFERENCES Supplier (SupplierID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_product_warehouse
        FOREIGN KEY (WarehouseID) REFERENCES Warehouse (WarehouseID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_product_price CHECK (Price >= 0),
    CONSTRAINT chk_product_stock CHECK (StockQuantity >= 0)
) ENGINE=InnoDB;

CREATE TABLE Supplier_Phone (
    SupplierID INT UNSIGNED NOT NULL,
    Phone      VARCHAR(20)  NOT NULL,
    PRIMARY KEY (SupplierID, Phone),
    CONSTRAINT fk_supplier_phone_supplier
        FOREIGN KEY (SupplierID) REFERENCES Supplier (SupplierID)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE User (
    UserID       INT UNSIGNED NOT NULL AUTO_INCREMENT,
    FName        VARCHAR(80)  NOT NULL,
    LName        VARCHAR(80)  NOT NULL,
    Email        VARCHAR(255) NOT NULL,
    PasswordHash VARCHAR(64)  NOT NULL,
    Role         ENUM('CUSTOMER', 'SUPPLIER', 'ADMIN') NOT NULL DEFAULT 'CUSTOMER',
    Street       VARCHAR(200) NOT NULL,
    City         VARCHAR(100) NOT NULL,
    Zip          VARCHAR(20)  NOT NULL,
    SupplierID   INT UNSIGNED NULL,
    IsActive     TINYINT(1)   NOT NULL DEFAULT 1,
    CreatedAt    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (UserID),
    UNIQUE KEY uq_user_email (Email),
    CONSTRAINT fk_user_supplier
        FOREIGN KEY (SupplierID) REFERENCES Supplier (SupplierID)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT chk_user_email CHECK (Email LIKE '%@%')
) ENGINE=InnoDB;

CREATE TABLE User_Phone (
    UserID INT UNSIGNED NOT NULL,
    Phone  VARCHAR(20)  NOT NULL,
    PRIMARY KEY (UserID, Phone),
    CONSTRAINT fk_user_phone_user
        FOREIGN KEY (UserID) REFERENCES User (UserID)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE `Transaction` (
    TransactionID   INT UNSIGNED   NOT NULL AUTO_INCREMENT,
    Type            ENUM('INWARD', 'OUTWARD') NOT NULL,
    Quantity        INT UNSIGNED   NOT NULL,
    TransactionDate DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    TotalAmount     DECIMAL(14, 2) NOT NULL DEFAULT 0.00,
    UserID          INT UNSIGNED   NOT NULL,
    ProductID       INT UNSIGNED   NOT NULL,
    PRIMARY KEY (TransactionID),
    CONSTRAINT fk_transaction_user
        FOREIGN KEY (UserID) REFERENCES User (UserID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_transaction_product
        FOREIGN KEY (ProductID) REFERENCES Product (ProductID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_transaction_quantity CHECK (Quantity > 0)
) ENGINE=InnoDB;

CREATE TABLE Product_Transaction (
    ProductID     INT UNSIGNED NOT NULL,
    TransactionID INT UNSIGNED NOT NULL,
    Quantity      INT UNSIGNED NOT NULL,
    UnitPrice     DECIMAL(12, 2) NOT NULL,
    PRIMARY KEY (ProductID, TransactionID),
    CONSTRAINT fk_pt_product
        FOREIGN KEY (ProductID) REFERENCES Product (ProductID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_pt_transaction
        FOREIGN KEY (TransactionID) REFERENCES `Transaction` (TransactionID)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- Indexes
CREATE INDEX idx_product_category ON Product (Category);
CREATE INDEX idx_transaction_date ON `Transaction` (TransactionDate);