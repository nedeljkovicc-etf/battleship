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
        
    # ── game initialisation ────────────────────────────────────────────────────
    def new_game(self):
        # state
        self.player_board  = make_grid()
        self.enemy_board   = make_grid()
        self.enemy_hidden  = make_grid()   # what player sees of enemy
        self.player_ships  = place_ships_random(self.player_board)
        self.enemy_ships   = place_ships_random(self.enemy_board)
        self.player_hits   = 0
        self.player_misses = 0
        self.player_sunk   = 0
        self.ai_hits       = 0
        self.ai_misses     = 0
        self.ai_sunk       = 0
        self.game_over     = False
        self.player_turn   = True
        self.hover_cell    = None

    # ── drawing ────────────────────────────────────────────────────────────────
    def _redraw_all(self):
        self._redraw_player()
        self._redraw_enemy()

    def _redraw_player(self):
        c = self.player_canvas
        c.delete("cell")
        for r in range(GRID):
            for col in range(GRID):
                x1, y1, x2, y2 = self._cell_coords(r, col)
                ship = self.player_board[r][col]
                if ship:
                    # check if sunk
                    ship_obj = next((s for s in self.player_ships if s["name"]==ship), None)
                    if ship_obj and len(ship_obj["hits"]) == ship_obj["size"]:
                        fill = SUNK_CLR
                    else:
                        fill = SHIP_CLR
                else:
                    fill = OCEAN
                state = self.enemy_hidden[r][col] if self.enemy_hidden[r][col] else None
                # draw cell (player board shows ships + AI shots)
                c.create_rectangle(x1+1, y1+1, x2-1, y2-1,
                                   fill=fill, outline="", tags="cell")
                # mark AI shots on player board
                shot = self._get_player_shot(r, col)
                if shot == "hit":
                    self._draw_explosion(c, x1, y1, x2, y2)
                elif shot == "miss":
                    self._draw_splash(c, x1, y1, x2, y2)

    def _redraw_enemy(self):
        c = self.enemy_canvas
        c.delete("cell")
        for r in range(GRID):
            for col in range(GRID):
                x1, y1, x2, y2 = self._cell_coords(r, col)
                shot = self.enemy_hidden[r][col]
                if shot == "hit":
                    c.create_rectangle(x1+1,y1+1,x2-1,y2-1,
                                       fill=HIT_CLR, outline="", tags="cell")
                    self._draw_explosion(c, x1, y1, x2, y2)
                elif shot == "miss":
                    c.create_rectangle(x1+1,y1+1,x2-1,y2-1,
                                       fill=MISS_CLR, outline="", tags="cell")
                    self._draw_splash(c, x1, y1, x2, y2)
                else:
                    fill = OCEAN
                    if self.hover_cell == (r, col) and self.player_turn and not self.game_over:
                        fill = "#0f2d47"
                    c.create_rectangle(x1+1,y1+1,x2-1,y2-1,
                                       fill=fill, outline="", tags="cell")

        # draw sunk ships on enemy board
        for ship in self.enemy_ships:
            if len(ship["hits"]) == ship["size"]:
                for (r, col) in ship["cells"]:
                    x1,y1,x2,y2 = self._cell_coords(r, col)
                    c.create_rectangle(x1+1,y1+1,x2-1,y2-1,
                                       fill=SUNK_CLR, outline="", tags="cell")
                    self._draw_explosion(c, x1, y1, x2, y2)

    def _cell_coords(self, r, col):
        x1 = PAD + col*CELL
        y1 = PAD + r*CELL
        return x1, y1, x1+CELL, y1+CELL

    def _draw_explosion(self, c, x1, y1, x2, y2):
        cx, cy = (x1+x2)//2, (y1+y2)//2
        r = CELL//2 - 6
        c.create_oval(cx-r, cy-r, cx+r, cy+r,
                      fill=HIT_CLR, outline="#ff8060", width=1, tags="cell")
        c.create_text(cx, cy, text="✕", fill="white",
                      font=("Courier New", 11, "bold"), tags="cell")

    def _draw_splash(self, c, x1, y1, x2, y2):
        cx, cy = (x1+x2)//2, (y1+y2)//2
        c.create_text(cx, cy, text="·", fill="#3a7fa8",
                      font=("Courier New", 16, "bold"), tags="cell")

    def _get_player_shot(self, r, col):
        """Return 'hit'/'miss'/None for what AI has shot on player board."""
        ship = self.player_board[r][col]
        # check if AI fired here: we store in enemy_board-like structure
        return getattr(self, "_ai_shots", {}).get((r, col))

    # ── fleet panel ───────────────────────────────────────────────────────────
    def _update_fleet_panel(self):
        for name, info in self.fleet_labels.items():
            for w in info["widgets"]:
                w.destroy()
            info["widgets"].clear()
            ship_obj = next((s for s in self.enemy_ships if s["name"]==name), None)
            sunk = ship_obj and len(ship_obj["hits"]) == ship_obj["size"]
            for i in range(info["size"]):
                hit = ship_obj and i in {h for h in range(info["size"])
                                         if list(ship_obj["cells"])[i] in
                                         [(r,c) for (r,c) in ship_obj["hits"]]} \
                      if ship_obj else False
                # simpler: just colour all red if sunk, partial hits yellow
                if sunk:
                    clr = SUNK_CLR
                else:
                    clr = SHIP_CLR
                sq = tk.Frame(info["squares"], width=8, height=8,
                              bg=clr, relief="flat")
                sq.pack(side="left", padx=1)
                sq.pack_propagate(False)
                info["widgets"].append(sq)

    def _update_fleet_status(self):
        """Colour fleet squares to show hits / sunk."""
        for name, info in self.fleet_labels.items():
            ship_obj = next((s for s in self.enemy_ships if s["name"]==name), None)
            if not ship_obj:
                continue
            sunk = len(ship_obj["hits"]) == ship_obj["size"]
            for i, w in enumerate(info["widgets"]):
                cell = ship_obj["cells"][i]
                if sunk:
                    clr = SUNK_CLR
                elif cell in ship_obj["hits"]:
                    clr = HIT_CLR
                else:
                    clr = SHIP_CLR
                w.configure(bg=clr)

    # ── stats ─────────────────────────────────────────────────────────────────
    def _update_stats(self):
        self.hits_var.set(f"Hits: {self.player_hits}")
        self.misses_var.set(f"Misses: {self.player_misses}")
        self.sunk_var.set(f"Sunk: {self.player_sunk}/5")

    # ── event handlers ────────────────────────────────────────────────────────
    def _on_hover(self, event):
        cell = self._pixel_to_cell(event.x, event.y)
        if cell != self.hover_cell:
            self.hover_cell = cell
            self._redraw_enemy()

    def _on_leave(self, event):
        self.hover_cell = None
        self._redraw_enemy()

    def _on_click(self, event):
        if self.game_over or not self.player_turn:
            return
        cell = self._pixel_to_cell(event.x, event.y)
        if not cell:
            return
        r, col = cell
        if self.enemy_hidden[r][col]:
            self.msg_var.set("Already fired there! Pick another cell.")
            return
        self._player_fire(r, col)

    def _pixel_to_cell(self, x, y):
        col = (x - PAD) // CELL
        row = (y - PAD) // CELL
        if 0 <= row < GRID and 0 <= col < GRID:
            return (row, col)
        return None
    
    # ── game logic ────────────────────────────────────────────────────────────
    def _player_fire(self, r, col):
        self.player_turn = False
        hit, sunk_name = self._fire(r, col, self.enemy_board,
                                    self.enemy_ships, self.enemy_hidden)
        if hit:
            self.player_hits += 1
        else:
            self.player_misses += 1

        if sunk_name:
            self.player_sunk += 1
            self.msg_var.set(f"💥 You sunk their {sunk_name}!")
            self._update_fleet_status()
        elif hit:
            self.msg_var.set("🎯 Direct hit!")
        else:
            self.msg_var.set("💧 Miss!")

        self._update_stats()
        self._redraw_enemy()

        if self._check_win(self.enemy_ships):
            self._end_game(player_wins=True)
            return

        self.turn_var.set("Enemy turn...")
        self.after(900, self._ai_turn)

    def _fire(self, r, col, board, ships, visible):
        ship_name = board[r][col]
        if ship_name:
            visible[r][col] = "hit"
            ship_obj = next((s for s in ships if s["name"]==ship_name), None)
            if ship_obj:
                ship_obj["hits"].add((r, col))
                if len(ship_obj["hits"]) == ship_obj["size"]:
                    return True, ship_name
            return True, None
        else:
            visible[r][col] = "miss"
            return False, None

    def _check_win(self, ships):
        return all(len(s["hits"]) == s["size"] for s in ships)