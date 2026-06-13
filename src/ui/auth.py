"""Authentication screen — delegates identity verification to sp_authenticate."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from db.connection import Database, DatabaseError
from ui.theme import colors
from ui.widgets import action_button, show_error, show_warning


class LoginFrame(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.Misc,
        db: Database,
        on_login: Callable[[dict], None],
        *,
        mode: str = "dark",
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.db = db
        self.on_login = on_login
        self._c = colors(mode)

        ctk.CTkLabel(
            self, text="Sign in to continue", font=ctk.CTkFont(size=13), text_color=self._c["text_muted"]
        ).pack(pady=(0, 16))

        ctk.CTkLabel(self, text="Email", anchor="w", text_color=self._c["text_muted"]).pack(
            fill="x", pady=(0, 4)
        )
        self.email_entry = ctk.CTkEntry(
            self,
            placeholder_text="admin@ims.local",
            height=40,
            corner_radius=8,
            fg_color=self._c["input_bg"],
            border_color=self._c["border"],
        )
        self.email_entry.pack(fill="x", pady=(0, 12))
        self.email_entry.insert(0, "admin@ims.local")

        ctk.CTkLabel(self, text="Password", anchor="w", text_color=self._c["text_muted"]).pack(
            fill="x", pady=(0, 4)
        )
        self.password_entry = ctk.CTkEntry(
            self,
            placeholder_text="password123",
            show="•",
            height=40,
            corner_radius=8,
            fg_color=self._c["input_bg"],
            border_color=self._c["border"],
        )
        self.password_entry.pack(fill="x", pady=(0, 20))
        self.password_entry.insert(0, "password123")

        action_button(self, "Login", self._login, mode=mode, width=360).pack(fill="x")

        ctk.CTkLabel(
            self,
            text="Demo: admin / customer / supplier @ims.local — password123",
            font=ctk.CTkFont(size=11),
            text_color=self._c["text_muted"],
        ).pack(pady=(16, 0))

    def _login(self) -> None:
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        if not email or not password:
            show_warning("Login", "Email and password are required.")
            return
        try:
            rows = self.db.call_procedure("sp_authenticate", (email, password))
            if not rows:
                show_error("Login", "Invalid credentials.")
                return
            self.on_login(rows[0])
        except DatabaseError as exc:
            show_error("Login", str(exc))
