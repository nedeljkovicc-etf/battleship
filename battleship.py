import tkinter as tk
from tkinter import messagebox
import random

# ── constants ──────────────────────────────────────────────────────────────────
GRID = 10
CELL = 44
PAD  = 14

SHIPS = [
    ("Carrier",    5),
    ("Battleship", 4),
    ("Cruiser",    3),
    ("Submarine",  3),
    ("Destroyer",  2),
]

# colour palette – naval dark theme
BG        = "#0a0f1a"
OCEAN     = "#0d2137"
OCEAN_HIT = "#0f3a5c"
GRID_LINE = "#1a3a55"
SHIP_CLR  = "#2d6a8f"
HIT_CLR   = "#e85d3a"      # red explosion
MISS_CLR  = "#1e4d6e"      # dark splash
SUNK_CLR  = "#8b0000"
LABEL_CLR = "#4a90b8"
TEXT_CLR  = "#cce7f5"
ACCENT    = "#00d4ff"
PANEL_BG  = "#080e18"
BTN_ACTIVE= "#1a3a55"

# ── helpers ────────────────────────────────────────────────────────────────────
def make_grid():
    return [[None]*GRID for _ in range(GRID)]

def place_ships_random(board):
    """Returns list of ship dicts placed randomly on board."""
    ships_placed = []
    for name, size in SHIPS:
        placed = False
        while not placed:
            horiz = random.choice([True, False])
            if horiz:
                r = random.randint(0, GRID-1)
                c = random.randint(0, GRID-size)
            else:
                r = random.randint(0, GRID-size)
                c = random.randint(0, GRID-1)
            cells = [(r, c+i) if horiz else (r+i, c) for i in range(size)]
            if all(board[rr][cc] is None for rr,cc in cells):
                for rr,cc in cells:
                    board[rr][cc] = name
                ships_placed.append({"name": name, "size": size,
                                     "cells": cells, "hits": set()})
                placed = True
    return ships_placed

# ── main application ───────────────────────────────────────────────────────────
class Battleship(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BATTLESHIP")
        self.configure(bg=BG)
        self.resizable(False, False)
        self._build_ui()
        self.new_game()

    # ── UI construction ────────────────────────────────────────────────────────
    def _build_ui(self):
        # title bar
        title = tk.Label(self, text="⚓  B A T T L E S H I P",
                         font=("Courier New", 18, "bold"),
                         fg=ACCENT, bg=BG)
        title.pack(pady=(18, 4))

        sub = tk.Label(self, text="sink the enemy fleet before they sink yours",
                       font=("Courier New", 9), fg=LABEL_CLR, bg=BG)
        sub.pack()

        # main content row
        content = tk.Frame(self, bg=BG)
        content.pack(padx=20, pady=10)

        # player board
        player_col = tk.Frame(content, bg=BG)
        player_col.grid(row=0, column=0, padx=(0, 18))
        tk.Label(player_col, text="YOUR FLEET", font=("Courier New", 10, "bold"),
                 fg=LABEL_CLR, bg=BG).pack(pady=(0,6))
        self.player_canvas = self._make_canvas(player_col, clickable=False)
        self.player_canvas.pack()

        # separator
        sep = tk.Frame(content, bg=GRID_LINE, width=1)
        sep.grid(row=0, column=1, sticky="ns", padx=6)

        # enemy board
        enemy_col = tk.Frame(content, bg=BG)
        enemy_col.grid(row=0, column=2, padx=(18, 0))
        tk.Label(enemy_col, text="ENEMY WATERS", font=("Courier New", 10, "bold"),
                 fg=LABEL_CLR, bg=BG).pack(pady=(0,6))
        self.enemy_canvas = self._make_canvas(enemy_col, clickable=True)
        self.enemy_canvas.pack()

        # status & fleet panels
        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", padx=20, pady=(0, 10))

        self._build_fleet_panel(bottom)
        self._build_status_panel(bottom)
        self._build_controls(bottom)

    def _make_canvas(self, parent, clickable):
        size = PAD + GRID*CELL + PAD
        c = tk.Canvas(parent, width=size, height=size,
                      bg=OCEAN, highlightthickness=0)
        self._draw_grid_lines(c)
        self._draw_labels(c)
        if clickable:
            c.bind("<Button-1>", self._on_click)
            c.bind("<Motion>",   self._on_hover)
            c.bind("<Leave>",    self._on_leave)
        return c

    def _draw_grid_lines(self, canvas):
        size = PAD + GRID*CELL + PAD
        for i in range(GRID+1):
            x = PAD + i*CELL
            y = PAD + i*CELL
            canvas.create_line(x, PAD, x, PAD+GRID*CELL,
                               fill=GRID_LINE, width=1)
            canvas.create_line(PAD, y, PAD+GRID*CELL, y,
                               fill=GRID_LINE, width=1)

    def _draw_labels(self, canvas):
        cols = "ABCDEFGHIJ"
        for i in range(GRID):
            x = PAD + i*CELL + CELL//2
            canvas.create_text(x, PAD//2, text=cols[i],
                               fill=LABEL_CLR, font=("Courier New", 9, "bold"))
            canvas.create_text(PAD//2, PAD + i*CELL + CELL//2,
                               text=str(i+1),
                               fill=LABEL_CLR, font=("Courier New", 9, "bold"))

    def _build_fleet_panel(self, parent):
        frame = tk.Frame(parent, bg=PANEL_BG,
                         highlightbackground=GRID_LINE, highlightthickness=1)
        frame.pack(side="left", fill="y", padx=(0,8), pady=4)
        tk.Label(frame, text="FLEET STATUS", font=("Courier New", 9, "bold"),
                 fg=ACCENT, bg=PANEL_BG).pack(padx=10, pady=(8,4))

        self.fleet_labels = {}
        for name, size in SHIPS:
            row = tk.Frame(frame, bg=PANEL_BG)
            row.pack(fill="x", padx=10, pady=2)
            squares = tk.Frame(row, bg=PANEL_BG)
            squares.pack(side="left")
            self.fleet_labels[name] = {"squares": squares, "size": size, "widgets": []}
            lbl = tk.Label(row, text=f"  {name}", font=("Courier New", 8),
                           fg=TEXT_CLR, bg=PANEL_BG, anchor="w")
            lbl.pack(side="left")
        tk.Frame(frame, bg=PANEL_BG).pack(pady=4)

    def _build_status_panel(self, parent):
        frame = tk.Frame(parent, bg=PANEL_BG,
                         highlightbackground=GRID_LINE, highlightthickness=1)
        frame.pack(side="left", fill="both", expand=True, padx=(0,8), pady=4)

        self.msg_var = tk.StringVar(value="")
        self.msg_lbl = tk.Label(frame, textvariable=self.msg_var,
                                font=("Courier New", 10, "bold"),
                                fg=ACCENT, bg=PANEL_BG, wraplength=260, justify="center")
        self.msg_lbl.pack(padx=14, pady=(12, 4))

        stats = tk.Frame(frame, bg=PANEL_BG)
        stats.pack()
        self.hits_var  = tk.StringVar(value="Hits: 0")
        self.misses_var= tk.StringVar(value="Misses: 0")
        self.sunk_var  = tk.StringVar(value="Sunk: 0/5")
        for v in [self.hits_var, self.misses_var, self.sunk_var]:
            tk.Label(stats, textvariable=v, font=("Courier New", 9),
                     fg=TEXT_CLR, bg=PANEL_BG).pack(side="left", padx=8)

        self.turn_var = tk.StringVar(value="")
        tk.Label(frame, textvariable=self.turn_var,
                 font=("Courier New", 9), fg=LABEL_CLR, bg=PANEL_BG).pack(pady=(4,10))
        
    def _build_controls(self, parent):
        frame = tk.Frame(parent, bg=PANEL_BG,
                         highlightbackground=GRID_LINE, highlightthickness=1)
        frame.pack(side="right", fill="y", padx=0, pady=4)
        btn_cfg = dict(font=("Courier New", 9, "bold"), fg=ACCENT, bg=PANEL_BG,
                       activeforeground=TEXT_CLR, activebackground=BTN_ACTIVE,
                       relief="flat", cursor="hand2", padx=14, pady=6,
                       highlightthickness=0, bd=0)
        tk.Button(frame, text="⟳  NEW GAME", command=self.new_game,
                  **btn_cfg).pack(padx=14, pady=(10,4), fill="x")
        tk.Button(frame, text="?  RULES",    command=self._show_rules,
                  **btn_cfg).pack(padx=14, pady=(0,10), fill="x")