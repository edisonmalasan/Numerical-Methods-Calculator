import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# Import advanced parsing tools to handle "3x", "cos x", etc.
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

class NewtonRaphsonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Newton-Raphson Method Calculator")
        self.root.geometry("1100x650") # Widened to fit the graph
        
        # Configure grid weights to make it resizeable
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)

        # --- Styles ---
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Bold.TLabel", font=('Arial', 10, 'bold'))
        style.configure("Result.TLabel", font=('Arial', 12, 'bold'), foreground="blue")

        # ==========================
        # 1. TOP INPUT SECTION
        # ==========================
        input_frame = ttk.Frame(root, padding="20")
        input_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Row 0: Function
        ttk.Label(input_frame, text="Function:", style="Bold.TLabel").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.func_entry = ttk.Entry(input_frame, font=('Arial', 11))
        self.func_entry.grid(row=0, column=1, columnspan=5, sticky="ew", padx=5, pady=5)
        self.func_entry.insert(0, "e**x + cos x - 3x - 6") # Updated default value to test user case

        # Row 1: Initial Guess, Stopping %, Calculate Button
        ttk.Label(input_frame, text="Initial Guess:", style="Bold.TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=20)
        self.guess_entry = ttk.Entry(input_frame, width=15, font=('Arial', 11))
        self.guess_entry.grid(row=1, column=1, sticky="w", padx=5, pady=20)
        self.guess_entry.insert(0, "1")

        ttk.Label(input_frame, text="Stopping Percentage:", style="Bold.TLabel").grid(row=1, column=2, sticky="e", padx=5, pady=20)
        self.stop_entry = ttk.Entry(input_frame, width=15, font=('Arial', 11))
        self.stop_entry.grid(row=1, column=3, sticky="w", padx=5, pady=20)
        self.stop_entry.insert(0, "0.01") # Default 0.01%

        # Calculate Button (styled to look a bit thicker like the sketch)
        self.calc_btn = tk.Button(input_frame, text="Calculate", font=('Arial', 10, 'bold'), 
                                  bg="#e1e1e1", command=self.calculate, relief="raised", bd=3)
        self.calc_btn.grid(row=1, column=4, sticky="ew", padx=20, pady=20, ipadx=10)

        # ==========================
        # 2. OUTPUT SECTION (Table + Graph)
        # ==========================
        ttk.Label(root, text="Output:", style="Bold.TLabel").grid(row=2, column=0, sticky="nw", padx=20)
        
        # Container for both Table and Graph
        output_container = ttk.Frame(root)
        output_container.grid(row=2, column=1, sticky="nsew", padx=(0, 20))
        output_container.columnconfigure(0, weight=1) # Table weight
        output_container.columnconfigure(1, weight=1) # Graph weight
        output_container.rowconfigure(0, weight=1)

        # --- Left Side: Table ---
        table_frame = ttk.Frame(output_container, padding=(0, 0, 10, 0))
        table_frame.grid(row=0, column=0, sticky="nsew")

        scroll = ttk.Scrollbar(table_frame, orient="vertical")
        columns = ("Iter", "x_current", "f(x)", "f'(x)", "Error %")
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', yscrollcommand=scroll.set, height=10)
        
        self.tree.heading("Iter", text="Iter")
        self.tree.heading("x_current", text="x (Root)")
        self.tree.heading("f(x)", text="f(x)")
        self.tree.heading("f'(x)", text="f'(x)")
        self.tree.heading("Error %", text="Error %")

        self.tree.column("Iter", width=40, anchor="center")
        self.tree.column("x_current", width=80, anchor="center")
        self.tree.column("f(x)", width=80, anchor="center")
        self.tree.column("f'(x)", width=80, anchor="center")
        self.tree.column("Error %", width=80, anchor="center")

        scroll.config(command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # --- Right Side: Graph ---
        graph_frame = ttk.Frame(output_container, relief="sunken", borderwidth=1)
        graph_frame.grid(row=0, column=1, sticky="nsew")

        self.figure, self.ax = plt.subplots(figsize=(4, 3), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # ==========================
        # 3. FINAL RESULT SECTION
        # ==========================
        final_frame = ttk.Frame(root, padding="20")
        final_frame.grid(row=3, column=0, columnspan=2, sticky="ew")

        ttk.Label(final_frame, text="Final:", style="Bold.TLabel").pack(side="left", padx=(0, 10))
        self.final_result_var = tk.StringVar()
        self.final_label = ttk.Label(final_frame, textvariable=self.final_result_var, style="Result.TLabel", relief="sunken", anchor="center")
        self.final_label.pack(side="left", fill="x", expand=True, ipady=5)

    def calculate(self):
        # 1. Clear previous data
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.final_result_var.set("")
        self.ax.clear() # Clear graph
        self.canvas.draw()

        # 2. Get Inputs
        try:
            func_str = self.func_entry.get()
            x_curr = float(self.guess_entry.get())
            stop_percent = float(self.stop_entry.get())
            max_iter = 50 
        except ValueError:
            messagebox.showerror("Input Error", "Please check your numbers. Ensure Guess and Percentage are valid numbers.")
            return

        # 3. Parse Function
        x = sp.symbols('x')
        try:
            # Handle user convenience: "3x" -> "3*x", "e^x" -> "exp(x)"
            # Replace basic caret for power if used
            func_str_clean = func_str.replace('^', '**')
            
            # Use advanced parsing transformations to handle implicit multiplication (3x) and functions (cos x)
            transformations = (standard_transformations + (implicit_multiplication_application,))
            f_expr = parse_expr(func_str_clean, transformations=transformations)
            
            # Important: 'e' is parsed as a Symbol by default, not the constant 2.718...
            # We explicitly substitute the symbol 'e' with SymPy's Euler number 'E'
            f_expr = f_expr.subs(sp.Symbol('e'), sp.E)
            
            df_expr = sp.diff(f_expr, x)
            f = sp.lambdify(x, f_expr, 'numpy')
            df = sp.lambdify(x, df_expr, 'numpy')
        except Exception as e:
            messagebox.showerror("Syntax Error", f"Could not parse function: {e}\nTry using standard syntax like 3*x or cos(x).")
            return

        # 4. Iteration Loop
        plot_data = [] # Store points for plotting
        
        try:
            for i in range(max_iter):
                f_val = f(x_curr)
                df_val = df(x_curr)
                
                # Store for plotting
                plot_data.append(x_curr)

                if df_val == 0:
                    messagebox.showerror("Math Error", "Derivative is zero. Division by zero occurred.")
                    self.final_result_var.set("Failed (Derivative = 0)")
                    return

                x_next = x_curr - (f_val / df_val)

                if x_next != 0:
                    ea = abs((x_next - x_curr) / x_next) * 100
                else:
                    ea = abs(x_next - x_curr) * 100

                self.tree.insert("", "end", values=(
                    i+1, 
                    f"{x_curr:.6f}", 
                    f"{f_val:.6f}", 
                    f"{df_val:.6f}", 
                    f"{ea:.4f}%"
                ))

                if ea < stop_percent:
                    self.final_result_var.set(f"Root found: {x_next:.6f} at Iteration {i+1}")
                    plot_data.append(x_next) # Add final point
                    self.plot_graph(f, plot_data)
                    return
                
                x_curr = x_next
            
            self.final_result_var.set(f"Did not converge within {max_iter} iterations.")
            self.plot_graph(f, plot_data)

        except Exception as e:
             messagebox.showerror("Calculation Error", f"An error occurred: {e}")

    def plot_graph(self, f, points):
        self.ax.clear()
        
        if not points: return

        # Determine Range for Plotting
        # We want to see the root and where we started
        min_x = min(points)
        max_x = max(points)
        padding = (max_x - min_x) * 0.5
        if padding == 0: padding = 1.0
        
        t = np.linspace(min_x - padding, max_x + padding, 400)
        
        try:
            # Plot Function Line
            y = f(t)
            # Handle constant functions returning scalar
            if np.isscalar(y): y = np.full_like(t, y)
            
            self.ax.plot(t, y, 'b-', label='f(x)', linewidth=1.5)
            self.ax.axhline(0, color='black', linewidth=1) # X-axis
            
            # Plot Iteration Points
            # Evaluate y for the specific points
            pts_arr = np.array(points)
            y_pts = f(pts_arr)
            if np.isscalar(y_pts): y_pts = np.full_like(pts_arr, y_pts)

            self.ax.plot(pts_arr, y_pts, 'g.', label='Iterations', markersize=8, alpha=0.6)
            
            # Highlight Result (Last point)
            self.ax.plot(points[-1], y_pts[-1], 'r*', label='Root', markersize=12)

            self.ax.set_title("Function Visualization")
            self.ax.legend()
            self.ax.grid(True, linestyle='--', alpha=0.6)
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Plotting Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NewtonRaphsonApp(root)
    root.mainloop()