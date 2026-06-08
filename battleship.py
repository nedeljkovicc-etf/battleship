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