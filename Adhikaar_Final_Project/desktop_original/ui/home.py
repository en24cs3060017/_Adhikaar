# -*- coding: utf-8 -*-
"""Front page - the original 1506463.jpg home screen (same layout, texts, buttons)."""
import os
import tkinter as tk
from tkinter import ttk, messagebox

from PIL import Image, ImageTk

from config import (PANEL, CARD, GOLD, BROWN, MUTED, FONT, W, H, BG_IMAGE_CANDIDATES)


def rounded_rect(canvas, x1, y1, x2, y2, r=14, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


def build_background(path, w, h):
    """Resize the photo and darken the left side and bottom so text stays readable,
    while the statue on the right is left untouched."""
    base = Image.open(path).convert("RGB").resize((w, h), Image.Resampling.LANCZOS)
    dark = Image.new("RGB", (w, h), (20, 13, 9))
    side = Image.new("L", (w, 1))
    side.putdata([int(215 * max(0.0, 1 - x / 560) ** 0.8) for x in range(w)])
    base = Image.composite(dark, base, side.resize((w, h)))
    bottom = Image.new("L", (1, h))
    bottom.putdata([int(190 * min(1.0, max(0.0, (y - (h - 110)) / 110))) for y in range(h)])
    return Image.composite(dark, base, bottom.resize((w, h)))


def find_background():
    for path in BG_IMAGE_CANDIDATES:
        if os.path.exists(path):
            return path
    return BG_IMAGE_CANDIDATES[0]      # missing -> Image.open raises OSError -> plain background


class HomeScreen:
    def __init__(self, app, on_start):
        self.app = app
        self.on_start = on_start                  # called with "Urgent" / "Summarised" / "Detailed"
        self.language = tk.StringVar(value="English")
        self.labels = {}
        self.buttons = {}
        self.home = tk.Canvas(app, width=W, height=H, highlightthickness=0)
        self.home.pack(fill="both", expand=True)
        self.photo = None
        self._load_background()
        self._add_texts()
        self._add_language_menu()
        self.make_button("Urgent", "Urgent", "तत्काल", "Quick steps for right now", "अभी के लिए तुरंत कदम", 352)
        self.make_button("Summarised", "Summarised", "संक्षिप्त", "Short, clear overview", "छोटी और स्पष्ट जानकारी", 407)
        self.make_button("Detailed", "Detailed", "विस्तृत", "Full explanation with sources", "स्रोतों के साथ पूरी जानकारी", 462)
        self.change_language()

    # --- show / hide (used by the chat screen) ---
    def hide(self):
        self.home.pack_forget()

    def show(self):
        self.home.pack(fill="both", expand=True)
        self.change_language()

    # --- building the page ---
    def _load_background(self):
        try:
            self.photo = ImageTk.PhotoImage(build_background(find_background(), W, H))
            self.home.create_image(0, 0, image=self.photo, anchor="nw")
        except (OSError, AttributeError):
            self.photo = None
            self.home.configure(bg=PANEL)
            messagebox.showwarning(
                "Adhikaar",
                "1506463.jpg was not found in the assets folder (or beside main.py). "
                "The app will open with a plain background."
            )

    def add_text(self, key, x, y, english, hindi, color, font, anchor="w"):
        item = self.home.create_text(x, y, text=english, fill=color, font=font, anchor=anchor)
        self.labels[key] = (item, english, hindi)
        return item

    def _add_texts(self):
        self.add_text("name", 50, 105, "ADHIKAAR", "अधिकार", GOLD, (FONT, 40, "bold"))
        self.add_text("tagline", 54, 160, "Know your rights. Know what to do.",
                      "अपने अधिकार जानें। जानें कि क्या करना है।", "white", (FONT, 12))
        self.home.create_line(54, 190, 340, 190, fill=GOLD, width=2)
        self.add_text("language", 55, 222, "Choose your language", "अपनी भाषा चुनें", "white", (FONT, 12))
        self.add_text("situation", 55, 295, "How much detail do you need?", "कितनी जानकारी चाहिए?",
                      "white", (FONT, 14, "bold"))
        self.add_text("helplines", 55, 518, "112 Police  ·  15100 Legal aid  ·  1930 Cyber fraud",
                      "112 पुलिस  ·  15100 कानूनी सहायता  ·  1930 साइबर ठगी", GOLD, (FONT, 10, "bold"))
        self.add_text("disclaimer", 45, 560, "General educational information only — not legal advice",
                      "यह केवल सामान्य शैक्षिक जानकारी है — कानूनी सलाह नहीं", MUTED, (FONT, 9))

    def _add_language_menu(self):
        menu = ttk.Combobox(self.app, textvariable=self.language, values=["English", "Hindi"],
                            state="readonly", width=18, font=(FONT, 10))
        self.home.create_window(55, 252, window=menu, anchor="w")
        menu.bind("<<ComboboxSelected>>", self.change_language)

    def change_language(self, _event=None):
        hindi = self.language.get() == "Hindi"
        self.app.title("अधिकार" if hindi else "Adhikaar")
        for item, english, hindi_text in self.labels.values():
            self.home.itemconfigure(item, text=hindi_text if hindi else english)
        for title, sub, en, hi, sub_en, sub_hi in self.buttons.values():
            self.home.itemconfigure(title, text=hi if hindi else en)
            self.home.itemconfigure(sub, text=sub_hi if hindi else sub_en)

    def make_button(self, mode, english, hindi, sub_en, sub_hi, y):
        home = self.home
        x1, x2, h = 55, 355, 46
        tag = "btn_" + mode
        shape = rounded_rect(home, x1, y - h // 2, x2, y + h // 2, 14,
                             fill=CARD, outline=GOLD, width=1, tags=(tag,))
        title = home.create_text(x1 + 20, y - 8, anchor="w", text=english, fill=GOLD,
                                 font=(FONT, 13, "bold"), tags=(tag,))
        sub = home.create_text(x1 + 20, y + 11, anchor="w", text=sub_en, fill=MUTED,
                               font=(FONT, 9), tags=(tag,))

        def on_enter(_e):
            home.itemconfigure(shape, fill=BROWN)
            home.configure(cursor="hand2")

        def on_leave(_e):
            home.itemconfigure(shape, fill=CARD)
            home.configure(cursor="")

        home.tag_bind(tag, "<Enter>", on_enter)
        home.tag_bind(tag, "<Leave>", on_leave)
        home.tag_bind(tag, "<Button-1>", lambda _e, m=english: (on_leave(None), self.on_start(m)))
        self.buttons[mode] = (title, sub, english, hindi, sub_en, sub_hi)
