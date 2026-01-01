import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
from styles import *
import random

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None # For Doubly Linked List

class LinkedListVisualizer(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("⚙️ TP2 : Gestion et Tri des Listes Chaînées Avancés")
        self.geometry("1400x800")
        apply_theme(self)

        self.head = None
        self.list_type = "Chaînée Simple"
        self.data_type = "Entier"
        self.sort_algo = "Tri à Bulle"
        self.gen_mode = "Aléatoire" 
        
        self.node_positions = []
        self.is_animating = False

        self.setup_ui()

    def setup_ui(self):
        # Configure Grid
        self.columnconfigure(0, weight=1) # Sidebar allows expansion
        self.columnconfigure(1, weight=4) # Canvas area takes more space
        self.rowconfigure(0, weight=1)

        # Style configuration for Black Buttons
        style = ttk.Style()
        style.configure("Clean.TFrame", background="#ffffff")
        # Configure Black Button Style
        # Note: On Windows native theme, background color changes might be subtle or require 'clam' theme which is set in styles.py
        style.configure("Black.TButton", 
                        background="#000000", 
                        foreground="white", 
                        font=("Arial", 10, "bold"),
                        borderwidth=1,
                        padding=3)
        style.map("Black.TButton", 
                  background=[('active', "#333333"), ('pressed', "#555555")],
                  foreground=[('active', 'white')])

        # Main Control Container - Removed fixed width=380 to allow responsiveness
        control_panel = ttk.Frame(self, padding=10, style="Clean.TFrame")
        control_panel.grid(row=0, column=0, sticky="nsew")
        
        # --- PACKING ORDER FOR VISIBILITY ---
        # --- PACKING ORDER FOR VISIBILITY ---
        # 1. Footer Buttons (Packed FIRST to stay at BOTTOM)
        
        # 1b. Reset / Return (Very Bottom)
        footer_nav_frame = ttk.Frame(control_panel)
        footer_nav_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        btn_reset = ttk.Button(footer_nav_frame, text="Réinitialiser la Liste", command=self.reset_list, style="Black.TButton")
        btn_reset.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=0)

        # 1a. Important Actions (Pinned above Reset/Return)
        footer_actions_frame = ttk.Frame(control_panel)
        footer_actions_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 5))

        ttk.Button(footer_actions_frame, text="Modifier (Position)", command=self.modify_node, style="Black.TButton").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        ttk.Button(footer_actions_frame, text="Trier la Liste", command=self.sort_list, style="Black.TButton").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))


        # 2. Header (Packed TOP)
        ttk.Label(control_panel, text="Contrôles", font=("Helvetica", 16, "bold"), background="#ffffff", foreground="#2c3e50").pack(side=tk.TOP, pady=(0, 20), anchor="w")

        # 3. Configuration et Génération Frame (Packed TOP)
        lbl_conf = ttk.LabelFrame(control_panel, text="Configuration et Génération", padding=10)
        lbl_conf.pack(side=tk.TOP, fill=tk.X, pady=(0, 15))

        # Type de Liste
        ttk.Label(lbl_conf, text="Type de Liste:").grid(row=0, column=0, sticky="w", pady=5)
        self.cb_list_type = ttk.Combobox(lbl_conf, values=["Chaînée Simple", "Chaînée Double"], state="readonly")
        self.cb_list_type.set("Chaînée Simple")
        self.cb_list_type.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.cb_list_type.bind("<<ComboboxSelected>>", self.reset_list)

        # Type de Données
        ttk.Label(lbl_conf, text="Type de Données:").grid(row=1, column=0, sticky="w", pady=5)
        self.cb_data_type = ttk.Combobox(lbl_conf, values=["Entier", "Réel", "String", "Caractère"], state="readonly")
        self.cb_data_type.set("Entier")
        self.cb_data_type.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Méthode de Tri
        ttk.Label(lbl_conf, text="Méthode de Tri:").grid(row=2, column=0, sticky="w", pady=5)
        self.cb_sort_algo = ttk.Combobox(lbl_conf, values=["Tri à Bulle", "Tri par Insertion", "Tri Shell", "Tri Rapide"], state="readonly")
        self.cb_sort_algo.set("Tri par Insertion")
        self.cb_sort_algo.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Mode Génération
        ttk.Label(lbl_conf, text="Mode Génération:").grid(row=3, column=0, sticky="w", pady=5)
        
        frame_radio = ttk.Frame(lbl_conf)
        frame_radio.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.var_gen_mode = tk.StringVar(value="Aléatoire")
        ttk.Radiobutton(frame_radio, text="Aléatoire", variable=self.var_gen_mode, value="Aléatoire").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(frame_radio, text="Manuel", variable=self.var_gen_mode, value="Manuel").pack(side=tk.LEFT, padx=5)

        # Générer Button - Black Style
        ttk.Button(lbl_conf, text="⊞ Générer Liste", command=self.start_generation, style="Black.TButton").grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
        
        lbl_conf.columnconfigure(1, weight=1)

        # 4. Opérations de Manipulation et Tri Frame (Packed TOP)
        lbl_ops = ttk.LabelFrame(control_panel, text="Opérations de Manipulation et Tri", padding=10)
        lbl_ops.pack(side=tk.TOP, fill=tk.X, pady=10)

        # Inputs
        ttk.Label(lbl_ops, text="Valeur:").pack(anchor="w")
        self.entry_val = ttk.Entry(lbl_ops)
        self.entry_val.pack(fill=tk.X, pady=5)

        ttk.Label(lbl_ops, text="Position (Index/Tri):").pack(anchor="w")
        self.entry_pos = ttk.Entry(lbl_ops)
        self.entry_pos.insert(0, "0")
        self.entry_pos.pack(fill=tk.X, pady=5)

        # Buttons Row 1: Insertions - Consolidé en MenuButton
        frame_ins = ttk.Frame(lbl_ops)
        frame_ins.pack(fill=tk.X, pady=5)
        
        # MenuButton "Insérer"
        self.btn_insert_menu = ttk.Menubutton(frame_ins, text="Insérer ▾", style="Black.TButton")
        self.btn_insert_menu.pack(fill=tk.X, expand=True)
        
        # Menu for Insérer
        self.menu_insert = tk.Menu(self.btn_insert_menu, tearoff=0)
        self.menu_insert.add_command(label="Au Début", command=lambda: self.safe_animate(lambda: self.animate_op("add", 0)))
        self.menu_insert.add_command(label="À la Fin", command=lambda: self.safe_animate(lambda: self.animate_op("add", -1)))
        self.menu_insert.add_command(label="À une Position...", command=lambda: self.safe_animate(lambda: self.animate_op("add", "idx")))
        
        self.btn_insert_menu["menu"] = self.menu_insert

        # Big Action Buttons - Black Style
        ttk.Button(lbl_ops, text="Supprimer (Pos/Valeur)", command=lambda: self.safe_animate(lambda: self.animate_op("delete", "idx")), style="Black.TButton").pack(fill=tk.X, pady=5)




        # --- RIGHT PANEL (Visuals) ---
        display_panel = ttk.Frame(self, padding=10)
        display_panel.grid(row=0, column=1, sticky="nsew")
        
        # Results Frame
        lbl_res = ttk.LabelFrame(display_panel, text="Résultats: []", padding=5)
        lbl_res.pack(fill=tk.BOTH, expand=True)
        self.lbl_res_frame = lbl_res # To update text later

        # Canvas
        self.canvas = tk.Canvas(lbl_res, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        sb = ttk.Scrollbar(lbl_res, orient=tk.HORIZONTAL, command=self.canvas.xview)
        sb.pack(fill=tk.X, side=tk.BOTTOM)
        self.canvas.configure(xscrollcommand=sb.set)

        # Log Area
        lbl_log = ttk.LabelFrame(display_panel, text="Journal d'activité", padding=5)
        lbl_log.pack(fill=tk.X, pady=(10, 0))
        
        self.log_area = tk.Text(lbl_log, height=6, state="disabled", font=("Consolas", 9))
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log("Interface chargée.")

    # --- Logic ---

    def log(self, msg):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"> {msg}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def safe_animate(self, func):
        if self.is_animating:
            return
        func()

    def reset_list(self, event=None):
        self.head = None
        self.is_animating = False
        self.node_positions = []
        self.log("Liste réinitialisée.")
        self.draw_list()

    def get_list_size(self):
        c = 0
        curr = self.head
        while curr:
            c += 1
            curr = curr.next
        return c

    def start_generation(self):
        if self.is_animating: return
        
        mode = self.var_gen_mode.get()
        values = []
        dtype = self.cb_data_type.get()
        
        if mode == "Manuel":
            val_str = simpledialog.askstring("Mode Manuel", "Entrez des valeurs séparées par une virgule (ex: 10, 5, 3):")
            if not val_str: return
            parts = val_str.split(',')
            for p in parts:
                v = self.parse_single_val(p.strip(), dtype)
                if v is not None: values.append(v)
        else:
            # Random
            try:
                size_str = simpledialog.askstring("Génération Aléatoire", "Taille de la liste (max 50):", initialvalue="10")
                if not size_str: return
                size = int(size_str)
                if size < 1: size = 1
                if size > 50: size = 50 
            except: return

            for _ in range(size):
                val = None
                if dtype == "Entier": val = random.randint(0, 100)
                elif dtype == "Réel": val = round(random.uniform(0, 100), 2)
                elif dtype == "String": val = "".join(random.choices("ABC", k=2))
                else: val = random.choice("XYZ")
                values.append(val)
        
        if not values: return

        self.reset_list()
        self.is_animating = True
        self.animate_creation_step(values, 0)
        self.log(f"Génération {len(values)} éléments ({mode}).")

    def parse_single_val(self, s, dtype):
        try:
            if dtype == "Entier": return int(s)
            elif dtype == "Réel": return float(s)
            else: return s
        except: return None

    def animate_creation_step(self, values, index):
        if index >= len(values):
            self.is_animating = False
            return
        
        val = values[index]
        self.append_node_logic(val)
        self.draw_list()
        
        if self.node_positions:
            last_pos = self.node_positions[-1]
            self.highlight_circle(last_pos[0], last_pos[1], "#2ecc71") # Green highlight
            
        self.after(300, lambda: self.animate_creation_step(values, index + 1))

    # --- Animation Operations ---

    def animate_op(self, op_type, target_idx_arg):
        self.is_animating = True
        list_size = self.get_list_size()
        
        idx = 0
        if target_idx_arg == -1: 
            idx = list_size
        elif target_idx_arg == "idx":
            try:
                txt = self.entry_pos.get().strip()
                if txt.lower() == "tri" or txt.lower() == "trie":
                    idx = -999 
                else:
                    idx = int(txt)
            except: 
                messagebox.showerror("Error", "Index invalide")
                self.is_animating = False
                return
        else:
            idx = int(target_idx_arg)

        # Value parsing
        val = None
        if op_type == "add":
            val = self.parse_single_val(self.entry_val.get(), self.cb_data_type.get())
            if val is None:
                messagebox.showerror("Error", "Valeur invalide")
                self.is_animating = False
                return
            
            if idx == -999: # Sorted insert
                 self.finish_op("add_sorted", 0, val)
                 return
            
            if idx > list_size: idx = list_size
            if idx < 0: idx = 0

        if op_type == "delete":
            if idx >= list_size or idx < 0:
                val_to_del = self.parse_single_val(self.entry_val.get(), self.cb_data_type.get())
                if val_to_del is not None:
                    found_idx = self.find_index_by_val(val_to_del)
                    if found_idx != -1:
                        idx = found_idx
                        self.log(f"Valeur trouvée à l'index {idx}")
                    else:
                        messagebox.showerror("Error", "Index hors limites ou Valeur introuvable")
                        self.is_animating = False
                        return
                else:
                    messagebox.showerror("Error", "Index hors limites")
                    self.is_animating = False
                    return

        # Animate traversal
        limit = idx
        if op_type == "add" and idx == list_size: limit = list_size - 1
        if limit < 0: limit = 0
        
        self.animate_traversal_step(0, limit, op_type, idx, val)

    def find_index_by_val(self, val):
        curr = self.head
        idx = 0
        while curr:
            if str(curr.data) == str(val): return idx
            curr = curr.next
            idx += 1
        return -1

    def animate_traversal_step(self, current_v_idx, target_v_idx, op_type, final_logic_idx, val):
        if not self.node_positions and op_type == "add":
             self.finish_op(op_type, final_logic_idx, val)
             return

        if current_v_idx > target_v_idx or current_v_idx >= len(self.node_positions):
            self.finish_op(op_type, final_logic_idx, val)
            return

        self.draw_list()
        pos = self.node_positions[current_v_idx]
        self.canvas.create_text(pos[0] + 35, pos[1] + 70, text="curr", font=("Arial", 9, "bold"), fill="red")
        self.canvas.create_line(pos[0] + 35, pos[1] + 60, pos[0] + 35, pos[1] + 40, arrow=tk.LAST, fill="red", width=2)
        
        self.after(400, lambda: self.animate_traversal_step(current_v_idx + 1, target_v_idx, op_type, final_logic_idx, val))

    def finish_op(self, op_type, idx, val):
        if op_type == "add":
            self.add_node_logic(idx, val)
            self.log(f"Ajouté {val} à l'index {idx}")
        elif op_type == "add_sorted":
            self.add_sorted_logic(val)
            self.log(f"Ajouté {val} trié")
        elif op_type == "delete":
            self.delete_node_logic(idx)
            self.log(f"Supprimé index {idx}")
        
        self.draw_list()
        self.is_animating = False

    # --- Core Logic ---
    def append_node_logic(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            curr = self.head
            while curr.next: curr = curr.next
            curr.next = new_node
            new_node.prev = curr

    def add_node_logic(self, idx, val):
        new_node = Node(val)
        if idx <= 0:
            new_node.next = self.head
            if self.head: self.head.prev = new_node
            self.head = new_node
        else:
            curr = self.head
            cnt = 0
            while curr and cnt < idx - 1:
                curr = curr.next
                cnt += 1
            if curr:
                new_node.next = curr.next
                if curr.next: curr.next.prev = new_node
                curr.next = new_node
                new_node.prev = curr
            else: self.append_node_logic(val)
    
    def add_sorted_logic(self, val):
        new_node = Node(val)
        if not self.head:
            self.head = new_node
            return
        
        if str(val) < str(self.head.data):
             new_node.next = self.head
             self.head.prev = new_node
             self.head = new_node
             return
        
        curr = self.head
        while curr.next and str(curr.next.data) < str(val):
            curr = curr.next
        
        new_node.next = curr.next
        if curr.next: curr.next.prev = new_node
        curr.next = new_node
        new_node.prev = curr

    def delete_node_logic(self, idx):
        if not self.head: return
        if idx == 0:
            self.head = self.head.next
            if self.head: self.head.prev = None
            return
        
        curr = self.head
        cnt = 0
        while curr and cnt < idx:
            curr = curr.next
            cnt += 1
        if curr:
            if curr.prev: curr.prev.next = curr.next
            if curr.next: curr.next.prev = curr.prev

    def modify_node(self):
        try:
            idx = int(self.entry_pos.get())
            val = self.parse_single_val(self.entry_val.get(), self.cb_data_type.get())
            if val is None: return
            
            curr = self.head
            count = 0
            while curr and count < idx:
                curr = curr.next
                count += 1
            if curr:
                curr.data = val
                self.log(f"Modifié index {idx} -> {val}")
            else:
                messagebox.showerror("Erreur", "Index hors limites")
        except: pass
        self.draw_list()

    def sort_list(self):
        if not self.head: return
        
        algo = self.cb_sort_algo.get()
        self.log(f"Tri en cours ({algo})...")
        
        arr = []
        curr = self.head
        while curr:
            arr.append(curr.data)
            curr = curr.next
        
        try:
            arr.sort() 
        except:
             arr.sort(key=str)

        self.head = None
        for x in arr: self.append_node_logic(x)
        self.draw_list()
        self.log(f"Liste triée avec {algo}.")

    # --- Drawing Logic ---
    def draw_list(self):
        self.canvas.delete("all")
        self.node_positions = []
        
        x, y = 80, 200
        node_w, node_h = 70, 50
        gap = 60
        
        if not self.head:
            self.lbl_res_frame.config(text="Résultats: [0 éléments]")
            self.canvas.create_text(400, 200, text="La liste est vide.", font=("Courier", 14), fill="black")
            return
        
        # Update Results Label
        count = self.get_list_size()
        self.lbl_res_frame.config(text=f"Résultats: [{count} éléments]")
        
        # HEAD Indicator
        self.canvas.create_text(x + node_w/2, y - 50, text="HEAD", font=("Arial", 10, "bold"), fill="red")
        self.canvas.create_line(x + node_w/2, y - 40, x + node_w/2, y-5, arrow=tk.LAST, fill="red")
        
        curr = self.head
        idx = 0
        cx = x
        
        colors = ["#3498db", "#e67e22", "#16a085", "#8e44ad", "#c0392b", "#27ae60", "#d35400"]

        # Connections
        curr_for_lines = self.head
        lx = x
        while curr_for_lines:
            if curr_for_lines.next:
                start = lx + node_w
                end = lx + node_w + gap
                self.canvas.create_line(start, y + node_h/2, end, y + node_h/2, arrow=tk.LAST, width=2, fill="#2c3e50")
                if "Double" in self.cb_list_type.get():
                     self.canvas.create_line(start, y + node_h/2 + 10, end, y + node_h/2 + 10, arrow=tk.FIRST, width=2, fill="#2c3e50")
            lx += node_w + gap
            curr_for_lines = curr_for_lines.next
        
        # NULL
        self.canvas.create_text(lx + node_w + 30, y + node_h/2, text="NULL", font=("Arial", 10, "bold"))

        while curr:
            color = colors[idx % len(colors)]
            
            # Shadow
            self.canvas.create_rectangle(cx+4, y+4, cx+node_w+4, y+node_h+4, fill="#bdc3c7", outline="")
            
            # Main Box - FILLED color
            self.canvas.create_rectangle(cx, y, cx+node_w, y+node_h, fill=color, outline="black", width=2)
            self.canvas.create_line(cx + node_w - 20, y, cx + node_w - 20, y + node_h, fill="black") # Pointer part
            
            self.canvas.create_text(cx + (node_w-20)/2, y + node_h/2, text=str(curr.data), fill="white", font=("Arial", 11, "bold"))
            
            self.canvas.create_text(cx + node_w/2, y + node_h + 15, text=str(idx), fill="gray", font=("Arial", 8))
            
            self.node_positions.append((cx, y, curr.data))
            
            cx += node_w + gap
            curr = curr.next
            idx += 1
            
        self.canvas.configure(scrollregion=(0, 0, cx + 100, 400))

    def highlight_circle(self, x, y, color):
        self.canvas.create_oval(x-5, y-5, x+75, y+55, outline=color, width=3)

if __name__ == "__main__":
    root = tk.Tk()
    app = LinkedListVisualizer(root)
    app.mainloop()
