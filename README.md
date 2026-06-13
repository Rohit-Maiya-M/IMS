# Smart Inventory Management System (IMS)

A modern, high-performance, and secure **Inventory Management System (IMS)** built using **Python (CustomTkinter)** and **MySQL 8.0**. The application provides role-based access control, supplier-level data isolation, inventory analytics, transaction management, and an administrative SQL management interface.

---

## 📖 Overview

The Smart Inventory Management System is designed to streamline inventory operations for organizations that manage products, suppliers, warehouses, and customer transactions.

The system supports three primary user roles:

* **Admin (Product Manager)**
* **Supplier**
* **Customer**

Each role receives a dedicated dashboard with functionality tailored to its responsibilities.

---

## ✨ Features

### 🎨 Modern User Interface

* Built with **CustomTkinter** for a modern desktop experience.
* Responsive dashboard layouts.
* Dark and Light mode support.
* Sidebar navigation architecture.
* Centralized card-based information panels.

### 🔐 Role-Based Access Control (RBAC)

#### Admin Dashboard

* Full inventory management.
* Product CRUD operations.
* Supplier onboarding and management.
* Warehouse monitoring.
* Transaction history analysis.
* Low-stock alerts and reorder monitoring.
* SQL Developer Panel for debugging and administrative operations.

#### Supplier Dashboard

* Supplier-specific inventory visibility.
* Product registration and updates.
* Inward stock processing.
* Restricted access to owned inventory only.

#### Customer Dashboard

* Browse available products.
* Search inventory in real time.
* Purchase products.
* Generate transaction receipts.

---

## 🛡️ Security Features

### Password Security

* SHA-256 password hashing.
* Secure credential verification.
* No plaintext password storage.

### SQL Injection Protection

* Parameterized queries throughout the application.
* Strict input validation.
* Stored procedure-based business operations.

### Multi-Tenant Data Isolation

Suppliers can only access products belonging to their own organization.

Cross-supplier access attempts are blocked through both:

* Application-level validation
* Database-level enforcement

### Anti-Tampering Protection

Inventory modifications are validated against ownership constraints.

Unauthorized stock operations trigger:

```sql
SQLSTATE '45000'
```

and are automatically rejected.

---

## 📊 Analytics Dashboard

The dashboard provides live inventory insights including:

* Total Products
* Total Suppliers
* Total Warehouses
* Total Transactions
* Low Stock Products
* Storage Capacity Utilization
* Inventory Valuation Metrics

---

## 🏗️ Technology Stack

| Layer         | Technology              |
| ------------- | ----------------------- |
| Frontend      | Python 3.12+            |
| UI Framework  | CustomTkinter           |
| Database      | MySQL 8.0+              |
| Driver        | mysql-connector-python  |
| Configuration | python-dotenv           |
| Security      | SHA-256 Hashing         |
| Architecture  | Stored Procedure Driven |

---

## 📂 Project Structure

```text
IMS/
├── database/
│   ├── 01_schema.sql
│   ├── 02_views.sql
│   └── 03_stored_procedures.sql
│
├── src/
│   ├── db/
│   │   └── connection.py
│   │
│   ├── ui/
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── customer.py
│   │   ├── supplier.py
│   │   ├── theme.py
│   │   └── widgets.py
│   │
│   └── main.py
│
├── .env
└── README.md
```

---

## 🗄️ Database Design

The system follows **Third Normal Form (3NF)** principles.

### Core Entities

* Supplier
* Warehouse
* Product
* User
* Transaction
* Supplier_Phone
* User_Phone
* Product_Transaction

### Relationships

* One Supplier → Many Products
* One Warehouse → Many Products
* One User → Many Transactions
* One Product → Many Transactions

---

## ⚙️ Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/IMS.git
cd IMS
```

---

### 2. Create Database

```sql
CREATE DATABASE ims_db;
USE ims_db;
```

Execute the database scripts in order:

```sql
SOURCE database/01_schema.sql;
SOURCE database/02_views.sql;
SOURCE database/03_stored_procedures.sql;
```

---

### 3. Configure Environment Variables

Create a `.env` file in the project root.

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ims_db
DB_USER=root
DB_PASSWORD=your_mysql_password
```

---

### 4. Install Dependencies

```bash
pip install customtkinter
pip install mysql-connector-python
pip install python-dotenv
```

or

```bash
pip install -r requirements.txt
```

---

### 5. Launch Application

```bash
python src/main.py
```

---

## 🔄 Application Workflow

### Authentication Flow

1. User enters credentials.
2. Password hash verification occurs.
3. Role is determined.
4. Appropriate dashboard loads.

### Inventory Flow

1. Supplier registers products.
2. Inventory stored in warehouse.
3. Customer purchases products.
4. Transaction records generated.
5. Stock quantities update automatically.

---

## 📈 Stored Procedure Layer

The application delegates critical business operations to MySQL stored procedures.

Examples include:

* User Authentication
* Product Registration
* Stock Updates
* Transaction Processing
* Inventory Reporting
* Supplier Validation

Benefits:

* Reduced network overhead
* Centralized business logic
* Enhanced security
* Improved performance

---

## 🧪 SQL Developer Panel

Administrative users have access to an embedded SQL console.

Capabilities:

* Execute custom SQL queries
* Inspect database state
* Validate stored procedure outputs
* Debug inventory workflows

**Access Restriction:** Admin role only.

---

## 🚨 Data Integrity Rules

### Product Constraints

* Product names must be unique.
* Stock quantity cannot be negative.
* Product price must be greater than or equal to zero.

### Warehouse Constraints

* Capacity must be greater than zero.

### User Constraints

* Email addresses must be unique.
* Role assignment controlled by system rules.

### Supplier Constraints

* Duplicate supplier emails are prohibited.

---

## 🔮 Future Enhancements

* Barcode Scanner Integration
* QR Code Product Tracking
* PDF Invoice Generation
* Email Notifications
* Advanced Sales Analytics
* Multi-Warehouse Transfers
* REST API Integration
* Cloud Deployment Support
* AI-Based Demand Forecasting

---

## 👨‍💻 Contributors

Developed as a Smart Inventory Management System project using Python, CustomTkinter, and MySQL.

---

## 📄 License

This project is intended for educational and academic purposes.

Feel free to modify and extend it according to your requirements.
