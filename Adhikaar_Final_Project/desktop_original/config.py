# -*- coding: utf-8 -*-
"""Central settings: theme (colours / fonts), window size and AI options."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# ---------- theme (change colours / fonts here only) ----------
BG = "#17100d"
PANEL = "#241A14"
CARD = "#30251B"
GOLD = "#F3D69A"
BROWN = "#5A4228"
BROWN_HOVER = "#795A36"
DANGER = "#B03A2E"
MUTED = "#CDBFA8"
FONT = "Segoe UI"
W, H = 1040, 585

# ---------- home-screen background (first file found is used) ----------
BG_IMAGE_CANDIDATES = [
    os.path.join(BASE, "assets", "1506463.jpg"),
    os.path.join(BASE, "1506463.jpg"),
]

# ---------- AI ----------
MODEL = "claude-sonnet-5-5"
API_URL = "https://api.anthropic.com/v1/messages"
MAX_TOKENS = 900
TIMEOUT = 40


def _load_key():
    """API key from ANTHROPIC_API_KEY, else from api_key.txt in the project folder."""
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    path = os.path.join(BASE, "api_key.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    return ""


API_KEY = _load_key()
