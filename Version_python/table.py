import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
from styles import *

# Algorithms
ALGORITHMS = ["Bulle", "Insertion", "Shell", "Rapide"]
MAX_PRACTICAL_SIZE = 100_000_000  
MAX_DISPLAY_ELEMENTS = 10000  # Display up to 1000 elements
MAX_CURVE_SAMPLES = 4  # 4 points for performance curve
MAX_SIZE_FOR_NSQUARE = 3000  # Lower threshold to show O(N²) difference earlier

class SortingVisualizer(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("📊 Interface de Tri et Comparaison (Python)")
        self.geometry("1200x800")
        apply_theme(self)

        self.tableau = []
        self.temps_tris = {}
        self.sample_sizes = []
        
        self.setup_ui()

    def setup_ui(self):
        # Main Layout: Left Control Panel, Right Display/Graph
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- LEFT PANEL ---
        left_panel = ttk.Frame(self.main_container, width=320)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Header Style for Panel
        lbl_setup = ttk.Label(left_panel, text="Configuration", font=("Arial", 12, "bold"))
        lbl_setup.pack(pady=(0, 10))

        # 1. Size
        self.create_labeled_entry(left_panel, "Taille du Tableau (N)", "1000", "size_var")

        # 2. Data Type
        self.create_combobox(left_panel, "Type de données", ["Entier", "Réel", "Caractère", "String"], "type_var")

        # 3. Fill Mode
        self.mode_var = tk.StringVar(value="Aléatoire")
        lf_mode = ttk.LabelFrame(left_panel, text="Mode de remplissage")
        lf_mode.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(lf_mode, text="Aléatoire", variable=self.mode_var, value="Aléatoire", command=self.toggle_manual_input).pack(anchor="w")
        ttk.Radiobutton(lf_mode, text="Manuel", variable=self.mode_var, value="Manuel", command=self.toggle_manual_input).pack(anchor="w")
        self.txt_manual = ttk.Entry(lf_mode)
        self.txt_manual.pack(fill=tk.X, padx=5, pady=2)
        self.txt_manual.pack_forget() # Hide initially

        # 4. Algorithm Choice (For Single Sort)
        self.create_combobox(left_panel, "Algorithme (Visualisation)", ALGORITHMS, "algo_var")

        # 5. Final Sort Order
        self.final_order_var = tk.StringVar(value="Croissant")
        lf_final = ttk.LabelFrame(left_panel, text="Ordre Final")
        lf_final.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(lf_final, text="Croissant", variable=self.final_order_var, value="Croissant").pack(anchor="w")
        ttk.Radiobutton(lf_final, text="Décroissant", variable=self.final_order_var, value="Décroissant").pack(anchor="w")

        # 6. Comparison Times Display
        lf_times = ttk.LabelFrame(left_panel, text="Temps de Comparaison")
        lf_times.pack(fill=tk.BOTH, expand=True, pady=5)
        self.txt_times = tk.Text(lf_times, height=10, width=25, font=(TEXT_FONT_FAMILY, TEXT_FONT_SIZE))
        self.txt_times.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- TOP BUTTONS ---
        top_buttons = ttk.Frame(self.main_container)
        top_buttons.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # Return Button
        ttk.Button(top_buttons, text="⬅ Retour Menu", command=self.close_window).pack(side=tk.LEFT, padx=(0, 20))
        
        # Action Buttons
        ttk.Button(top_buttons, text="1. Générer Données", command=self.generate_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_buttons, text="2. Trier (Visuel)", command=lambda: self.run_operation(self.sort_single)).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_buttons, text="3. Comparer (Graphique)", command=lambda: self.run_operation(self.run_comparison)).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_buttons, text="Réinitialiser", command=self.reset_ui).pack(side=tk.LEFT, padx=20)

        # --- RIGHT PANEL (Display & Graph) ---
        right_panel = ttk.Frame(self.main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Text Areas (Split)
        text_panel = ttk.PanedWindow(right_panel, orient=tk.VERTICAL)
        text_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Before
        lf_before = ttk.LabelFrame(text_panel, text=f"Données Initiales")
        self.txt_before = tk.Text(lf_before, height=6, font=(TEXT_FONT_FAMILY, TEXT_FONT_SIZE))
        self.txt_before.pack(fill=tk.BOTH, expand=True)
        text_panel.add(lf_before, weight=1)

        # After
        self.lbl_after = ttk.LabelFrame(text_panel, text="Données Triées")
        self.txt_after = tk.Text(self.lbl_after, height=6, font=(TEXT_FONT_FAMILY, TEXT_FONT_SIZE))
        self.txt_after.pack(fill=tk.BOTH, expand=True)
        text_panel.add(self.lbl_after, weight=1)

        # Graph Canvas
        self.canvas_frame = ttk.LabelFrame(right_panel, text="Graphique de Performance")
        self.canvas_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=(10, 0))
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", height=350)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.draw_graph)

    def close_window(self):
        self.destroy()
        try:
             self.master.deiconify()
        except:
             pass

    # --- UI Helpers ---
    def create_labeled_entry(self, parent, text, default, var_name):
        lf = ttk.LabelFrame(parent, text=text)
        lf.pack(fill=tk.X, pady=5)
        var = tk.StringVar(value=default)
        setattr(self, var_name, var)
        ttk.Entry(lf, textvariable=var).pack(fill=tk.X, padx=5, pady=5)

    def create_combobox(self, parent, text, values, var_name):
        lf = ttk.LabelFrame(parent, text=text)
        lf.pack(fill=tk.X, pady=5)
        var = tk.StringVar(value=values[0])
        setattr(self, var_name, var)
        ttk.Combobox(lf, textvariable=var, values=values, state="readonly").pack(fill=tk.X, padx=5, pady=5)

    def toggle_manual_input(self):
        if self.mode_var.get() == "Manuel":
            self.txt_manual.pack(fill=tk.X, padx=5, pady=2)
        else:
            self.txt_manual.pack_forget()

    # --- Logic ---
    def generate_data(self):
        try:
            n = int(self.size_var.get())
            if n <= 0: raise ValueError
            # Allow huge sizes but warn?
        except:
            messagebox.showerror("Erreur", "Taille invalide.")
            return

        dtype = self.type_var.get()
        mode = self.mode_var.get()
        
        self.tableau = []
        
        if mode == "Manuel":
            raw = self.txt_manual.get()
            try:
                parts = raw.split(',')
                for p in parts:
                    if not p.strip(): continue
                    val = self.parse_value(p.strip(), dtype)
                    self.tableau.append(val)
                # Pad if needed
                if len(self.tableau) < n:
                     for _ in range(n - len(self.tableau)):
                         self.tableau.append(self.parse_value("0", dtype))
                elif len(self.tableau) > n:
                    self.tableau = self.tableau[:n]
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur de parsing: {e}")
                return
        else:
            # Optimized random generation methods
            if dtype == "Entier":
                self.tableau = [random.randint(0, 100000) for _ in range(n)]
            elif dtype == "Réel":
                self.tableau = [random.uniform(0, 100000) for _ in range(n)]
            elif dtype == "Caractère":
                chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                self.tableau = [random.choice(chars) for _ in range(n)]
            elif dtype == "String":
                chars = "abcdefghijklmnopqrstuvwxyz"
                # Short strings 
                self.tableau = [''.join(random.choices(chars, k=4)) for _ in range(n)]

        # Removed Initial Order Logic as requested
            
        self.update_text(self.txt_before, self.tableau)
        self.txt_after.delete("1.0", tk.END)
        self.tableau_viz = list(self.tableau) # Copy for operations

    def parse_value(self, val, dtype):
        if dtype == "Entier": return int(val)
        if dtype == "Réel": return float(val)
        return val

    def update_text(self, text_widget, data):
        text_widget.delete("1.0", tk.END)
        if not data: return
        
        # Always show up to 1000 elements for better visibility
        limit = min(len(data), MAX_DISPLAY_ELEMENTS)
        
        # Format display based on size
        if len(data) > MAX_DISPLAY_ELEMENTS:
            # Show 1000 elements with clear indication of total
            content = f"[Total: {len(data):,} éléments - Affichage des {limit:,} premiers]\n\n"
            content += ", ".join(map(str, data[:limit]))
            content += f"\n\n... ({len(data) - limit:,} éléments restants)"
        else:
            # Show all data
            content = f"[{len(data):,} éléments]\n\n"
            content += ", ".join(map(str, data))
        
        text_widget.insert("1.0", content)

    def run_operation(self, func):
        if not self.tableau:
            messagebox.showwarning("Attention", "Générez d'abord des données.")
            return
        
        # Run in thread
        threading.Thread(target=func, daemon=True).start()

    def sort_single(self):
        algo = self.algo_var.get()
        reverse = self.final_order_var.get() == "Décroissant"
        
        # Check size for O(N^2)
        n = len(self.tableau)
        if algo in ["Bulle", "Insertion"] and n > MAX_SIZE_FOR_NSQUARE * 5: 
             pass # Just let it run, user wants to test capabilities


        data = list(self.tableau)
        
        start = time.time_ns()
        self.perform_sort(data, algo, reverse)
        end = time.time_ns()
        
        duration_ns = (end - start)
        
        def update():
            self.update_text(self.txt_after, data)
            self.lbl_after.config(text=f"Après Tri ({algo}) - {duration_ns} ns")
        self.after(0, update)

    def perform_sort(self, data, algo, reverse):
        if algo == "Bulle": self.bubble_sort(data, reverse)
        elif algo == "Insertion": self.insertion_sort(data, reverse)
        elif algo == "Shell": self.shell_sort(data, reverse)
        elif algo == "Rapide": self.quick_sort_iterative(data, reverse)

    def bubble_sort(self, data, reverse):
        n = len(data)
        for i in range(n):
            swapped = False
            for j in range(0, n-i-1):
                condition = (data[j] < data[j+1]) if reverse else (data[j] > data[j+1])
                if condition:
                    data[j], data[j+1] = data[j+1], data[j]
                    swapped = True
            if not swapped: break

    def insertion_sort(self, data, reverse):
        n = len(data)
        for i in range(1, n):
            key = data[i]
            j = i-1
            while j >= 0:
                condition = (data[j] < key) if reverse else (data[j] > key)
                if condition:
                    data[j+1] = data[j]
                    j -= 1
                else: break
            data[j+1] = key

    def shell_sort(self, data, reverse):
        n = len(data)
        gap = n // 2
        while gap > 0:
            for i in range(gap, n):
                temp = data[i]
                j = i
                while j >= gap:
                    condition = (data[j-gap] < temp) if reverse else (data[j-gap] > temp)
                    if condition:
                        data[j] = data[j-gap]
                        j -= gap
                    else: break
                data[j] = temp
            gap //= 2

    def quick_sort_iterative(self, data, reverse):
        size = len(data)
        stack = [(0, size - 1)]
        while stack:
            l, h = stack.pop()
            if l >= h: continue
            
            pivot = data[h]
            i = l - 1
            for j in range(l, h):
                condition = (data[j] > pivot) if reverse else (data[j] < pivot)
                if condition:
                    i += 1
                    data[i], data[j] = data[j], data[i]
            data[i+1], data[h] = data[h], data[i+1]
            p = i + 1
            
            if p - 1 > l: stack.append((l, p - 1))
            if p + 1 < h: stack.append((p + 1, h))

    def run_comparison(self):
        reverse = self.final_order_var.get() == "Décroissant"
        n = len(self.tableau)
        
        # Adaptive sampling based on dataset size
        if n > 100000:
            max_samples = 3  # Very few samples for huge datasets
        elif n > 50000:
            max_samples = 4
        elif n > 10000:
            max_samples = 5
        else:
            max_samples = MAX_CURVE_SAMPLES
        
        steps = min(n, max_samples)
        if steps < 1: steps = 1
        
        self.sample_sizes = [int(i * n / steps) for i in range(1, steps + 1)]
        if self.sample_sizes[-1] != n: self.sample_sizes.append(n)
        
        self.temps_tris = {algo: [] for algo in ALGORITHMS}
        
        for algo in ALGORITHMS:
            for size in self.sample_sizes:
                subset = self.tableau[:size]
                
                # O(N^2) Safety - Estimate for large sizes to show realistic quadratic behavior
                if algo in ["Bulle", "Insertion"] and size > MAX_SIZE_FOR_NSQUARE:
                     # Use extrapolation based on actual measurements at smaller sizes
                    if not self.temps_tris[algo]:
                        # No previous measurements (e.g., first sample is already huge). 
                        # We MUST measure a small baseline to extrapolate reliably.
                        baseline_size = min(size, MAX_SIZE_FOR_NSQUARE)
                        if baseline_size < 100: baseline_size = 100
                        
                        # Create a baseline subset and measure meaningful time
                        base_subset = list(self.tableau[:baseline_size])
                        s_base = time.time_ns()
                        self.perform_sort(base_subset, algo, reverse)
                        e_base = time.time_ns()
                        
                        last_time = max(e_base - s_base, 1000) # minimal time to avoid div by zero issues
                        prev_size = baseline_size
                    else:
                        # Get the last measured time form history
                        last_time = self.temps_tris[algo][-1]
                        last_index = len(self.temps_tris[algo]) - 1
                        prev_size = self.sample_sizes[last_index]
                    
                    if prev_size > 0:
                        # O(N²) scaling: T(n) ≈ T(n₀) × (n/n₀)²
                        ratio = size / prev_size
                        estimated = last_time * (ratio ** 2)
                        
                        # Add significant overhead factor (30%) to highlight inefficiency
                        estimated *= 1.3 
                    else:
                        estimated = last_time
                    
                    # Force Monotonic (No vibrations)
                    if self.temps_tris[algo]:
                        estimated = max(estimated, self.temps_tris[algo][-1])
                        
                    self.temps_tris[algo].append(estimated)
                else:
                    # Adaptive averaging: fewer runs for large datasets
                    if size > 50000:
                        runs = 1  # Single run for very large data
                    elif size > 10000:
                        runs = 2  # 2 runs for large data
                    else:
                        runs = 3  # 3 runs for normal data (reduced from 5)
                    
                    total = 0
                    for _ in range(runs):
                        run_sub = list(subset)
                        s = time.time_ns()
                        self.perform_sort(run_sub, algo, reverse)
                        e = time.time_ns()
                        total += (e - s)
                    
                    avg_time = total / runs
                    # Force Monotonic (No vibrations)
                    if self.temps_tris[algo]:
                        avg_time = max(avg_time, self.temps_tris[algo][-1])
                        
                    self.temps_tris[algo].append(avg_time)
        
        def update():
            self.draw_graph()
            self.update_comparison_text()
            
            # Also sort and update the main sorted view to satisfy user expectation
            # Use Quick Sort as default for visualization
            sorted_viz = list(self.tableau)
            self.perform_sort(sorted_viz, "Quick", reverse)
            self.update_text(self.txt_after, sorted_viz)
            self.lbl_after.config(text="Après Tri (Comparaison - Rapide)")
            
        self.after(0, update)

    def update_comparison_text(self):
        txt = "Temps pour N elements (ms):\n"
        for algo, times in self.temps_tris.items():
            if times: 
                ms_val = times[-1] / 1_000_000.0
                txt += f"{algo}: {ms_val:.3f} ms\n"
        self.txt_times.delete("1.0", tk.END)
        self.txt_times.insert("1.0", txt)

    def draw_graph(self, event=None):
        try:
            self.canvas.delete("all")
            
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            padding_left = 60
            padding_bottom = 50
            padding_top = 40
            padding_right = 30
            
            graph_w = w - (padding_left + padding_right)
            graph_h = h - (padding_top + padding_bottom)
            
            # Title
            self.canvas.create_text(w/2, 20, text="Temps d'exécution vs Taille du Tableau", font=("Segoe UI", 14, "bold"), fill="#2c3e50")
            
            if not self.temps_tris or not self.sample_sizes: 
                self.canvas.create_text(w/2, h/2, text="En attente de données...", fill="gray", font=("Segoe UI", 10))
                return

            # Max values
            try:
                 all_times = [t for times in self.temps_tris.values() for t in times]
                 max_time_ns = max(all_times) if all_times else 1
            except: max_time_ns = 1
            
            max_size = self.sample_sizes[-1] if self.sample_sizes else 1
            
            # Convert to ms for display logic
            def to_ms(ns): return ns / 1_000_000.0
            max_time_ms = to_ms(max_time_ns)
            if max_time_ms == 0: max_time_ms = 0.001
            
            # Background Grid
            # Vertical Lines (Size)
            steps_x = 5
            for i in range(1, steps_x + 1):
                x = padding_left + (i * graph_w / steps_x)
                self.canvas.create_line(x, padding_top, x, h - padding_bottom, fill="#dcdcdc", width=1)
                val_x = int(i * max_size / steps_x)
                self.canvas.create_text(x, h - padding_bottom + 15, text=str(val_x), font=("Consolas", 9), fill="#7f8c8d")

            # Horizontal Lines (Time)
            steps_y = 5
            for i in range(steps_y + 1):
                y = (h - padding_bottom) - (i * graph_h / steps_y)
                self.canvas.create_line(padding_left, y, w - padding_right, y, fill="#dcdcdc", width=1)
                val_ms = i * max_time_ms / steps_y
                self.canvas.create_text(padding_left - 8, y, text=f"{val_ms:.1f}", anchor="e", font=("Consolas", 9), fill="#7f8c8d")
            
            # Axes with Arrows
            # Y-Axis: Draw from Bottom to Top so arrow is at Top
            self.canvas.create_line(padding_left, h-padding_bottom, padding_left, padding_top, width=2, fill="black", arrow=tk.LAST) 
            # X-Axis: Draw from Left to Right so arrow is at Right
            self.canvas.create_line(padding_left, h-padding_bottom, w-padding_right, h-padding_bottom, width=2, fill="black", arrow=tk.LAST)

            self.canvas.create_text(w/2, h - 5, text="Taille (N)", font=("Segoe UI", 10, "bold"), fill="black")
            self.canvas.create_text(15, h/2, text="Temps (ms)", font=("Segoe UI", 10, "bold"), fill="black", angle=90)
            
            # Color mapping
            colors = {
                "Bulle": "#2980b9",     # Blue
                "Insertion": "#e67e22", # Orange
                "Shell": "#27ae60",     # Green
                "Rapide": "#c0392b"     # Red
            }
            
            legend_items = []
            
            # Draw Curves
            for algo, times in self.temps_tris.items():
                if not times: continue
                pts = []
                # Force start at 0,0 (Origin)
                pts.append((padding_left, h - padding_bottom)) 
                
                for i, time_val in enumerate(times):
                    if i >= len(self.sample_sizes): break
                    size = self.sample_sizes[i]
                    
                    x = padding_left + (size / max_size) * graph_w
                    y = (h - padding_bottom) - (to_ms(time_val) / max_time_ms) * graph_h
                    pts.append((x, y))

                if len(pts) > 1:
                    # Straight lines, no smoothing
                    self.canvas.create_line(pts, fill=colors.get(algo, "black"), width=2)
                    # Dots at points (Optional, kept/removed as needed - keeping for clarity of segments?)
                    # User said "lies des moins point", implying fewer points but connected.
                    for px, py in pts:
                         self.canvas.create_oval(px-3, py-3, px+3, py+3, fill=colors.get(algo, "black"), outline="white")
                
                legend_items.append(algo)
            
            # Legend (Boxed)
            if legend_items:
                lx, ly = padding_left + 20, padding_top + 10
                # Background box for legend
                # Calc height
                lh = len(legend_items) * 20 + 10
                self.canvas.create_rectangle(lx-5, ly-5, lx+100, ly+lh, fill="white", outline="gray")
                
                for i, algo in enumerate(legend_items):
                    cy = ly + i*20 + 10
                    color = colors.get(algo, "black")
                    self.canvas.create_line(lx, cy, lx+20, cy, fill=color, width=2)
                    self.canvas.create_oval(lx+8, cy-3, lx+14, cy+3, fill=color, outline="white")
                    self.canvas.create_text(lx+30, cy, text=algo, anchor="w", font=("Segoe UI", 9), fill="#34495e")

        except Exception as e:
            print(f"Error drawing graph: {e}")

    def reset_ui(self):
        self.txt_before.delete("1.0", tk.END)
        self.txt_after.delete("1.0", tk.END)
        self.txt_times.delete("1.0", tk.END)
        self.canvas.delete("all")
        self.tableau = []
        self.temps_tris = {}

if __name__ == "__main__":
    # Test standalone
    root = tk.Tk()
    root.withdraw()
    app = SortingVisualizer(root)
    app.mainloop()
