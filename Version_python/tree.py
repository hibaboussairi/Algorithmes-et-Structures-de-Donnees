import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from styles import *
import random

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = [] # List of TreeNode
        # For layout
        self.x = 0
        self.y = 0

class TreeVisualizer(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("🌳 TP3 - Traitement des Arbres (Python)")
        self.geometry("1400x900")
        try:
            self.state('zoomed') # Full screen / Maximized
        except: pass
        apply_theme(self)
        
        self.root_node = None
        
        # Animation state
        self.animation_speed = 600 # ms
        self.is_animating = False

        # Styles specific to this window
        style = ttk.Style()
        style.configure("PurpleTitle.TLabel", foreground="#8e44ad", font=("Helvetica", 20, "bold"))
        style.configure("Group.TLabelframe.Label", foreground="#8e44ad", font=("Helvetica", 11, "bold"))
        style.configure("Sidebar.TFrame", background="#f0f0f0") 

        self.setup_ui()

    def setup_ui(self):
        try:
            # Title
            ttk.Label(self, text="Les Arbres", style="PurpleTitle.TLabel").pack(pady=(10, 20))

            # Main Layout
            main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
            main_paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

            # --- LEFT PANEL ---
            left_frame = ttk.Frame(main_paned, width=350, style="Sidebar.TFrame")
            main_paned.add(left_frame, weight=1)

            lf_params = ttk.LabelFrame(left_frame, text="Paramètres de l'Arbre", style="Group.TLabelframe", padding=15)
            lf_params.pack(fill=tk.X, padx=5, pady=5)

            # 1. Type d'Arbre
            self.create_param_row(lf_params, "Type d'Arbre (Binaire/N-aire):", ["Binaire", "N-aire"], 0, "Binaire")
            self.combo_type = self.last_combo

            # 2. Type de Donnée
            self.create_param_row(lf_params, "Type de Donnée :", ["Entiers", "Réels", "Chaînes"], 1, "Entiers")
            self.combo_dtype = self.last_combo

            # 3. Taille
            tk.Label(lf_params, text="Taille (Nb Nœuds, max 100) :").grid(row=2, column=0, sticky="w", pady=5)
            self.entry_size = ttk.Entry(lf_params)
            self.entry_size.insert(0, "10")
            self.entry_size.grid(row=2, column=1, sticky="ew", pady=5)

            # 4. Mode d'Entrée
            tk.Label(lf_params, text="Mode d'Entrée :").grid(row=3, column=0, sticky="w", pady=5)
            self.combo_mode = ttk.Combobox(lf_params, values=["Aléatoire", "Manuel"], state="readonly")
            self.combo_mode.set("Aléatoire")
            self.combo_mode.grid(row=3, column=1, sticky="ew", pady=5)
            self.combo_mode.bind("<<ComboboxSelected>>", self.toggle_manual_input)
            
            # Hidden Manual Input
            self.lbl_manual = tk.Label(lf_params, text="Valeurs (x,y,z...):")
            self.entry_manual = ttk.Entry(lf_params)

            # 5. Type de Parcours (Triggers visibility logic)
            tk.Label(lf_params, text="Type de Parcours :").grid(row=5, column=0, sticky="w", pady=5)
            self.combo_traversal_type = ttk.Combobox(lf_params, values=["Profondeur", "Largeur"], state="readonly")
            self.combo_traversal_type.set("Profondeur")
            self.combo_traversal_type.grid(row=5, column=1, sticky="ew", pady=5)
            self.combo_traversal_type.bind("<<ComboboxSelected>>", self.toggle_traversal_options)
            
            # 6. Méthode de Profondeur (Conditional)
            self.lbl_depth_method = tk.Label(lf_params, text="Méthode de Profondeur :")
            self.lbl_depth_method.grid(row=6, column=0, sticky="w", pady=5)
            self.combo_depth_method = ttk.Combobox(lf_params, values=["Pré-ordre", "Ordre", "Poste fixe"], state="readonly")
            self.combo_depth_method.set("Pré-ordre")
            self.combo_depth_method.grid(row=6, column=1, sticky="ew", pady=5)
            # Bind selection to auto-run traversal
            self.combo_depth_method.bind("<<ComboboxSelected>>", lambda e: self.traverse())
            
            lf_params.columnconfigure(1, weight=1)

            # Operations
            btn_frame = ttk.Frame(left_frame, padding=10)
            btn_frame.pack(fill=tk.X)
            
            def mk_btn(txt, cmd):
                b = ttk.Button(btn_frame, text=txt, command=cmd)
                b.pack(fill=tk.X, pady=5)
                return b
            
            mk_btn("✔ Créer et Afficher", self.create_tree)
            mk_btn("⚙ Insérer/Modifier/Supprimer", self.manage_nodes_dialog)
            mk_btn("🌪 Ordonner un Arbre", self.sort_tree_children) 
            mk_btn("♻ Transformer N-aire -> Binaire", self.transform_binary)
            
            # Explicit Traversal Button for clarity
            ttk.Button(btn_frame, text="▶ Lancer le Parcours", command=self.traverse).pack(fill=tk.X, pady=5)

            ttk.Separator(btn_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
            ttk.Button(btn_frame, text="🗑 Réinitialiser tout", command=self.reset).pack(fill=tk.X, pady=5)
            
            # Speed Control
            ttk.Label(left_frame, text="Vitesse d'Animation:").pack(pady=(20,5))
            self.scale_speed = ttk.Scale(left_frame, from_=50, to=2000, value=600, orient=tk.HORIZONTAL)
            self.scale_speed.pack(fill=tk.X, padx=20)


            # --- RIGHT PANEL ---
            right_frame = ttk.Frame(main_paned, style="Sidebar.TFrame")
            main_paned.add(right_frame, weight=3)
            
            lf_viz = ttk.LabelFrame(right_frame, text="Visualisation et Résultats", style="Group.TLabelframe", padding=10)
            lf_viz.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            lbl_graph_title = ttk.LabelFrame(lf_viz, text="Affichage Graphique de l'Arbre")
            lbl_graph_title.pack(fill=tk.BOTH, expand=True)

            self.canvas = tk.Canvas(lbl_graph_title, bg="#f9f9f9", highlightthickness=0)
            
            # Scrollbars Frame
            canvas_container = ttk.Frame(lbl_graph_title)
            canvas_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            self.canvas = tk.Canvas(canvas_container, bg="#f9f9f9", highlightthickness=0)
            v_scroll = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
            h_scroll = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
            
            self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
            
            # Grid Layout for Scrollbars
            self.canvas.grid(row=0, column=0, sticky="nsew")
            v_scroll.grid(row=0, column=1, sticky="ns")
            h_scroll.grid(row=1, column=0, sticky="ew")
            
            canvas_container.columnconfigure(0, weight=1)
            canvas_container.columnconfigure(1, weight=0)
            canvas_container.rowconfigure(0, weight=1)
            canvas_container.rowconfigure(1, weight=0)
            
            self.canvas.create_text(400, 300, text="Cliquez sur 'Créer...' pour générer le dessin.", font=("Arial", 10), fill="gray", justify="center")

            lbl_log = ttk.LabelFrame(lf_viz, text="Journal d'activité")
            lbl_log.pack(fill=tk.X, pady=(10, 0))
            
            self.log_area = tk.Text(lbl_log, height=5, font=("Consolas", 9), state="disabled", bg="#f4f4f4")
            self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.log("Interface prête.")

            # Return
            ttk.Button(self, text="⬅ Retour au Menu Principal", command=self.destroy).pack(side=tk.BOTTOM, pady=10)

            # Init state
            self.toggle_traversal_options()

        except Exception as e:
            messagebox.showerror("UI Error", f"{e}")
            self.destroy()

    def create_param_row(self, parent, label, values, row, default):
        tk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5)
        cb = ttk.Combobox(parent, values=values, state="readonly")
        cb.set(default)
        cb.grid(row=row, column=1, sticky="ew", pady=5)
        self.last_combo = cb

    def toggle_manual_input(self, event=None):
        if self.combo_mode.get() == "Manuel":
            self.lbl_manual.grid(row=4, column=0, sticky="w", pady=5)
            self.entry_manual.grid(row=4, column=1, sticky="ew", pady=5)
        else:
            self.lbl_manual.grid_remove()
            self.entry_manual.grid_remove()

    def toggle_traversal_options(self, event=None):
        t_type = self.combo_traversal_type.get()
        if t_type == "Profondeur":
            self.lbl_depth_method.grid()
            self.combo_depth_method.grid()
        else:
            self.lbl_depth_method.grid_remove()
            self.combo_depth_method.grid_remove()

    def log(self, msg):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"> {msg}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def reset(self):
        self.root_node = None
        self.is_animating = False
        self.canvas.delete("all")
        self.log("Réinitialisé.")

    def update_scrollregion(self):
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # --- ANIMATION CORE ---
    def animate_sequence(self, steps, callback=None):
        self.is_animating = True
        
        def run_step(idx):
            if not self.is_animating: return
            if idx >= len(steps):
                self.is_animating = False
                if callback: callback()
                return
            
            action_func = steps[idx]
            action_func()
            
            # Dynamic speed fetch
            # Invert scalar: High value = Slow? Or Low value = Fast?
            # User scale 50 (Fast) to 2000 (Slow). 
            delay = int(self.scale_speed.get())
            self.after(delay, lambda: run_step(idx + 1))
            
        run_step(0)

    # --- Creation & Drawing ---
    def create_tree(self):
        if self.is_animating: return 
        try:
            nodes = self._generate_nodes()
            if not nodes: 
                messagebox.showerror("Erreur", "Aucun nœud généré.")
                return

            self.root_node = nodes[0]
            self.is_animating = True # Lock
            
            # 1. Build structure logic first
            self._connect_nodes_randomly(nodes)
            
            # 2. Layout positions
            w = self.canvas.winfo_width()
            if w < 100: w = 1200
            self.layout_tree(self.root_node, 0, w/2, w/2)
            
            # 3. Animate Drawing (Node by Node BFS order for visual effect)
            self.canvas.delete("all")
            self.log("Début de l'animation de construction...")
            
            # BFS for drawing order
            animation_steps = []
            q = [self.root_node]
            visited = []
            
            # To draw lines, we need Parent already drawn. 
            
            while q:
                curr = q.pop(0)
                visited.append(curr)
                
                # Closure to capture current node 'n'
                def draw_action(n=curr): 
                    self.render_node_single(n)
                
                animation_steps.append(draw_action)
                q.extend(curr.children)

            def on_anim_done():
                self.log("Construction terminée.")
                self.update_scrollregion()

            self.animate_sequence(animation_steps, on_anim_done)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"{e}")
            self.is_animating = False

    def _generate_nodes(self):
        mode = self.combo_mode.get()
        dtype = self.combo_dtype.get()
        nodes = []
        
        if mode == "Manuel":
            raw = self.entry_manual.get()
            if not raw: return []
            vals = [x.strip() for x in raw.split(',')]
            for v in vals:
                try:
                    if dtype == "Entiers": val = int(v)
                    elif dtype == "Réels": val = float(v)
                    else: val = v
                    nodes.append(TreeNode(val))
                except: pass
        else:
            try: size = int(self.entry_size.get())
            except: size = 15
            for i in range(size):
                if dtype == "Entiers": val = random.randint(1, 100)
                elif dtype == "Réels": val = round(random.uniform(1, 100), 2)
                else: val = f"N{i}"
                nodes.append(TreeNode(val))
        return nodes

    def _connect_nodes_randomly(self, nodes):
        is_binary = self.combo_type.get() == "Binaire"
        limit = 2 if is_binary else 4 # Limit N-ary visual clutter to 4 children max for better display
        
        connected = [nodes[0]]
        remaining = nodes[1:]
        
        for node in remaining:
            candidates = list(connected)
            random.shuffle(candidates)
            for parent in candidates:
                if len(parent.children) >= limit: continue
                parent.children.append(node)
                connected.append(node)
                break

    def draw_tree(self):
        # Instant draw (no animation) for data ops
        self.canvas.delete("all")
        if not self.root_node: return
        w = self.canvas.winfo_width()
        if w < 100: w = 1200
        self.layout_tree(self.root_node, 0, w/2, w/2)
        self.render_node_recursive(self.root_node)
        self.update_scrollregion()

    def layout_tree(self, node, depth, x, available_width):
        node.x = x
        node.y = 50 + depth * 80
        if not node.children: return
        num = len(node.children)
        step = available_width / max(2, num + 1)
        if num == 1:
             self.layout_tree(node.children[0], depth + 1, x, step)
        else:
            step_child = available_width / num
            start = x - (available_width/2) + step_child/2
            for i, child in enumerate(node.children):
                self.layout_tree(child, depth + 1, start + i*step_child, step_child)

    def render_node_single(self, node):
        r = 20
        # Color based on leaf/internal
        color = "#e67e22" if not node.children else "#3498db"
        
        # Draw line to parent if exists
        parent = self._find_parent(self.root_node, node)
        if parent:
            self.canvas.create_line(parent.x, parent.y+r, node.x, node.y-r, fill="gray", width=2)
            # Re-draw parent to cover line overlap?
            self.canvas.create_oval(parent.x-r, parent.y-r, parent.x+r, parent.y+r, fill="#3498db" if parent.children else "#e67e22", outline="white", width=2)
            self.canvas.create_text(parent.x, parent.y, text=str(parent.value), fill="white", font=("Arial", 9, "bold"))

        self.canvas.create_oval(node.x-r, node.y-r, node.x+r, node.y+r, fill=color, outline="white", width=2)
        self.canvas.create_text(node.x, node.y, text=str(node.value), fill="white", font=("Arial", 9, "bold"))

    def render_node_recursive(self, node):
        r = 20
        for child in node.children:
            self.canvas.create_line(node.x, node.y+r, child.x, child.y-r, fill="gray", width=2)
            self.render_node_recursive(child)
        color = "#e67e22" if not node.children else "#3498db"
        self.canvas.create_oval(node.x-r, node.y-r, node.x+r, node.y+r, fill=color, outline="white", width=2)
        self.canvas.create_text(node.x, node.y, text=str(node.value), fill="white", font=("Arial", 9, "bold"))

    def _find_parent(self, start, target):
        if not start: return None
        if target in start.children: return start
        for c in start.children:
            found = self._find_parent(c, target)
            if found: return found
        return None

    # --- TRAVERSAL ANIMATION ---
    def traverse(self, event=None):
        if not self.root_node or self.is_animating: return
        
        t_type = self.combo_traversal_type.get()
        method = self.combo_depth_method.get()
        
        path = []
        if t_type == "Largeur":
             # BFS
             q = [self.root_node]
             while q:
                 curr = q.pop(0)
                 path.append(curr)
                 q.extend(curr.children)
        else:
             # DFS
             def dfs(n):
                 if method == "Pré-ordre": path.append(n)
                 
                 if method == "Ordre":
                     # For N-ary, ambiguous. 
                     if n.children:
                         dfs(n.children[0])
                         path.append(n)
                         for c in n.children[1:]: dfs(c)
                     else:
                         path.append(n)
                         
                 if method == "Poste fixe": 
                     for c in n.children: dfs(c)
                     path.append(n)
                     
                 if method == "Pré-ordre": 
                     for c in n.children: dfs(c)
             dfs(self.root_node)
        
        # Build Result String
        result_values = [str(n.value) for n in path]
        full_res_str = " -> ".join(result_values)
        method_label = f"{t_type} - {method}" if t_type == "Profondeur" else t_type

        # Animation Steps
        steps = []
        r = 20
        for node in path:
            def highlight(n=node):
                # Orange highlight
                self.canvas.create_oval(n.x-r, n.y-r, n.x+r, n.y+r, fill="#f1c40f", outline="red", width=3)
                self.canvas.create_text(n.x, n.y, text=str(n.value), fill="black", font=("Arial", 9, "bold"))
                # self.log(f"Visite: {n.value}") # Reduced spam
            steps.append(highlight)
            
            def unhighlight(n=node):
                color = "#e67e22" if not n.children else "#3498db"
                self.canvas.create_oval(n.x-r, n.y-r, n.x+r, n.y+r, fill=color, outline="white", width=2)
                self.canvas.create_text(n.x, n.y, text=str(n.value), fill="white", font=("Arial", 9, "bold"))
            steps.append(unhighlight)
            
        self.log(f"Démarrage parcours: {method_label}...")
        
        def on_done():
            self.log(f"Résultat ({method_label}) : {full_res_str}")
            messagebox.showinfo("Résultat du Parcours", f"{method_label}:\n{full_res_str}")

        self.animate_sequence(steps, on_done)

    # --- OPS ---
    def manage_nodes_dialog(self):
        if not self.root_node:
            messagebox.showwarning("Attention", "Veuillez d'abord créer un arbre.")
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Gestion des Nœuds ({self.combo_type.get()})")
        dialog.geometry("400x300")
        apply_theme(dialog)
        
        ttk.Label(dialog, text="Choisissez l'opération à effectuer sur l'arbre :", font=("Arial", 11, "bold")).pack(pady=15)
        
        frame_btns = ttk.Frame(dialog)
        frame_btns.pack(expand=True, fill=tk.BOTH, padx=20)
        
        # Custom big buttons
        def btn_cmd(op):
            dialog.destroy()
            self.perform_node_op(op)

        ttk.Button(frame_btns, text="1. Insérer un Nœud", command=lambda: btn_cmd("insert"), style="TButton").pack(fill=tk.X, pady=10, ipady=5)
        ttk.Button(frame_btns, text="2. Modifier un Nœud", command=lambda: btn_cmd("modify"), style="TButton").pack(fill=tk.X, pady=10, ipady=5)
        ttk.Button(frame_btns, text="3. Supprimer un Nœud", command=lambda: btn_cmd("delete"), style="Red.TButton").pack(fill=tk.X, pady=10, ipady=5)

    def perform_node_op(self, op):
        if op == "insert":
            val = simpledialog.askstring("Insérer", "Valeur du nouveau nœud:")
            if val: 
                self.insert_node_logic(val)
                self.draw_tree()
                self.log(f"Nœud {val} inséré.")
        elif op == "modify":
            old_val = simpledialog.askstring("Modifier", "Valeur du nœud à modifier:")
            if old_val:
                new_val = simpledialog.askstring("Modifier", "Nouvelle valeur:")
                if self.modify_node_logic(self.root_node, old_val, new_val):
                    self.draw_tree()
                    self.log(f"Nœud {old_val} modifié en {new_val}.")
                else:
                    self.log(f"Nœud {old_val} introuvable.")
        elif op == "delete":
            val = simpledialog.askstring("Supprimer", "Valeur du nœud à supprimer:")
            if val:
                if self.delete_node_logic(self.root_node, val): 
                     self.draw_tree()
                     self.log(f"Nœud {val} supprimé.")
                else:
                     self.log(f"Impossible de supprimer {val} (Introuvable ou Racine).")

    def insert_node_logic(self, val):
        queue = [self.root_node]
        limit = 2 if self.combo_type.get() == "Binaire" else 5
        while queue:
            curr = queue.pop(0)
            if len(curr.children) < limit:
                curr.children.append(TreeNode(val))
                return
            queue.extend(curr.children)

    def modify_node_logic(self, node, old, new):
        if str(node.value) == str(old):
            node.value = new
            return True
        for child in node.children:
            if self.modify_node_logic(child, old, new): return True
        return False

    def delete_node_logic(self, parent, val):
        for i, child in enumerate(parent.children):
            if str(child.value) == str(val):
                del parent.children[i]
                return True
            if self.delete_node_logic(child, val): return True
        return False

    def sort_tree_children(self):
        """
        Rebuilds the entire tree as a Balanced Binary Search Tree (BST).
        Left Child < Root < Right Child.
        """
        if not self.root_node: 
             messagebox.showinfo("Info", "Créez d'abord un arbre.")
             return
             
        dtype = self.combo_dtype.get()
        
        # 1. Collect all values
        all_values = []
        q = [self.root_node]
        while q:
            curr = q.pop(0)
            all_values.append(curr.value)
            q.extend(curr.children)
            
        if not all_values: return

        # 2. Sort values strictly
        def parse_val(v):
            if dtype == "Entiers":
                try: return int(v)
                except: return 0
            elif dtype == "Réels":
                try: return float(v)
                except: return 0.0
            return str(v)

        # Sort based on parsed values
        all_values.sort(key=parse_val)
        
        # 3. Build Balanced BST Recursively
        def build_bst(vals):
            if not vals: return None
            
            mid = len(vals) // 2
            node = TreeNode(vals[mid])
            
            left_child = build_bst(vals[:mid])
            right_child = build_bst(vals[mid+1:])
            
            if left_child: node.children.append(left_child)
            if right_child: node.children.append(right_child)
            
            return node

        try:
            self.root_node = build_bst(all_values)
            
            # Force Type to Binaire for correct visualization/logic context
            self.combo_type.set("Binaire")
            
            self.draw_tree()
            self.log(f"Arbre transformé en BST (Arbre Binaire de Recherche).")
            messagebox.showinfo("Succès", "L'arbre a été ordonné en BST (Gauche < Racine < Droite).")
        except Exception as e:
            self.log(f"Erreur de tri: {e}")
            messagebox.showerror("Erreur", f"Echec du tri: {e}")

    def transform_binary(self):
        if not self.root_node: return
        if self.combo_type.get() == "Binaire":
             self.log("Déjà binaire.")
             return
             
        vals = []
        q = [self.root_node]
        while q:
            c = q.pop(0)
            vals.append(c.value)
            q.extend(c.children)
            
        self.root_node = TreeNode(vals[0])
        connected = [self.root_node]
        for v in vals[1:]:
             node = TreeNode(v)
             for p in connected:
                 if len(p.children) < 2:
                     p.children.append(node)
                     connected.append(node)
                     break
        
        self.combo_type.set("Binaire")
        self.draw_tree()
        self.log(f"Transformé en Arbre Binaire (Reconstruit {len(vals)} nœuds).")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = TreeVisualizer(root)
    app.mainloop()








