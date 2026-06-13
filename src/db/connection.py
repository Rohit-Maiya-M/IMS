"""Thin database access layer — calls stored procedures only (except admin raw SQL)."""

from __future__ import annotations

from typing import Any

import mysql.connector
from mysql.connector import Error as MySQLError
from mysql.connector.cursor import MySQLCursor

from config import DB_CONFIG


class DatabaseError(Exception):
    """Raised when the database returns an error."""


class Database:
    def __init__(self) -> None:
        self._conn: mysql.connector.MySQLConnection | None = None

    def connect(self) -> None:
        if self._conn is None or not self._conn.is_connected():
            self._conn = mysql.connector.connect(**DB_CONFIG)

    def close(self) -> None:
        if self._conn and self._conn.is_connected():
            self._conn.close()
        self._conn = None

    @property
    def connection(self) -> mysql.connector.MySQLConnection:
        self.connect()
        assert self._conn is not None
        return self._conn

    def _cursor(self) -> MySQLCursor:
        return self.connection.cursor(dictionary=True)

    def call_procedure(
        self,
        name: str,
        args: tuple[Any, ...] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a stored procedure and return all result sets as row dicts."""
        args = args or ()
        cursor = self._cursor()
        rows: list[dict[str, Any]] = []
        try:
            cursor.callproc(name, args)
            for result in cursor.stored_results():
                rows.extend(result.fetchall())
            return rows
        except MySQLError as exc:
            raise DatabaseError(str(exc)) from exc
        finally:
            cursor.close()

    def call_procedure_with_out(
        self,
        name: str,
        in_args: tuple[Any, ...],
        out_var: str = "@out_id",
    ) -> int | None:
        """Call a procedure with an OUT parameter and return its value."""
        cursor = self._cursor()
        try:
            cursor.execute(f"SET {out_var} = NULL")
            placeholders = ", ".join(["%s"] * len(in_args) + [out_var])
            cursor.execute(f"CALL {name}({placeholders})", (*in_args,))
            while cursor.nextset():
                pass
            cursor.execute(f"SELECT {out_var} AS out_value")
            row = cursor.fetchone()
            return row["out_value"] if row else None
        except MySQLError as exc:
            raise DatabaseError(str(exc)) from exc
        finally:
            cursor.close()

    def execute_raw_sql(self, sql: str) -> tuple[list[str], list[dict[str, Any]], str | None]:
        """
        Admin-only raw SQL execution. Returns (columns, rows, message).
        Supports SELECT and other statements that produce result sets.
        """
        sql = sql.strip()
        if not sql:
            raise DatabaseError("SQL statement is empty.")

        cursor = self._cursor()
        try:
            cursor.execute(sql)
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                return columns, rows, None
            affected = cursor.rowcount
            return [], [], f"Query OK. Rows affected: {affected}"
        except MySQLError as exc:
            raise DatabaseError(str(exc)) from exc
        finally:
            cursor.close()

    def test_connection(self) -> None:
        """Utility to verify connection and print database name."""
        try:
            cursor = self._cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            name = list(db_name.values())[0] if isinstance(db_name, dict) else db_name[0]
            print(f"Successfully connected to database: {name}")
            cursor.close()
        except MySQLError as e:
            print(f"Connection test failed: {e}")

    def onboard_new_supplier(self, form_data: dict[str, Any]) -> dict[str, Any]:
        """Onboards a supplier company and creates their portal login profile natively."""
        cursor = self._cursor()
        try:
            # STEP A: Create the Supplier Entity record first
            supplier_query = """
                INSERT INTO Supplier (SupplierName, Email, Street, City, Zip)
                VALUES (%s, %s, %s, %s, %s)
            """
            supplier_values = (
                form_data['supplier_name'], 
                form_data['email'], 
                form_data['street'], 
                form_data['city'], 
                form_data['zip']
            )
            cursor.execute(supplier_query, supplier_values)
            new_supplier_id = cursor.lastrowid

            # STEP B: Create their Portal User Account using the retrieved ID
            user_query = """
                INSERT INTO User (FName, LName, Email, PasswordHash, Role, Street, City, Zip, SupplierID, IsActive)
                VALUES (%s, %s, %s, SHA2(%s, 256), 'SUPPLIER', %s, %s, %s, %s, 1)
            """
            user_values = (
                form_data['first_name'],
                form_data['last_name'],
                form_data['portal_email'],
                form_data['temporary_password'],
                form_data['street'], 
                form_data['city'], 
                form_data['zip'],
                new_supplier_id
            )
            cursor.execute(user_query, user_values)

            # Safely commit the changes over the connection property layer
            self.connection.commit()
            return {"success": True, "message": "Supplier onboarded safely!"}

        except MySQLError as e:
            self.connection.rollback()
            return {"success": False, "message": str(e)}
        finally:
            cursor.close()