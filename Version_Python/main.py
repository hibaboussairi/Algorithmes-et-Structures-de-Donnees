import tkinter as tk
from tkinter import ttk, messagebox
from styles import *

# Import Modules
try:
    from table import SortingVisualizer
    from list import LinkedListVisualizer
    from tree import TreeVisualizer
    from graph import GraphVisualizer
except ImportError as e:
    messagebox.showerror("Erreur Critique", f"Impossible d'importer les modules : {e}")
    exit(1)

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🖥️ Menu Principal - Structures de Données (Python)")
        self.geometry("1100x800") # Larger window for the cards
        self.resizable(True, True)
        
        # Apply Theme
        apply_theme(self)
        self.configure(bg="#f4f6f9") # Light grey-blue background for modern feel
        
        self.setup_ui()

    def setup_ui(self):
        # 1. Header with visual flair
        header_frame = tk.Frame(self, bg="#2c3e50", height=80)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        header_frame.pack_propagate(False)
        
        lbl_title = tk.Label(header_frame, text="Exploration des Algorithmes & Structures", 
                             font=("Segoe UI", 24, "bold"), fg="white", bg="#2c3e50")
        lbl_title.pack(pady=20)

        # 2. Main Content (Grid of Cards)
        content_frame = tk.Frame(self, bg="#f4f6f9")
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Configure Grid
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)

        # Card 1: Sorting (Tableaux)
        self.create_card(content_frame, 0, 0, 
                         title="Tableaux", 
                         desc="Comparaison Bubble, Merge, Quick Sort...",
                         color="#27ae60", # Green
                         icon_func=self.draw_sorting_icon,
                         cmd=self.open_sorting)

        # Card 2: Linked Lists
        self.create_card(content_frame, 0, 1, 
                         title="Listes Chaînées", 
                         desc="Manipulation de nœuds et pointeurs",
                         color="#2980b9", # Blue
                         icon_func=self.draw_list_icon,
                         cmd=self.open_linked_list)

        # Card 3: Trees
        self.create_card(content_frame, 1, 0, 
                         title="Arbres", 
                         desc="Arbres Binaires, N-aires, Parcours",
                         color="#8e44ad", # Purple
                         icon_func=self.draw_tree_icon,
                         cmd=self.open_trees)

        # Card 4: Graphs
        self.create_card(content_frame, 1, 1, 
                         title="Graphes", 
                         desc="Dijkstra, Bellman-Ford, Connexions",
                         color="#e67e22", # Orange
                         icon_func=self.draw_graph_icon,
                         cmd=self.open_graphs)

        # 3. Footer
        footer_frame = tk.Frame(self, bg="#f4f6f9", height=50)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        btn_quit = ttk.Button(footer_frame, text="Quitter", style="Red.TButton", command=self.quit)
        btn_quit.pack(side=tk.RIGHT, padx=20, pady=10)

    def create_card(self, parent, row, col, title, desc, color, icon_func, cmd):
        # Card Container (Frame with border effect)
        card = tk.Frame(parent, bg="white", highlightbackground="#dcdcdc", highlightthickness=1)
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        # Hover Effect
        def on_enter(e): card.config(highlightbackground=color, highlightthickness=2)
        def on_leave(e): card.config(highlightbackground="#dcdcdc", highlightthickness=1)
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        # Interact allows clicking anywhere on the card
        def on_click(e): cmd()
        card.bind("<Button-1>", on_click)

        # Header Color Strip
        strip = tk.Frame(card, bg=color, height=10)
        strip.pack(side=tk.TOP, fill=tk.X)
        strip.bind("<Button-1>", on_click)

        # Icon Canvas
        cv = tk.Canvas(card, bg="white", width=150, height=100, highlightthickness=0)
        cv.pack(pady=20)
        cv.bind("<Button-1>", on_click)
        icon_func(cv, color) # Draw specific icon

        # Text
        lbl_t = tk.Label(card, text=title, font=("Segoe UI", 16, "bold"), bg="white", fg="#2c3e50")
        lbl_t.pack()
        lbl_t.bind("<Button-1>", on_click)

        lbl_d = tk.Label(card, text=desc, font=("Segoe UI", 11), bg="white", fg="#7f8c8d")
        lbl_d.pack(pady=(5, 20))
        lbl_d.bind("<Button-1>", on_click)
        
        # Action Button (Visual cue)
        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
        
        # Use a label as a button for consistent styling within the card
        lbl_btn = tk.Label(btn_frame, text="Ouvrir ➤", fg="white", bg=color, font=("Segoe UI", 10, "bold"), padx=15, pady=5, cursor="hand2")
        lbl_btn.pack(side=tk.RIGHT)
        lbl_btn.bind("<Button-1>", on_click)

    # --- Icon Drawing Functions ---
    def draw_sorting_icon(self, cv, color):
        # Bar Chart
        w, h = 150, 100
        data = [20, 50, 80, 40, 90, 30]
        width = 15
        gap = 5
        start_x = (w - (len(data)*(width+gap))) / 2
        for i, h_val in enumerate(data):
            x = start_x + i * (width + gap)
            cv.create_rectangle(x, h - h_val, x + width, h, fill=color, outline="")

    def draw_list_icon(self, cv, color):
        # Linked List: [ ]-> [ ]-> [ ]
        y = 50
        start_x = 20
        box_w = 30
        gap = 20
        for i in range(3):
            x = start_x + i*(box_w+gap)
            # Box
            cv.create_rectangle(x, y-15, x+box_w, y+15, outline=color, width=3)
            # Arrow
            if i < 2:
                cv.create_line(x+box_w, y, x+box_w+gap, y, fill=color, width=2, arrow=tk.LAST)
            # Value
            cv.create_text(x+box_w/2, y, text=str(i+1), fill=color, font=("Arial", 10, "bold"))

    def draw_tree_icon(self, cv, color):
        # Tree structure
        #      O
        #    /   \
        #   O     O
        cv.create_line(75, 20, 45, 60, fill=color, width=2)
        cv.create_line(75, 20, 105, 60, fill=color, width=2)
        
        r = 10
        cv.create_oval(75-r, 20-r, 75+r, 20+r, fill=color, outline="") # Root
        cv.create_oval(45-r, 60-r, 45+r, 60+r, fill=color, outline="") # Left
        cv.create_oval(105-r, 60-r, 105+r, 60+r, fill=color, outline="") # Right

    def draw_graph_icon(self, cv, color):
        # Graph mesh
        # O---O
        # | \ |
        # O---O
        nodes = [(45, 30), (105, 30), (45, 80), (105, 80)]
        
        # Edges
        cv.create_line(nodes[0], nodes[1], fill=color, width=2)
        cv.create_line(nodes[0], nodes[2], fill=color, width=2)
        cv.create_line(nodes[0], nodes[3], fill=color, width=2) # Diagonal
        cv.create_line(nodes[2], nodes[3], fill=color, width=2)
        cv.create_line(nodes[1], nodes[3], fill=color, width=2)

        r = 8
        for x, y in nodes:
            cv.create_oval(x-r, y-r, x+r, y+r, fill="white", outline=color, width=3)

    # --- Navigation ---
    def open_sorting(self):
        self.withdraw()
        win = SortingVisualizer(self)
        win.protocol("WM_DELETE_WINDOW", lambda: self.on_child_close(win))

    def open_linked_list(self):
        self.withdraw()
        win = LinkedListVisualizer(self)
        win.protocol("WM_DELETE_WINDOW", lambda: self.on_child_close(win))

    def open_trees(self):
        self.withdraw()
        win = TreeVisualizer(self)
        win.protocol("WM_DELETE_WINDOW", lambda: self.on_child_close(win))

    def open_graphs(self):
        self.withdraw()
        win = GraphVisualizer(self)
        win.protocol("WM_DELETE_WINDOW", lambda: self.on_child_close(win))

    def on_child_close(self, child_win):
        child_win.destroy()
        self.deiconify()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
