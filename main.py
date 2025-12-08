import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# Import advanced parsing tools to handle "3x", "cos x", etc.
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from calculate import calculate

class NewtonRaphsonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Newton-Raphson Method Calculator")
        self.root.geometry("1100x650") # Widened to fit the graph
        
        # Handle window close button
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        
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

    def close(self):
        """Handle window close event"""
        self.root.quit()
        self.root.destroy()

    def calculate(self):
        # Call the calculate function from calculate.py
        calculate(self.tree, self.func_entry, self.guess_entry, self.stop_entry, 
                 self.final_result_var, self.ax, self.canvas, self.figure)

if __name__ == "__main__":
    root = tk.Tk()
    app = NewtonRaphsonApp(root)
    root.mainloop()