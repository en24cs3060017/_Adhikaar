# -*- coding: utf-8 -*-
"""ADHIKAAR - MP Legal Rights Emergency Information System.   Run:  python main.py

Home screen (ui/home.py) -> guided chat + AI follow-up (ui/chat.py).
Keep 1506463.jpg in the assets folder. Pillow (PIL) is required for the background.
"""
import tkinter as tk

from ai.engine import Engine
from config import W, H
from ui.chat import start_chat
from ui.home import HomeScreen
from ui.theme import apply_theme


def main():
    app = tk.Tk()
    app.title("Adhikaar")
    app.geometry(f"{W}x{H}")
    app.resizable(False, False)
    apply_theme(app)

    engine = Engine()
    holder = {}

    def open_chat(mode):
        start_chat(app, holder["home"], mode, engine)

    holder["home"] = HomeScreen(app, open_chat)
    app.mainloop()


if __name__ == "__main__":
    main()
