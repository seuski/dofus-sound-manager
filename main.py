import tkinter as tk
from tkinter import ttk, filedialog
import threading
import time
import json
import os
import random
import urllib.request
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import pygame
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

try:
    from sniffer import MapSniffer
    SNIFFER_AVAILABLE = True
except ImportError:
    SNIFFER_AVAILABLE = False

# ─── PALETTE EXACTE DOFUS ────────────────────────────────────────────────────
BG_MAIN      = "#1b1d32"
BG_BAR       = "#515171"
BTN_BG       = "#41425e"
BTN_BORDER   = "#5a5b7a"
TEXT_MAIN    = "#c6c6cd"
GREEN_BTN    = "#98b11a"
RED_BTN      = "#8a2020"
TEXT_DIM     = "#7a7a9a"
TEXT_GOLD    = "#c8a824"
DOT_ON       = "#98b11a"
DOT_OFF      = "#cc3a3a"
STAT_ON      = "#98b11a"
STAT_OFF     = "#cc3a3a"
SEP_COL      = "#2a2b46"
BG_LOG       = "#141525"
LOG_OK       = "#6a8a18"
LOG_WARN     = "#8a7020"
LOG_MAP      = "#c8a824"
LOG_DIM      = "#3a3a5a"
VER_ACT_BG   = "#c8a824"
VER_ACT_BD   = "#daba30"
VER_ACT_TXT  = "#1a1a28"
BTN_MUTED    = "#8a8aaa"
VOL_TROUGH   = "#2e3050"
VOL_SLIDER   = "#d0d0e8"

# ─── THÈMES DOFUS ─────────────────────────────────────────────────────────────
THEMES = {
    "default":      {"accent": "#98b11a", "bg_main": "#1b1d32", "bg_dark": "#515171", "bg_log": "#141525", "sep": "#2a2b46", "btn": "#41425e", "label": "Défaut"},
    "bonta":        {"accent": "#5b749c", "bg_main": "#3c3e42", "bg_dark": "#262931", "bg_log": "#1e2028", "sep": "#1e2028", "btn": "#2e3038", "label": "Bonta"},
    "brakmar":      {"accent": "#973c4a", "bg_main": "#262526", "bg_dark": "#1e1d1e", "bg_log": "#191819", "sep": "#1a191a", "btn": "#2a2829", "label": "Brakmar"},
    "tribute":      {"accent": "#737173", "bg_main": "#393b32", "bg_dark": "#262931", "bg_log": "#1e201a", "sep": "#20221a", "btn": "#2e302a", "label": "Tribute"},
    "gold_steel":   {"accent": "#947858", "bg_main": "#343434", "bg_dark": "#26282e", "bg_log": "#1e1e1e", "sep": "#202020", "btn": "#2a2a2a", "label": "Gold & Steel"},
    "belladone":    {"accent": "#816b89", "bg_main": "#312c39", "bg_dark": "#262931", "bg_log": "#1e1a22", "sep": "#1e1a22", "btn": "#2a2530", "label": "Belladone"},
    "unicorn":      {"accent": "#8f5a86", "bg_main": "#393434", "bg_dark": "#26272e", "bg_log": "#221e1e", "sep": "#221e1e", "btn": "#2e2828", "label": "Unicorn"},
    "emerald_mine": {"accent": "#588184", "bg_main": "#242835", "bg_dark": "#262931", "bg_log": "#181c22", "sep": "#181c22", "btn": "#202430", "label": "Emerald Mine"},
    "sufokia":      {"accent": "#4d8a86", "bg_main": "#373740", "bg_dark": "#26272e", "bg_log": "#202028", "sep": "#202028", "btn": "#2c2c35", "label": "Sufokia"},
    "pandala":      {"accent": "#819d58", "bg_main": "#2d2c2d", "bg_dark": "#262931", "bg_log": "#1a1a1a", "sep": "#1a1a1a", "btn": "#252525", "label": "Pandala"},
    "wabbit":       {"accent": "#e07d4a", "bg_main": "#383330", "bg_dark": "#262931", "bg_log": "#221e1c", "sep": "#221e1c", "btn": "#2e2824", "label": "Wabbit"},
}
THEME_ORDER = ["default", "bonta", "brakmar", "tribute", "gold_steel",
               "belladone", "unicorn", "emerald_mine", "sufokia", "pandala", "wabbit"]

DBI_API        = "https://api.dofusbatteriesincluded.fr/data-center/versions/latest/world/maps"
MAP_CACHE_FILE = os.path.join(SCRIPT_DIR, "map_cache.json")

# ─── TABLES MUSICALES ────────────────────────────────────────────────────────
SUBAREA_MUSIC = {
    1: "amakna", 2: "amakna", 3: "amakna", 4: "amakna",
    5: "amakna", 6: "amakna", 7: "amakna", 9: "amakna", 10: "amakna",
    8: "donjon_qutan",
    11: "astrub", 12: "astrub", 13: "astrub", 14: "astrub", 16: "astrub",
    17: "bonta", 18: "bonta", 19: "bonta", 20: "bonta", 21: "bonta",
    22: "brakmar", 23: "brakmar", 24: "brakmar",
    25: "sidimote", 26: "sidimote", 27: "sidimote",
    28: "cania", 29: "cania", 30: "cania", 31: "cania", 32: "cania", 33: "cania",
    34: "ingalsses", 35: "ingalsses", 36: "ingalsses",
    37: "rocky_plains", 38: "rocky_plains",
    39: "sufokia", 40: "sufokia", 41: "sufokia", 42: "sufokia",
    43: "otomai", 44: "otomai", 45: "otomai", 46: "otomai",
    47: "ile_moon", 48: "ile_moon",
    49: "donjon_ilyzaelle",
    50: "ile_wabbits", 51: "ile_wabbits",
    52: "pandala", 53: "pandala_foret", 54: "pandala",
    55: "pandala", 56: "pandala", 57: "pandala", 58: "pandala",
    59: "donjon_sakai",
    60: "foire_trool",
    61: "frigost", 62: "frigost", 63: "frigost", 64: "frigost",
    65: "frigost", 66: "frigost", 67: "frigost", 68: "frigost",
    69: "frigost", 70: "frigost",
    71: "srambad",
    72: "havre_monde", 73: "havre_monde",
    74: "dimensions_divines", 75: "dimensions_divines", 76: "dimensions_divines",
    77: "dimensions_divines", 78: "dimensions_divines", 79: "dimensions_divines",
    80: "dimensions_divines", 81: "dimensions_divines", 82: "dimensions_divines",
    83: "dimensions_divines", 84: "dimensions_divines", 85: "dimensions_divines",
    86: "dimensions_divines", 87: "dimensions_divines", 88: "dimensions_divines",
    89: "dimensions_divines", 90: "dimensions_divines", 91: "dimensions_divines",
    200: "combat_general", 201: "amakna_combat",
    202: "cania_combat",   203: "pandala_combat",
    204: "frigost_combat", 205: "otomai_combat",
    206: "sidimote_combat",
}

SUBAREA_NAME_MUSIC = {
    "amakna": "amakna", "madrestam": "amakna", "craqueleur": "amakna",
    "ingalsse": "ingalsses", "bouftou": "amakna", "cimetière": "amakna",
    "bwork": "amakna", "koalak": "amakna", "champ": "amakna",
    "tofu": "amakna", "plaine": "amakna",
    "astrub": "astrub",
    "bonta": "bonta", "lande": "bonta", "bontarien": "bonta",
    "brakmar": "brakmar", "brakmarian": "brakmar", "brakmaren": "brakmar",
    "sidimote": "sidimote",
    "cania": "cania", "massif": "cania", "kanojedo": "cania",
    "ingalsses": "ingalsses",
    "rocky": "rocky_plains", "rocailleu": "rocky_plains",
    "plaines rocailleuses": "rocky_plains",
    "sufokia": "sufokia", "sufok": "sufokia",
    "otomaï": "otomai", "otomai": "otomai",
    "moon": "ile_moon", "île de moon": "ile_moon",
    "ilyzaelle": "donjon_ilyzaelle",
    "wabbit": "ile_wabbits", "cawotte": "ile_wabbits",
    "pandala": "pandala", "sakaï": "donjon_sakai", "sakai": "donjon_sakai",
    "trool": "foire_trool",
    "frigost": "frigost", "arvel": "frigost", "gelée": "frigost",
    "srambad": "srambad",
    "havre": "havre_monde", "havre-monde": "havre_monde",
    "dimension": "dimensions_divines",
    "qu'tan": "donjon_qutan",
    "donjon": "donjon_theme",
    "salle": "donjon_theme",
    "antre": "donjon_theme",
    "repaire": "donjon_theme",
    "caverne": "donjon_theme",
    "souterrain": "donjon_theme",
    "labyrinthe": "donjon_theme",
    "épreuve": "donjon_theme",
    "combat": "combat_general",
}


# ─── SOUS-ZONES DONJONS ───────────────────────────────────────────────────────
DUNGEON_SUBAREA_IDS = {7, 8, 25, 29, 34, 39, 55, 62, 94, 96, 99, 154, 163, 170, 180, 200, 201, 209, 210, 211, 223, 254, 277, 284, 297, 314, 316, 319, 321, 325, 336, 339, 447, 460, 491, 493, 495, 516, 528, 537, 538, 606, 616, 620, 621, 622, 623, 624, 626, 650, 651, 653, 700, 750, 751, 759, 779, 783, 786, 788, 789, 794, 795, 796, 797, 804, 805, 806, 808, 811, 816, 821, 825, 844, 857, 870, 871, 876, 887, 889, 893, 898, 899, 910, 918, 919, 920, 929, 938, 940, 955, 1025, 1028, 1034, 1038}

# ─── MAP RESOLVER ─────────────────────────────────────────────────────────────
class MapResolver:
    MAP_DB_FILE = os.path.join(SCRIPT_DIR, "map_database.json")

    def __init__(self):
        self.db    = {}
        self.cache = {}
        self._load_db()
        self._load_cache()

    def _load_db(self):
        if os.path.exists(self.MAP_DB_FILE):
            try:
                with open(self.MAP_DB_FILE, encoding="utf-8") as f:
                    self.db = json.load(f)
            except Exception:
                self.db = {}

    def _load_cache(self):
        if os.path.exists(MAP_CACHE_FILE):
            try:
                with open(MAP_CACHE_FILE, encoding="utf-8") as f:
                    self.cache = json.load(f)
            except Exception:
                self.cache = {}

    def save_cache(self):
        try:
            with open(MAP_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def resolve(self, map_id: str) -> dict:
        if map_id in self.db:
            return self.db[map_id]
        if map_id in self.cache:
            return self.cache[map_id]
        try:
            url = f"{DBI_API}/{map_id}"
            req = urllib.request.Request(
                url, headers={"Accept": "application/json",
                              "User-Agent": "DofusSoundManager/2.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
            sub_name = data.get("subAreaName", {}).get("french", "?")
            result = {
                "subAreaId":   data.get("subAreaId"),
                "subAreaName": sub_name,
                "areaName":    data.get("areaName", {}).get("french", "?"),
                "musicKey":    self._name_to_key(sub_name),
                "x":           data.get("position", {}).get("x", 0),
                "y":           data.get("position", {}).get("y", 0),
            }
            self.cache[map_id] = result
            self.save_cache()
            return result
        except Exception:
            return None

    def _name_to_key(self, name: str) -> str:
        n = name.lower()
        for kw, key in SUBAREA_NAME_MUSIC.items():
            if kw in n:
                return key
        return "amakna"

    def get_music_key(self, map_info: dict) -> str:
        if not map_info:
            return "amakna"
        sub_id = map_info.get("subAreaId")
        # Priorité absolue : subzone donjon → donjon_theme
        if sub_id and sub_id in DUNGEON_SUBAREA_IDS:
            return "donjon_theme"
        # Clé pré-calculée dans map_database.json
        if "musicKey" in map_info:
            return map_info["musicKey"]
        # Table statique
        if sub_id and sub_id in SUBAREA_MUSIC:
            return SUBAREA_MUSIC[sub_id]
        return self._name_to_key(map_info.get("subAreaName", ""))


# ─── HELPERS WINDOWS ──────────────────────────────────────────────────────────
def _set_rounded(tk_win):
    try:
        from ctypes import windll, c_int, byref
        hwnd = windll.user32.GetParent(tk_win.winfo_id())
        windll.dwmapi.DwmSetWindowAttribute(hwnd, 33, byref(c_int(2)), 4)
    except Exception:
        pass


def _add_to_taskbar(tk_win):
    """
    Astuce classique : créer une fenêtre parent cachée avec
    overrideredirect=False pour que la fenêtre fille (overrideredirect=True)
    apparaisse quand même dans la barre des tâches Windows.
    """
    try:
        from ctypes import windll, c_int, byref
        import ctypes

        GWL_EXSTYLE    = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        SWP_FLAGS = 0x0027

        hwnd = windll.user32.GetParent(tk_win.winfo_id())
        ex_style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        # Retirer TOOLWINDOW, ajouter APPWINDOW → entrée dans la barre des tâches
        ex_style = (ex_style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
        windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)
        windll.user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, SWP_FLAGS)
    except Exception:
        pass


# ─── APPLICATION ──────────────────────────────────────────────────────────────
class DofusSoundManager:

    WIN_W = 260
    WIN_H = 440

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dofus Sound Manager")
        try:
            self.root.iconbitmap(os.path.join(SCRIPT_DIR, "dofus_logo.ico"))
        except Exception:
            pass
        self.root.geometry(f"{self.WIN_W}x{self.WIN_H}")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(True, True)
        self.root.minsize(220, 300)

        # ── overrideredirect=True : supprime TOUTE la décoration Windows
        #    (barre de titre native incluse). On gère nous-mêmes titre/fermer/min.
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.97)

        # Centrer
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(
            f"{self.WIN_W}x{self.WIN_H}"
            f"+{(sw - self.WIN_W) // 2}+{(sh - self.WIN_H) // 2}")

        _set_rounded(self.root)

        # Forcer l'apparition dans la barre des tâches malgré overrideredirect
        self.root.after(10, lambda: _add_to_taskbar(self.root))

        # Minimiser custom (overrideredirect bloque iconify natif sur certains WM)
        self._is_minimized = False

        # Logo
        self._logo_img = None
        try:
            from PIL import Image, ImageTk
            logo_path = os.path.join(SCRIPT_DIR, "dofus_logo.png")
            if os.path.exists(logo_path):
                img = Image.open(logo_path).convert("RGBA")
                self._logo_img = ImageTk.PhotoImage(
                    img.resize((20, 20), Image.LANCZOS))
        except Exception:
            pass

        # State
        self.version            = tk.StringVar(value="1.29")
        self.is_active          = tk.BooleanVar(value=False)
        self.current_map        = tk.StringVar(value="—")
        self.current_zone       = tk.StringVar(value="—")
        self.volume             = tk.DoubleVar(value=0.7)
        self.custom_folder      = tk.StringVar(value="")
        self._last_map_info     = None
        self._current_music_key = None
        self._sniffer           = None
        self._last_zone_key     = None
        self._music_tip_shown   = False
        self._drag_x = self._drag_y = 0
        self._current_theme    = "default"
        self._theme_circle_refs = {}
        self._tooltip_widget   = None
        self._vol_fill_color   = GREEN_BTN
        self._vol_trough_color = VOL_TROUGH
        self._cur_bg_main = BG_MAIN
        self._cur_bg_dark = BG_BAR
        self._cur_sep     = SEP_COL
        self._cur_btn     = BTN_BG
        self._cur_bg_log  = BG_LOG
        self._toggle_state = "activer"
        self._toggle_hover = False
        self._fade_thread   = None
        self._next_path     = None
        self._compact = False

        self.resolver = MapResolver()
        self._build_ui()
        self._load_config()
        self.root.after(300, self._highlight_active_theme)
        self._log("Dofus Sound Manager démarré.")
        if self.resolver.db:
            self._log(f"✓ {len(self.resolver.db)} maps chargées.", "ok")
        threading.Thread(target=self._check_api, daemon=True).start()
        threading.Thread(target=self._check_update, daemon=True).start()

    # ── MINIMISER custom ──────────────────────────────────────────────────────
    def _minimize(self):
        """
        Avec overrideredirect=True, iconify() ne fonctionne pas sur tous les
        systèmes. On utilise l'API Win32 directement.
        """
        try:
            from ctypes import windll
            hwnd = windll.user32.GetParent(self.root.winfo_id())
            windll.user32.ShowWindow(hwnd, 6)   # SW_MINIMIZE = 6
        except Exception:
            self.root.iconify()

    # ── DRAG ──────────────────────────────────────────────────────────────────
    def _drag_start(self, e):
        self._drag_x = e.x_root - self.root.winfo_x()
        self._drag_y = e.y_root - self.root.winfo_y()

    def _drag_move(self, e):
        self.root.geometry(
            f"+{e.x_root - self._drag_x}+{e.y_root - self._drag_y}")

    def _grip_start(self, e):
        self._grip_x = e.x_root
        self._grip_y = e.y_root
        self._grip_w = self.root.winfo_width()
        self._grip_h = self.root.winfo_height()

    def _grip_drag(self, e):
        nw = max(220, self._grip_w + e.x_root - self._grip_x)
        nh = max(300, self._grip_h + e.y_root - self._grip_y)
        self.root.geometry(f"{nw}x{nh}")

    def _make_draggable(self, w):
        w.bind("<ButtonPress-1>", self._drag_start)
        w.bind("<B1-Motion>",     self._drag_move)

    # ── BUILD UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        r = self.root

        # ── TITLEBAR ────────────────────────────────────────────────────────
        tb = tk.Frame(r, bg=BG_BAR, height=38)
        tb.pack(fill="x")
        tb.pack_propagate(False)
        self._make_draggable(tb)

        # Logo gauche
        logo_frame = tk.Frame(tb, bg=BG_BAR, width=32)
        logo_frame.pack(side="left", fill="y")
        logo_frame.pack_propagate(False)
        if self._logo_img:
            lbl = tk.Label(logo_frame, image=self._logo_img,
                           bg=BG_BAR, cursor="fleur")
            lbl.place(relx=0.5, rely=0.5, anchor="center")
            self._make_draggable(lbl)

        # Titre centré
        lbl_t = tk.Label(tb, text="Sound Manager",
                         font=("Segoe UI", 10, "bold"),
                         bg=BG_BAR, fg=TEXT_MAIN)
        lbl_t.pack(side="left", expand=True)
        self._make_draggable(lbl_t)

        # ── Ordre corrigé : CROIX d'abord (à droite), puis TIRET (avant la croix)
        # On pack side="right" : le premier packé est le plus à droite.

        # ── Bouton FERMER (tout à droite) ──
        lbl_x = tk.Label(tb, text="✕", font=("Segoe UI", 10),
                         bg=BG_BAR, fg=TEXT_DIM,
                         cursor="hand2", padx=8)
        lbl_x.pack(side="right", fill="y")
        lbl_x.bind("<Button-1>", lambda e: self._on_close())
        lbl_x.bind("<Enter>",    lambda e: lbl_x.config(fg="#ee4444"))
        lbl_x.bind("<Leave>",    lambda e: lbl_x.config(fg=TEXT_DIM))

        # ── Bouton MINIMISER (juste avant la croix) ──
        lbl_min = tk.Label(tb, text="─", font=("Segoe UI", 11),
                           bg=BG_BAR, fg=TEXT_DIM,
                           cursor="hand2", padx=8)
        lbl_min.pack(side="right", fill="y")
        lbl_min.bind("<Button-1>", lambda e: self._minimize())
        lbl_min.bind("<Enter>",    lambda e: lbl_min.config(fg=TEXT_MAIN))
        lbl_min.bind("<Leave>",    lambda e: lbl_min.config(fg=TEXT_DIM))

        # ── Bouton COMPACT (flèche haut/bas)
        self._lbl_compact = tk.Label(tb, text="▲", font=("Segoe UI", 9),
                                     bg=BG_BAR, fg=TEXT_DIM,
                                     cursor="hand2", padx=8)
        self._lbl_compact.pack(side="right", fill="y")
        self._lbl_compact.bind("<Button-1>", lambda e: self._toggle_compact())
        self._lbl_compact.bind("<Enter>",    lambda e: self._lbl_compact.config(fg=TEXT_MAIN))
        self._lbl_compact.bind("<Leave>",    lambda e: self._lbl_compact.config(fg=TEXT_DIM))

        tk.Frame(r, bg=SEP_COL, height=1).pack(fill="x")

        # ── BODY (collapsible)
        self._collapsible = tk.Frame(r, bg=BG_MAIN)
        self._collapsible.pack(fill="both", expand=True)
        body = tk.Frame(self._collapsible, bg=BG_MAIN, padx=12, pady=6)
        body.pack(fill="both", expand=True)

        # VERSION
        self._sec(body, "VERSION")
        self._ver_labels = [("⚔  1.29", "1.29"), ("⊙  2.0", "2.0"), ("♪  Custom", "perso")]
        self._ver_active = "1.29"
        self._ver_hover  = None
        self.ver_btns    = {}
        self._ver_canvas = tk.Canvas(body, height=30, bg=BG_MAIN,
                                     highlightthickness=0, cursor="hand2")
        self._ver_canvas.pack(fill="x", pady=(3, 0))
        self._ver_canvas.bind("<Configure>", lambda e: self._draw_ver_btns())
        self._ver_canvas.bind("<Button-1>",  self._ver_canvas_click)
        self._ver_canvas.bind("<Motion>",    self._ver_canvas_motion)
        self._ver_canvas.bind("<Leave>",     lambda e: self._ver_canvas_leave())
        self.root.after(80, self._draw_ver_btns)

        self._sep(body)

        # STATUT
        self._sec(body, "STATUT")
        sr = tk.Frame(body, bg=BG_MAIN)
        sr.pack(fill="x", pady=(3, 2))
        self.dot_cv = tk.Canvas(sr, width=9, height=9,
                                bg=BG_MAIN, highlightthickness=0)
        self.dot_cv.pack(side="left", padx=(0, 5))
        self._dot = self.dot_cv.create_oval(1, 1, 8, 8,
                                            fill=DOT_OFF, outline="")
        self.stat_lbl = tk.Label(sr, text="INACTIF",
                                 font=("Segoe UI", 8, "bold"),
                                 bg=BG_MAIN, fg=STAT_OFF)
        self.stat_lbl.pack(side="left")

        for key_txt, var in [("MAP", self.current_map), ("ZONE", self.current_zone)]:
            row = tk.Frame(body, bg=BG_MAIN)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=key_txt,
                     font=("Segoe UI", 7, "bold"),
                     bg=BG_MAIN, fg=TEXT_DIM,
                     width=5, anchor="w").pack(side="left")
            tk.Label(row, textvariable=var,
                     font=("Segoe UI", 8),
                     bg=BG_MAIN, fg=TEXT_GOLD,
                     anchor="w", justify="left",
                     wraplength=0).pack(side="left", padx=3, fill="x", expand=True)

        self._sep(body)

        # ── VOLUME ── (barre plus visible, curseur clair)
        self._sec(body, "VOLUME")
        vr = tk.Frame(body, bg=BG_MAIN)
        vr.pack(fill="x", pady=(3, 0))
        tk.Label(vr, text="🔊", bg=BG_MAIN, fg=TEXT_MAIN,
                 font=("Segoe UI", 10)).pack(side="left")

        # Style ttk Scale avec curseur clair et piste plus visible
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "D.Horizontal.TScale",
            background=BG_MAIN,
            troughcolor=VOL_TROUGH,      # piste plus foncée / contrastée
            sliderlength=16,             # curseur plus grand
            sliderrelief="flat",
            borderwidth=0,
        )
        # Sur Windows le slider color se configure via element_create/layout,
        # on utilise un Canvas custom pour un rendu parfaitement contrôlé.
        self._vol_canvas = tk.Canvas(
            vr, height=20, bg=BG_MAIN, highlightthickness=0, cursor="hand2")
        self._vol_canvas.pack(side="left", fill="x", expand=True, padx=6)
        self._vol_canvas.bind("<Configure>",   self._draw_volume_bar)
        self._vol_canvas.bind("<ButtonPress-1>",  self._vol_click)
        self._vol_canvas.bind("<B1-Motion>",      self._vol_drag)

        self.vol_lbl = tk.Label(vr, text="70%",
                                font=("Segoe UI", 8, "bold"),
                                bg=BG_MAIN, fg=TEXT_MAIN, width=4)
        self.vol_lbl.pack(side="right")

        # Dessiner au prochain idle (après que le canvas ait une taille)
        self.root.after(50, lambda: self._draw_volume_bar(None))

        self._sep(body)

        # JOURNAL
        self._sec(body, "JOURNAL")
        self.log_text = tk.Text(
            body, height=4,
            bg=BG_LOG, fg=LOG_DIM,
            font=("Consolas", 7),
            relief="flat", bd=0,
            state="disabled", wrap="word",
            highlightthickness=1,
            highlightbackground=SEP_COL,
            highlightcolor=SEP_COL,
            padx=5, pady=3)
        self.log_text.pack(fill="both", expand=True, pady=(3, 0))
        self.log_text.tag_config("ok",   foreground=LOG_OK)
        self.log_text.tag_config("warn", foreground=LOG_WARN)
        self.log_text.tag_config("map",  foreground=LOG_MAP)

        self._sep(body)

        # ── THÈME
        self._sec(body, "THÈME")
        self._theme_palette_frame = tk.Frame(body, bg=BG_MAIN)
        self._theme_palette_frame.pack(fill="x", pady=(4, 2))
        for key in THEME_ORDER:
            t = THEMES[key]
            cv = tk.Canvas(self._theme_palette_frame, width=16, height=16,
                           bg=BG_MAIN, highlightthickness=0, cursor="hand2")
            cv.pack(side="left", padx=(0, 4))
            oid = cv.create_oval(1, 1, 15, 15, fill=t["accent"], outline="")
            self._theme_circle_refs[key] = (cv, oid)
            cv.bind("<Button-1>", lambda e, k=key: self._apply_theme(k))
            cv.bind("<Enter>",    lambda e, k=key, c=cv: self._theme_tooltip_show(k, c))
            cv.bind("<Leave>",    lambda e: self._theme_tooltip_hide())

        # FOOTER
        self._footer_sep = tk.Frame(r, bg=SEP_COL, height=1)
        self._footer_sep.pack(fill="x")
        self._footer_frame = tk.Frame(r, bg=BG_BAR, padx=12, pady=10)
        self._footer_frame.pack(fill="x")
        self._toggle_canvas = tk.Canvas(self._footer_frame, height=36,
                                        bg=BG_BAR, highlightthickness=0, cursor="hand2")
        self._toggle_canvas.pack(fill="x")
        self._toggle_canvas.bind("<Configure>", lambda e: self._draw_toggle_btn())
        self._toggle_canvas.bind("<Button-1>",  lambda e: self._toggle_active())
        self._toggle_canvas.bind("<Enter>",     lambda e: self._toggle_btn_hover(True))
        self._toggle_canvas.bind("<Leave>",     lambda e: self._toggle_btn_hover(False))
        self.root.after(80, self._draw_toggle_btn)

        # ── RESIZE GRIP (coin bas-droite)
        self._grip = tk.Canvas(r, width=12, height=12,
                               bg=BG_BAR, highlightthickness=0, cursor="size_nw_se")
        self._grip.place(relx=1.0, rely=1.0, anchor="se")
        self._grip.create_line(4,12,12,4, fill=TEXT_DIM, width=1)
        self._grip.create_line(8,12,12,8, fill=TEXT_DIM, width=1)
        self._grip.bind("<ButtonPress-1>",  self._grip_start)
        self._grip.bind("<B1-Motion>",      self._grip_drag)
        self._grip_x = self._grip_y = 0

    # ── VOLUME BAR (canvas custom) ────────────────────────────────────────────
    def _draw_volume_bar(self, event):
        cv = self._vol_canvas
        cv.delete("all")
        w = cv.winfo_width()
        h = cv.winfo_height()
        if w <= 1:
            return
        bar_h   = 6
        knob_r  = 7
        y_mid   = h // 2
        val     = self.volume.get()                    # 0.0 – 1.0
        fill_x  = int(knob_r + (w - 2 * knob_r) * val)

        # Piste fond
        cv.create_rounded_rect = _canvas_rounded_rect.__get__(cv, tk.Canvas)
        _canvas_rounded_rect(cv,
            knob_r, y_mid - bar_h // 2,
            w - knob_r, y_mid + bar_h // 2,
            r=3, fill=self._vol_trough_color, outline="")

        # Piste remplie (vert Dofus)
        if fill_x > knob_r:
            _canvas_rounded_rect(cv,
                knob_r, y_mid - bar_h // 2,
                fill_x, y_mid + bar_h // 2,
                r=3, fill=self._vol_fill_color, outline="")

        # Curseur clair
        cv.create_oval(
            fill_x - knob_r, y_mid - knob_r,
            fill_x + knob_r, y_mid + knob_r,
            fill=VOL_SLIDER, outline=BTN_BORDER, width=1)

    def _vol_set(self, x):
        cv   = self._vol_canvas
        w    = cv.winfo_width()
        knob_r = 7
        val  = max(0.0, min(1.0, (x - knob_r) / max(1, w - 2 * knob_r)))
        self.volume.set(val)
        pct  = int(val * 100)
        self.vol_lbl.config(text=f"{pct}%")
        self._draw_volume_bar(None)
        if AUDIO_AVAILABLE:
            try:
                pygame.mixer.music.set_volume(val)
            except Exception:
                pass

    def _vol_click(self, e):
        self._vol_set(e.x)

    def _vol_drag(self, e):
        self._vol_set(e.x)

    # ── HELPERS ───────────────────────────────────────────────────────────────
    def _sec(self, parent, text):
        f = tk.Frame(parent, bg=BG_MAIN)
        f.pack(fill="x", pady=(4, 0))
        tk.Label(f, text=text, font=("Segoe UI", 7, "bold"),
                 bg=BG_MAIN, fg=TEXT_DIM).pack(side="left")

    def _sep(self, parent):
        tk.Frame(parent, bg=SEP_COL, height=1).pack(fill="x", pady=5)

    # ── BOUTONS CANVAS ────────────────────────────────────────────────────────
    @staticmethod
    def _hex_lighten(hex_col, factor):
        h = hex_col.lstrip("#")
        r,g,b = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
        return "#{:02x}{:02x}{:02x}".format(
            min(255,int(r*factor)),min(255,int(g*factor)),min(255,int(b*factor)))

    @staticmethod
    def _hex_darken(hex_col, factor):
        h = hex_col.lstrip("#")
        r,g,b = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
        return "#{:02x}{:02x}{:02x}".format(int(r*factor),int(g*factor),int(b*factor))

    def _draw_ver_btns(self):
        # Redessiner aussi le canvas mini si en mode compact
        if self._compact and hasattr(self, "_mini_ver_canvas"):
            self._draw_ver_btns_on(self._mini_ver_canvas)
        cv = self._ver_canvas
        cv.delete("all")
        w = cv.winfo_width(); h = cv.winfo_height()
        if w <= 4: return
        t   = THEMES[self._current_theme]
        n   = len(self._ver_labels)
        gap = 4
        bw  = (w - gap * (n - 1)) // n
        for i, (lbl, val) in enumerate(self._ver_labels):
            x1 = i * (bw + gap)
            x2 = x1 + bw
            if val == self._ver_active:
                fill = t["accent"]; fg = "#ffffff"
            elif val == self._ver_hover:
                fill = self._hex_lighten(t["btn"], 1.2); fg = "#aaaaaa"
            else:
                fill = t["btn"]; fg = "#8a8aaa"
            _canvas_rounded_rect(cv, x1, 0, x2, h, r=6, fill=fill, outline="")
            cv.create_text((x1+x2)//2, h//2, text=lbl,
                           font=("Segoe UI", 8, "bold"), fill=fg, anchor="center")

    def _ver_canvas_click(self, event):
        w  = self._ver_canvas.winfo_width()
        n  = len(self._ver_labels)
        bw = (w - 4*(n-1)) // n
        for i, (_, val) in enumerate(self._ver_labels):
            x1 = i*(bw+4); x2 = x1+bw
            if x1 <= event.x <= x2:
                self._select_version(val); break

    def _ver_canvas_motion(self, event):
        w  = self._ver_canvas.winfo_width()
        n  = len(self._ver_labels)
        bw = (w - 4*(n-1)) // n
        hov = None
        for i, (_, val) in enumerate(self._ver_labels):
            x1 = i*(bw+4); x2 = x1+bw
            if x1 <= event.x <= x2:
                hov = val; break
        if hov != self._ver_hover:
            self._ver_hover = hov
            self._draw_ver_btns()

    def _ver_canvas_leave(self):
        self._ver_hover = None
        self._draw_ver_btns()

    def _draw_ver_btns_on(self, cv):
        """Dessine les boutons version sur n'importe quel canvas (normal ou mini)."""
        cv.delete("all")
        w = cv.winfo_width(); h = cv.winfo_height()
        if w <= 4: return
        t   = THEMES[self._current_theme]
        n   = len(self._ver_labels)
        gap = 4
        bw  = (w - gap * (n - 1)) // n
        for i, (lbl, val) in enumerate(self._ver_labels):
            x1 = i * (bw + gap); x2 = x1 + bw
            fill = t["accent"] if val == self._ver_active else t["btn"]
            fg   = "#ffffff"    if val == self._ver_active else "#8a8aaa"
            _canvas_rounded_rect(cv, x1, 0, x2, h, r=6, fill=fill, outline="")
            cv.create_text((x1+x2)//2, h//2, text=lbl,
                           font=("Segoe UI", 8, "bold"), fill=fg, anchor="center")

    def _mini_ver_click(self, event):
        cv = self._mini_ver_canvas
        w  = cv.winfo_width()
        n  = len(self._ver_labels)
        bw = (w - 4*(n-1)) // n
        for i, (_, val) in enumerate(self._ver_labels):
            x1 = i*(bw+4); x2 = x1+bw
            if x1 <= event.x <= x2:
                self._select_version(val)
                self._draw_ver_btns_on(cv)
                break

    def _draw_toggle_btn(self):
        cv = self._toggle_canvas
        cv.delete("all")
        w = cv.winfo_width(); h = cv.winfo_height()
        if w <= 1: return
        t = THEMES[self._current_theme]
        if self._toggle_state == "desactiver":
            color = RED_BTN
            text  = "⏹  DÉSACTIVER"
        else:
            color = t["accent"]
            text  = "▶  ACTIVER"
        fill = self._hex_lighten(color, 1.15) if self._toggle_hover else color
        _canvas_rounded_rect(cv, 0, 0, w, h, r=8, fill=fill, outline="")
        cv.create_text(w//2, h//2, text=text,
                       font=("Segoe UI", 10, "bold"), fill="#ffffff", anchor="center")

    def _toggle_btn_hover(self, on):
        self._toggle_hover = on
        self._draw_toggle_btn()

    # ── THÈME ─────────────────────────────────────────────────────────────────
    def _highlight_active_theme(self):
        key = self._current_theme
        if key in self._theme_circle_refs:
            cv, oid = self._theme_circle_refs[key]
            cv.itemconfig(oid, outline="#ffffff", width=2)

    def _apply_theme(self, key):
        old_key = self._current_theme
        if old_key in self._theme_circle_refs:
            ov, oo = self._theme_circle_refs[old_key]
            ov.itemconfig(oo, outline="")
        self._current_theme = key
        t       = THEMES[key]
        accent  = t["accent"]; bg_main = t["bg_main"]; bg_dark = t["bg_dark"]
        sep_col = t["sep"];    btn_bg  = t["btn"];     bg_log  = t["bg_log"]
        last = (self._cur_bg_main, self._cur_bg_dark, self._cur_sep,
                self._cur_btn, self._cur_bg_log)

        def recolor(widget):
            try:
                cur = widget.cget("bg")
                if   cur in (BG_MAIN, last[0]): widget.configure(bg=bg_main)
                elif cur in (BG_BAR,  last[1]): widget.configure(bg=bg_dark)
                elif cur in (SEP_COL, last[2]): widget.configure(bg=sep_col)
                elif cur in (BTN_BG,  last[3]): widget.configure(bg=btn_bg)
                elif cur in (BG_LOG,  last[4]): widget.configure(bg=bg_log)
            except Exception: pass
            for child in widget.winfo_children():
                recolor(child)

        recolor(self.root)
        self._cur_bg_main = bg_main; self._cur_bg_dark = bg_dark
        self._cur_sep = sep_col;     self._cur_btn = btn_bg
        self._cur_bg_log = bg_log

        self._theme_palette_frame.configure(bg=bg_main)
        for k, (cv2, _) in self._theme_circle_refs.items():
            cv2.configure(bg=bg_main)

        if self.is_active.get():
            self.dot_cv.itemconfig(self._dot, fill=accent)

        self._vol_fill_color   = accent
        self._vol_trough_color = self._hex_darken(bg_main, 0.5)
        self._draw_volume_bar(None)

        self.log_text.configure(bg=bg_log)
        self.log_text.tag_config("ok", foreground=accent)

        self._footer_sep.configure(bg=sep_col)
        self._footer_frame.configure(bg=bg_dark)
        self._toggle_canvas.configure(bg=bg_dark)
        self._draw_toggle_btn()

        self._draw_ver_btns()

        cv, oid = self._theme_circle_refs[key]
        cv.itemconfig(oid, outline="#ffffff", width=2)
        self._save_config()

    def _theme_tooltip_show(self, key, canvas):
        self._theme_tooltip_hide()
        label = THEMES[key]["label"]
        cx = canvas.winfo_rootx() + 8 - self.root.winfo_rootx()
        cy = canvas.winfo_rooty() - self.root.winfo_rooty() - 20
        t  = THEMES[self._current_theme]
        tip = tk.Label(self.root, text=label, font=("Segoe UI", 7),
                       bg=t["bg_dark"], fg=TEXT_MAIN, padx=5, pady=2,
                       relief="flat", bd=0)
        tip.place(x=cx, y=cy)
        tip.update_idletasks()
        tip.place(x=max(0, cx - tip.winfo_width()//2), y=cy)
        self._tooltip_widget = tip

    def _theme_tooltip_hide(self):
        if self._tooltip_widget:
            try: self._tooltip_widget.destroy()
            except Exception: pass
            self._tooltip_widget = None

    # ── COMPACT MODE ──────────────────────────────────────────────────────────
    def _toggle_compact(self):
        self._compact = not self._compact
        t  = THEMES[self._current_theme]
        cw = self.root.winfo_width()

        if self._compact:
            self._collapsible.pack_forget()
            self._footer_sep.pack_forget()
            self._footer_frame.pack_forget()
            self._lbl_compact.config(text="▼")

            self._mini_frame = tk.Frame(self.root, bg=t["bg_main"], padx=12, pady=6)
            self._mini_frame.pack(fill="x")

            # VERSION mini
            tk.Label(self._mini_frame, text="VERSION",
                     font=("Segoe UI", 7, "bold"),
                     bg=t["bg_main"], fg=TEXT_DIM).pack(anchor="w")
            self._mini_ver_canvas = tk.Canvas(self._mini_frame, height=26,
                                              bg=t["bg_main"], highlightthickness=0,
                                              cursor="hand2")
            self._mini_ver_canvas.pack(fill="x", pady=(2, 6))
            self._mini_ver_canvas.bind("<Configure>", lambda e: self._draw_ver_btns_on(self._mini_ver_canvas))
            self._mini_ver_canvas.bind("<Button-1>",  self._mini_ver_click)

            # STATUT
            tk.Frame(self._mini_frame, bg=t["sep"], height=1).pack(fill="x", pady=(0, 4))
            sr = tk.Frame(self._mini_frame, bg=t["bg_main"])
            sr.pack(fill="x", pady=(0, 2))
            dot_cv = tk.Canvas(sr, width=9, height=9, bg=t["bg_main"], highlightthickness=0)
            dot_cv.pack(side="left", padx=(0, 5))
            fill_c = t["accent"] if self.is_active.get() else DOT_OFF
            dot_cv.create_oval(1, 1, 8, 8, fill=fill_c, outline="")
            status_txt = "ACTIF" if self.is_active.get() else "INACTIF"
            status_fg  = t["accent"] if self.is_active.get() else STAT_OFF
            tk.Label(sr, text=status_txt, font=("Segoe UI", 8, "bold"),
                     bg=t["bg_main"], fg=status_fg).pack(side="left")

            for key_txt, var in [("MAP", self.current_map), ("ZONE", self.current_zone)]:
                row = tk.Frame(self._mini_frame, bg=t["bg_main"])
                row.pack(fill="x", pady=1)
                tk.Label(row, text=key_txt, font=("Segoe UI", 7, "bold"),
                         bg=t["bg_main"], fg=TEXT_DIM,
                         width=5, anchor="w").pack(side="left")
                tk.Label(row, textvariable=var, font=("Segoe UI", 8),
                         bg=t["bg_main"], fg=TEXT_GOLD,
                         anchor="w", justify="left",
                         wraplength=0).pack(side="left", padx=3, fill="x", expand=True)

            # Hauteur naturelle calculée par tkinter
            self.root.update_idletasks()
            natural_h = self.root.winfo_reqheight()
            self.root.geometry(f"{cw}x{natural_h}")
            self.root.minsize(180, natural_h)
            self.root.after(60, lambda: self._draw_ver_btns_on(self._mini_ver_canvas))

        else:
            if hasattr(self, "_mini_frame"):
                self._mini_frame.destroy()
            self._collapsible.pack(fill="both", expand=True)
            self._footer_sep.pack(fill="x")
            self._footer_frame.pack(fill="x")
            self._lbl_compact.config(text="▲")
            self.root.minsize(220, 300)
            self.root.geometry(f"{cw}x{self.WIN_H}")

    # ── VERSION ───────────────────────────────────────────────────────────────
    def _select_version(self, v, restart_music=True):
        prev = self.version.get()
        # Si Custom : ouvrir sélecteur de dossier
        if v == "perso":
            folder = filedialog.askdirectory(
                title="Choisir le dossier de musiques Custom",
                initialdir=self.custom_folder.get() or SCRIPT_DIR)
            if not folder:
                return  # annulé — on ne change pas de version
            self.custom_folder.set(folder)
            self._log(f"📁 Custom : {os.path.basename(folder)}", "ok")
            self._save_config()
        self.version.set(v)
        self._ver_active = v
        self._draw_ver_btns()
        if restart_music and prev != v:
            self._log(f"Version : {v}")
            if self._last_map_info and self.is_active.get():
                self._current_music_key = None
                self._play_for_info(self._last_map_info)

    # ── TOGGLE ────────────────────────────────────────────────────────────────
    def _toggle_active(self):
        if not self.is_active.get():
            self.is_active.set(True)
            self.stat_lbl.config(text="ACTIF", fg=THEMES[self._current_theme]["accent"])
            self.dot_cv.itemconfig(self._dot, fill=THEMES[self._current_theme]["accent"])
            self._toggle_state = "desactiver"
            self._draw_toggle_btn()
            self._log("Gestionnaire activé.")
            if not self._music_tip_shown:
                self._show_music_tip()
            if SNIFFER_AVAILABLE:
                initial_id = self._ask_mapid()
                sniffer = MapSniffer(callback=self._on_map_change,
                                     resync_callback=self._resync_mapid)
                if initial_id:
                    sniffer._last_map_id = initial_id
                    self._log("🔍 Scan en cours, musique dans quelques secondes...", "warn")
                self._sniffer = sniffer
                threading.Thread(target=lambda s=sniffer: s.start(),
                                 daemon=True).start()
            else:
                self._log("⚠ Sniffer non disponible.", "warn")
        else:
            self.is_active.set(False)
            self.stat_lbl.config(text="INACTIF", fg=STAT_OFF)
            self.dot_cv.itemconfig(self._dot, fill=DOT_OFF)
            self.stat_lbl.config(text="INACTIF", fg=STAT_OFF)
            self._toggle_state = "activer"
            self._draw_toggle_btn()
            self.current_map.set("—")
            self.current_zone.set("—")
            self._stop_music()
            self._log("Gestionnaire désactivé.")

    # ── POPUPS ────────────────────────────────────────────────────────────────
    def _make_popup(self, title, w, h):
        t = THEMES[self._current_theme]
        win = tk.Toplevel(self.root)
        win.title(title); win.configure(bg=t["bg_main"])
        win.resizable(False, False); win.overrideredirect(True)
        win.attributes("-topmost", True); win.grab_set()
        win._theme = t
        wx = self.root.winfo_x() + (self.WIN_W - w) // 2
        wy = self.root.winfo_y() + (self.WIN_H - h) // 2
        win.geometry(f"{w}x{h}+{wx}+{wy}")
        _set_rounded(win)
        _dx, _dy = [0], [0]
        def ds(e): _dx[0]=e.x_root-win.winfo_x(); _dy[0]=e.y_root-win.winfo_y()
        def dm(e): win.geometry(f"+{e.x_root-_dx[0]}+{e.y_root-_dy[0]}")
        tb = tk.Frame(win, bg=t["bg_dark"], height=36)
        tb.pack(fill="x"); tb.pack_propagate(False)
        tb.bind("<ButtonPress-1>", ds); tb.bind("<B1-Motion>", dm)
        lbl = tk.Label(tb, text=title, font=("Segoe UI", 9, "bold"),
                       bg=t["bg_dark"], fg=TEXT_MAIN)
        lbl.place(relx=0.5, rely=0.5, anchor="center")
        lbl.bind("<ButtonPress-1>", ds); lbl.bind("<B1-Motion>", dm)
        tk.Frame(win, bg=t["sep"], height=1).pack(fill="x")
        return win

    def _popup_ok_btn(self, win, cmd, text="OK"):
        t = getattr(win, "_theme", THEMES[self._current_theme])
        tk.Frame(win, bg=t["sep"], height=1).pack(fill="x", side="bottom")
        f = tk.Frame(win, bg=t["bg_dark"], padx=12, pady=10)
        f.pack(fill="x", side="bottom")
        tk.Button(f, text=text, font=("Segoe UI", 10, "bold"),
                  bg=t["accent"], fg="#ffffff",
                  activebackground=t["accent"], activeforeground="#ffffff",
                  relief="flat", bd=0, pady=10, cursor="hand2",
                  highlightthickness=0, command=cmd).pack(fill="x")

    def _show_music_tip(self):
        win = self._make_popup("Son Dofus", 270, 200)
        t = win._theme
        body = tk.Frame(win, bg=t["bg_main"], padx=18, pady=12)
        body.pack(fill="both", expand=True)
        tk.Label(body,
                 text="Dans Dofus  →  Options  →  Son\n"
                      "mettez le curseur  Musique  à  0.\n\n"
                      "Les effets sonores resteront actifs !",
                 font=("Segoe UI", 9), bg=t["bg_main"], fg=TEXT_MAIN,
                 justify="center").pack()
        dont_show = tk.BooleanVar(value=False)
        tk.Checkbutton(body, text="Ne plus afficher",
                       variable=dont_show, bg=t["bg_main"], fg=TEXT_DIM,
                       selectcolor=t["btn"], activebackground=t["bg_main"],
                       font=("Segoe UI", 8)).pack(pady=(8, 0))

        def close():
            if dont_show.get():
                self._music_tip_shown = True
                self._save_config()
            win.destroy()

        self._popup_ok_btn(win, close)
        win.wait_window()

    def _ask_mapid(self):
        result = [None]
        win = self._make_popup("MapId initial", 260, 195)
        t = win._theme
        body = tk.Frame(win, bg=t["bg_main"], padx=16, pady=12)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Tapez /mapid dans Dofus\npuis entrez le numéro ici :",
                 font=("Segoe UI", 9), bg=t["bg_main"], fg=TEXT_MAIN,
                 justify="center").pack()
        entry = tk.Entry(body, font=("Consolas", 11),
                         bg=t["btn"], fg=TEXT_MAIN, insertbackground=TEXT_MAIN,
                         relief="flat", bd=6, justify="center",
                         highlightthickness=1, highlightbackground=t["accent"])
        entry.pack(fill="x", pady=10)
        entry.focus()

        def confirm(e=None):
            try:
                result[0] = int(entry.get().strip())
            except Exception:
                result[0] = None
            win.destroy()

        entry.bind("<Return>", confirm)
        self._popup_ok_btn(win, confirm)
        win.wait_window()
        return result[0]

    # ── MAP CHANGE ────────────────────────────────────────────────────────────
    def _on_map_change(self, map_id: str):
        if not self.is_active.get():
            return False
        info = self.resolver.resolve(map_id)
        if info:
            self._last_map_info = info
            name = f"{info['subAreaName']}  ({info['x']},{info['y']})"
            zone = f"{info['subAreaName']} — {info['areaName']}"
            self.root.after(0, lambda: self.current_map.set(name))
            self.root.after(0, lambda: self.current_zone.set(zone))
            self.root.after(0, lambda: self._log(f"📍 {name}", "map"))
            self.root.after(0, lambda: self._play_for_info(info))
            return True
        else:
            # Map inconnue — si on vient d'une zone connue, jouer la musique de combat
            if self._last_zone_key and self._current_music_key not in self.COMBAT_KEYS:
                combat_key = self.ZONE_COMBAT_MAP.get(self._last_zone_key,
                             random.choice(self.COMBAT_GENERAL_POOL))
                ver = self.version.get()
                path = self._find_file(combat_key, ver)
                if path:
                    self._current_music_key = combat_key
                    self.root.after(0, lambda p=path, k=combat_key: (
                        self._play_audio(p),
                        self._log(f"🎵 {os.path.basename(p)}", "ok")
                    ))
            # Map inconnue : on ne logge rien, c'est du bruit pendant le scan
            return False

    def _resync_mapid(self):
        def ask():
            import tkinter.simpledialog
            self._log("⚠ Sniffer perdu — tapez /mapid dans Dofus", "warn")
            mid = tkinter.simpledialog.askstring(
                "Resynchronisation",
                "Le sniffer a perdu la map.\nTapez /mapid puis entrez ici :",
                parent=self.root)
            if mid:
                try:
                    if self._sniffer:
                        self._sniffer.set_mapid(int(mid.strip()))
                except Exception:
                    pass
        self.root.after(0, ask)

    # ── MUSIQUE ───────────────────────────────────────────────────────────────
    COMBAT_KEYS = {
        "combat_general", "combat", "combat_6",
        "frigost_combat", "sufokia_combat", "xelorium_combat",
        "cimetieres_combat", "dimensions_combat", "saharach_combat1", "saharach_combat2",
        "crocuzco_combat", "martegel_combat", "astrub_combat",
        "pwak_combat", "nimotopia_combat", "clepsydre_combat",
        "songes_combat", "eliocalypse_combat", "combat_kolizeum",
        # Combats donjon
        *[f"donjon_combat{i}" for i in range(1, 9)],
        *["donjon_boss1","donjon_boss2","donjon_boss3","donjon_boss4",
          "donjon_boss_harebourg","donjon_boss_crocabulia",
          "donjon_boss_kralamoure","donjon_boss_wabbit","donjon_boss_minotoror",
          "donjon_pandala_combat"],
    }

    ZONE_COMBAT_MAP = {
        "frigost": "frigost_combat",
        "frigost_village": "frigost_combat",
        "frigost_port": "frigost_combat",
        "frigost_foret": "frigost_combat",
        "frigost_jardins": "frigost_combat",
        "frigost_peninsule": "frigost_combat",
        "donjon_clepsydre": "clepsydre_combat",
        "sufokia": "sufokia_combat",
        "sufokia_abysses": "sufokia_combat",
        "sufokia_ville": "sufokia_combat",
        "sufokia_fosse": "sufokia_combat",
        "xelorium": "xelorium_combat",
        "cimetieres": "cimetieres_combat",
        "dimensions_divines": "dimensions_combat",
        "dimensions_ecaflipus": "dimensions_combat",
        "saharach":         "saharach_combat1",
        "saharach2":        "saharach_combat2",
        "crocuzco": "crocuzco_combat",
        "martegel": "martegel_combat",
        "astrub": "astrub_combat",
        "ile_pwak": "pwak_combat",
        "nonowel": "nimotopia_combat",
        "nimotopia": "nimotopia_combat",
        "songe":            "songes_combat",
        "eliocalypse":      "eliocalypse_combat",
        "kolizeum":         "combat_kolizeum",
        # Donjons génériques → combat salle donjon
        "donjon_theme":     "donjon_combat_pool",
        "donjon_pandala":   "donjon_pandala_combat",
    }

    COMBAT_GENERAL_POOL  = ["combat_general", "combat_6"]

    # Pools donjon — exploration (shuffle)
    DONJON_EXPLORE_POOL  = [f"donjon_theme{i}" for i in range(1, 10)]

    # Pools donjon — combat en salle (shuffle)
    DONJON_COMBAT_POOL   = [f"donjon_combat{i}" for i in range(1, 9)]

    # Pools donjon — combat boss (shuffle)
    DONJON_BOSS_POOL     = ["donjon_boss1", "donjon_boss2", "donjon_boss3", "donjon_boss4",
                            "donjon_boss_harebourg", "donjon_boss_crocabulia",
                            "donjon_boss_kralamoure", "donjon_boss_wabbit",
                            "donjon_boss_minotoror"]

    # Clés d'exploration donjon
    DONJON_EXPLORE_KEYS  = {"donjon_theme"}

    # Clés de combat donjon
    DONJON_COMBAT_KEYS   = {"donjon_combat", "donjon_boss"}

    def _play_for_info(self, info: dict):
        key        = self.resolver.get_music_key(info)
        ver        = self.version.get()
        was_combat = self._current_music_key in self.COMBAT_KEYS

        # ── Exploration donjon → shuffle thèmes donjon
        if key == "donjon_theme":
            key = random.choice(self.DONJON_EXPLORE_POOL)
            # Pas de _last_zone_key = "donjon_theme" pour éviter de bloquer
            # On garde le dernier _last_zone_key de zone pour les combats

        # ── Combat général → chercher la musique de combat de la zone
        elif key == "combat_general" and self._last_zone_key:
            combat = self.ZONE_COMBAT_MAP.get(self._last_zone_key, "combat_general")
            if combat == "donjon_combat_pool":
                key = random.choice(self.DONJON_COMBAT_POOL)
            elif combat == "combat_general":
                key = random.choice(self.COMBAT_GENERAL_POOL)
            else:
                key = combat

        # ── combat_general sans zone connue → pool général
        elif key == "combat_general":
            key = random.choice(self.COMBAT_GENERAL_POOL)

        # Mémoriser la zone non-combat pour les combats suivants
        if key not in self.COMBAT_KEYS and not key.startswith("donjon_theme"):
            self._last_zone_key = key

        if key == self._current_music_key and not was_combat:
            return

        # Essayer de trouver le fichier ; si donjon_themeX introuvable → en choisir un autre
        path = self._find_file(key, ver)
        if not path and key.startswith("donjon_theme"):
            for k in random.sample(self.DONJON_EXPLORE_POOL, len(self.DONJON_EXPLORE_POOL)):
                path = self._find_file(k, ver)
                if path:
                    key = k
                    break
        if not path and key.startswith("donjon_combat"):
            for k in random.sample(self.DONJON_COMBAT_POOL, len(self.DONJON_COMBAT_POOL)):
                path = self._find_file(k, ver)
                if path:
                    key = k
                    break

        if path:
            self._current_music_key = key
            # Entrée en combat → coupure nette, pas de fondu
            entering_combat = (key in self.COMBAT_KEYS and
                               (self._current_music_key not in self.COMBAT_KEYS
                                if self._current_music_key else True))
            if key in self.COMBAT_KEYS and not was_combat:
                self._play_audio_instant(path)
            else:
                self._play_audio(path)
            self._log(f"🎵 {os.path.basename(path)}", "ok")
        else:
            self._log(f"🎵 [{ver}] {key} introuvable", "warn")

    def _find_file(self, key, version):
        dirs = []
        if version == "perso" and self.custom_folder.get():
            dirs.append(self.custom_folder.get())
        ver_clean = version.replace(".", "")
        dirs.append(os.path.join(SCRIPT_DIR, f"musiques/v{ver_clean}"))
        dirs.append(os.path.join(SCRIPT_DIR, "musiques"))
        for d in dirs:
            for ext in ["mp3", "ogg", "wav", "flac"]:
                p = os.path.join(d, f"{key}.{ext}")
                if os.path.exists(p):
                    return p
        return None

    def _play_audio(self, path):
        if not AUDIO_AVAILABLE:
            return
        # Annuler tout fondu en cours
        self._next_path = path
        if self._fade_thread and self._fade_thread.is_alive():
            return  # le thread en cours va charger _next_path à la fin
        self._fade_thread = threading.Thread(
            target=self._fade_and_play, daemon=True)
        self._fade_thread.start()

    def _fade_and_play(self):
        """Fade out la musique actuelle puis fade in la suivante."""
        FADE_STEPS = 20
        FADE_MS    = 400   # durée totale du fondu en ms
        step_time  = FADE_MS / 1000 / FADE_STEPS
        try:
            if pygame.mixer.music.get_busy():
                base_vol = pygame.mixer.music.get_volume()
                for i in range(FADE_STEPS):
                    # Vérifier si une nouvelle musique est arrivée pendant le fondu
                    if self._next_path != self._fade_thread._target_path if hasattr(self._fade_thread, "_target_path") else False:
                        break
                    vol = base_vol * (1 - (i + 1) / FADE_STEPS)
                    try:
                        pygame.mixer.music.set_volume(max(0, vol))
                    except Exception:
                        break
                    time.sleep(step_time)
            # Charger et jouer la prochaine musique
            path = self._next_path
            if not path:
                return
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            target_vol = self.volume.get()
            pygame.mixer.music.set_volume(0)
            pygame.mixer.music.play(-1)
            # Fade in
            for i in range(FADE_STEPS):
                vol = target_vol * (i + 1) / FADE_STEPS
                try:
                    pygame.mixer.music.set_volume(vol)
                except Exception:
                    break
                time.sleep(step_time)
            try:
                pygame.mixer.music.set_volume(target_vol)
            except Exception:
                pass
        except Exception as e:
            self.root.after(0, lambda: self._log(f"⚠ Fondu : {e}", "warn"))

    def _play_audio_instant(self, path):
        """Lance la musique immédiatement sans fondu (entrée en combat)."""
        if not AUDIO_AVAILABLE:
            return
        self._next_path = path
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.volume.get())
            pygame.mixer.music.play(-1)
        except Exception as e:
            self._log(f"⚠ Audio : {e}", "warn")

    def _stop_music(self):
        self._current_music_key = None
        self._next_path = None
        if AUDIO_AVAILABLE:
            try:
                pygame.mixer.music.fadeout(400)
            except Exception:
                pass

    def _on_volume_change(self, val):
        pct = int(float(val) * 100)
        self.vol_lbl.config(text=f"{pct}%")
        if AUDIO_AVAILABLE:
            try:
                pygame.mixer.music.set_volume(float(val))
            except Exception:
                pass

    # ── API ───────────────────────────────────────────────────────────────────
    def _check_api(self):
        try:
            req = urllib.request.Request(
                "https://api.dofusbatteriesincluded.fr/data-center/game-versions",
                headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read())
            latest = data.get("latest", "?")
            self.root.after(0,
                lambda: self._log(f"✓ API DBI — Dofus {latest}", "ok"))
        except Exception:
            self.root.after(0,
                lambda: self._log("⚠ API DBI hors ligne (mode cache)", "warn"))

    APP_VERSION = "1.3"
    UPDATE_URL  = "https://raw.githubusercontent.com/seuski/dofus-sound-manager/main/version.json"

    def _check_update(self):
        try:
            req = urllib.request.Request(self.UPDATE_URL,
                headers={"User-Agent": "DofusSoundManager"})
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read())
            latest  = data.get("version", "1.0")
            dl_url  = data.get("download_url", "")
            changelog = data.get("changelog", "")
            if latest != self.APP_VERSION:
                self.root.after(0, lambda: self._show_update(latest, dl_url, changelog))
            else:
                self.root.after(0, lambda: self._log("✓ Application à jour.", "ok"))
        except Exception:
            pass  # Pas de connexion — on ignore silencieusement

    def _show_update(self, version, url, changelog):
        win = self._make_popup("Mise a jour disponible", 280, 210)
        t = win._theme
        body = tk.Frame(win, bg=t["bg_main"], padx=16, pady=10)
        body.pack(fill="both", expand=True)
        tk.Label(body, text=f"Version {version} disponible !",
                 font=("Segoe UI", 10, "bold"),
                 bg=t["bg_main"], fg=TEXT_GOLD).pack(pady=(0, 6))
        if changelog:
            tk.Label(body, text=changelog,
                     font=("Segoe UI", 8), bg=t["bg_main"], fg=TEXT_MAIN,
                     wraplength=240, justify="center").pack(pady=(0, 10))
        def download():
            import webbrowser
            webbrowser.open(url)
            win.destroy()
        tk.Button(body, text="Telecharger la mise a jour",
                  font=("Segoe UI", 9, "bold"),
                  bg=t["accent"], fg="#fff", relief="flat",
                  bd=0, pady=7, cursor="hand2",
                  command=download).pack(fill="x", pady=(0, 6))
        tk.Button(body, text="Plus tard",
                  font=("Segoe UI", 8),
                  bg=t["btn"], fg=TEXT_DIM, relief="flat",
                  bd=0, pady=5, cursor="hand2",
                  command=win.destroy).pack(fill="x")

    # ── LOG ───────────────────────────────────────────────────────────────────
    def _log(self, msg: str, tag: str = None):
        ts   = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}\n"
        try:
            self.log_text.configure(state="normal")
            if tag:
                self.log_text.insert("end", line, tag)
            else:
                self.log_text.insert("end", line)
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        except Exception:
            pass

    # ── CONFIG ────────────────────────────────────────────────────────────────
    def _save_config(self):
        try:
            with open(os.path.join(SCRIPT_DIR, "config.json"), "w") as f:
                json.dump({
                    "version":         self.version.get(),
                    "volume":          self.volume.get(),
                    "custom_folder":   self.custom_folder.get(),
                    "music_tip_shown": self._music_tip_shown,
                    "theme":           self._current_theme,
                }, f, indent=2)
        except Exception:
            pass

    def _load_config(self):
        cfg = os.path.join(SCRIPT_DIR, "config.json")
        if os.path.exists(cfg):
            try:
                with open(cfg) as f:
                    c = json.load(f)
                self._select_version(c.get("version", "1.29"), restart_music=False)
                self.volume.set(c.get("volume", 0.7))
                self.custom_folder.set(c.get("custom_folder", ""))
                self._music_tip_shown = c.get("music_tip_shown", False)
                self._on_volume_change(self.volume.get())
                saved_theme = c.get("theme", "default")
                if saved_theme in THEMES:
                    self.root.after(200, lambda k=saved_theme: self._apply_theme(k))
            except Exception:
                pass

    # ── RUN ───────────────────────────────────────────────────────────────────
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        self._save_config()
        self.resolver.save_cache()
        self._stop_music()
        self.root.destroy()


# ─── CANVAS HELPER ────────────────────────────────────────────────────────────
def _canvas_rounded_rect(canvas, x1, y1, x2, y2, r=4, **kwargs):
    """Dessine un rectangle aux coins arrondis sur un Canvas tkinter."""
    points = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


if __name__ == "__main__":
    DofusSoundManager().run()
