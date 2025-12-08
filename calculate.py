import sympy as sp
import numpy as np
from tkinter import messagebox

def calculate(tree, func_entry, guess_entry, stop_entry, final_result_var, ax, canvas, figure):
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    
    # 1. Clear previous data
    for item in tree.get_children():
        tree.delete(item)
    final_result_var.set("")
    ax.clear()
    canvas.draw()

    # 2. Get Inputs
    try:
        func_str = func_entry.get()
        x_curr = float(guess_entry.get())
        stop_percent = float(stop_entry.get())
        max_iter = 100 
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
                final_result_var.set("Failed (Derivative = 0)")
                return

            x_next = x_curr - (f_val / df_val)

            if x_next != 0:
                ea = abs((x_next - x_curr) / x_next) * 100
            else:
                ea = abs(x_next - x_curr) * 100

            tree.insert("", "end", values=(
                i+1, 
                f"{x_curr:.6f}", 
                f"{f_val:.6f}", 
                f"{df_val:.6f}", 
                f"{ea:.4f}%"
            ))

            if ea < stop_percent:
                final_result_var.set(f"Root found: {x_next:.6f} at Iteration {i+1}")
                plot_data.append(x_next) # Add final point
                # Get the last item in the tree and tag it as root
                last_item = tree.get_children()[-1]
                tree.item(last_item, tags=('root',))
                plot_graph(f, plot_data, ax, canvas, figure)
                return
            
            x_curr = x_next
        
        final_result_var.set(f"Did not converge within {max_iter} iterations.")
        plot_graph(f, plot_data, ax, canvas, figure)

    except Exception as e:
         messagebox.showerror("Calculation Error", f"An error occurred: {e}")


def plot_graph(f, points, ax, canvas, figure):
    # Plot the function and iteration points
    ax.clear()
    
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
        
        ax.plot(t, y, 'b-', label='f(x)', linewidth=1.5)
        ax.axhline(0, color='black', linewidth=1) # X-axis
        
        # Plot Iteration Points
        # Evaluate y for the specific points
        pts_arr = np.array(points)
        y_pts = f(pts_arr)
        if np.isscalar(y_pts): y_pts = np.full_like(pts_arr, y_pts)

        ax.plot(pts_arr, y_pts, 'g.', label='Iterations', markersize=8, alpha=0.6)
        
        # Highlight Result (Last point)
        ax.plot(points[-1], y_pts[-1], 'r*', label='Root', markersize=12)

        ax.set_title("Function Visualization")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)
        figure.tight_layout()
        canvas.draw()
        
    except Exception as e:
        print(f"Plotting Error: {e}")
