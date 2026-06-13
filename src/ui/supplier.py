"""Supplier module — inward stock, product registration, and isolated catalog."""

from __future__ import annotations

import customtkinter as ctk

from db.connection import Database, DatabaseError
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


class SupplierFrame(ctk.CTkFrame):
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
        self._warehouses: list[dict] = []

        # Fetch supplier company details dynamically based on logged-in representative
        self.supplier_company_name = self._get_supplier_company_name()

        name = f"{user['FName']} {user['LName']}"
        shell = SidebarLayout(
            self,
            title="Supplier Portal" if not embedded else "Supplier Tools",
            subtitle=name,
            nav_items=[
                ("📥", "Inward Stock"),
                ("➕", "Register Product"),
                ("📦", "My Products"),
            ],
            mode=mode,
        )
        shell.pack(fill="both", expand=True)

        inward = ctk.CTkScrollableFrame(shell.content, fg_color="transparent")
        register = ctk.CTkScrollableFrame(shell.content, fg_color="transparent")
        products = ctk.CTkScrollableFrame(shell.content, fg_color="transparent")

        shell.register_page("Inward Stock", inward)
        shell.register_page("Register Product", register)
        shell.register_page("My Products", products)

        # --- Inward ---
        page_header(inward, "Inward Stock", "Record procurement and restock your inventory.", mode)
        from ui.theme import colors as theme_colors

        inward_card = ctk.CTkFrame(
            inward, fg_color=theme_colors(mode)["card"], corner_radius=14
        )
        inward_card.pack(fill="x", pady=(0, 16))

        self.inward_product_entry = form_field(
            inward_card, "Product ID", placeholder="Your product ID", mode=mode
        )
        self.inward_qty_entry = form_field(
            inward_card, "Quantity Received", placeholder="e.g. 50", mode=mode
        )
        self.inward_qty_entry.insert(0, "10")

        action_button(
            inward_card, "Submit Inward", self.submit_inward, mode=mode, width=200
        ).pack(padx=20, pady=(8, 20), anchor="w")

        # --- Register ---
        page_header(register, "Register Product", "Add a new SKU to your supplier catalog.", mode)

        reg_grid = ctk.CTkFrame(register, fg_color="transparent")
        reg_grid.pack(fill="x")
        reg_grid.grid_columnconfigure((0, 1), weight=1)

        left_card = FormCard(reg_grid, title="Product Details", mode=mode)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 16))

        self.reg_name = form_field(left_card, "Product Name", placeholder="Wireless Mouse", mode=mode)
        self.reg_category = form_field(left_card, "Category", placeholder="Electronics", mode=mode)
        self.reg_price = form_field(left_card, "Unit Price (₹)", placeholder="599.00", mode=mode)
        self.reg_reorder = form_field(left_card, "Reorder Point", placeholder="10", mode=mode)
        self.reg_reorder.insert(0, "10")

        right_card = FormCard(reg_grid, title="Warehouse & Stock", mode=mode)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 16))

        wh_wrap = ctk.CTkFrame(right_card, fg_color="transparent")
        wh_wrap.pack(fill="x", padx=20, pady=6)
        ctk.CTkLabel(
            wh_wrap, text="Warehouse", font=ctk.CTkFont(size=12), text_color="#a6adc8"
        ).pack(anchor="w", pady=(0, 4))
        self.warehouse_menu = ctk.CTkOptionMenu(wh_wrap, values=["Loading..."], height=38, corner_radius=8)
        self.warehouse_menu.pack(fill="x")

        self.reg_initial = form_field(
            right_card, "Initial Quantity", placeholder="Optional opening stock", mode=mode
        )
        self.reg_initial.insert(0, "0")

        action_button(
            register, "Register Product", self.register_product, mode=mode, width=220
        ).pack(anchor="w", pady=(0, 16))

        # --- My Products ---
        page_header(
            products,
            "My Products",
            "Only products linked to your supplier account are shown.",
            mode,
        )
        self.product_metrics = MetricsRow(products, mode=mode)
        self.product_metrics.pack(fill="x", pady=(0, 16))
        self.product_metrics.add_metric("skus", "Your SKUs", "—")
        self.product_metrics.add_metric("stock", "Total Units", "—")
        self.product_metrics.add_metric("low", "Low Stock", "—", accent="#f9e2af")

        prod_actions = ctk.CTkFrame(products, fg_color="transparent")
        prod_actions.pack(fill="x", pady=(0, 12))
        action_button(prod_actions, "Refresh", self.load_products, mode=mode).pack(side="left")

        self.products_table = DataTable(products, mode=mode)
        self.products_table.pack(fill="both", expand=True)

        shell.show_first_page()
        self._load_warehouses()
        self.load_products()

    def _get_supplier_company_name(self) -> str:
        """Finds the company profile name linked to this user's SupplierID."""
        if not self.user.get("SupplierID"):
            return ""
        try:
            suppliers = self.db.call_procedure("sp_get_suppliers")
            for s in suppliers:
                if int(s.get("SupplierID", 0)) == int(self.user["SupplierID"]):
                    return s.get("SupplierName", "")
        except Exception:
            pass
        return ""

    def _load_warehouses(self) -> None:
        try:
            self._warehouses = self.db.call_procedure("sp_get_warehouses")
            labels = [f"{w['WarehouseID']} — {w['Location']}" for w in self._warehouses]
            self.warehouse_menu.configure(values=labels if labels else ["No warehouses"])
            if labels:
                self.warehouse_menu.set(labels[0])
        except DatabaseError as exc:
            show_error("Warehouses", str(exc))

    def load_products(self) -> None:
        try:
            # 1. CALL THE SAFE 0-ARGUMENT PROCEDURE (Avoids 1318 error completely)
            all_products = self.db.call_procedure("sp_get_products")
            
            # 2. ISOLATION OVERRIDE: Filter the list down using Python matching logic
            if self.supplier_company_name:
                rows = [
                    p for p in all_products 
                    if str(p.get("SupplierName", "")).strip().lower() == self.supplier_company_name.strip().lower()
                ]
            else:
                rows = all_products

            # 3. Populate Table & Update UI Metrics
            self.products_table.populate(rows)
            
            total_stock = sum(int(r.get("StockQuantity", 0)) for r in rows)
            low = sum(
                1 for r in rows
                if int(r.get("StockQuantity", 0)) <= int(r.get("ReorderPoint", 0))
            )
            
            self.product_metrics.set_metric("skus", str(len(rows)))
            self.product_metrics.set_metric("stock", str(total_stock))
            self.product_metrics.set_metric("low", str(low))
            
        except DatabaseError as exc:
            show_error("Products Fetch Error", str(exc))

    def submit_inward(self) -> None:
        try:
            product_id = int(self.inward_product_entry.get().strip())
            quantity = int(self.inward_qty_entry.get().strip())
        except ValueError:
            show_warning("Inward", "Product ID and quantity must be integers.")
            return

        try:
            txn_id = self.db.call_procedure_with_out(
                "sp_create_inward_transaction",
                (self.user["UserID"], product_id, quantity),
            )
            show_info("Inward", f"Stock received successfully.\nTransaction ID: {txn_id}")
            self.load_products()
        except DatabaseError as exc:
            show_error("Inward", str(exc))

    def register_product(self) -> None:
        wh_selection = self.warehouse_menu.get()
        if not wh_selection or wh_selection == "No warehouses":
            show_warning("Register", "Select a warehouse.")
            return

        warehouse_id = int(wh_selection.split("—")[0].strip())
        try:
            price = float(self.reg_price.get().strip())
            reorder = int(self.reg_reorder.get().strip() or "10")
            initial = int(self.reg_initial.get().strip() or "0")
        except ValueError:
            show_warning("Register", "Price, reorder point, and quantity must be numeric.")
            return

        try:
            rows = self.db.call_procedure(
                "sp_register_product",
                (
                    self.user["UserID"],
                    self.reg_name.get().strip(),
                    self.reg_category.get().strip(),
                    price,
                    reorder,
                    warehouse_id,
                    None,
                    initial,
                ),
            )
            product_id = rows[0]["ProductID"] if rows else "?"
            show_info("Register", f"Product registered successfully.\nProduct ID: {product_id}")
            self.reg_name.delete(0, "end")
            self.reg_category.delete(0, "end")
            self.reg_price.delete(0, "end")
            self.load_products()
        except DatabaseError as exc:
            show_error("Register", str(exc))