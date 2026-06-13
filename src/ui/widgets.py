"""Reusable CustomTkinter dashboard components."""

from __future__ import annotations

from typing import Any, Callable

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk

from ui.theme import apply_treeview_style, colors


class SidebarLayout(ctk.CTkFrame):
    """Left sidebar navigation with stacked content pages."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        title: str,
        subtitle: str,
        nav_items: list[tuple[str, str]],
        mode: str = "dark",
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._mode = mode
        self._c = colors(mode)
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        self._pages: dict[str, ctk.CTkFrame] = {}
        self._active_key: str | None = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=self._c["sidebar"])
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(28, 24))
        ctk.CTkLabel(
            brand, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=self._c["text"]
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand, text=subtitle, font=ctk.CTkFont(size=12), text_color=self._c["text_muted"]
        ).pack(anchor="w", pady=(4, 0))

        nav_wrap = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_wrap.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        for icon, label in nav_items:
            key = label
            btn = ctk.CTkButton(
                nav_wrap,
                text=f"  {icon}   {label}",
                anchor="w",
                height=42,
                corner_radius=10,
                fg_color="transparent",
                text_color=self._c["text_muted"],
                hover_color=self._c["card_hover"],
                font=ctk.CTkFont(size=13),
                command=lambda k=key: self.show_page(k),
            )
            btn.pack(fill="x", pady=3)
            self._nav_buttons[key] = btn

        self.content = ctk.CTkFrame(self, fg_color=self._c["bg"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def register_page(self, key: str, page: ctk.CTkFrame) -> None:
        self._pages[key] = page
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_remove()

    def show_page(self, key: str) -> None:
        if key not in self._pages:
            return
        for k, page in self._pages.items():
            if k == key:
                page.grid()
            else:
                page.grid_remove()

        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=self._c["accent"],
                    text_color="#ffffff",
                    hover_color=self._c["accent_hover"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self._c["text_muted"],
                    hover_color=self._c["card_hover"],
                )
        self._active_key = key

    def show_first_page(self) -> None:
        if self._pages:
            self.show_page(next(iter(self._pages)))


class MetricCard(ctk.CTkFrame):
    def __init__(
        self,
        master: tk.Misc,
        *,
        label: str,
        value: str = "—",
        accent: str | None = None,
        mode: str = "dark",
        **kwargs,
    ) -> None:
        c = colors(mode)
        super().__init__(master, fg_color=c["card"], corner_radius=14, **kwargs)
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=accent or c["accent"],
        )
        self.value_label.pack(anchor="w", padx=20, pady=(18, 0))
        ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(size=12),
            text_color=c["text_muted"],
        ).pack(anchor="w", padx=20, pady=(4, 18))

    def set_value(self, value: str) -> None:
        self.value_label.configure(text=value)


class MetricsRow(ctk.CTkFrame):
    def __init__(self, master: tk.Misc, mode: str = "dark", **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._mode = mode
        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="metrics")
        self._cards: dict[str, MetricCard] = {}

    def add_metric(self, key: str, label: str, value: str = "—", accent: str | None = None) -> MetricCard:
        idx = len(self._cards)
        card = MetricCard(self, label=label, value=value, accent=accent, mode=self._mode)
        card.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 8, 0))
        self._cards[key] = card
        return card

    def set_metric(self, key: str, value: str) -> None:
        if key in self._cards:
            self._cards[key].set_value(value)


class DataTable(ctk.CTkFrame):
    """Styled Treeview with alternating rows and no harsh grid lines."""

    def __init__(self, master: tk.Misc, mode: str = "dark", **kwargs) -> None:
        super().__init__(master, fg_color=colors(mode)["card"], corner_radius=12, **kwargs)
        self._mode = mode
        self._c = colors(mode)
        apply_treeview_style(mode)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        inner = tk.Frame(self, bg=self._c["card"], highlightthickness=0)
        inner.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        inner.grid_rowconfigure(0, weight=1)
        inner.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(inner, style="IMS.Treeview", show="headings", selectmode="browse")
        vsb = ttk.Scrollbar(inner, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(inner, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.tree.tag_configure("odd", background=self._c["row_odd"])
        self.tree.tag_configure("even", background=self._c["row_even"])

    def populate(self, rows: list[dict[str, Any]]) -> None:
        self.tree.delete(*self.tree.get_children())
        if not rows:
            return

        columns = list(rows[0].keys())
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=max(120, len(col) * 11), anchor="w", stretch=True)

        for idx, row in enumerate(rows):
            tag = "even" if idx % 2 == 0 else "odd"
            self.tree.insert(
                "",
                "end",
                values=[row.get(c, "") for c in columns],
                tags=(tag,),
            )


class FormCard(ctk.CTkFrame):
    """Padded card container for form sections."""

    def __init__(self, master: tk.Misc, *, title: str, mode: str = "dark", **kwargs) -> None:
        c = colors(mode)
        super().__init__(master, fg_color=c["card"], corner_radius=14, **kwargs)
        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=c["text"],
        ).pack(anchor="w", padx=20, pady=(16, 8))


def form_field(
    parent: tk.Misc,
    label: str,
    *,
    placeholder: str = "",
    show: str | None = None,
    mode: str = "dark",
    width: int = 260,
) -> ctk.CTkEntry:
    c = colors(mode)
    wrap = ctk.CTkFrame(parent, fg_color="transparent")
    wrap.pack(fill="x", padx=20, pady=6)
    ctk.CTkLabel(wrap, text=label, font=ctk.CTkFont(size=12), text_color=c["text_muted"]).pack(
        anchor="w", pady=(0, 4)
    )
    entry = ctk.CTkEntry(
        wrap,
        placeholder_text=placeholder,
        height=38,
        corner_radius=8,
        border_color=c["border"],
        fg_color=c["input_bg"],
        text_color=c["text"],
        width=width,
        show=show or "",
    )
    entry.pack(fill="x")
    return entry


def page_header(parent: tk.Misc, title: str, subtitle: str, mode: str = "dark") -> ctk.CTkFrame:
    c = colors(mode)
    bar = ctk.CTkFrame(parent, fg_color="transparent")
    bar.pack(fill="x", pady=(0, 16))
    ctk.CTkLabel(bar, text=title, font=ctk.CTkFont(size=22, weight="bold"), text_color=c["text"]).pack(
        anchor="w"
    )
    ctk.CTkLabel(
        bar, text=subtitle, font=ctk.CTkFont(size=12), text_color=c["text_muted"]
    ).pack(anchor="w", pady=(4, 0))
    return bar


def action_button(
    parent: tk.Misc,
    text: str,
    command: Callable[[], None],
    *,
    mode: str = "dark",
    width: int = 160,
    secondary: bool = False,
) -> ctk.CTkButton:
    c = colors(mode)
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=40,
        corner_radius=10,
        width=width,
        fg_color=c["card_hover"] if secondary else c["accent"],
        hover_color=c["border"] if secondary else c["accent_hover"],
        text_color=c["text"],
    )


def show_error(title: str, message: str) -> None:
    messagebox.showerror(title, message)


def show_warning(title: str, message: str) -> None:
    messagebox.showwarning(title, message)


def show_info(title: str, message: str) -> None:
    messagebox.showinfo(title, message)


def fetch_products(db: Any, user_id: int) -> list[dict[str, Any]]:
    """Centralized sp_get_products call — always passes p_user_id."""
    return db.call_procedure("sp_get_products", (user_id,))
