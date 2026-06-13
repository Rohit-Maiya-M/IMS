"""IMS design tokens and ttk Treeview styling for dark / light modes."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

PALETTE = {
    "dark": {
        "bg": "#1e1e2e",
        "sidebar": "#181825",
        "card": "#252538",
        "card_hover": "#2d2d44",
        "accent": "#00adb5",
        "accent_hover": "#00c4ce",
        "text": "#ffffff",
        "text_muted": "#a6adc8",
        "border": "#313244",
        "success": "#a6e3a1",
        "warning": "#f9e2af",
        "danger": "#f38ba8",
        "row_odd": "#252538",
        "row_even": "#2a2a3d",
        "row_selected": "#00adb5",
        "input_bg": "#313244",
    },
    "light": {
        "bg": "#eef1f6",
        "sidebar": "#ffffff",
        "card": "#ffffff",
        "card_hover": "#f4f6fa",
        "accent": "#00939a",
        "accent_hover": "#00adb5",
        "text": "#1e1e2e",
        "text_muted": "#5c6370",
        "border": "#d8dee9",
        "success": "#2e7d52",
        "warning": "#b8860b",
        "danger": "#c0392b",
        "row_odd": "#ffffff",
        "row_even": "#f6f8fb",
        "row_selected": "#00adb5",
        "input_bg": "#f4f6fa",
    },
}


def colors(mode: str = "dark") -> dict[str, str]:
    return PALETTE["light" if mode == "light" else "dark"]


def apply_treeview_style(mode: str = "dark") -> ttk.Style:
    """Configure a modern, borderless Treeview that matches the dashboard palette."""
    c = colors(mode)
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "IMS.Treeview",
        background=c["row_odd"],
        foreground=c["text"],
        fieldbackground=c["row_odd"],
        rowheight=36,
        borderwidth=0,
        relief="flat",
        font=("Segoe UI", 10),
    )
    style.configure(
        "IMS.Treeview.Heading",
        background=c["card"],
        foreground=c["text_muted"],
        relief="flat",
        borderwidth=0,
        font=("Segoe UI", 10, "bold"),
        padding=(12, 8),
    )
    style.map(
        "IMS.Treeview",
        background=[("selected", c["row_selected"])],
        foreground=[("selected", "#ffffff")],
    )
    style.layout("IMS.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    return style
