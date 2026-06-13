"""Admin (Product Manager) module — dashboard, suppliers onboarding, SQL console."""

from __future__ import annotations

import customtkinter as ctk

from db.connection import Database, DatabaseError
from ui.customer import CustomerFrame
from ui.supplier import SupplierFrame
from ui.widgets import (
    DataTable,
    FormCard,
    MetricsRow,
    SidebarLayout,
    action_button,
    form_field,
    page_header,
    show_error,
    show_info,
    show_warning,
)


class AdminFrame(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.Misc,
        db: Database,
        user: dict,
        *,
        mode: str = "dark",
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.db = db
        self.user = user
        self.mode = mode

        name = f"{user['FName']} {user['LName']}"
        shell = SidebarLayout(
            self,
            title="IMS Admin",
            subtitle=f"Product Manager · {name}",
            nav_items=[
                ("📊", "Dashboard"),
                ("⚠️", "Reorder Alerts"),
                ("🔄", "Transactions"),
                ("🏢", "Suppliers"),
                ("🛒", "Customer Actions"),
                ("📥", "Supplier Actions"),
                ("💻", "SQL Instance"),
            ],
            mode=mode,
        )
        shell.pack(fill="both", expand=True)

        dashboard = ctk.CTkScrollableFrame(shell.content, fg_color="transparent")
        reorder = ctk.CTkScrollableFrame(shell.content, fg_color="transparent")
        transactions = ctk.CTkScrollableFrame(shell.content, fg_color="transparent")
        suppliers = ctk.CTkScrollableFrame(shell.content, fg_color="transparent")
        customer_embed = ctk.CTkFrame(shell.content, fg_color="transparent")
        supplier_embed = ctk.CTkFrame(shell.content, fg_color="transparent")
        sql_page = ctk.CTkScrollableFrame(shell.content, fg_color="transparent")

        for key, page in [
            ("Dashboard", dashboard),
            ("Reorder Alerts", reorder),
            ("Transactions", transactions),
            ("Suppliers", suppliers),
            ("Customer Actions", customer_embed),
            ("Supplier Actions", supplier_embed),
            ("SQL Instance", sql_page),
        ]:
            shell.register_page(key, page)

        self._build_dashboard(dashboard)
        self._build_reorder(reorder)
        self._build_transactions(transactions)
        self._build_suppliers(suppliers)
        self._build_sql_console(sql_page)

        CustomerFrame(customer_embed, db, user, mode=mode, embedded=True).pack(
            fill="both", expand=True
        )
        SupplierFrame(supplier_embed, db, user, mode=mode, embedded=True).pack(
            fill="both", expand=True
        )

        shell.show_page("Dashboard")
        self.refresh_all()

    # ------------------------------------------------------------------ pages
    def _build_dashboard(self, parent: ctk.CTkScrollableFrame) -> None:
        page_header(parent, "Dashboard", "Live inventory overview and product catalog.", self.mode)

        self.dashboard_metrics = MetricsRow(parent, mode=self.mode)
        self.dashboard_metrics.pack(fill="x", pady=(0, 16))
        self.dashboard_metrics.add_metric("products", "Total Products", "—")
        self.dashboard_metrics.add_metric("alerts", "Low Stock Alerts", "—", accent="#f9e2af")
        self.dashboard_metrics.add_metric("suppliers", "Active Suppliers", "—")

        actions = ctk.CTkFrame(parent, fg_color="transparent")
        actions.pack(fill="x", pady=(0, 12))
        action_button(actions, "Refresh", self.load_products, mode=self.mode).pack(side="left")

        self.products_table = DataTable(parent, mode=self.mode)
        self.products_table.pack(fill="both", expand=True)

    def _build_reorder(self, parent: ctk.CTkScrollableFrame) -> None:
        page_header(
            parent, "Reorder Alerts", "Products at or below their reorder threshold.", self.mode
        )
        action_button(parent, "Refresh Alerts", self.load_reorder, mode=self.mode).pack(
            anchor="w", pady=(0, 12)
        )
        self.reorder_table = DataTable(parent, mode=self.mode)
        self.reorder_table.pack(fill="both", expand=True)

    def _build_transactions(self, parent: ctk.CTkScrollableFrame) -> None:
        page_header(parent, "All Transactions", "Complete audit trail of stock movements.", self.mode)
        action_button(parent, "Refresh", self.load_transactions, mode=self.mode).pack(
            anchor="w", pady=(0, 12)
        )
        self.transactions_table = DataTable(parent, mode=self.mode)
        self.transactions_table.pack(fill="both", expand=True)

    def _build_suppliers(self, parent: ctk.CTkScrollableFrame) -> None:
        page_header(
            parent,
            "Supplier Management",
            "Onboard vendors and manage the supplier directory.",
            self.mode,
        )

        self.supplier_metrics = MetricsRow(parent, mode=self.mode)
        self.supplier_metrics.pack(fill="x", pady=(0, 16))
        self.supplier_metrics.add_metric("registered", "Registered Suppliers", "—")

        split = ctk.CTkFrame(parent, fg_color="transparent")
        split.pack(fill="x", pady=(0, 16))
        split.grid_columnconfigure((0, 1), weight=1)

        company_card = FormCard(split, title="Company Profile", mode=self.mode)
        company_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.supplier_name_entry = form_field(
            company_card, "Supplier Name", placeholder="Acme Supplies Ltd", mode=self.mode
        )
        self.company_email_entry = form_field(
            company_card, "Company Email", placeholder="contact@vendor.com", mode=self.mode
        )
        self.street_entry = form_field(
            company_card, "Street Address", placeholder="42 Industrial Ave", mode=self.mode
        )
        self.city_entry = form_field(
            company_card, "City", placeholder="Bangalore", mode=self.mode
        )
        self.zip_entry = form_field(
            company_card, "Postal Code", placeholder="560001", mode=self.mode
        )

        portal_card = FormCard(split, title="Portal Account (Role: SUPPLIER)", mode=self.mode)
        portal_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self.fname_entry = form_field(
            portal_card, "Representative First Name", placeholder="Sam", mode=self.mode
        )
        self.lname_entry = form_field(
            portal_card, "Representative Last Name", placeholder="Vendor", mode=self.mode
        )
        self.user_email_entry = form_field(
            portal_card, "Login Email", placeholder="supplier@vendor.com", mode=self.mode
        )
        self.password_entry = form_field(
            portal_card,
            "Temporary Password",
            placeholder="Min. 8 characters",
            show="•",
            mode=self.mode,
        )

        action_button(
            parent,
            "Onboard Supplier & Generate Account",
            self.handle_onboard_click,
            mode=self.mode,
            width=280,
        ).pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(
            parent,
            text="Registered Suppliers",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(0, 8))

        action_button(parent, "Refresh List", self.load_suppliers, mode=self.mode, secondary=True).pack(
            anchor="w", pady=(0, 12)
        )
        self.suppliers_table = DataTable(parent, mode=self.mode)
        self.suppliers_table.pack(fill="both", expand=True)

    def _build_sql_console(self, parent: ctk.CTkScrollableFrame) -> None:
        page_header(
            parent,
            "SQL Instance",
            "Execute raw SQL directly against the database (Admin only).",
            self.mode,
        )

        self.sql_editor = ctk.CTkTextbox(
            parent,
            height=180,
            corner_radius=10,
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self.sql_editor.pack(fill="x", pady=(0, 12))
        self.sql_editor.insert("1.0", "SELECT * FROM Product LIMIT 10;")

        btn_row = ctk.CTkFrame(parent, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 12))
        action_button(btn_row, "Execute", self.run_sql, mode=self.mode).pack(side="left", padx=(0, 8))
        action_button(
            btn_row, "Clear Results", self._clear_sql_results, mode=self.mode, secondary=True
        ).pack(side="left")

        self.sql_status = ctk.CTkLabel(parent, text="", font=ctk.CTkFont(size=12))
        self.sql_status.pack(anchor="w", pady=(0, 8))

        self.sql_results_table = DataTable(parent, mode=self.mode)
        self.sql_results_table.pack(fill="both", expand=True)

    # -------------------------------------------------------------- data loads
    def refresh_all(self) -> None:
        self.load_products()
        self.load_reorder()
        self.load_transactions()
        self.load_suppliers()

    def load_products(self) -> None:
        try:
            try:
                # 1. Try running the 1-argument signature
                rows = self.db.call_procedure("sp_get_products", (self.user['UserID'],))
            except DatabaseError as e:
                # 2. Fall back to the legacy 0-argument call if needed
                if "Incorrect number of arguments" in str(e) or "1318" in str(e):
                    rows = self.db.call_procedure("sp_get_products")
                else:
                    raise e

            self.products_table.populate(rows)
            self.dashboard_metrics.set_metric("products", str(len(rows)))
        except DatabaseError as exc:
            show_error("Dashboard Products Error", str(exc))

    def load_reorder(self) -> None:
        try:
            rows = self.db.call_procedure("sp_get_reorder_alerts")
            self.reorder_table.populate(rows)
            self.dashboard_metrics.set_metric("alerts", str(len(rows)))
        except DatabaseError as exc:
            show_error("Reorder", str(exc))

    def load_transactions(self) -> None:
        try:
            rows = self.db.call_procedure("sp_get_transactions", (100,))
            self.transactions_table.populate(rows)
        except DatabaseError as exc:
            show_error("Transactions", str(exc))

    def load_suppliers(self) -> None:
        try:
            rows = self.db.call_procedure("sp_get_suppliers")
            self.suppliers_table.populate(rows)
            self.supplier_metrics.set_metric("registered", str(len(rows)))
            self.dashboard_metrics.set_metric("suppliers", str(len(rows)))
        except DatabaseError as exc:
            show_error("Suppliers", str(exc))

    # -------------------------------------------------------------- onboarding
    def handle_onboard_click(self) -> None:
        if (
            not self.supplier_name_entry.get().strip()
            or not self.user_email_entry.get().strip()
            or not self.password_entry.get().strip()
        ):
            show_warning(
                "Validation",
                "Supplier Name, Login Email, and Temporary Password are required.",
            )
            return

        form_data = {
            "supplier_name": self.supplier_name_entry.get().strip(),
            "email": self.company_email_entry.get().strip(),
            "street": self.street_entry.get().strip(),
            "city": self.city_entry.get().strip(),
            "zip": self.zip_entry.get().strip(),
            "first_name": self.fname_entry.get().strip(),
            "last_name": self.lname_entry.get().strip(),
            "portal_email": self.user_email_entry.get().strip(),
            "temporary_password": self.password_entry.get().strip(),
        }

        result = self.db.onboard_new_supplier(form_data)
        if result["success"]:
            show_info(
                "Success",
                "Supplier onboarded successfully!\n\n"
                f"Portal login:\n  Email: {form_data['portal_email']}\n"
                f"  Password: {form_data['temporary_password']}",
            )
            for entry in (
                self.supplier_name_entry,
                self.company_email_entry,
                self.street_entry,
                self.city_entry,
                self.zip_entry,
                self.fname_entry,
                self.lname_entry,
                self.user_email_entry,
                self.password_entry,
            ):
                entry.delete(0, "end")
            self.load_suppliers()
        else:
            show_error("Onboarding Failed", result["message"])

    # ------------------------------------------------------------------- SQL
    def _clear_sql_results(self) -> None:
        self.sql_results_table.populate([])
        self.sql_status.configure(text="")

    def run_sql(self) -> None:
        sql = self.sql_editor.get("1.0", "end").strip()
        if not sql:
            show_warning("SQL Instance", "Enter a SQL statement.")
            return
        try:
            _columns, rows, message = self.db.execute_raw_sql(sql)
            if message:
                self.sql_status.configure(text=message)
                self._clear_sql_results()
            else:
                self.sql_status.configure(text=f"{len(rows)} row(s) returned.")
                self.sql_results_table.populate(rows)
        except DatabaseError as exc:
            show_error("SQL Instance", str(exc))