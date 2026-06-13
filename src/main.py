"""IMS entry point — CustomTkinter shell with dark / light theme support."""

from __future__ import annotations

import sys

import customtkinter as ctk
from tkinter import messagebox

from db.connection import Database, DatabaseError
from ui.admin import AdminFrame
from ui.auth import LoginFrame
from ui.customer import CustomerFrame
from ui.supplier import SupplierFrame
from ui.theme import apply_treeview_style, colors


class IMSApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.appearance_mode = "dark"
        ctk.set_appearance_mode(self.appearance_mode)
        ctk.set_default_color_theme("dark-blue")

        self.title("Inventory Management System")
        self.geometry("1280x780")
        self.minsize(1024, 680)
        self._apply_window_colors()

        self.db = Database()
        self.db.test_connection()

        self.current_user: dict | None = None
        self._main_area = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self._main_area.pack(fill="both", expand=True)

        self._show_login()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _apply_window_colors(self) -> None:
        c = colors(self.appearance_mode)
        self.configure(fg_color=c["bg"])
        apply_treeview_style(self.appearance_mode)

    def _toggle_theme(self) -> None:
        self.appearance_mode = "light" if self.appearance_mode == "dark" else "dark"
        ctk.set_appearance_mode(self.appearance_mode)
        self._apply_window_colors()
        if self.current_user:
            self._on_login_success(self.current_user)

    def _clear_main(self) -> None:
        for child in self._main_area.winfo_children():
            child.destroy()

    def _show_login(self) -> None:
        self.current_user = None
        self._clear_main()

        # Center wrapper alignment anchor
        wrapper = ctk.CTkFrame(self._main_area, fg_color="transparent")
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        # Explicitly assigned a proportional height (480) to give elements room to draw
        card = ctk.CTkFrame(wrapper, width=420, height=540, corner_radius=16)
        card.pack(padx=40, pady=40)
        card.pack_propagate(False) # Now safe to use because height is explicitly defined

        c = colors(self.appearance_mode)
        ctk.CTkLabel(
            card,
            text="IMS",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=c["accent"],
        ).pack(pady=(32, 4))
        
        ctk.CTkLabel(
            card,
            text="Inventory Management System",
            font=ctk.CTkFont(size=14),
            text_color=c["text_muted"],
        ).pack(pady=(0, 24))

        login_host = ctk.CTkFrame(card, fg_color="transparent")
        login_host.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        
        LoginFrame(login_host, self.db, self._on_login_success, mode=self.appearance_mode).pack(
            fill="both", expand=True
        )

    def _build_top_bar(self, parent: ctk.CTkFrame, user: dict) -> None:
        c = colors(self.appearance_mode)
        bar = ctk.CTkFrame(parent, height=56, corner_radius=0, fg_color=c["sidebar"])
        bar.pack(fill="x")
        bar.pack_propagate(False)

        ctk.CTkLabel(
            bar,
            text=f"  Signed in as  {user['Email']}  ·  {user['Role']}",
            font=ctk.CTkFont(size=13),
            text_color=c["text_muted"],
        ).pack(side="left", padx=16, pady=14)

        ctk.CTkButton(
            bar,
            text="Toggle Theme",
            width=110,
            height=32,
            corner_radius=8,
            fg_color=c["card"],
            hover_color=c["card_hover"],
            command=self._toggle_theme,
        ).pack(side="right", padx=(0, 8), pady=12)

        ctk.CTkButton(
            bar,
            text="Logout",
            width=90,
            height=32,
            corner_radius=8,
            fg_color=c["accent"],
            hover_color=c["accent_hover"],
            command=self._show_login,
        ).pack(side="right", padx=(0, 16), pady=12)

    def _on_login_success(self, user: dict) -> None:
        self.current_user = user
        self._clear_main()

        shell = ctk.CTkFrame(self._main_area, fg_color="transparent", corner_radius=0)
        shell.pack(fill="both", expand=True)

        self._build_top_bar(shell, user)

        content = ctk.CTkFrame(shell, fg_color="transparent")
        content.pack(fill="both", expand=True)

        role = user["Role"]
        mode = self.appearance_mode
        if role == "ADMIN":
            AdminFrame(content, self.db, user, mode=mode).pack(fill="both", expand=True)
        elif role == "SUPPLIER":
            SupplierFrame(content, self.db, user, mode=mode).pack(fill="both", expand=True)
        else:
            CustomerFrame(content, self.db, user, mode=mode).pack(fill="both", expand=True)

    def _on_close(self) -> None:
        self.db.close()
        self.destroy()


def main() -> None:
    try:
        app = IMSApp()
        app.mainloop()
    except (DatabaseError, Exception) as exc:
        messagebox.showerror(
            "Database Connection Error",
            f"Could not connect to MySQL at localhost:3306.\n\n{exc}\n\n"
            "Ensure MySQL is running and credentials in .env are correct.",
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
