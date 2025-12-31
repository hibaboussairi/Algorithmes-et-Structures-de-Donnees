import tkinter as tk
from tkinter import ttk

# --- Constants & Configuration ---
PRIMARY_COLOR = "#3498db"      # Blue
SECONDARY_COLOR = "#2ecc71"    # Green
WARNING_COLOR = "#f39c12"      # Orange
DANGER_COLOR = "#e74c3c"       # Red
BACKGROUND_COLOR = "#f0f0f0"   # Light Gray
TEXT_COLOR = "#000000"
ACCENT_COLOR = "#1e90ff"       # Dodger Blue

# Fonts
TITLE_FONT_FAMILY = "Arial"
TITLE_FONT_SIZE = 20
TITLE_FONT_STYLE = "bold"

BUTTON_FONT_FAMILY = "Arial"
BUTTON_FONT_SIZE = 12
BUTTON_FONT_STYLE = "normal"

TEXT_FONT_FAMILY = "Consolas" # Monospace for data
TEXT_FONT_SIZE = 10

def apply_theme(root):
    """Applies a base theme to the Tkinter application."""
    style = ttk.Style()
    style.theme_use('clam') # 'clam' usually allows for more custom coloring than 'vista' or 'xpnative'

    # Configure Frames
    style.configure("TFrame", background=BACKGROUND_COLOR)
    
    # Configure Labels
    style.configure("TLabel", background=BACKGROUND_COLOR, foreground=TEXT_COLOR, font=(BUTTON_FONT_FAMILY, 11))
    style.configure("Title.TLabel", font=(TITLE_FONT_FAMILY, TITLE_FONT_SIZE, TITLE_FONT_STYLE), foreground=PRIMARY_COLOR)
    style.configure("Subtitle.TLabel", font=("Arial", 12, "italic"), foreground="#555555")

    # Configure Buttons
    style.configure("TButton", 
                    font=(BUTTON_FONT_FAMILY, BUTTON_FONT_SIZE, BUTTON_FONT_STYLE),
                    padding=10, 
                    background=PRIMARY_COLOR, 
                    foreground="white",
                    borderwidth=1,
                    focuscolor="none")
    
    style.map("TButton",
              background=[('active', ACCENT_COLOR)],
              foreground=[('active', 'white')])

    # Custom styles for specific buttons
    style.configure("Green.TButton", background=SECONDARY_COLOR)
    style.map("Green.TButton", background=[('active', "#27ae60")])

    style.configure("Orange.TButton", background=WARNING_COLOR)
    style.map("Orange.TButton", background=[('active', "#d35400")])
    
    style.configure("Red.TButton", background=DANGER_COLOR)
    style.map("Red.TButton", background=[('active', "#c0392b")])

    # --- Bright/Brilliant Styles ---
    style.configure("BrightBlue.TButton", background="#007BFF", font=("Helvetica", 10, "bold"))
    style.map("BrightBlue.TButton", background=[('active', "#0056b3")], foreground=[('active', 'white')])

    style.configure("BrightGreen.TButton", background="#28A745", font=("Helvetica", 10, "bold"))
    style.map("BrightGreen.TButton", background=[('active', "#1e7e34")], foreground=[('active', 'white')])

    style.configure("BrightOrange.TButton", background="#FFC107", font=("Helvetica", 10, "bold"), foreground="black")
    style.map("BrightOrange.TButton", background=[('active', "#e0a800")], foreground=[('active', 'black')])

    style.configure("BrightPurple.TButton", background="#9B59B6", font=("Helvetica", 10, "bold"))
    style.map("BrightPurple.TButton", background=[('active', "#8E44AD")], foreground=[('active', 'white')])

    root.configure(bg=BACKGROUND_COLOR)
