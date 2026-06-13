"""Customer module — product catalog, purchases, and transaction history."""

from __future__ import annotations

import customtkinter as ctk

from db.connection import Database, DatabaseError
from ui.widgets import (
    DataTable,
    MetricsRow,
    SidebarLayout,
    action_button,
    form_field,
    page_header,
    show_error,
    show_info,
    show_warning,
)


class CustomerFrame(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.Misc,
        db: Database,
        user: dict,
        *,
        mode: str = "dark",
        embedded: bool = False,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.db = db
        self.user = user
        self.mode = mode
        self.embedded = embedded

        name = f"{user['FName']} {user['LName']}"
        shell = SidebarLayout(
            self,
            title="Customer Portal" if not embedded else "Customer Tools",
            subtitle=name,
            nav_items=[
                ("📦", "Product Catalog"),
                ("🛒", "Purchase"),
                ("📋", "My Transactions"),
            ],
            mode=mode,
        )
        shell.pack(fill="both", expand=True)

        catalog = ctk.CTkScrollableFrame(shell.content, fg_color="transparent")
        purchase = ctk.CTkScrollableFrame(shell.content, fg_color="transparent")
        history = ctk.CTkScrollableFrame(shell.content, fg_color="transparent")

        shell.register_page("Product Catalog", catalog)
        shell.register_page("Purchase", purchase)
        shell.register_page("My Transactions", history)

        # --- Catalog ---
        page_header(catalog, "Product Catalog", "Browse available inventory in real time.", mode)
        self.catalog_metrics = MetricsRow(catalog, mode=mode)
        self.catalog_metrics.pack(fill="x", pady=(0, 16))
        self.catalog_metrics.add_metric("total", "Available Products", "—")
        self.catalog_metrics.add_metric("categories", "Categories", "—")
        self.catalog_metrics.add_metric("in_stock", "In Stock Items", "—")

        cat_actions = ctk.CTkFrame(catalog, fg_color="transparent")
        cat_actions.pack(fill="x", pady=(0, 12))
        action_button(cat_actions, "Refresh Catalog", self.load_products, mode=mode).pack(side="left")

        self.products_table = DataTable(catalog, mode=mode)
        self.products_table.pack(fill="both", expand=True)

        # --- Purchase ---
        page_header(purchase, "New Purchase", "Create an outward transaction to buy stock.", mode)
        from ui.theme import colors as theme_colors

        purchase_card = ctk.CTkFrame(
            purchase, fg_color=theme_colors(mode)["card"], corner_radius=14
        )
        purchase_card.pack(fill="x", pady=(0, 16))

        self.product_id_entry = form_field(
            purchase_card, "Product ID", placeholder="e.g. 1", mode=mode
        )
        self.quantity_entry = form_field(
            purchase_card, "Quantity", placeholder="e.g. 2", mode=mode
        )
        self.quantity_entry.insert(0, "1")

        action_button(
            purchase_card, "Submit Purchase", self.submit_purchase, mode=mode, width=200
        ).pack(padx=20, pady=(8, 20), anchor="w")

        # --- History ---
        page_header(history, "Transaction History", "Your recent outward purchases.", mode)
        hist_actions = ctk.CTkFrame(history, fg_color="transparent")
        hist_actions.pack(fill="x", pady=(0, 12))
        action_button(hist_actions, "Refresh History", self.load_history, mode=mode).pack(side="left")

        self.history_table = DataTable(history, mode=mode)
        self.history_table.pack(fill="both", expand=True)

        shell.show_first_page()
        self.load_products()
        self.load_history()

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

            # FIX: Use the modern CustomTkinter DataTable engine populate routine
            self.products_table.populate(rows)
            
            categories = len({r.get("Category") for r in rows})
            in_stock = sum(1 for r in rows if int(r.get("StockQuantity", 0)) > 0)
            self.catalog_metrics.set_metric("total", str(len(rows)))
            self.catalog_metrics.set_metric("categories", str(categories))
            self.catalog_metrics.set_metric("in_stock", str(in_stock))
        except DatabaseError as exc:
            show_error("Products Catalog Error", str(exc))

    def load_history(self) -> None:
        try:
            rows = self.db.call_procedure(
                "sp_get_user_transactions", (self.user["UserID"], 50)
            )
            self.history_table.populate(rows)
        except DatabaseError as exc:
            show_error("History", str(exc))

    def submit_purchase(self) -> None:
        try:
            product_id = int(self.product_id_entry.get().strip())
            quantity = int(self.quantity_entry.get().strip())
        except ValueError:
            show_warning("Purchase", "Product ID and quantity must be integers.")
            return

        try:
            txn_id = self.db.call_procedure_with_out(
                "sp_create_outward_transaction",
                (self.user["UserID"], product_id, quantity),
            )
            show_info("Purchase", f"Transaction recorded successfully.\nTransaction ID: {txn_id}")
            self.load_products()
            self.load_history()
        except DatabaseError as exc:
            show_error("Purchase", str(exc))