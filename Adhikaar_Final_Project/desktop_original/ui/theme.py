# -*- coding: utf-8 -*-
"""ttk styling (scrollbar, combobox) - unchanged from the original prototype."""
import tkinter as tk
from tkinter import ttk

from config import BG, CARD, GOLD, BROWN, BROWN_HOVER


def apply_theme(app):
    style = ttk.Style(app)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Vertical.TScrollbar", background=BROWN, troughcolor=BG, bordercolor=BG,
                    arrowcolor=GOLD, lightcolor=BROWN, darkcolor=BROWN)
    style.map("Vertical.TScrollbar", background=[("active", BROWN_HOVER)])
    style.configure("TCombobox", fieldbackground=CARD, background=BROWN, foreground="white",
                    arrowcolor=GOLD, bordercolor=GOLD, lightcolor=CARD, darkcolor=CARD)
    style.map("TCombobox", fieldbackground=[("readonly", CARD)], foreground=[("readonly", "white")],
              selectbackground=[("readonly", CARD)], selectforeground=[("readonly", "white")])
    app.option_add("*TCombobox*Listbox.background", CARD)
    app.option_add("*TCombobox*Listbox.foreground", "white")
    app.option_add("*TCombobox*Listbox.selectBackground", BROWN)
    app.option_add("*TCombobox*Listbox.selectForeground", "white")
