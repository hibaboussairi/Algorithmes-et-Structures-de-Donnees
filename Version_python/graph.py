import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import math
import string
import random
from styles import *

class GraphNode:
    def __init__(self, node_id, x, y, label):
        self.id = node_id
        self.x = x
        self.y = y
        self.label = label

class GraphEdge:
    def __init__(self, u, v, weight):
        self.u = u # GraphNode
        self.v = v # GraphNode
        self.weight = weight

class GraphVisualizer(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("🕸️ TP4 - Visualisateur de Graphes (Dijkstra, Bellman-Ford, Floyd-Warshall)")
        self.geometry("1400x900")
        try: self.state('zoomed')
        except: pass
        apply_theme(self)
        
        self.nodes = [] # List of GraphNode
        self.edges = [] # List of GraphEdge
        
        # Interaction state
        self.drag_start_node = None
        self.drag_current_pos = None
        self.node_counter = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        ttk.Label(self, text="🕸️  Exploration des Graphes", style="PurpleTitle.TLabel").pack(pady=10)
        
        main = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Sidebar
        left = ttk.Frame(main, width=300, style="Sidebar.TFrame")
        main.add(left, weight=1)
        
        # Tools
        lf_tools = ttk.LabelFrame(left, text="🛠️ Génération & Outils", padding=10)
        lf_tools.pack(fill=tk.X, pady=5)
        
        ttk.Label(lf_tools, text="🔢 Nombre de Nœuds :").pack(anchor="w")
        self.entry_node_count = ttk.Entry(lf_tools)
        self.entry_node_count.insert(0, "5")
        self.entry_node_count.pack(fill=tk.X, pady=5)
        
        ttk.Label(lf_tools, text="🔠 Type de Donnée :").pack(anchor="w")
        self.combo_dtype = ttk.Combobox(lf_tools, values=["Entiers", "Réels", "Caractère", "String"], state="readonly")
        self.combo_dtype.set("Caractère")
        self.combo_dtype.pack(fill=tk.X, pady=5)
        
        # New: Graph Type (Re-added as per user request)
        ttk.Label(lf_tools, text="🔗 Type de Graphe :").pack(anchor="w")
        self.combo_graph_type = ttk.Combobox(lf_tools, values=["GO (Orienté)", "GNO (Non Orienté)"], state="readonly")
        self.combo_graph_type.set("GO (Orienté)")
        self.combo_graph_type.pack(fill=tk.X, pady=5)
        self.combo_graph_type.bind("<<ComboboxSelected>>", lambda e: self.redraw())
        
        ttk.Button(lf_tools, text="✨ Générer Graphe", command=self.generate_nodes, style="Brillant.TButton").pack(fill=tk.X, pady=5)
        ttk.Button(lf_tools, text="🗑 Tout Effacer", command=self.reset_graph, style="Red.TButton").pack(fill=tk.X, pady=10)
        
        # Algorithms
        lf_algo = ttk.LabelFrame(left, text="⚡ Algorithmes de Chemin", padding=10)
        lf_algo.pack(fill=tk.X, pady=10)
        
        ttk.Label(lf_algo, text="🧠 Algorithme :").pack(anchor="w")
        self.combo_algo = ttk.Combobox(lf_algo, values=["Dijkstra", "Bellman-Ford", "Floyd-Warshall"], state="readonly")
        self.combo_algo.set("Dijkstra")
        self.combo_algo.pack(fill=tk.X, pady=5)
        
        ttk.Label(lf_algo, text="🚩 Départ (Label) :").pack(anchor="w")
        self.entry_start = ttk.Entry(lf_algo)
        self.entry_start.pack(fill=tk.X, pady=5)
        
        ttk.Label(lf_algo, text="🏁 Arrivée (Label) :").pack(anchor="w")
        self.entry_end = ttk.Entry(lf_algo)
        self.entry_end.pack(fill=tk.X, pady=5)
        
        ttk.Button(lf_algo, text="🚀 Calculer le Chemin", command=self.run_algorithm, style="BrightGreen.TButton").pack(fill=tk.X, pady=10)
        
        # Instructions
        lbl_inst = ttk.Label(left, text="📖 Guide Rapide :\n\n1. Entrez un nombre (ex: 5) et faites 'Générer'.\n2. Glissez d'un nœud à l'autre pour créer un lien.\n3. Entrez le poids du lien.\n4. Choisissez un algo (Dijkstra...) et lancez !", font=("Arial", 9), justify="left")
        lbl_inst.pack(pady=20, anchor="w")
        
        ttk.Button(left, text="🔙 Menu Principal", command=self.destroy).pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Canvas
        # Right Panel Container (Split for Canvas + Log)
        right_panel = ttk.Frame(main)
        main.add(right_panel, weight=4)
        
        # 1. Canvas
        lf_canvas = ttk.LabelFrame(right_panel, text="🎨 Zone de Dessin")
        lf_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(lf_canvas, bg="#fafafa")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 2. Activity Log (Journal)
        lf_log = ttk.LabelFrame(right_panel, text="📜 Journal d'Activité (Tous les Chemins)", padding=5)
        lf_log.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5, ipady=5)
        
        self.log_area = tk.Text(lf_log, height=8, font=("Consolas", 9), state="disabled")
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        # Events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        self.path_result = [] # List of edges in path
        self.matrix_result = None

    def log(self, msg):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"> {msg}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def find_all_paths(self, start_node, end_node, path=[]):
        path = path + [start_node]
        if start_node == end_node:
            return [path]
            
        paths = []
        is_directed = self.combo_graph_type.get() == "GO (Orienté)"
        
        neighbors = []
        for e in self.edges:
            if e.u == start_node:
                neighbors.append(e.v)
            elif not is_directed and e.v == start_node:
                neighbors.append(e.u)
        
        # Simple DFS
        for node in neighbors:
            if node not in path:
                newpaths = self.find_all_paths(node, end_node, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths

    def calculate_path_weight(self, path_nodes):
        total = 0
        is_directed = self.combo_graph_type.get() == "GO (Orienté)"
        
        for i in range(len(path_nodes) - 1):
            u, v = path_nodes[i], path_nodes[i+1]
            found_weight = float('inf')
            
            # Find edge weight
            for e in self.edges:
                if e.u == u and e.v == v:
                    found_weight = e.weight; break
                if not is_directed and e.u == v and e.v == u:
                    found_weight = e.weight; break
            
            if found_weight != float('inf'): total += found_weight
            
        return total
        
    def reset_graph(self):
        self.nodes = []
        self.edges = []
        self.node_counter = 0
        self.path_result = []
        self.matrix_result = None
        # Clear Algo inputs
        self.entry_start.delete(0, tk.END)
        self.entry_end.delete(0, tk.END)
        
        # Clear Log
        self.log_area.config(state="normal")
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state="disabled")
        
        self.redraw()
        
    def get_node_at(self, x, y):
        # Slightly larger hit area for drag
        for n in self.nodes:
            dist = math.sqrt((n.x - x)**2 + (n.y - y)**2)
            if dist <= 25: return n # Reduced hit area slightly (was 30) matching new size
        return None
        
    def generate_nodes(self):
        try:
            count = int(self.entry_node_count.get())
            if count <= 0: return
        except: return
        
        self.reset_graph()
        self.node_counter = 0
        dtype = self.combo_dtype.get()
        
        # Dynamic Center & Radius
        self.canvas.update_idletasks() # Ensure geometry
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Fallback if window not fully drawn
        if w < 100: w = 800
        if h < 100: h = 600
        
        cx, cy = w / 2, h / 2
        min_dim = min(w, h)
        radius = (min_dim / 2) - 60 # Padding
        if radius < 50: radius = 50 # Minimum radius
        
        for i in range(count):
            angle = 2 * math.pi * i / count
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            
            # Label based on Type
            if dtype == "Entiers":
                label = str(random.randint(1, 99))
                # Ensure uniqueness? Simple retry
                while any(n.label == label for n in self.nodes):
                    label = str(random.randint(1, 99))
            elif dtype == "Réels":
                 label = str(round(random.uniform(1.0, 99.0), 1))
            elif dtype == "Caractère":
                 # A, B, C... Z, AA, AB...
                 if i < 26: label = string.ascii_uppercase[i]
                 else: label = f"C{i}"
            else: # String
                 label = f"S{i}"
                 
            self.nodes.append(GraphNode(i, x, y, label))
            self.node_counter += 1
            
        self.redraw()

    def on_click(self, event):
        x, y = event.x, event.y
        target = self.get_node_at(x, y)
        if target:
            self.drag_start_node = target
            self.drag_current_pos = (x, y)
        else:
            self.drag_start_node = None
            
    def on_drag(self, event):
        if self.drag_start_node:
            self.drag_current_pos = (event.x, event.y)
            self.redraw() # Redraw to show dynamic line
            
    def on_release(self, event):
        if self.drag_start_node:
            end_node = self.get_node_at(event.x, event.y)
            if end_node and end_node != self.drag_start_node:
                # Create Edge
                w = simpledialog.askinteger("Poids", f"Poids de {self.drag_start_node.label} -> {end_node.label} :", initialvalue=1)
                if w is not None:
                     # Check if exists (update?)
                     exists = False
                     for e in self.edges:
                         if e.u == self.drag_start_node and e.v == end_node:
                             e.weight = w
                             exists = True
                             break
                     if not exists:
                         self.edges.append(GraphEdge(self.drag_start_node, end_node, w))
            
            self.drag_start_node = None
            self.drag_current_pos = None
            self.redraw()
            
    def redraw(self):
        self.canvas.delete("all")
        
        # Draw Grid (Simple background)
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w > 100 and h > 100:
            for i in range(0, w, 50):
                self.canvas.create_line(i, 0, i, h, fill="#f0f0f0")
            for j in range(0, h, 50):
                self.canvas.create_line(0, j, w, j, fill="#f0f0f0")
        
        # Temp line
        if self.drag_start_node and self.drag_current_pos:
            self.canvas.create_line(self.drag_start_node.x, self.drag_start_node.y, 
                                    self.drag_current_pos[0], self.drag_current_pos[1], 
                                    fill="gray", dash=(4, 2))
        
        # Draw Edges
        for e in self.edges:
            color = "black"
            width = 2
            
            # Highlight path logic could go here
            if self.path_result:
                # Check if this edge is in path (undirected check? or directed?)
                # We assume directed for algos usually, but let's treat as directed visual
                for pe in self.path_result:
                    if pe == e:
                        color = "red"
                        width = 4
                        break
            
            # Determine arrow style based on graph type
            is_directed = self.combo_graph_type.get() == "GO (Orienté)"
            arrow_style = tk.LAST if is_directed else None
            
            # Make arrows more visible if directed
            arrow_shape = (16, 20, 6) if is_directed else None

            self.canvas.create_line(e.u.x, e.u.y, e.v.x, e.v.y, fill=color, width=width, arrow=arrow_style, arrowshape=arrow_shape)
            # Weight label
            mx, my = (e.u.x + e.v.x)/2, (e.u.y + e.v.y)/2
            self.canvas.create_rectangle(mx-10, my-10, mx+10, my+10, fill="white", outline="")
            self.canvas.create_text(mx, my, text=str(e.weight), fill="blue", font=("Arial", 9, "bold"))
            
        # Draw Nodes
        r = 15 # Reduced size (was 20)
        for n in self.nodes:
            fill = "#3498db"
            outline = "white"
            # Highlight selected if needed, or start/end?
            # Reusing code... drag start?
            if n == self.drag_start_node:
                outline = "orange"
                
            self.canvas.create_oval(n.x-r, n.y-r, n.x+r, n.y+r, fill=fill, outline=outline, width=2)
            self.canvas.create_text(n.x, n.y, text=n.label, fill="white", font=("Arial", 10, "bold"))
            
    def get_node_by_label(self, lbl):
        search = lbl.strip()
        for n in self.nodes:
            if n.label.lower() == search.lower(): return n
        return None

    def run_algorithm(self):
        start_lbl = self.entry_start.get().strip()
        start_node = self.get_node_by_label(start_lbl)
        
        if not start_node:
            messagebox.showerror("Erreur", f"Nœud de départ '{start_lbl}' introuvable.")
            return

        # --- LOG ALL PATHS FEATURE ---
        end_lbl = self.entry_end.get().strip()
        end_node = self.get_node_by_label(end_lbl)
        
        self.log_area.config(state="normal")
        self.log_area.delete("1.0", tk.END) # Clear log
        self.log_area.config(state="disabled")
        
        if end_node:
            self.log(f"--- Recherche de TOUS les chemins: {start_node.label} -> {end_node.label} ---")
            all_paths = self.find_all_paths(start_node, end_node)
            if not all_paths:
                self.log("Aucun chemin trouvé.")
            else:
                for i, p in enumerate(all_paths):
                    txt_path = " -> ".join([n.label for n in p])
                    w = self.calculate_path_weight(p)
                    self.log(f"{i+1}. {txt_path} (Poids: {w})")
            self.log("-" * 40)

        algo = self.combo_algo.get()
        self.path_result = []
        
        if algo == "Dijkstra":
            self.run_dijkstra(start_node)
        elif algo == "Bellman-Ford":
            self.run_bellman_ford(start_node)
        elif algo == "Floyd-Warshall":
            self.run_floyd_warshall()
            
        self.redraw()

    def reconstruct_path(self, predecessors, start, end):
        # Reconstruct path from predecessors map
        path_edges = []
        curr = end
        while curr != start:
            prev = predecessors.get(curr)
            if not prev: return [] # No path
            # Find edge
            edge_obj = None
            for e in self.edges:
                if e.u == prev and e.v == curr:
                    edge_obj = e
                    break
            if edge_obj: path_edges.append(edge_obj)
            curr = prev
        return path_edges

    def run_dijkstra(self, start_node):
        end_lbl = self.entry_end.get()
        end_node = self.get_node_by_label(end_lbl)
        
        import heapq
        # Distances
        dist = {n: float('inf') for n in self.nodes}
        dist[start_node] = 0
        pred = {n: None for n in self.nodes}
        pq = [(0, start_node.id, start_node)] # (dist, id, node) - id for tie break
        
        while pq:
            d, _, u = heapq.heappop(pq)
            if d > dist[u]: continue
            if u == end_node: break
            
            for e in self.edges:
                if e.u == u:
                    v = e.v
                    alt = dist[u] + e.weight
                    if alt < dist[v]:
                        dist[v] = alt
                        pred[v] = u
                        heapq.heappush(pq, (alt, v.id, v))
                        
        if end_node:
            if dist[end_node] == float('inf'):
                self.log(f"Résultat Dijkstra: Aucun chemin vers {end_lbl}.")
                messagebox.showinfo("Résultat", "Aucun chemin trouvé.")
            else:
                self.path_result = self.reconstruct_path(pred, start_node, end_node)
                # Parse path for logging
                path_tokens = [start_node.label]
                for e in self.path_result[::-1]: # Edges are reversed? No, reconstruct returns end->start order? Actually check reconstruct logic.
                   # reconstruct returns list of edge objects walking backwards from end to start.
                   # So path_result[0] is (prev->end), path_result[1] is (prev2->prev)...
                   pass 
                
                # Let's rebuild labels from edges properly
                # self.path_result is [edge(prev->end), edge(prev2->prev)...]
                # wait, list append order in reconstruct_path: curr=end, loop while curr!=start. append edge. curr=prev.
                # So it's [Last Edge, ..., First Edge]. We need to reverse it.
                
                ordered_edges = self.path_result[::-1]
                path_str = start_node.label
                for e in ordered_edges:
                    path_str += f" -> {e.v.label}"
                
                final_dist = dist[end_node]
                self.log(f"★ COURT CHEMIN (Dijkstra): {path_str}")
                self.log(f"★ DISTANCE TOTALE: {final_dist}")
                messagebox.showinfo("Résultat", f"Distance minimale (Dijkstra) : {final_dist}")
        else:
             self.log("Calcul Dijkstra terminé (toutes destinations).")
             messagebox.showinfo("Info", "Destination non spécifiée. Distances calculées.")

    def run_bellman_ford(self, start_node):
        end_lbl = self.entry_end.get()
        end_node = self.get_node_by_label(end_lbl)
        
        dist = {n: float('inf') for n in self.nodes}
        dist[start_node] = 0
        pred = {n: None for n in self.nodes}
        
        for _ in range(len(self.nodes) - 1):
            for e in self.edges:
                if dist[e.u] + e.weight < dist[e.v]:
                    dist[e.v] = dist[e.u] + e.weight
                    pred[e.v] = e.u
                    
        # Check negative cycles
        for e in self.edges:
             if dist[e.u] + e.weight < dist[e.v]:
                 messagebox.showerror("Erreur", "Cycle négatif détecté !")
                 return

        if end_node:
             if dist[end_node] == float('inf'):
                self.log(f"Résultat Bellman-Ford: Aucun chemin vers {end_lbl}.")
                messagebox.showinfo("Résultat", "Aucun chemin trouvé.")
             else:
                self.path_result = self.reconstruct_path(pred, start_node, end_node)
                ordered_edges = self.path_result[::-1]
                path_str = start_node.label
                for e in ordered_edges:
                    path_str += f" -> {e.v.label}"
                    
                final_dist = dist[end_node]
                self.log(f"★ COURT CHEMIN (Bellman-Ford): {path_str}")
                self.log(f"★ DISTANCE TOTALE: {final_dist}")
                messagebox.showinfo("Résultat", f"Distance minimale (Bellman-Ford) : {final_dist}")

    def run_floyd_warshall(self):
        # Index map
        n_map = {n: i for i, n in enumerate(self.nodes)}
        N = len(self.nodes)
        
        # Init matrix
        dist_matrix = [[float('inf')] * N for _ in range(N)]
        for i in range(N): dist_matrix[i][i] = 0
        
        for e in self.edges:
            u_idx = n_map[e.u]
            v_idx = n_map[e.v]
            dist_matrix[u_idx][v_idx] = e.weight
            
        # Computed
        for k in range(N):
            for i in range(N):
                for j in range(N):
                    if dist_matrix[i][k] + dist_matrix[k][j] < dist_matrix[i][j]:
                        dist_matrix[i][j] = dist_matrix[i][k] + dist_matrix[k][j]
        
        # Show Matrix
        res_win = tk.Toplevel(self)
        res_win.title("Matrice Floyd-Warshall")
        txt = tk.Text(res_win, font=("Consolas", 10))
        txt.pack()
        
        # Header
        header = "      " + " ".join([f"{n.label:>5}" for n in self.nodes]) + "\n"
        txt.insert(tk.END, header)
        
        for i, row in enumerate(dist_matrix):
            line = f"{self.nodes[i].label:>5} "
            for val in row:
                v_str = "INF" if val == float('inf') else str(val)
                line += f"{v_str:>5} "
            txt.insert(tk.END, line + "\n")
            
        messagebox.showinfo("Info", "Matrice calculée (voir fenêtre). Pour voir un chemin, utilisez Dijkstra ou Bellman-Ford.")

if __name__ == "__main__":
    app = tk.Tk()
    app.withdraw()
    GraphVisualizer(app)
    app.mainloop()
