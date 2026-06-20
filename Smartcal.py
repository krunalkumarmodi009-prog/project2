from tkinter import *
from tkinter import ttk, messagebox
import math
import statistics
import sqlite3
from datetime import datetime, date, timedelta

# Initialize database
def init_db():
    conn = sqlite3.connect("calculator_history.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS history
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       calculation TEXT,
                       result TEXT,
                       timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

root = Tk()
root.title("🧮 Modern Calculator Suite")
root.geometry("400x600")  
root.configure(bg="#f0f0f0")
root.minsize(1000,700)  
history_data = []

# =========================
# THEME VARIABLES
# =========================
current_theme = "dark"  # "dark" or "light"

# Theme colors
THEMES = {
    "dark": {
        "bg": "#1a1a2e",
        "fg": "#ffffff",
        "accent": "#16213e",
        "button_bg": "#2d2d44",
        "button_fg": "#ffffff",
        "display_bg": "#0f0f1a",
        "display_fg": "#00ff88",
        "sidebar_bg": "#0f0f1a",
        "sidebar_fg": "#ffffff",
        "operator_bg": "#e94560",
        "operator_fg": "#ffffff",
        "function_bg": "#533483",
        "function_fg": "#ffffff",
        "number_bg": "#2d2d44",
        "number_fg": "#ffffff",
        "equal_bg": "#00d4ff",
        "equal_fg": "#1a1a2e",
    },
    "light": {
        "bg": "#eac0c0",
        "fg": "#1a1a2e",
        "accent": "#e8e0e0",
        "button_bg": "#f7efef",
        "button_fg": "#1a1a2e",
        "display_bg": "#ebe6e6",
        "display_fg": "#1a1a2e",
        "sidebar_bg": "#2c3e50",
        "sidebar_fg": "#f1eded",
        "operator_bg": "#e94560",
        "operator_fg": "#ffffff",
        "function_bg": "#6c5ce7",
        "function_fg": "#ffffff",
        "number_bg": "#ffffff",
        "number_fg": "#1a1a2e",
        "equal_bg": "#00b894",
        "equal_fg": "#ffffff",
    }
}

# =========================
# PAGE MANAGEMENT
# =========================

pages = {}

def show_page(name):
    for page in pages.values():
        page.pack_forget()
    pages[name].pack(fill="both", expand=True)

# =========================
# SIDEBAR
# =========================

sidebar = Frame(root, bg="#0f0f1a", width=200)
sidebar.pack(side=LEFT, fill=Y)
sidebar.pack_propagate(False)

content = Frame(root, bg="#1a1a2e")
content.pack(side=RIGHT, fill=BOTH, expand=True)

# =========================
# THEME TOGGLE (Sliding Switch)
# =========================

def toggle_theme():
    global current_theme
    if current_theme == "dark":
        current_theme = "light"
        apply_theme("light")
    else:
        current_theme = "dark"
        apply_theme("dark")

def apply_theme(theme_name):
    theme = THEMES[theme_name]
    
    # Update root
    root.configure(bg=theme["bg"])
    content.configure(bg=theme["bg"])
    sidebar.configure(bg=theme["sidebar_bg"])
    
    # Update sidebar buttons
    for widget in sidebar.winfo_children():
        if isinstance(widget, Button) and widget.cget("text") not in ["🌓", "🌙", "☀️"]:
            widget.configure(bg=theme["sidebar_bg"], fg=theme["sidebar_fg"])
    
    # Update all pages
    for page_name, page in pages.items():
        page.configure(bg=theme["bg"])
        update_widget_colors(page, theme)
    
    # Update theme toggle button
    toggle_btn.configure(bg=theme["sidebar_bg"], fg=theme["sidebar_fg"])
    
    # Update display
    try:
        display.configure(bg=theme["display_bg"], fg=theme["display_fg"])
    except:
        pass
    
    # Update calculator buttons
    update_calculator_buttons(theme)

def update_widget_colors(widget, theme):
    """Recursively update colors for all widgets"""
    try:
        if isinstance(widget, (Frame, LabelFrame)):
            widget.configure(bg=theme["bg"])
        elif isinstance(widget, Label):
            widget.configure(bg=theme["bg"], fg=theme["fg"])
        elif isinstance(widget, Button):
            # Skip if it's already styled differently
            pass
        elif isinstance(widget, (Entry, Text)):
            widget.configure(bg=theme["display_bg"], fg=theme["display_fg"])
        elif isinstance(widget, Listbox):
            widget.configure(bg=theme["display_bg"], fg=theme["display_fg"])
    except:
        pass
    
    for child in widget.winfo_children():
        update_widget_colors(child, theme)

def update_calculator_buttons(theme):
    """Update calculator button colors based on theme"""
    for widget in btn_frame.winfo_children():
        if isinstance(widget, Button):
            text = widget.cget("text")
            if text in ['+', '-', '*', '/', '=', '%']:
                widget.configure(bg=theme["operator_bg"], fg=theme["operator_fg"])
            elif text in ['√', 'x²', 'x³', 'xʸ', '10ˣ', 'eˣ', 'ln', 'log', 'π', 'e', '(', ')']:
                widget.configure(bg=theme["function_bg"], fg=theme["function_fg"])
            else:
                widget.configure(bg=theme["number_bg"], fg=theme["number_fg"])

# Theme toggle button (sliding switch style)
theme_frame = Frame(sidebar, bg="#0f0f1a")
theme_frame.pack(pady=10)

toggle_btn = Button(theme_frame, text="🌓", font=("Segoe UI", 16), 
                    bg="#0f0f1a", fg="white", bd=0,
                    command=toggle_theme, relief="flat")
toggle_btn.pack()

# Theme label
theme_label = Label(sidebar, text="Dark Mode", font=("Segoe UI", 9), 
                    bg="#0f0f1a", fg="#888888")
theme_label.pack()

def update_theme_label():
    if current_theme == "dark":
        theme_label.config(text="Dark Mode")
        toggle_btn.config(text="🌙")
    else:
        theme_label.config(text="Light Mode")
        toggle_btn.config(text="☀️")

# =========================
# CALCULATOR PAGE 
# =========================

calc_page = Frame(content, bg="white")
pages["Basic Calculator"] = calc_page

display = Entry(calc_page, font=("Consolas", 36), justify="right", bg="white", 
                relief="sunken", bd=2)
display.pack(fill=X, padx=20, pady=20)

btn_frame = Frame(calc_page, bg="white")
btn_frame.pack()

# ========== FLAGS FOR CALCULATOR BEHAVIOR ==========
just_calculated = False  # True when a calculation just happened
waiting_for_operator = True  # True when waiting for operator after result

def press(value):
    global just_calculated, waiting_for_operator
    
    current = display.get()
    
    # Handle parentheses - they don't trigger operator waiting
    if value == '(':
        display.insert(END, '(')
        display.focus_set()
        return
    elif value == ')':
        display.insert(END, ')')
        display.focus_set()
        return
    
    # If value is an operator (+, -, *, /)
    if value in ['+', '-', '*', '/']:
        # Clear the waiting_for_operator flag and add operator
        if waiting_for_operator:
            waiting_for_operator = False
            just_calculated = False
            display.insert(END, value)
        else:
            # Normal operator addition
            if current and current[-1] not in ['+', '-', '*', '/']:
                display.insert(END, value)
            elif current and current[-1] in ['+', '-', '*', '/']:
                display.delete(END-1, END)
                display.insert(END, value)
        display.focus_set()
        return
    
    # If value is a number or decimal point
    if value.isdigit() or value == '.':
        # CHECK: If waiting_for_operator is True, show error
        if waiting_for_operator:
            messagebox.showerror("Invalid Operation", 
                               "Please use an operator (+, -, ×, ÷) first!\n\n"
                               "After getting a result, you must press an operator\n"
                               "before typing a new number.")
            display.focus_set()
            return
        
        # Add the number/decimal
        if value == '.':
            # Prevent multiple decimals in current number
            current = display.get()
            last_number = current.split('+')[-1].split('-')[-1].split('*')[-1].split('/')[-1]
            if '.' not in last_number:
                display.insert(END, '.')
        else:
            display.insert(END, value)
        
        just_calculated = False
        display.focus_set()
        return
    
    # Handle special functions (%, √, x², n!)
    if value == "%":
        try:
            current = display.get()
            if current:
                result = float(eval(current)) / 100
                display.delete(0, END)
                display.insert(0, str(result))
                just_calculated = True
                waiting_for_operator = True  # Now waiting for operator
        except:
            pass
    elif value == "√":
        try:
            current = float(display.get())
            display.delete(0, END)
            display.insert(0, str(math.sqrt(current)))
            just_calculated = True
            waiting_for_operator = True
        except:
            pass
    elif value == "x²":
        try:
            current = float(display.get())
            display.delete(0, END)
            display.insert(0, str(current ** 2))
            just_calculated = True
            waiting_for_operator = True
        except:
            pass
    elif value == "n!":
        try:
            current = int(float(display.get()))
            display.delete(0, END)
            display.insert(0, str(math.factorial(current)))
            just_calculated = True
            waiting_for_operator = True
        except:
            pass
    
    display.focus_set()

def clear():
    """Clear everything - only clear button does this"""
    global just_calculated, waiting_for_operator
    display.delete(0, END)
    just_calculated = False
    waiting_for_operator = False  # Reset to False (can type numbers freely)
    display.focus_set()

def backspace():
    """Remove last character - works on any character including parentheses"""
    global just_calculated, waiting_for_operator
    current = display.get()
    
    # Don't allow backspace if just calculated a result (waiting_for_operator)
    if waiting_for_operator and current:
        messagebox.showwarning("Cannot Backspace", 
                             "Cannot modify result. Press Clear (C) to start over,\n"
                             "or press an operator (+, -, ×, ÷) to continue.")
        display.focus_set()
        return
    
    if current:
        display.delete(0, END)
        display.insert(0, current[:-1])
        # Reset flags when display becomes empty
        if not display.get():
            just_calculated = False
            waiting_for_operator = False
    display.focus_set()

def calculate():
    global just_calculated, waiting_for_operator
    try:
        expr = display.get()
        expr = expr.replace("×", "*").replace("÷", "/")
        result = eval(expr)
        calc_text = f"{expr} = {result}"
        history_data.append(calc_text)
        
        conn = sqlite3.connect("calculator_history.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO history (calculation, result, timestamp) VALUES (?, ?, ?)",
                      (expr, str(result), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        
        display.delete(0, END)
        display.insert(0, str(result))
        just_calculated = True
        waiting_for_operator = True  # After result, must use operator first
        refresh_history()
        display.focus_set()
    except Exception as e:
        messagebox.showerror("Calculator Error", str(e))
        display.focus_set()

# =========================
# BUTTON LAYOUT - BASIC CALCULATOR WITH PARENTHESES
# =========================

# Only basic calculator buttons + parentheses + backspace
buttons = [
    # Row 0: Parentheses and Clear
    ("(", 0, 0), (")", 0, 1), ("AC", 0, 2), ("C", 0, 3),
    # Row 1: Numbers and operators
    ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
    # Row 2: Numbers and operators
    ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
    # Row 3: Numbers and operators
    ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
    # Row 4: Numbers and operators
    ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("+", 4, 3),
    # Row 5: Additional functions
    ("%", 5, 0), ("√", 5, 1), ("x²", 5, 2), ("n!", 5, 3),
]

# Create buttons with different styles
for text, r, c in buttons:
    # Determine button style based on text type
    if text in ['+', '-', '*', '/', '=', '%']:
        # Operator buttons - orange/red
        bg_color = "#e94560"
        fg_color = "#ffffff"
        font_size = 14
    elif text in ['(', ')', '√', 'x²', 'n!']:
        # Function buttons - purple
        bg_color = "#533483"
        fg_color = "#ffffff"
        font_size = 12
    elif text in ['AC', 'C']:
        # Clear buttons - red
        bg_color = "#ff6b6b"
        fg_color = "#ffffff"
        font_size = 12
    else:
        # Number buttons - dark
        bg_color = "#2d2d44"
        fg_color = "#ffffff"
        font_size = 14
    
    # Command for button
    if text == "=":
        cmd = calculate
    elif text == "AC":
        cmd = clear
    elif text == "C":
        cmd = lambda: display.delete(0, END)
    else:
        cmd = lambda t=text: press(t)
    
    btn = Button(btn_frame, text=text, width=7, height=3, 
                font=("Consolas", font_size, "bold"),
                command=cmd, relief="raised", bd=2 ,
                bg=bg_color, fg=fg_color,
                activebackground=bg_color, activeforeground=fg_color)
    btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")

# Configure grid weights for responsive layout
for i in range(6):
    btn_frame.grid_rowconfigure(i, weight=1)
for i in range(4):
    btn_frame.grid_columnconfigure(i, weight=1)

# ========== CONTROL FRAME (Backspace button) ==========
ctrl_frame = Frame(calc_page, bg="white")
ctrl_frame.pack(pady=10)

Button(ctrl_frame, text="⌫ Backspace", command=backspace, bg="#e74c3c", fg="white", 
       font=("Consolas", 12), width=16).pack(side=LEFT, padx=5)

# ========== KEYBOARD HANDLER (UPDATED WITH PARENTHESES) ==========
def calculator_keyboard(event):
    """Keyboard handler for calculator with operator-first requirement"""
    global just_calculated, waiting_for_operator
    key = event.keysym
    char = event.char
    
    # Get current display text
    current = display.get()
    
    # Numbers 0-9
    if char.isdigit():
        # CHECK: If waiting_for_operator is True, show error
        if waiting_for_operator:
            messagebox.showerror("Invalid Operation", 
                               "Please use an operator (+, -, *, /) first!\n\n"
                               "After getting a result, you must press an operator\n"
                               "before typing a new number.")
            return 'break'
        
        display.insert(END, char)
        return 'break'
    
    # Decimal point
    elif char == '.':
        if waiting_for_operator:
            messagebox.showerror("Invalid Operation", 
                               "Please use an operator (+, -, *, /) first!\n\n"
                               "After getting a result, you must press an operator\n"
                               "before typing a decimal point.")
            return 'break'
        
        # Prevent multiple decimals in current number
        current = display.get()
        last_number = current.split('+')[-1].split('-')[-1].split('*')[-1].split('/')[-1]
        if '.' not in last_number:
            display.insert(END, '.')
        return 'break'
    
    # Parentheses
    elif char == '(' or char == ')':
        display.insert(END, char)
        return 'break'
    
    # Operators + - * /
    elif char in ['+', '-']:
        # Clear the waiting_for_operator flag and add operator
        if waiting_for_operator:
            waiting_for_operator = False
            just_calculated = False
            display.insert(END, char)
        else:
            # Normal operator handling
            if current and current[-1] not in ['+', '-', '*', '/']:
                display.insert(END, char)
            elif current and current[-1] in ['+', '-', '*', '/']:
                display.delete(END-1, END)
                display.insert(END, char)
        return 'break'
    
    elif char == '*':
        if waiting_for_operator:
            waiting_for_operator = False
            just_calculated = False
            display.insert(END, char)
        else:
            if current and current[-1] not in ['+', '-', '*', '/']:
                display.insert(END, char)
            elif current and current[-1] in ['+', '-', '*', '/']:
                display.delete(END-1, END)
                display.insert(END, char)
        return 'break'
    
    elif char == '/':
        if waiting_for_operator:
            waiting_for_operator = False
            just_calculated = False
            display.insert(END, char)
        else:
            if current and current[-1] not in ['+', '-', '*', '/']:
                display.insert(END, char)
            elif current and current[-1] in ['+', '-', '*', '/']:
                display.delete(END-1, END)
                display.insert(END, char)
        return 'break'
    
    # 'x' key for multiplication
    elif char.lower() == 'x':
        if waiting_for_operator:
            waiting_for_operator = False
            just_calculated = False
            display.insert(END, '*')
        else:
            if current and current[-1] not in ['+', '-', '*', '/']:
                display.insert(END, '*')
        return 'break'
    
    # ENTER KEY - CALCULATE
    elif key == 'Return' or key == 'KP_Enter':
        calculate()
        return 'break'
    
    # Backspace - only removes characters, but not after result
    elif key == 'BackSpace':
        if waiting_for_operator and current:
            messagebox.showwarning("Cannot Backspace", 
                                 "Cannot modify result. Press Clear (C) to start over,\n"
                                 "or press an operator (+, -, *, /) to continue.")
            return 'break'
        
        if current:
            display.delete(len(current)-1, END)
            # Reset flags if display becomes empty
            if not display.get():
                just_calculated = False
                waiting_for_operator = False
        return 'break'
    
    # Escape key - Clear
    elif key == 'Escape':
        clear()
        return 'break'
    
    # Percentage
    elif char == '%':
        try:
            if current:
                result = eval(current) / 100
                display.delete(0, END)
                display.insert(0, str(result))
                just_calculated = True
                waiting_for_operator = True
        except:
            pass
        return 'break'
    
    # Square root (r key)
    elif key == 'r' or key == 'R':
        try:
            value = float(current) if current else 0
            display.delete(0, END)
            display.insert(0, str(math.sqrt(value)))
            just_calculated = True
            waiting_for_operator = True
        except:
            pass
        return 'break'
    
    # Square (s key)
    elif key == 's' or key == 'S':
        try:
            value = float(current) if current else 0
            display.delete(0, END)
            display.insert(0, str(value ** 2))
            just_calculated = True
            waiting_for_operator = True
        except:
            pass
        return 'break'
    
    # Factorial (f key)
    elif key == 'f' or key == 'F':
        try:
            value = int(float(current)) if current else 0
            display.delete(0, END)
            display.insert(0, str(math.factorial(value)))
            just_calculated = True
            waiting_for_operator = True
        except:
            pass
        return 'break'
    
    return None

# Bind keyboard to calculator page
calc_page.bind('<Key>', calculator_keyboard)

# Focus the display
display.focus_set()

# Keep focus on display when clicking buttons
def set_focus():
    display.focus_set()

calc_page.bind('<Button-1>', lambda e: set_focus())
display.bind('<Button-1>', lambda e: set_focus())

# =========================
# SCIENTIFIC PAGE 
# =========================

sci_page = Frame(content, bg="#1a1a2e")
pages["Scientific"] = sci_page

sci_main_frame = Frame(sci_page, bg="#1a1a2e")
sci_main_frame.pack(expand=True, fill=BOTH, padx=20, pady=20)

# Header
Label(sci_main_frame, text="🔬 SCIENTIFIC CALCULATOR", 
      font=("Consolas", 18, "bold"), 
      bg="#1a1a2e", fg="#00ff88").pack(pady=(0, 10))

# Display Frame
display_frame = Frame(sci_main_frame, bg="#1a1a2e")
display_frame.pack(fill=X, pady=(0, 15))

sci_entry = Entry(display_frame, font=("Consolas", 28), justify="right", 
                  relief="sunken", bd=3, bg="#0f0f1a", fg="#00ff88",
                  insertbackground="#00ff88")
sci_entry.pack(fill=X, ipady=8)

sci_result = Label(display_frame, text="", font=("Consolas", 18), 
                   bg="#0f0f1a", fg="#00d4ff", anchor="e", height=2)
sci_result.pack(fill=X, pady=(5, 0))

# Separator
ttk.Separator(sci_main_frame, orient='horizontal').pack(fill=X, pady=10)

# DEFINE ALL FUNCTIONS FIRST (BEFORE CREATING BUTTONS)

def clear_sci():
    """Clear all scientific calculator fields"""
    sci_entry.delete(0, END)
    sci_result.config(text="")
    sci_entry.focus_set()

def backspace_sci():
    """Backspace for scientific calculator"""
    current = sci_entry.get()
    if current:
        sci_entry.delete(len(current) - 1, END)
    sci_entry.focus_set()

def add_to_entry(value):
    """Add value to scientific entry"""
    sci_entry.insert(END, value)
    sci_entry.focus_set()

def sci_calc(fn):
    """Scientific calculation function"""
    try:
        x = float(sci_entry.get())
        if fn == "sin":
            result = math.sin(math.radians(x))
        elif fn == "cos":
            result = math.cos(math.radians(x))
        elif fn == "tan":
            result = math.tan(math.radians(x))
        elif fn == "asin":
            result = math.degrees(math.asin(x)) if -1 <= x <= 1 else "Domain Error"
        elif fn == "acos":
            result = math.degrees(math.acos(x)) if -1 <= x <= 1 else "Domain Error"
        elif fn == "atan":
            result = math.degrees(math.atan(x))
        elif fn == "sqrt":
            result = math.sqrt(x) if x >= 0 else "Domain Error"
        elif fn == "square":
            result = x * x
        elif fn == "cube":
            result = x ** 3
        elif fn == "log":
            result = math.log10(x) if x > 0 else "Domain Error"
        elif fn == "ln":
            result = math.log(x) if x > 0 else "Domain Error"
        elif fn == "exp":
            result = math.exp(x)
        elif fn == "10x":
            result = 10 ** x
        elif fn == "pi":
            result = math.pi
        elif fn == "euler":
            result = math.e
        sci_result.config(text=f"Result = {result}")
        # Store result in entry for further calculations
        sci_entry.delete(0, END)
        sci_entry.insert(0, str(result))
    except ValueError:
        # If entry is empty or not a number, treat as expression
        try:
            expr = sci_entry.get()
            # Replace display symbols
            expr = expr.replace("×", "*").replace("÷", "/")
            result = eval(expr)
            sci_result.config(text=f"Result = {result}")
            sci_entry.delete(0, END)
            sci_entry.insert(0, str(result))
        except Exception as e:
            messagebox.showerror("Error", f"Invalid Input: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Invalid Input: {str(e)}")

def sci_evaluate():
    """Evaluate scientific calculator expression"""
    try:
        expr = sci_entry.get()
        # Replace display symbols with Python operators
        expr = expr.replace("×", "*").replace("÷", "/")
        result = eval(expr)
        sci_result.config(text=f"= {result}", fg="#00ff88")
        # Store result in entry for further calculations
        sci_entry.delete(0, END)
        sci_entry.insert(0, str(result))
    except Exception as e:
        messagebox.showerror("Error", f"Invalid Expression: {str(e)}")
        sci_result.config(text="Error", fg="#ff6b6b")

# CREATE SCIENTIFIC BUTTONS GRID

sci_grid_frame = Frame(sci_main_frame, bg="#1a1a2e")
sci_grid_frame.pack(pady=5)

# Row 1: Trigonometry functions
trig_buttons = [
    ("sin", "sin"), ("cos", "cos"), ("tan", "tan"),
    ("asin", "asin"), ("acos", "acos"), ("atan", "atan"),
    ("π", "pi"),
    ]

row, col = 0, 0
for text, func in trig_buttons:
    btn = Button(sci_grid_frame, text=text.upper(), width=6, height=2, 
                font=("Consolas", 9, "bold"),
                command=lambda f=func: sci_calc(f),
                bg="#6c5ce7", fg="#ffffff",
                activebackground="#7d6ff0", activeforeground="#ffffff",
                relief="raised", bd=2)
    btn.grid(row=row, column=col, padx=2, pady=2)
    col += 1
    if col > 6:
        col = 0
        row += 1

# Row 2: Scientific functions
sci_func_buttons = [
    ("√", "sqrt"), ("x²", "square"), ("x³", "cube"),
    ("log", "log"), ("ln", "ln"), ("eˣ", "exp"),
    ("10ˣ", "10x"), 
]

row += 1
col = 0
for text, func in sci_func_buttons:
    btn = Button(sci_grid_frame, text=text, width=6, height=2, 
                font=("Consolas", 9, "bold"),
                command=lambda f=func: sci_calc(f),
                bg="#533483", fg="#ffffff",
                activebackground="#6c5ce7", activeforeground="#ffffff",
                relief="raised", bd=2)
    btn.grid(row=row, column=col, padx=2, pady=2)
    col += 1
    if col > 6:
        col = 0
        row += 1

# Row 3: Parentheses and control buttons
row += 1
col = 0
paren_buttons = [
    ("e", "euler"),("(", "("), (")", ")"), ("C", "clear"), ("⌫", "backspace")
]

for text, func in paren_buttons:
    if func == "clear":
        btn = Button(sci_grid_frame, text=text, width=6, height=2, 
                    font=("Consolas", 9, "bold"),
                    command=clear_sci,
                    bg="#ff6b6b", fg="#ffffff",
                    activebackground="#ff7a7a", activeforeground="#ffffff",
                    relief="raised", bd=2)
    elif func == "backspace":
        btn = Button(sci_grid_frame, text=text, width=6, height=2, 
                    font=("Consolas", 9, "bold"),
                    command=backspace_sci,
                    bg="#e94560", fg="#ffffff",
                    activebackground="#f05a6e", activeforeground="#ffffff",
                    relief="raised", bd=2)
    else:
        btn = Button(sci_grid_frame, text=text, width=6, height=2, 
                    font=("Consolas", 9, "bold"),
                    command=lambda t=text: add_to_entry(t),
                    bg="#2d2d44", fg="#ffffff",
                    activebackground="#3d3d54", activeforeground="#ffffff",
                    relief="raised", bd=2)
    btn.grid(row=row, column=col, padx=2, pady=2)
    col += 1

# NUMBER PAD

number_grid_frame = Frame(sci_main_frame, bg="#1a1a2e")
number_grid_frame.pack()

# Number buttons in a professional layout
number_buttons = [
    ("7", 0, 0), ("8", 0, 1), ("9", 0, 2), ("÷", 0, 3),
    ("4", 1, 0), ("5", 1, 1), ("6", 1, 2), ("×", 1, 3),
    ("1", 2, 0), ("2", 2, 1), ("3", 2, 2), ("-", 2, 3),
    ("0", 3, 0), (".", 3, 1), ("=", 3, 2), ("+", 3, 3),
]

for text, r, c in number_buttons:
    # Style based on button type
    if text in ["+", "-", "×", "÷"]:
        bg_color = "#e94560"
        fg_color = "#ffffff"
        font_size = 15
    elif text == "=":
        bg_color = "#00b894"
        fg_color = "#ffffff"
        font_size = 15
    else:
        bg_color = "#2d2d44"
        fg_color = "#ffffff"
        font_size = 15
    
    if text == "=":
        cmd = sci_evaluate
    elif text == "÷":
        cmd = lambda: add_to_entry("/")
    elif text == "×":
        cmd = lambda: add_to_entry("*")
    else:
        cmd = lambda t=text: add_to_entry(t)
    
    btn = Button(number_grid_frame, text=text, width=8, height=3, 
                font=("Consolas", font_size, "bold"),
                command=cmd, relief="raised", bd=2,
                bg=bg_color, fg=fg_color,
                activebackground=bg_color, activeforeground=fg_color)
    btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")

# Configure grid weights
for i in range(4):
    number_grid_frame.grid_rowconfigure(i, weight=1)
for i in range(4):
    number_grid_frame.grid_columnconfigure(i, weight=1)

# KEYBOARD HANDLER

def sci_keyboard_handler(event):
    key = event.keysym
    char = event.char
    
    if char.isdigit():
        add_to_entry(char)
        return 'break'
    elif char == '.':
        add_to_entry('.')
        return 'break'
    elif char == '(' or char == ')':
        add_to_entry(char)
        return 'break'
    elif char in ['+', '-']:
        add_to_entry(char)
        return 'break'
    elif char == '*':
        add_to_entry('*')
        return 'break'
    elif char == '/':
        add_to_entry('/')
        return 'break'
    elif char == '=' or key == 'Return' or key == 'KP_Enter':
        sci_evaluate()
        return 'break'
    elif key == 'BackSpace':
        backspace_sci()
        return 'break'
    elif key == 'Escape':
        clear_sci()
        return 'break'
    return None

sci_page.bind('<Key>', sci_keyboard_handler)
sci_entry.bind('<Key>', sci_keyboard_handler)

# Focus the entry
sci_entry.focus_set()

# ====================================================
# HELP TEXT
# ====================================================

help_frame = Frame(sci_main_frame, bg="#1a1a2e")
help_frame.pack(pady=(10, 0), fill=X)

help_label = Label(help_frame, text="💡 Enter expression and press = or Enter to evaluate", 
                   font=("Consolas", 9, "italic"), 
                   bg="#1a1a2e", fg="#666666")
help_label.pack()

# =========================
# STATISTICS PAGE
# =========================

statistics_page = Frame(content, bg="white")
pages["Statistics"] = statistics_page

stats_main_frame = Frame(statistics_page, bg="white")
stats_main_frame.pack(expand=True, fill=BOTH, padx=20, pady=20)

Label(stats_main_frame, text="📊 STATISTICS CALCULATOR", font=("Consolas", 16, "bold"), 
      bg="white", fg="#2c3e50").pack(pady=10)
Label(stats_main_frame, text="Enter numbers separated by commas (e.g., 1,2,3,4,5)", 
      bg="white", font=("Consolas", 10), fg="#7f8c8d").pack()

# Entry frame with clear button
entry_frame = Frame(stats_main_frame, bg="white")
entry_frame.pack(pady=10, fill=X)

stats_entry = Entry(entry_frame, width=50, font=("Consolas", 32), 
                    relief="sunken", bd=2)
stats_entry.pack(side=LEFT, padx=(0, 10), fill=X, expand=True)

# Result display with scrollable text
result_frame = Frame(stats_main_frame, bg="white")
result_frame.pack(pady=10, fill=BOTH, expand=True)

stats_result = Text(result_frame, height=3, width=20, font=("Consolas", 10), 
                    bg="#f8f9fa", fg="#2c3e50", relief="sunken", bd=2,
                    wrap=WORD)
stats_result.pack(side=LEFT, fill=BOTH, expand=True)

result_scrollbar = Scrollbar(result_frame, command=stats_result.yview)
result_scrollbar.pack(side=RIGHT, fill=Y)
stats_result.config(yscrollcommand=result_scrollbar.set)

# ========== STATISTICS FUNCTIONS ==========
def get_stats_data():
    """Extract numbers from entry field"""
    try:
        text = stats_entry.get()
        # Replace spaces and handle multiple delimiters
        text = text.replace(" ", ",")
        # Split by comma and filter empty strings
        numbers_list = [float(x.strip()) for x in text.split(",") if x.strip()]
        if not numbers_list:
            raise ValueError("No numbers entered")
        return numbers_list
    except ValueError as e:
        messagebox.showerror("Error", "Please enter valid numbers separated by commas!")
        return None

def display_result(title, value, details=None):
    """Display result in the text widget"""
    stats_result.delete(1.0, END)
    stats_result.insert(END, f"{'='*50}\n")
    stats_result.insert(END, f"📊 {title}\n")
    stats_result.insert(END, f"{'='*50}\n\n")
    stats_result.insert(END, f"Result: {value}\n")
    if details:
        stats_result.insert(END, f"\n{details}\n")
    stats_result.insert(END, f"\n{'='*50}")

def calc_mean():
    data = get_stats_data()
    if data:
        mean = statistics.mean(data)
        display_result("MEAN", f"{mean:.6f}", 
                      f"Sum: {sum(data):.4f}\nCount: {len(data)} values")

def calc_median():
    data = get_stats_data()
    if data:
        median = statistics.median(data)
        display_result("MEDIAN", f"{median:.6f}", 
                      f"Sorted data: {sorted(data)}\nMiddle value")

def calc_mode():
    data = get_stats_data()
    if data:
        try:
            mode = statistics.mode(data)
            display_result("MODE", f"{mode}", 
                          f"Most frequent value in the dataset")
        except statistics.StatisticsError:
            display_result("MODE", "No unique mode", 
                          "All values appear with equal frequency")

def calc_variance():
    data = get_stats_data()
    if data:
        variance = statistics.variance(data)
        display_result("VARIANCE", f"{variance:.6f}", 
                      f"Population variance: {statistics.pvariance(data):.6f}\n"
                      f"Sample variance (n-1): {variance:.6f}")

def calc_std():
    data = get_stats_data()
    if data:
        std = statistics.stdev(data)
        display_result("STANDARD DEVIATION", f"{std:.6f}", 
                      f"Population std: {statistics.pstdev(data):.6f}\n"
                      f"Sample std (n-1): {std:.6f}")

def calc_correlation():
    """Calculate correlation coefficient between two datasets"""
    try:
        text = stats_entry.get().strip()
        
        # Check if input is empty
        if not text:
            messagebox.showerror("Error", "Please enter data!\n\n"
                               "Format: 1,2,3,4,5; 2,4,6,8,10")
            return
        
        # Check if semicolon exists
        if ';' not in text:
            messagebox.showerror("Error", "Missing semicolon (;) separator!\n\n"
                               "Format: 1,2,3,4,5; 2,4,6,8,10")
            return
        
        # Split into two datasets separated by semicolon
        parts = text.split(";")
        
        # Check if we have exactly 2 parts
        if len(parts) != 2:
            messagebox.showerror("Error", "Invalid format!\n\n"
                               "Use exactly ONE semicolon (;) to separate datasets.\n"
                               "Example: 1,2,3,4,5; 2,4,6,8,10")
            return
        
        # Clean and parse both datasets
        part1 = parts[0].strip()
        part2 = parts[1].strip()
        
        if not part1 or not part2:
            messagebox.showerror("Error", "Both datasets must have values!\n\n"
                               "Example: 1,2,3,4,5; 2,4,6,8,10")
            return
        
        # Parse both datasets
        data1 = []
        data2 = []
        
        try:
            data1 = [float(x.strip()) for x in part1.split(",") if x.strip()]
            data2 = [float(x.strip()) for x in part2.split(",") if x.strip()]
        except ValueError:
            messagebox.showerror("Error", "Invalid numbers in dataset!\n\n"
                               "Use only numbers separated by commas.\n"
                               "Example: 1,2,3,4,5; 2,4,6,8,10")
            return
        
        # Check if datasets have values
        if not data1 or not data2:
            messagebox.showerror("Error", "Both datasets must contain numbers!\n\n"
                               "Example: 1,2,3,4,5; 2,4,6,8,10")
            return
        
        # Check if datasets have same length
        if len(data1) != len(data2):
            messagebox.showerror("Error", f"Datasets must have the same length!\n\n"
                               f"Dataset 1 has {len(data1)} values\n"
                               f"Dataset 2 has {len(data2)} values\n"
                               "Please make them equal length.")
            return
        
        # Need at least 2 pairs for correlation
        if len(data1) < 2:
            messagebox.showerror("Error", "Need at least 2 pairs for correlation!\n\n"
                               f"Currently have {len(data1)} pairs.")
            return
        
        # Calculate correlation coefficient
        corr = statistics.correlation(data1, data2)
        
        # Determine correlation strength
        strength = ""
        if abs(corr) >= 0.8:
            strength = "Very Strong"
        elif abs(corr) >= 0.6:
            strength = "Strong"
        elif abs(corr) >= 0.4:
            strength = "Moderate"
        elif abs(corr) >= 0.2:
            strength = "Weak"
        else:
            strength = "Very Weak"
        
        direction = "Positive" if corr > 0 else "Negative" if corr < 0 else "No"
        
        display_result("CORRELATION COEFFICIENT", f"{corr:.6f}", 
                      f"Strength: {strength} {direction} correlation\n"
                      f"Dataset 1 ({len(data1)} values): {data1}\n"
                      f"Dataset 2 ({len(data2)} values): {data2}\n"
                      f"n = {len(data1)} pairs")
        
    except statistics.StatisticsError as e:
        messagebox.showerror("Error", f"Correlation calculation error:\n\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error:\n\n{str(e)}\n\n"
                            "Please use format: 1,2,3,4,5; 2,4,6,8,10")

def calc_percentile():
    """Calculate percentile of data"""
    try:
        text = stats_entry.get().strip()
        
        # Check if input is empty
        if not text:
            messagebox.showerror("Error", "Please enter data!\n\n"
                               "Format: 1,2,3,4,5,6,7,8,9,10; 75")
            return
        
        # Check if semicolon exists
        if ';' not in text:
            messagebox.showerror("Error", "Missing semicolon (;) separator!\n\n"
                               "Format: 1,2,3,4,5,6,7,8,9,10; 75")
            return
        
        # Split data and percentile value
        parts = text.split(";")
        
        # Check if we have exactly 2 parts
        if len(parts) != 2:
            messagebox.showerror("Error", "Invalid format!\n\n"
                               "Use exactly ONE semicolon (;) to separate data and percentile.\n"
                               "Example: 1,2,3,4,5,6,7,8,9,10; 75")
            return
        
        # Clean and parse
        data_part = parts[0].strip()
        percentile_part = parts[1].strip()
        
        if not data_part or not percentile_part:
            messagebox.showerror("Error", "Both data and percentile values are required!\n\n"
                               "Example: 1,2,3,4,5,6,7,8,9,10; 75")
            return
        
        # Parse data
        try:
            data = [float(x.strip()) for x in data_part.split(",") if x.strip()]
        except ValueError:
            messagebox.showerror("Error", "Invalid numbers in dataset!\n\n"
                               "Use only numbers separated by commas.\n"
                               "Example: 1,2,3,4,5,6,7,8,9,10; 75")
            return
        
        if not data:
            messagebox.showerror("Error", "No data provided!\n\n"
                               "Example: 1,2,3,4,5,6,7,8,9,10; 75")
            return
        
        # Parse percentile value
        try:
            percentile_value = float(percentile_part)
        except ValueError:
            messagebox.showerror("Error", "Invalid percentile value!\n\n"
                               "Percentile must be a number between 0 and 100.\n"
                               "Example: 1,2,3,4,5,6,7,8,9,10; 75")
            return
        
        # Validate percentile range
        if not 0 <= percentile_value <= 100:
            messagebox.showerror("Error", "Percentile must be between 0 and 100!\n\n"
                               f"Current value: {percentile_value}\n"
                               "Use a value like 25, 50, 75, etc.")
            return
        
        # Need at least 1 data point
        if len(data) < 1:
            messagebox.showerror("Error", "Need at least 1 value for percentile calculation!")
            return
        
        # Calculate percentile
        # For n=100 quantiles, we need to handle the index properly
        try:
            quantiles = statistics.quantiles(data, n=100)
            
            # Check if we have enough quantiles
            if not quantiles:
                messagebox.showerror("Error", "Not enough data for percentile calculation!")
                return
            
            # Calculate index for the requested percentile
            # For percentile p, we want the p-th quantile (0-indexed)
            index = int(percentile_value)
            
            # Handle edge cases
            if index == 0:
                result = min(data)
            elif index >= len(quantiles):
                result = max(data)
            else:
                result = quantiles[index - 1] if index > 0 else quantiles[0]
            
            sorted_data = sorted(data)
            display_result(f"{percentile_value}th PERCENTILE", f"{result:.6f}", 
                          f"Sorted Data: {sorted_data}\n"
                          f"n = {len(data)} values\n"
                          f"{percentile_value}% of values are at or below {result:.4f}")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Percentile calculation error:\n\n{str(e)}\n\n"
                                "For small datasets, try using fewer quantiles.")
        except IndexError:
            messagebox.showerror("Error", f"Percentile {percentile_value} out of range!\n\n"
                                f"Data has {len(data)} values.\n"
                                f"Valid percentiles: 0 to 100")
        
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error:\n\n{str(e)}\n\n"
                            "Please use format: 1,2,3,4,5,6,7,8,9,10; 75")

def calc_avg():
    """Calculate average (mean) - alias for mean"""
    calc_mean()

def clear_all():
    """Clear entry and result"""
    stats_entry.delete(0, END)
    stats_result.delete(1.0, END)
    stats_entry.focus_set()

# ========== STATISTICS BUTTONS ==========
stats_btn_frame = Frame(stats_main_frame, bg="white")
stats_btn_frame.pack(pady=10)

# Row 1: Basic statistics
basic_stats = [
    ("📊 Mean", calc_mean), ("📈 Median", calc_median), ("📉 Mode", calc_mode),
    ("📐 Variance", calc_variance), ("📏 Std Dev", calc_std)
]

for i, (text, cmd) in enumerate(basic_stats):
    Button(stats_btn_frame, text=text, width=11, command=cmd, 
           font=("Consolas", 8, "bold"), bg="#3498db", fg="white",
           relief="raised", bd=2).grid(row=i//3, column=i%3, padx=3, pady=3)

# Row 2: Advanced statistics
advanced_stats = [
    ("🔄 Correlation", calc_correlation), 
    ("📊 Percentile", calc_percentile),
    ("📋 Avg", calc_avg),
    ("🗑️ Clear", clear_all)
]
  
for i, (text, cmd) in enumerate(advanced_stats):
    if text == "🗑️ Clear":
        btn = Button(stats_btn_frame, text=text, width=11, command=cmd, 
                    font=("Consolas", 8, "bold"), bg="#e74c3c", fg="white",
                    relief="raised", bd=2)
    else:
        btn = Button(stats_btn_frame, text=text, width=11, command=cmd, 
                    font=("Consolas", 8, "bold"), bg="#2ecc71", fg="white",
                    relief="raised", bd=2)
    btn.grid(row=1, column=i, padx=3, pady=3)
    
# ========== NUMBER PAD ==========
number_pad_frame = Frame(stats_main_frame, bg="white")
number_pad_frame.pack(pady=10)
# Updated number pad with semicolon button for Correlation and Percentile
numbers = [
    ("7",0,0), ("8",0,1), ("9",0,2), (",",0,3),
    ("4",1,0), ("5",1,1), ("6",1,2), (".",1,3),
    ("1",2,0), ("2",2,1), ("3",2,2), (";",2,3),
    ("0",3,1), ("⌫",3,0), ("(",3,2), (")",3,3),
]

def num_pad_click(value):
    if value == "C":
        stats_entry.delete(0, END)
    elif value == "⌫":
        current = stats_entry.get()
        if current:
            stats_entry.delete(len(current) - 1, END)
    else:
        stats_entry.insert(END, value)
    stats_entry.focus_set()

for text, r, c in numbers:
    if text in ["C"]:
        bg_color = "#e74c3c"
        fg_color = "white"
    elif text == "⌫":
        bg_color = "#f39c12"
        fg_color = "white"
    elif text in ["(", ")", ";"]:
        bg_color = "#8e44ad"
        fg_color = "white"
    else:
        bg_color = "#ecf0f1"
        fg_color = "#2c3e50"
    
    btn = Button(number_pad_frame, text=text, width=10, height=3, 
                font=("Consolas", 9, "bold"),
                command=lambda t=text: num_pad_click(t), 
                bg=bg_color, fg=fg_color)
    btn.grid(row=r, column=c, padx=2, pady=2)

# ========== KEYBOARD HANDLER ==========
def stats_keyboard(event):
    key = event.keysym
    char = event.char
    
    if char.isdigit() or char == ',' or char == '.':
        stats_entry.insert(END, char)
        return 'break'
    elif char == '(' or char == ')':
        stats_entry.insert(END, char)
        return 'break'
    elif char == ';':
        stats_entry.insert(END, '; ')
        return 'break'
    elif key == 'BackSpace':
        current = stats_entry.get()
        if current:
            stats_entry.delete(len(current) - 1, END)
        return 'break'
    elif key == 'Escape':
        clear_all()
        return 'break'
    elif key == 'Return' or key == 'KP_Enter':
        # Try to determine what to calculate based on input
        text = stats_entry.get()
        if ';' in text:
            if ';' in text and text.count(';') == 1:
                # Check if it's percentile or correlation
                parts = text.split(';')
                if len(parts) == 2:
                    try:
                        # Try to parse as percentile
                        float(parts[1].strip())
                        calc_percentile()
                    except:
                        calc_correlation()
        else:
            calc_mean()
        return 'break'
    return None

statistics_page.bind('<Key>', stats_keyboard)
stats_entry.bind('<Key>', stats_keyboard)

stats_entry.focus_set()

# =========================
# FINANCE PAGE 
# =========================

finance_page = Frame(content, bg="#1a1a2e")
pages["Finance"] = finance_page

Label(finance_page, text="💰 FINANCE CALCULATOR", font=("Consolas", 18, "bold"), 
      bg="#1a1a2e", fg="#00ff88").pack(pady=10)

finance_tabs = ttk.Notebook(finance_page)
finance_tabs.pack(fill="both", expand=True, padx=10, pady=10)

# Configure notebook style for dark theme
style = ttk.Style()
style.configure("TNotebook", background="#1a1a2e", borderwidth=0)
style.configure("TNotebook.Tab", background="#2d2d44", foreground="#0E0101", 
                padding=[10, 5], font=("Consolas", 10))
style.map("TNotebook.Tab", background=[("selected", "#533483")])

# =========================
# FD CALCULATOR
# =========================

fd_frame = Frame(finance_tabs, bg="#202062")
finance_tabs.add(fd_frame, text="FD Calculator")

fd_main = Frame(fd_frame, bg="#1919cb")
fd_main.pack(padx=20, pady=20, fill="both", expand=True)

Label(fd_main, text="🏦 FD CALCULATOR", font=("Consolas", 14, "bold"), 
      bg="#1a1a2e", fg="#00ff88").pack(pady=(0, 15))

input_frame = Frame(fd_main, bg="#010117")
input_frame.pack(fill="x", pady=5)

Label(input_frame, text="Principal Amount (₹):", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#b65e5e").pack(anchor="w", pady=3)
fd_principal = Entry(input_frame, font=("Consolas", 11), bg="#0f0f1a", fg="#00ff88",
                     insertbackground="#00ff88", relief="sunken", bd=2)
fd_principal.pack(fill="x", pady=3, ipady=5)

Label(input_frame, text="Interest Rate (%):", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
fd_rate = Entry(input_frame, font=("Consolas", 11), bg="#0f0f1a", fg="#00ff88",
                insertbackground="#00ff88", relief="sunken", bd=2)
fd_rate.pack(fill="x", pady=3, ipady=5)

Label(input_frame, text="Time Period (Years):", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
fd_years = Entry(input_frame, font=("Consolas", 11), bg="#0f0f1a", fg="#00ff88",
                 insertbackground="#00ff88", relief="sunken", bd=2)
fd_years.pack(fill="x", pady=3, ipady=5)

fd_result = Label(fd_main, text="", font=("Consolas", 11), 
                  bg="#1a1a2e", fg="#00d4ff", justify=LEFT)
fd_result.pack(pady=15)

def calculate_fd():
    try:
        P = float(fd_principal.get())
        r = float(fd_rate.get()) / 100
        t = float(fd_years.get())
        maturity = P * ((1 + r) ** t)
        interest = maturity - P
        fd_result.config(text=f"💰 Maturity Amount: ₹{maturity:,.2f}\n📈 Interest Earned: ₹{interest:,.2f}")
    except:
        messagebox.showerror("Error", "Invalid Input")

Button(fd_main, text="🧮 Calculate FD", command=calculate_fd, 
       bg="#e94560", fg="#ffffff", font=("Consolas", 11, "bold"), 
       width=20, height=1).pack(pady=10)

# =========================
# EMI CALCULATOR
# =========================

emi_frame = Frame(finance_tabs, bg="#1a1a2e")
finance_tabs.add(emi_frame, text="EMI Calculator")

emi_main = Frame(emi_frame, bg="#1a1a2e")
emi_main.pack(padx=20, pady=20, fill="both", expand=True)

Label(emi_main, text="📊 EMI CALCULATOR", font=("Consolas", 14, "bold"), 
      bg="#1a1a2e", fg="#00ff88").pack(pady=(0, 15))

# Input fields with dark theme
input_frame = Frame(emi_main, bg="#1a1a2e")
input_frame.pack(fill="x", pady=5)

Label(input_frame, text="Loan Amount (₹):", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
emi_amount = Entry(input_frame, font=("Consolas", 11), bg="#0f0f1a", fg="#00ff88",
                   insertbackground="#00ff88", relief="sunken", bd=2)
emi_amount.pack(fill="x", pady=3, ipady=5)

Label(input_frame, text="Annual Interest Rate (%):", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
emi_rate = Entry(input_frame, font=("Consolas", 11), bg="#0f0f1a", fg="#00ff88",
                 insertbackground="#00ff88", relief="sunken", bd=2)
emi_rate.pack(fill="x", pady=3, ipady=5)

Label(input_frame, text="Loan Tenure (Years):", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
emi_years = Entry(input_frame, font=("Consolas", 11), bg="#0f0f1a", fg="#00ff88",
                  insertbackground="#00ff88", relief="sunken", bd=2)
emi_years.pack(fill="x", pady=3, ipady=5)

emi_result = Label(emi_main, text="", font=("Consolas", 11), 
                   bg="#1a1a2e", fg="#00d4ff", justify=LEFT)
emi_result.pack(pady=15)

def calculate_emi():
    try:
        P = float(emi_amount.get())
        r = float(emi_rate.get()) / (12 * 100)
        n = float(emi_years.get()) * 12
        emi = P * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
        total = emi * n
        interest = total - P
        emi_result.config(text=f"📌 EMI: ₹{emi:,.2f}\n💰 Total Payment: ₹{total:,.2f}\n📈 Total Interest: ₹{interest:,.2f}")
    except:
        messagebox.showerror("Error", "Invalid Input")

Button(emi_main, text="🧮 Calculate EMI", command=calculate_emi, 
       bg="#e94560", fg="#ffffff", font=("Consolas", 11, "bold"), 
       width=20, height=1).pack(pady=10)

# =========================
# SIP CALCULATOR
# =========================

sip_frame = Frame(finance_tabs, bg="#1a1a2e")
finance_tabs.add(sip_frame, text="SIP Calculator")

sip_main = Frame(sip_frame, bg="#1a1a2e")
sip_main.pack(padx=20, pady=20, fill="both", expand=True)

Label(sip_main, text="📈 SIP CALCULATOR", font=("Consolas", 14, "bold"), 
      bg="#1a1a2e", fg="#00ff88").pack(pady=(0, 15))

input_frame = Frame(sip_main, bg="#1a1a2e")
input_frame.pack(fill="x", pady=5)

Label(input_frame, text="Monthly Investment (₹):", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
sip_amount = Entry(input_frame, font=("Consolas", 11), bg="#0f0f1a", fg="#00ff88",
                   insertbackground="#00ff88", relief="sunken", bd=2)
sip_amount.pack(fill="x", pady=3, ipady=5)

Label(input_frame, text="Expected Return Rate (%):", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
sip_rate = Entry(input_frame, font=("Consolas", 11), bg="#0f0f1a", fg="#00ff88",
                 insertbackground="#00ff88", relief="sunken", bd=2)
sip_rate.pack(fill="x", pady=3, ipady=5)

Label(input_frame, text="Time Period (Years):", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
sip_years = Entry(input_frame, font=("Consolas", 11), bg="#0f0f1a", fg="#00ff88",
                  insertbackground="#00ff88", relief="sunken", bd=2)
sip_years.pack(fill="x", pady=3, ipady=5)

sip_result = Label(sip_main, text="", font=("Consolas", 11), 
                   bg="#1a1a2e", fg="#00d4ff", justify=LEFT)
sip_result.pack(pady=15)

def calculate_sip():
    try:
        P = float(sip_amount.get())
        r = float(sip_rate.get()) / (12 * 100)
        n = float(sip_years.get()) * 12
        future_value = P * (((1 + r) ** n - 1) / r) * (1 + r)
        invested = P * n
        returns = future_value - invested
        sip_result.config(text=f"📈 Future Value: ₹{future_value:,.2f}\n💰 Invested: ₹{invested:,.2f}\n📊 Returns: ₹{returns:,.2f}")
    except:
        messagebox.showerror("Error", "Invalid Input")

Button(sip_main, text="🧮 Calculate SIP", command=calculate_sip, 
       bg="#e94560", fg="#ffffff", font=("Consolas", 11, "bold"), 
       width=20, height=1).pack(pady=10)

# =========================
# GST CALCULATOR
# =========================

gst_frame = Frame(finance_tabs, bg="#1a1a2e")
finance_tabs.add(gst_frame, text="GST Calculator")

gst_main = Frame(gst_frame, bg="#1a1a2e")
gst_main.pack(padx=20, pady=20, fill="both", expand=True)

Label(gst_main, text="📊 GST CALCULATOR", font=("Consolas", 14, "bold"), 
      bg="#1a1a2e", fg="#00ff88").pack(pady=(0, 15))

input_frame = Frame(gst_main, bg="#1a1a2e")
input_frame.pack(fill="x", pady=5)

Label(input_frame, text="Original Amount (₹):", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
gst_amount = Entry(input_frame, font=("Consolas", 11), bg="#0f0f1a", fg="#00ff88",
                   insertbackground="#00ff88", relief="sunken", bd=2)
gst_amount.pack(fill="x", pady=3, ipady=5)

Label(input_frame, text="GST Rate (%):", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
gst_rate = Entry(input_frame, font=("Consolas", 11), bg="#0f0f1a", fg="#00ff88",
                 insertbackground="#00ff88", relief="sunken", bd=2)
gst_rate.pack(fill="x", pady=3, ipady=5)

gst_result = Label(gst_main, text="", font=("Consolas", 11), 
                   bg="#1a1a2e", fg="#00d4ff", justify=LEFT)
gst_result.pack(pady=15)

def calculate_gst():
    try:
        amount = float(gst_amount.get())
        rate = float(gst_rate.get())
        gst = amount * rate / 100
        total = amount + gst
        gst_result.config(text=f"📊 GST Amount: ₹{gst:,.2f}\n💰 Total Amount: ₹{total:,.2f}")
    except:
        messagebox.showerror("Error", "Invalid Input")

Button(gst_main, text="🧮 Calculate GST", command=calculate_gst, 
       bg="#e94560", fg="#ffffff", font=("Consolas", 11, "bold"), 
       width=20, height=1).pack(pady=10)

# =========================
# RETIREMENT PLANNING CALCULATOR
# =========================

retirement_frame = Frame(finance_tabs, bg="#1a1a2e")
finance_tabs.add(retirement_frame, text="Retirement Planning")

# Create a canvas with scrollbar for retirement frame
retirement_canvas = Canvas(retirement_frame, bg="#1a1a2e", highlightthickness=0)
retirement_scrollbar = Scrollbar(retirement_frame, orient="vertical", command=retirement_canvas.yview)
retirement_scrollable_frame = Frame(retirement_canvas, bg="#1a1a2e")

retirement_scrollable_frame.bind(
    "<Configure>",
    lambda e: retirement_canvas.configure(scrollregion=retirement_canvas.bbox("all"))
)

retirement_canvas.create_window((0, 0), window=retirement_scrollable_frame, anchor="nw")
retirement_canvas.configure(yscrollcommand=retirement_scrollbar.set)

retirement_canvas.pack(side="left", fill="both", expand=True)
retirement_scrollbar.pack(side="right", fill="y")

# Retirement Planning Inputs
retirement_main = Frame(retirement_scrollable_frame, bg="#1a1a2e")
retirement_main.pack(padx=20, pady=20, fill="both", expand=True)

Label(retirement_main, text="🏖️ RETIREMENT PLANNING CALCULATOR", 
      font=("Consolas", 16, "bold"), bg="#1a1a2e", fg="#00ff88").pack(pady=15)

# Personal Details Frame
personal_frame = LabelFrame(retirement_main, text="Personal Details", 
                            font=("Consolas", 12, "bold"), bg="#1a1a2e", 
                            fg="#ffffff", padx=15, pady=10)
personal_frame.pack(fill="x", pady=10)

Label(personal_frame, text="Current Age (years):", font=("Consolas", 10), 
      bg="#1a1a2e", fg="#ffffff").grid(row=0, column=0, sticky="w", pady=5, padx=5)
current_age_entry = Entry(personal_frame, width=15, font=("Consolas", 10),
                          bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
current_age_entry.grid(row=0, column=1, pady=5, padx=5)
Label(personal_frame, text="(e.g., 30)", font=("Consolas", 8), 
      fg="#888888", bg="#1a1a2e").grid(row=0, column=2, sticky="w")

Label(personal_frame, text="Retirement Age (years):", font=("Consolas", 10), 
      bg="#1a1a2e", fg="#ffffff").grid(row=1, column=0, sticky="w", pady=5, padx=5)
retirement_age_entry = Entry(personal_frame, width=15, font=("Consolas", 10),
                             bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
retirement_age_entry.grid(row=1, column=1, pady=5, padx=5)
Label(personal_frame, text="(e.g., 60)", font=("Consolas", 8), 
      fg="#888888", bg="#1a1a2e").grid(row=1, column=2, sticky="w")

Label(personal_frame, text="Expected Life Span (years):", font=("Consolas", 10), 
      bg="#1a1a2e", fg="#ffffff").grid(row=2, column=0, sticky="w", pady=5, padx=5)
life_span_entry = Entry(personal_frame, width=15, font=("Consolas", 10),
                        bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
life_span_entry.grid(row=2, column=1, pady=5, padx=5)
Label(personal_frame, text="(e.g., 85)", font=("Consolas", 8), 
      fg="#888888", bg="#1a1a2e").grid(row=2, column=2, sticky="w")

# Financial Details Frame
financial_frame = LabelFrame(retirement_main, text="Financial Details", 
                             font=("Consolas", 12, "bold"), bg="#1a1a2e", 
                             fg="#ffffff", padx=15, pady=10)
financial_frame.pack(fill="x", pady=10)

Label(financial_frame, text="Current Monthly Household Expenses (₹):", 
      font=("Consolas", 10), bg="#1a1a2e", fg="#ffffff").grid(row=0, column=0, sticky="w", pady=5, padx=5)
monthly_expense_entry = Entry(financial_frame, width=15, font=("Consolas", 10),
                              bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
monthly_expense_entry.grid(row=0, column=1, pady=5, padx=5)
Label(financial_frame, text="(e.g., 50000)", font=("Consolas", 8), 
      fg="#888888", bg="#1a1a2e").grid(row=0, column=2, sticky="w")

Label(financial_frame, text="Current Monthly Savings (₹):", 
      font=("Consolas", 10), bg="#1a1a2e", fg="#ffffff").grid(row=1, column=0, sticky="w", pady=5, padx=5)
monthly_savings_entry = Entry(financial_frame, width=15, font=("Consolas", 10),
                              bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
monthly_savings_entry.grid(row=1, column=1, pady=5, padx=5)
Label(financial_frame, text="(e.g., 20000)", font=("Consolas", 8), 
      fg="#888888", bg="#1a1a2e").grid(row=1, column=2, sticky="w")

Label(financial_frame, text="Current Savings/Investments (₹):", 
      font=("Consolas", 10), bg="#1a1a2e", fg="#ffffff").grid(row=2, column=0, sticky="w", pady=5, padx=5)
current_savings_entry = Entry(financial_frame, width=15, font=("Consolas", 10),
                              bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
current_savings_entry.grid(row=2, column=1, pady=5, padx=5)
Label(financial_frame, text="(e.g., 500000)", font=("Consolas", 8), 
      fg="#888888", bg="#1a1a2e").grid(row=2, column=2, sticky="w")

# Assumptions Frame
assumptions_frame = LabelFrame(retirement_main, text="Assumptions", 
                               font=("Consolas", 12, "bold"), bg="#1a1a2e", 
                               fg="#ffffff", padx=15, pady=10)
assumptions_frame.pack(fill="x", pady=10)

Label(assumptions_frame, text="Expected Rate of Return (% p.a.):", 
      font=("Consolas", 10), bg="#1a1a2e", fg="#ffffff").grid(row=0, column=0, sticky="w", pady=5, padx=5)
return_rate_entry = Entry(assumptions_frame, width=15, font=("Consolas", 10),
                          bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
return_rate_entry.grid(row=0, column=1, pady=5, padx=5)
return_rate_entry.insert(0, "12")
Label(assumptions_frame, text="(e.g., 12)", font=("Consolas", 8), 
      fg="#888888", bg="#1a1a2e").grid(row=0, column=2, sticky="w")

Label(assumptions_frame, text="Expected Inflation Rate (% p.a.):", 
      font=("Consolas", 10), bg="#1a1a2e", fg="#ffffff").grid(row=1, column=0, sticky="w", pady=5, padx=5)
inflation_rate_entry = Entry(assumptions_frame, width=15, font=("Consolas", 10),
                             bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
inflation_rate_entry.grid(row=1, column=1, pady=5, padx=5)
inflation_rate_entry.insert(0, "6")
Label(assumptions_frame, text="(e.g., 6)", font=("Consolas", 8), 
      fg="#888888", bg="#1a1a2e").grid(row=1, column=2, sticky="w")

# Additional Expenses Frame
additional_frame = LabelFrame(retirement_main, text="Additional Retirement Expenses (Optional)", 
                              font=("Consolas", 12, "bold"), bg="#1a1a2e", 
                              fg="#ffffff", padx=15, pady=10)
additional_frame.pack(fill="x", pady=10)

Label(additional_frame, text="Monthly Healthcare/Medicine Expenses (₹):", 
      font=("Consolas", 10), bg="#1a1a2e", fg="#ffffff").grid(row=0, column=0, sticky="w", pady=5, padx=5)
healthcare_entry = Entry(additional_frame, width=15, font=("Consolas", 10),
                         bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
healthcare_entry.grid(row=0, column=1, pady=5, padx=5)
healthcare_entry.insert(0, "0")
Label(additional_frame, text="(e.g., 5000)", font=("Consolas", 8), 
      fg="#888888", bg="#1a1a2e").grid(row=0, column=2, sticky="w")

Label(additional_frame, text="Monthly Travel/Recreation Expenses (₹):", 
      font=("Consolas", 10), bg="#1a1a2e", fg="#ffffff").grid(row=1, column=0, sticky="w", pady=5, padx=5)
travel_entry = Entry(additional_frame, width=15, font=("Consolas", 10),
                     bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
travel_entry.grid(row=1, column=1, pady=5, padx=5)
travel_entry.insert(0, "0")
Label(additional_frame, text="(e.g., 3000)", font=("Consolas", 8), 
      fg="#888888", bg="#1a1a2e").grid(row=1, column=2, sticky="w")

Label(additional_frame, text="Any Other Monthly Expenses (₹):", 
      font=("Consolas", 10), bg="#1a1a2e", fg="#ffffff").grid(row=2, column=0, sticky="w", pady=5, padx=5)
other_entry = Entry(additional_frame, width=15, font=("Consolas", 10),
                    bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
other_entry.grid(row=2, column=1, pady=5, padx=5)
other_entry.insert(0, "0")
Label(additional_frame, text="(e.g., 2000)", font=("Consolas", 8), 
      fg="#888888", bg="#1a1a2e").grid(row=2, column=2, sticky="w")

# Result Display
retirement_result_text = Text(retirement_main, height=18, width=80, 
                              font=("Consolas", 9), wrap=WORD,
                              bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
retirement_result_text.pack(pady=15)

def calculate_retirement():
    try:
        # Get all inputs
        current_age = int(current_age_entry.get())
        retirement_age = int(retirement_age_entry.get())
        life_span = int(life_span_entry.get())
        
        monthly_expense = float(monthly_expense_entry.get())
        monthly_savings = float(monthly_savings_entry.get())
        current_savings = float(current_savings_entry.get())
        
        return_rate = float(return_rate_entry.get()) / 100
        inflation_rate = float(inflation_rate_entry.get()) / 100
        
        healthcare = float(healthcare_entry.get())
        travel = float(travel_entry.get())
        other = float(other_entry.get())
        
        # Calculations
        years_to_retirement = retirement_age - current_age
        years_in_retirement = life_span - retirement_age
        
        if years_to_retirement <= 0:
            messagebox.showerror("Error", "Retirement age must be greater than current age!")
            return
        
        # Calculate future monthly expenses considering inflation
        future_monthly_expense = monthly_expense * ((1 + inflation_rate) ** years_to_retirement)
        total_monthly_retirement_expense = future_monthly_expense + healthcare + travel + other
        
        # Calculate corpus needed at retirement (using annuity formula)
        monthly_rate = return_rate / 12
        months_in_retirement = years_in_retirement * 12
        
        if monthly_rate > 0:
            corpus_needed = total_monthly_retirement_expense * ((1 - (1 + monthly_rate) ** -months_in_retirement) / monthly_rate)
        else:
            corpus_needed = total_monthly_retirement_expense * months_in_retirement
        
        # Calculate future value of current savings
        future_current_savings = current_savings * ((1 + return_rate) ** years_to_retirement)
        
        # Calculate future value of monthly savings (SIP)
        monthly_rate_invest = return_rate / 12
        months_to_retirement = years_to_retirement * 12
        
        if monthly_rate_invest > 0:
            future_savings = monthly_savings * (((1 + monthly_rate_invest) ** months_to_retirement - 1) / monthly_rate_invest) * (1 + monthly_rate_invest)
        else:
            future_savings = monthly_savings * months_to_retirement
        
        total_future_corpus = future_current_savings + future_savings
        
        # Calculate monthly withdrawal amount during retirement
        if months_in_retirement > 0 and monthly_rate > 0:
            monthly_withdrawal = total_future_corpus * monthly_rate * ((1 + monthly_rate) ** months_in_retirement) / (((1 + monthly_rate) ** months_in_retirement) - 1)
        else:
            monthly_withdrawal = total_future_corpus / months_in_retirement if months_in_retirement > 0 else 0
        
        # Calculate shortfall or surplus
        shortfall = corpus_needed - total_future_corpus
        additional_savings_needed = 0
        
        if shortfall > 0 and months_to_retirement > 0 and monthly_rate_invest > 0:
            additional_savings_needed = shortfall * monthly_rate_invest / (((1 + monthly_rate_invest) ** months_to_retirement - 1) * (1 + monthly_rate_invest))
        
        # Prepare result text
        result = f"""
{'='*70}
                    RETIREMENT PLANNING REPORT
{'='*70}

📊 PERSONAL DETAILS:
   • Current Age: {current_age} years
   • Retirement Age: {retirement_age} years
   • Years to Retirement: {years_to_retirement} years
   • Expected Life Span: {life_span} years
   • Years in Retirement: {years_in_retirement} years

💰 CURRENT FINANCIAL STATUS:
   • Monthly Household Expenses: ₹{monthly_expense:,.2f}
   • Monthly Savings: ₹{monthly_savings:,.2f}
   • Current Savings/Investments: ₹{current_savings:,.2f}

📈 ASSUMPTIONS:
   • Expected Rate of Return: {return_rate*100:.1f}% p.a.
   • Expected Inflation Rate: {inflation_rate*100:.1f}% p.a.

💊 ADDITIONAL RETIREMENT EXPENSES (Monthly):
   • Healthcare/Medicine: ₹{healthcare:,.2f}
   • Travel/Recreation: ₹{travel:,.2f}
   • Other Expenses: ₹{other:,.2f}
   • Total Additional: ₹{healthcare+travel+other:,.2f}

🎯 RETIREMENT CORPUS CALCULATION:
   • Future Monthly Expense (adjusted for inflation): ₹{future_monthly_expense:,.2f}
   • Total Monthly Need in Retirement: ₹{total_monthly_retirement_expense:,.2f}
   • Corpus Needed at Retirement: ₹{corpus_needed:,.2f}

📈 PROJECTED CORPUS AT RETIREMENT:
   • Future Value of Current Savings: ₹{future_current_savings:,.2f}
   • Future Value of Monthly Savings: ₹{future_savings:,.2f}
   • Total Projected Corpus: ₹{total_future_corpus:,.2f}

{'='*70}
{'🔴 SHORTFALL ANALYSIS ' + '🔴'*50 if shortfall > 0 else '🟢 SURPLUS ANALYSIS ' + '🟢'*50}
{'='*70}

   • {'Shortfall' if shortfall > 0 else 'Surplus'}: ₹{abs(shortfall):,.2f}
   • Percentage of Need: {(total_future_corpus/corpus_needed)*100:.1f}%

"""
        
        if shortfall > 0:
            result += f"""
   • Additional Monthly Savings Needed: ₹{additional_savings_needed:,.2f}
   • Recommendation: Increase monthly savings by ₹{additional_savings_needed:,.2f}
"""
        else:
            result += f"""
   • You have a surplus of ₹{shortfall:,.2f}!
   • Your retirement plan looks healthy! ✅
"""
        
        result += f"""
{'='*70}
💰 MONTHLY WITHDRAWAL DURING RETIREMENT:
   • You can withdraw approximately ₹{monthly_withdrawal:,.2f} per month
   • This will last for {years_in_retirement} years of retirement

📌 RECOMMENDATIONS:
"""
        
        if shortfall > 0:
            result += f"""   1. Increase monthly savings by ₹{additional_savings_needed:,.2f}
   2. Consider higher return investments (8-12% returns)
   3. Reduce expected expenses or extend retirement age
   4. Start additional SIP or investment plans
"""
        else:
            result += f"""   1. Your current savings plan is sufficient! 🎉
   2. Consider investing the surplus for legacy planning
   3. Review plan annually and adjust for inflation
"""
        
        result += f"""
{'='*70}
        """
        
        retirement_result_text.delete(1.0, END)
        retirement_result_text.insert(1.0, result)
        
    except Exception as e:
        messagebox.showerror("Calculation Error", f"Please check all inputs!\n\nError: {str(e)}")

def clear_retirement():
    current_age_entry.delete(0, END)
    retirement_age_entry.delete(0, END)
    life_span_entry.delete(0, END)
    monthly_expense_entry.delete(0, END)
    monthly_savings_entry.delete(0, END)
    current_savings_entry.delete(0, END)
    return_rate_entry.delete(0, END)
    return_rate_entry.insert(0, "12")
    inflation_rate_entry.delete(0, END)
    inflation_rate_entry.insert(0, "6")
    healthcare_entry.delete(0, END)
    healthcare_entry.insert(0, "0")
    travel_entry.delete(0, END)
    travel_entry.insert(0, "0")
    other_entry.delete(0, END)
    other_entry.insert(0, "0")
    retirement_result_text.delete(1.0, END)

# Buttons for Retirement
retirement_btn_frame = Frame(retirement_main, bg="#1a1a2e")
retirement_btn_frame.pack(pady=10)

Button(retirement_btn_frame, text="📊 Cal Retirement Plan", command=calculate_retirement,
       bg="#e94560", fg="#ffffff", font=("Consolas", 11, "bold"), width=25).pack(side=LEFT, padx=5)
Button(retirement_btn_frame, text="🗑️Clear All", command=clear_retirement,
       bg="#ff6b6b", fg="#ffffff", font=("Consolas", 11), width=15).pack(side=LEFT, padx=5)

# =========================
# PPF CALCULATOR 
# =========================

ppf_frame = Frame(finance_tabs, bg="#1a1a2e")
finance_tabs.add(ppf_frame, text="PPF Calculator")

# Create main frame with scrollbar for PPF
ppf_main_container = Frame(ppf_frame, bg="#1a1a2e")
ppf_main_container.pack(fill="both", expand=True)

# Create canvas and scrollbar for PPF results
ppf_canvas = Canvas(ppf_main_container, bg="#1a1a2e", highlightthickness=0)
ppf_scrollbar = Scrollbar(ppf_main_container, orient="vertical", command=ppf_canvas.yview)
ppf_scrollable_frame = Frame(ppf_canvas, bg="#1a1a2e")

ppf_scrollable_frame.bind(
    "<Configure>",
    lambda e: ppf_canvas.configure(scrollregion=ppf_canvas.bbox("all"))
)

ppf_canvas.create_window((0, 0), window=ppf_scrollable_frame, anchor="nw")
ppf_canvas.configure(yscrollcommand=ppf_scrollbar.set)

ppf_canvas.pack(side="left", fill="both", expand=True)
ppf_scrollbar.pack(side="right", fill="y")

# Main content frame (scrollable)
ppf_main = Frame(ppf_scrollable_frame, bg="#1a1a2e")
ppf_main.pack(padx=20, pady=20, fill="both", expand=True)

# Title
Label(ppf_main, text="🏦 PUBLIC PROVIDENT FUND (PPF) CALCULATOR", 
      font=("Consolas", 16, "bold"), bg="#1a1a2e", fg="#00ff88").pack(pady=15)

# PPF Info Frame
ppf_info = LabelFrame(ppf_main, text="PPF Information", font=("Consolas", 11, "bold"), 
                      bg="#1a1a2e", fg="#00d4ff", padx=15, pady=10)
ppf_info.pack(fill="x", pady=10)

# PPF Input Frame
ppf_input_frame = LabelFrame(ppf_main, text="Investment Details", 
                             font=("Consolas", 12, "bold"), bg="#1a1a2e", 
                             fg="#ffffff", padx=15, pady=10)
ppf_input_frame.pack(fill="x", pady=10)

Label(ppf_input_frame, text="Annual Investment Amount (₹):", font=("Consolas", 10), 
      bg="#1a1a2e", fg="#ffffff").grid(row=0, column=0, sticky="w", pady=8, padx=5)
ppf_annual_entry = Entry(ppf_input_frame, width=15, font=("Consolas", 10),
                         bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
ppf_annual_entry.grid(row=0, column=1, pady=8, padx=5)
Label(ppf_input_frame, text="(Min: ₹500, Max: ₹1,50,000)", font=("Consolas", 8), 
      fg="#888888", bg="#1a1a2e").grid(row=0, column=2, sticky="w", padx=5)

Label(ppf_input_frame, text="Interest Rate (% p.a.):", font=("Consolas", 10), 
      bg="#1a1a2e", fg="#ffffff").grid(row=1, column=0, sticky="w", pady=8, padx=5)
ppf_rate_entry = Entry(ppf_input_frame, width=15, font=("Consolas", 10),
                       bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
ppf_rate_entry.grid(row=1, column=1, pady=8, padx=5)
ppf_rate_entry.insert(0, "7.1")
Label(ppf_input_frame, text="(Current rate: 7.1%)", font=("Consolas", 8), 
      fg="#888888", bg="#1a1a2e").grid(row=1, column=2, sticky="w", padx=5)

Label(ppf_input_frame, text="Time Period (Years):", font=("Consolas", 10), 
      bg="#1a1a2e", fg="#ffffff").grid(row=2, column=0, sticky="w", pady=8, padx=5)
ppf_years_entry = Entry(ppf_input_frame, width=15, font=("Consolas", 10),
                        bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
ppf_years_entry.grid(row=2, column=1, pady=8, padx=5)
ppf_years_entry.insert(0, "15")
Label(ppf_input_frame, text="(Minimum: 15 years)", font=("Consolas", 8), 
      fg="#888888", bg="#1a1a2e").grid(row=2, column=2, sticky="w", padx=5)

# Partial Withdrawal Frame
withdrawal_frame = LabelFrame(ppf_main, text="Partial Withdrawal (Available from 7th year onwards)", 
                              font=("Consolas", 12, "bold"), bg="#1a1a2e", 
                              fg="#ffffff", padx=15, pady=10)
withdrawal_frame.pack(fill="x", pady=10)

Label(withdrawal_frame, text="Do you want to calculate partial withdrawal?", 
      font=("Consolas", 10, "bold"), bg="#1a1a2e", fg="#e67e22").grid(row=0, column=0, columnspan=3, pady=5, sticky="w", padx=5)

Label(withdrawal_frame, text="Withdrawal Year (7-15):", font=("Consolas", 10), 
      bg="#1a1a2e", fg="#ffffff").grid(row=1, column=0, sticky="w", pady=5, padx=5)
withdrawal_year_entry = Entry(withdrawal_frame, width=10, font=("Consolas", 10),
                              bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
withdrawal_year_entry.grid(row=1, column=1, pady=5, padx=5)
Label(withdrawal_frame, text="(e.g., 10 - leave blank if no withdrawal)", 
      font=("Consolas", 8), fg="#888888", bg="#1a1a2e").grid(row=1, column=2, sticky="w", padx=5)

Label(withdrawal_frame, text="Withdrawal Amount (₹):", font=("Consolas", 10), 
      bg="#1a1a2e", fg="#ffffff").grid(row=2, column=0, sticky="w", pady=5, padx=5)
withdrawal_amount_entry = Entry(withdrawal_frame, width=15, font=("Consolas", 10),
                                bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
withdrawal_amount_entry.grid(row=2, column=1, pady=5, padx=5)
Label(withdrawal_frame, text="(Max: 50% of previous year's balance)", 
      font=("Consolas", 8), fg="#888888", bg="#1a1a2e").grid(row=2, column=2, sticky="w", padx=5)

# ==================================================
# PPF CALCULATION FUNCTIONS - DEFINED BEFORE BUTTONS
# ==================================================

def calculate_ppf():
    """Calculate PPF maturity and partial withdrawal"""
    try:
        annual_investment = float(ppf_annual_entry.get())
        interest_rate = float(ppf_rate_entry.get()) / 100
        years = int(ppf_years_entry.get())
        
        if annual_investment < 500:
            messagebox.showerror("Error", "Minimum annual investment is ₹500!")
            return
        if annual_investment > 150000:
            messagebox.showerror("Error", "Maximum annual investment is ₹1,50,000!")
            return
        if years < 15:
            messagebox.showerror("Error", "PPF minimum lock-in period is 15 years!")
            return
        if years > 50:
            messagebox.showerror("Error", "Maximum period is 50 years (15 years + 5-year blocks)!")
            return
        
        total_investment = annual_investment * years
        yearly_balances = []
        balance = 0
        
        for year in range(1, years + 1):
            balance = balance + annual_investment
            balance = balance * (1 + interest_rate)
            yearly_balances.append({
                'year': year,
                'balance': balance,
                'investment': annual_investment * year,
                'interest': balance - (annual_investment * year)
            })
        
        maturity_amount = balance
        interest_earned = maturity_amount - total_investment
        
        partial_withdrawal_info = None
        
        if withdrawal_year_entry.get().strip():
            withdrawal_year = int(withdrawal_year_entry.get())
            withdrawal_amount = float(withdrawal_amount_entry.get()) if withdrawal_amount_entry.get().strip() else 0
            
            if 7 <= withdrawal_year <= 15:
                if withdrawal_year == 1:
                    balance_before = 0
                else:
                    balance_before = yearly_balances[withdrawal_year - 2]['balance']
                
                max_withdrawal = balance_before * 0.5
                
                if withdrawal_amount <= max_withdrawal:
                    balance_after_withdrawal = yearly_balances[withdrawal_year - 1]['balance'] - withdrawal_amount
                    
                    for year in range(withdrawal_year + 1, years + 1):
                        balance_after_withdrawal = (balance_after_withdrawal + annual_investment) * (1 + interest_rate)
                    
                    remaining_balance = balance_after_withdrawal
                    reduced_interest = remaining_balance - (annual_investment * years - withdrawal_amount)
                    
                    partial_withdrawal_info = {
                        'year': withdrawal_year,
                        'amount': withdrawal_amount,
                        'max_allowed': max_withdrawal,
                        'balance_before': balance_before,
                        'balance_after_withdrawal': yearly_balances[withdrawal_year - 1]['balance'],
                        'remaining_maturity': remaining_balance,
                        'reduced_interest': reduced_interest
                    }
                else:
                    messagebox.showwarning("Warning", f"Maximum withdrawal allowed at year {withdrawal_year} is ₹{max_withdrawal:,.2f}")
                    return
            else:
                messagebox.showwarning("Warning", "Partial withdrawal is only allowed from year 7 to 15!")
                return
        
        result = f"""
{'='*80}
                        PPF CALCULATION REPORT
{'='*80}

📊 INVESTMENT DETAILS:
   • Annual Investment: ₹{annual_investment:,.2f}
   • Interest Rate: {interest_rate*100:.2f}% p.a.
   • Investment Period: {years} years
   • Total Investment: ₹{total_investment:,.2f}

💰 MATURITY DETAILS:
   • Maturity Amount (After {years} years): ₹{maturity_amount:,.2f}
   • Total Interest Earned: ₹{interest_earned:,.2f}
   • Effective Total Return: {((maturity_amount/total_investment) - 1)*100:.2f}%
   • CAGR Return: {(((maturity_amount/total_investment) ** (1/years)) - 1)*100:.2f}% p.a.

{'='*80}
📈 YEAR-WISE BREAKDOWN:
{'─'*80}
 Year    Balance (₹)        Investment (₹)     Interest (₹)     Yearly Return
{'─'*80}
"""
        
        for i, y in enumerate(yearly_balances):
            if i == 0:
                yearly_return = y['interest']
            else:
                yearly_return = y['interest'] - yearly_balances[i-1]['interest']
            result += f" {y['year']:3d}   {y['balance']:14,.2f}   {y['investment']:12,.2f}   {y['interest']:12,.2f}   {yearly_return:12,.2f}\n"
        
        result += f"""
{'='*80}
"""
        
        if partial_withdrawal_info:
            result += f"""
🏦 PARTIAL WITHDRAWAL ANALYSIS:
   ✓ Withdrawal Year: {partial_withdrawal_info['year']}
   ✓ Balance Before Withdrawal: ₹{partial_withdrawal_info['balance_after_withdrawal']:,.2f}
   ✓ Withdrawal Amount: ₹{partial_withdrawal_info['amount']:,.2f}
   ✓ Maximum Allowed (50% of previous year): ₹{partial_withdrawal_info['max_allowed']:,.2f}
   ✓ Balance After Withdrawal: ₹{partial_withdrawal_info['balance_after_withdrawal'] - partial_withdrawal_info['amount']:,.2f}
   
   📉 IMPACT ON MATURITY:
   • Original Maturity Amount: ₹{maturity_amount:,.2f}
   • New Maturity Amount after Withdrawal: ₹{partial_withdrawal_info['remaining_maturity']:,.2f}
   • Reduction in Maturity Amount: ₹{maturity_amount - partial_withdrawal_info['remaining_maturity']:,.2f}
   • Reduced Interest Earned: ₹{partial_withdrawal_info['reduced_interest']:,.2f}
"""
        else:
            result += """
🏦 PARTIAL WITHDRAWAL:
   • No partial withdrawal calculated
   • To calculate, enter withdrawal year (7-15) and amount
   • Maximum withdrawal: 50% of previous year's balance
"""
        
        result += f"""
{'='*80}
📌 IMPORTANT NOTES:
   1. PPF has a 15-year lock-in period (can be extended in 5-year blocks)
   2. Partial withdrawals allowed from 7th financial year onwards
   3. Loan facility available from 3rd to 6th year
   4. Tax-free returns under Section 80C (up to ₹1.5 lakh per year)
   5. Interest rate is revised quarterly by the Government of India
   6. PPF comes under EEE (Exempt-Exempt-Exempt) tax category
{'='*80}
"""
        
        ppf_result_text.delete(1.0, END)
        ppf_result_text.insert(1.0, result)
        
    except ValueError as e:
        messagebox.showerror("Input Error", f"Please enter valid numbers!\n\nError: {str(e)}")
    except Exception as e:
        messagebox.showerror("Calculation Error", f"An error occurred!\n\nError: {str(e)}")

def clear_ppf():
    """Clear all input fields and results"""
    ppf_annual_entry.delete(0, END)
    ppf_rate_entry.delete(0, END)
    ppf_rate_entry.insert(0, "7.1")
    ppf_years_entry.delete(0, END)
    ppf_years_entry.insert(0, "15")
    withdrawal_year_entry.delete(0, END)
    withdrawal_amount_entry.delete(0, END)
    ppf_result_text.delete(1.0, END)

def reset_ppf_defaults():
    """Reset to default values"""
    ppf_annual_entry.delete(0, END)
    ppf_annual_entry.insert(0, "50000")
    ppf_rate_entry.delete(0, END)
    ppf_rate_entry.insert(0, "7.1")
    ppf_years_entry.delete(0, END)
    ppf_years_entry.insert(0, "15")
    withdrawal_year_entry.delete(0, END)
    withdrawal_amount_entry.delete(0, END)
    ppf_result_text.delete(1.0, END)
    messagebox.showinfo("Reset", "Default values loaded!\nAnnual Investment: ₹50,000\nRate: 7.1%\nPeriod: 15 years")

def load_ppf_example():
    """Load example values for demonstration"""
    ppf_annual_entry.delete(0, END)
    ppf_annual_entry.insert(0, "50000")
    ppf_rate_entry.delete(0, END)
    ppf_rate_entry.insert(0, "7.1")
    ppf_years_entry.delete(0, END)
    ppf_years_entry.insert(0, "15")
    withdrawal_year_entry.delete(0, END)
    withdrawal_amount_entry.delete(0, END)
    messagebox.showinfo("Example Loaded", "Example values loaded:\nAnnual Investment: ₹50,000\nRate: 7.1%\nPeriod: 15 years\n\nClick 'Calculate' to see results!")

# ==================================================
# BUTTON FRAME - CREATED AFTER FUNCTIONS ARE DEFINED
# ==================================================

ppf_button_frame = Frame(ppf_main, bg="#1a1a2e")
ppf_button_frame.pack(pady=15)

Button(ppf_button_frame, text="📊 Cal PPF Maturity", command=calculate_ppf,
       bg="#e94560", fg="#ffffff", font=("Consolas", 11, "bold"), width=22, height=1).pack(side=LEFT, padx=5)

Button(ppf_button_frame, text="🗑️Clear All", command=clear_ppf,
       bg="#ff6b6b", fg="#ffffff", font=("Consolas", 11, "bold"), width=15, height=1).pack(side=LEFT, padx=5)

Button(ppf_button_frame, text="🔄Reset Default", command=reset_ppf_defaults,
       bg="#533483", fg="#ffffff", font=("Consolas", 11, "bold"), width=18, height=1).pack(side=LEFT, padx=5)

Button(ppf_button_frame, text="📝Load Example", command=load_ppf_example,
       bg="#00b894", fg="#ffffff", font=("Consolas", 11, "bold"), width=15, height=1).pack(side=LEFT, padx=5)

# Result Display Area (with scrollbar)
ppf_result_frame = LabelFrame(ppf_main, text="Calculation Results", 
                              font=("Consolas", 11, "bold"), bg="#1a1a2e", 
                              fg="#ffffff", padx=10, pady=10)
ppf_result_frame.pack(fill="both", expand=True, pady=10)

ppf_result_container = Frame(ppf_result_frame, bg="#1a1a2e")
ppf_result_container.pack(fill="both", expand=True)

ppf_result_scrollbar = Scrollbar(ppf_result_container)
ppf_result_scrollbar.pack(side=RIGHT, fill=Y)

ppf_result_text = Text(ppf_result_container, height=20, width=90, 
                       font=("Consolas", 9), wrap=WORD, 
                       yscrollcommand=ppf_result_scrollbar.set,
                       bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
ppf_result_text.pack(side=LEFT, fill="both", expand=True, padx=5, pady=5)
ppf_result_scrollbar.config(command=ppf_result_text.yview)

# Help text
help_text = Label(ppf_main, text="💡 Tip: PPF interest is compounded annually. Partial withdrawals reduce final maturity amount.",
                  font=("Consolas", 8, "italic"), bg="#1a1a2e", fg="#666666")
help_text.pack(pady=5)

# =========================
# BMI PAGE
# =========================

bmi_page = Frame(content, bg="#1a1a2e")
pages["BMI"] = bmi_page

bmi_main_frame = Frame(bmi_page, bg="#1a1a2e")
bmi_main_frame.pack(expand=True, fill=BOTH, padx=20, pady=20)

Label(bmi_main_frame, text="BMI Calculator", font=("Consolas", 18, "bold"), 
      bg="#1a1a2e", fg="#00ff88").pack(pady=10)

weight_frame = Frame(bmi_main_frame, bg="#1a1a2e")
weight_frame.pack(pady=5)
Label(weight_frame, text="Weight:", font=("Consolas", 12), 
      bg="#1a1a2e", fg="#ffffff").pack(side=LEFT, padx=5)
weight_entry = Entry(weight_frame, width=15, font=("Consolas", 11),
                     bg="#0f0f1a", fg="#00ff88")
weight_entry.pack(side=LEFT, padx=5)
weight_unit = ttk.Combobox(weight_frame, values=["kg", "lbs"], width=5)
weight_unit.set("kg")
weight_unit.pack(side=LEFT)

height_frame = Frame(bmi_main_frame, bg="#1a1a2e")
height_frame.pack(pady=5)
Label(height_frame, text="Height:", font=("Consolas", 12), 
      bg="#1a1a2e", fg="#ffffff").pack(side=LEFT, padx=5)
height_entry = Entry(height_frame, width=15, font=("Consolas", 11),
                     bg="#0f0f1a", fg="#00ff88")
height_entry.pack(side=LEFT, padx=5)
height_unit = ttk.Combobox(height_frame, values=["m", "cm", "ft"], width=5)
height_unit.set("m")
height_unit.pack(side=LEFT)

bmi_result = Label(bmi_main_frame, text="", font=("Consolas", 14), 
                   bg="#1a1a2e", fg="#00d4ff")
bmi_result.pack(pady=20)

def calculate_bmi():
    try:
        weight = float(weight_entry.get())
        height = float(height_entry.get())
        
        if weight_unit.get() == "lbs":
            weight = weight * 0.453592
        if height_unit.get() == "cm":
            height = height / 100
        elif height_unit.get() == "ft":
            height = height * 0.3048
        
        bmi = weight / (height ** 2)
        
        if bmi < 18.5:
            status = "Underweight"
        elif bmi < 25:
            status = "Normal weight"
        elif bmi < 30:
            status = "Overweight"
        else:
            status = "Obese"
        
        bmi_result.config(text=f"BMI = {bmi:.2f}\nStatus: {status}")
    except:
        messagebox.showerror("Error", "Invalid Input")

Button(bmi_main_frame, text="Calculate BMI", command=calculate_bmi, 
       bg="#e94560", fg="#ffffff", font=("Consolas", 12), width=15).pack(pady=10)

# =========================
# AGE CALCULATOR PAGE
# =========================

age_page = Frame(content, bg="#1a1a2e")
pages["Age Calculator"] = age_page

age_main_frame = Frame(age_page, bg="#1a1a2e")
age_main_frame.pack(expand=True, fill=BOTH, padx=20, pady=20)

Label(age_main_frame, text="Age Calculator", font=("Consolas", 18, "bold"), 
      bg="#1a1a2e", fg="#00ff88").pack(pady=10)

Label(age_main_frame, text="Date of Birth (YYYY-MM-DD):", 
      bg="#1a1a2e", fg="#ffffff").pack()
dob_entry = Entry(age_main_frame, width=25, font=("Consolas", 11),
                  bg="#0f0f1a", fg="#00ff88")
dob_entry.pack(pady=5)

age_result = Label(age_main_frame, text="", font=("Consolas", 11), 
                   bg="#1a1a2e", fg="#00d4ff")
age_result.pack(pady=20)

def calculate_age():
    try:
        dob = datetime.strptime(dob_entry.get(), "%Y-%m-%d").date()
        today = date.today()
        years = today.year - dob.year
        months = today.month - dob.month
        days = today.day - dob.day
        
        if days < 0:
            months -= 1
            if today.month == 1:
                prev_month = date(today.year - 1, 12, 1)
            else:
                prev_month = date(today.year, today.month - 1, 1)
            if prev_month.month == 2:
                if (prev_month.year % 4 == 0 and prev_month.year % 100 != 0) or (prev_month.year % 400 == 0):
                    days_in_prev_month = 29
                else:
                    days_in_prev_month = 28
            elif prev_month.month in [4, 6, 9, 11]:
                days_in_prev_month = 30
            else:
                days_in_prev_month = 31
            days += days_in_prev_month
        
        if months < 0:
            months += 12
            years -= 1
        
        age_result.config(text=f"Age: {years} years, {months} months, {days} days")
        messagebox.showinfo("Age", f"Your age is:\n{years} years\n{months} months\n{days} days")
    except:
        messagebox.showerror("Error", "Invalid Date Format! Use YYYY-MM-DD")

Button(age_main_frame, text="Calculate Age", command=calculate_age, 
       bg="#e94560", fg="#ffffff", font=("Consolas", 12), width=15).pack(pady=10)

# =========================
# UNIT CONVERTER PAGE 
# =========================

unit_page = Frame(content, bg="#1a1a2e")
pages["Unit Converter"] = unit_page

# ===== SUB-NAVIGATION BAR =====
sub_nav_frame = Frame(unit_page, bg="#0f0f1a", height=50)
sub_nav_frame.pack(fill="x", pady=(0, 10))
sub_nav_frame.pack_propagate(False)

# Sub-navigation buttons
sub_buttons = []

def show_unit_subpage(page_name):
    """Show selected sub-page in unit converter"""
    # Hide all sub-pages
    for page in unit_sub_pages.values():
        page.pack_forget()
    # Show selected sub-page
    unit_sub_pages[page_name].pack(fill="both", expand=True, padx=20, pady=10)
    
    # Update button colors
    for btn, name in sub_buttons:
        if name == page_name:
            btn.config(bg="#533483", fg="#ffffff")
        else:
            btn.config(bg="#2d2d44", fg="#888888")

# Create sub-navigation buttons
sub_menu_items = [
    ("📐 Length", "Length"),
    ("⚖️ Weight", "Weight"),
    ("🌡️ Temperature", "Temperature")
]

for text, page_name in sub_menu_items:
    btn = Button(sub_nav_frame, text=text, font=("Segoe UI", 10, "bold"),
                 bg="#2d2d44", fg="#888888", bd=0, padx=20, pady=8,
                 command=lambda p=page_name: show_unit_subpage(p),
                 activebackground="#533483", activeforeground="#ffffff",
                 relief="flat", cursor="hand2")
    btn.pack(side=LEFT, padx=2, pady=5)
    sub_buttons.append((btn, page_name))

# ===== SUB-PAGES CONTAINER =====
unit_sub_pages = {}

# ===== LENGTH SUB-PAGE =====
length_sub_page = Frame(unit_page, bg="#1a1a2e")
unit_sub_pages["Length"] = length_sub_page

length_main = Frame(length_sub_page, bg="#1a1a2e")
length_main.pack(fill="both", expand=True)

Label(length_main, text="📐 LENGTH CONVERTER", font=("Consolas", 16, "bold"), 
      bg="#1a1a2e", fg="#00ff88").pack(pady=(0, 15))

length_units = {"Meters": 1, "Kilometers": 1000, "Centimeters": 0.01, "Millimeters": 0.001, 
                "Miles": 1609.34, "Feet": 0.3048, "Inches": 0.0254, "Yards": 0.9144}

# Input Frame
input_frame = Frame(length_main, bg="#1a1a2e")
input_frame.pack(fill="x", pady=5)

Label(input_frame, text="Enter Value:", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
length_value = Entry(input_frame, width=20, font=("Consolas", 12),
                     bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
length_value.pack(fill="x", pady=3, ipady=5)

# From Unit
Label(length_main, text="From Unit:", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
length_from = ttk.Combobox(length_main, values=list(length_units.keys()), width=20, 
                           font=("Consolas", 11))
length_from.set("Meters")
length_from.pack(fill="x", pady=3)

# To Unit
Label(length_main, text="To Unit:", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
length_to = ttk.Combobox(length_main, values=list(length_units.keys()), width=20, 
                         font=("Consolas", 11))
length_to.set("Feet")
length_to.pack(fill="x", pady=3)

# Result Display
length_result = Label(length_main, text="", font=("Consolas", 14, "bold"), 
                      bg="#1a1a2e", fg="#00d4ff")
length_result.pack(pady=15)

def convert_length():
    try:
        val = float(length_value.get())
        from_unit = length_from.get()
        to_unit = length_to.get()
        meters = val * length_units[from_unit]
        result = meters / length_units[to_unit]
        length_result.config(text=f"✅ {val:.4f} {from_unit} = {result:.4f} {to_unit}")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number!")
    except:
        messagebox.showerror("Error", "Invalid Input")

Button(length_main, text="🔄 Convert", command=convert_length, 
       bg="#e94560", fg="#ffffff", font=("Consolas", 12, "bold"), 
       width=20, height=1).pack(pady=10)

# ===== WEIGHT SUB-PAGE =====
weight_sub_page = Frame(unit_page, bg="#1a1a2e")
unit_sub_pages["Weight"] = weight_sub_page

weight_main = Frame(weight_sub_page, bg="#1a1a2e")
weight_main.pack(fill="both", expand=True)

Label(weight_main, text="⚖️ WEIGHT CONVERTER", font=("Consolas", 16, "bold"), 
      bg="#1a1a2e", fg="#00ff88").pack(pady=(0, 15))

weight_units = {"Kilograms": 1, "Grams": 0.001, "Pounds": 0.453592, "Ounces": 0.0283495,
                "Milligrams": 0.000001, "Metric Tons": 1000}

# Input Frame
input_frame = Frame(weight_main, bg="#1a1a2e")
input_frame.pack(fill="x", pady=5)

Label(input_frame, text="Enter Value:", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
weight_value = Entry(input_frame, width=20, font=("Consolas", 12),
                     bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
weight_value.pack(fill="x", pady=3, ipady=5)

# From Unit
Label(weight_main, text="From Unit:", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
weight_from = ttk.Combobox(weight_main, values=list(weight_units.keys()), width=20,
                           font=("Consolas", 11))
weight_from.set("Kilograms")
weight_from.pack(fill="x", pady=3)

# To Unit
Label(weight_main, text="To Unit:", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
weight_to = ttk.Combobox(weight_main, values=list(weight_units.keys()), width=20,
                         font=("Consolas", 11))
weight_to.set("Pounds")
weight_to.pack(fill="x", pady=3)

# Result Display
weight_result = Label(weight_main, text="", font=("Consolas", 14, "bold"), 
                      bg="#1a1a2e", fg="#00d4ff")
weight_result.pack(pady=15)

def convert_weight():
    try:
        val = float(weight_value.get())
        from_unit = weight_from.get()
        to_unit = weight_to.get()
        kg = val * weight_units[from_unit]
        result = kg / weight_units[to_unit]
        weight_result.config(text=f"✅ {val:.4f} {from_unit} = {result:.4f} {to_unit}")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number!")
    except:
        messagebox.showerror("Error", "Invalid Input")

Button(weight_main, text="🔄 Convert", command=convert_weight, 
       bg="#e94560", fg="#ffffff", font=("Consolas", 12, "bold"), 
       width=20, height=1).pack(pady=10)

# ===== TEMPERATURE SUB-PAGE =====
temp_sub_page = Frame(unit_page, bg="#1a1a2e")
unit_sub_pages["Temperature"] = temp_sub_page

temp_main = Frame(temp_sub_page, bg="#1a1a2e")
temp_main.pack(fill="both", expand=True)

Label(temp_main, text="🌡️ TEMPERATURE CONVERTER", font=("Consolas", 16, "bold"), 
      bg="#1a1a2e", fg="#00ff88").pack(pady=(0, 15))

temp_units = ["Celsius", "Fahrenheit", "Kelvin"]

# Input Frame
input_frame = Frame(temp_main, bg="#1a1a2e")
input_frame.pack(fill="x", pady=5)

Label(input_frame, text="Enter Value:", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
temp_value = Entry(input_frame, width=20, font=("Consolas", 12),
                   bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
temp_value.pack(fill="x", pady=3, ipady=5)

# From Unit
Label(temp_main, text="From Unit:", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
temp_from = ttk.Combobox(temp_main, values=temp_units, width=20, font=("Consolas", 11))
temp_from.set("Celsius")
temp_from.pack(fill="x", pady=3)

# To Unit
Label(temp_main, text="To Unit:", font=("Consolas", 11), 
      bg="#1a1a2e", fg="#ffffff").pack(anchor="w", pady=3)
temp_to = ttk.Combobox(temp_main, values=temp_units, width=20, font=("Consolas", 11))
temp_to.set("Fahrenheit")
temp_to.pack(fill="x", pady=3)

# Result Display
temp_result = Label(temp_main, text="", font=("Consolas", 14, "bold"), 
                    bg="#1a1a2e", fg="#00d4ff")
temp_result.pack(pady=15)

def convert_temperature():
    try:
        val = float(temp_value.get())
        from_unit = temp_from.get()
        to_unit = temp_to.get()
        
        # Convert to Celsius first
        if from_unit == "Celsius":
            celsius = val
        elif from_unit == "Fahrenheit":
            celsius = (val - 32) * 5/9
        elif from_unit == "Kelvin":
            celsius = val - 273.15
        
        # Convert from Celsius to target
        if to_unit == "Celsius":
            result = celsius
        elif to_unit == "Fahrenheit":
            result = (celsius * 9/5) + 32
        elif to_unit == "Kelvin":
            result = celsius + 273.15
        
        temp_result.config(text=f"✅ {val:.2f} {from_unit} = {result:.2f} {to_unit}")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number!")
    except:
        messagebox.showerror("Error", "Invalid Input")

Button(temp_main, text="🔄 Convert", command=convert_temperature, 
       bg="#e94560", fg="#ffffff", font=("Consolas", 12, "bold"), 
       width=20, height=1).pack(pady=10)

# ===== SHOW DEFAULT SUB-PAGE =====
# Show Length as default
show_unit_subpage("Length")

# =========================
# CURRENCY CONVERTER PAGE 
# =========================

currency_page = Frame(content, bg="#1a1a2e")
pages["Currency"] = currency_page

currency_main_frame = Frame(currency_page, bg="#1a1a2e")
currency_main_frame.pack(expand=True, fill=BOTH, padx=20, pady=20)

Label(currency_main_frame, text="💱 CURRENCY CONVERTER", 
      font=("Consolas", 18, "bold"), bg="#1a1a2e", fg="#00ff88").pack(pady=10)

Label(currency_main_frame, text="Enter live exchange rates for accurate conversion", 
      font=("Consolas", 10), bg="#1a1a2e", fg="#888888").pack()

# Create notebook for tabs
currency_tabs = ttk.Notebook(currency_main_frame)
currency_tabs.pack(fill="both", expand=True, pady=10)

# Configure notebook style for dark theme
style = ttk.Style()
style.configure("TNotebook", background="#1a1a2e", borderwidth=0)
style.configure("TNotebook.Tab", background="#2d2d44", foreground="#0F0202", 
                padding=[10, 5], font=("Consolas", 10))
style.map("TNotebook.Tab", background=[("selected", "#533483")])

# ===== TAB 1: CURRENCY CONVERTER =====
converter_tab = Frame(currency_tabs, bg="#1a1a2e")
currency_tabs.add(converter_tab, text="💱 Currency Converter")

converter_frame = Frame(converter_tab, bg="#1a1a2e")
converter_frame.pack(padx=20, pady=20, fill="both", expand=True)

# Amount to convert
Label(converter_frame, text="Amount to Convert:", font=("Consolas", 12, "bold"), 
      bg="#1a1a2e", fg="#ffffff").pack(pady=5)
curr_amount = Entry(converter_frame, font=("Consolas", 14), width=20, justify="center",
                    bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
curr_amount.pack(pady=5)

# From Currency
Label(converter_frame, text="From Currency:", font=("Consolas", 12, "bold"), 
      bg="#1a1a2e", fg="#ffffff").pack(pady=5)
curr_from = ttk.Combobox(converter_frame, values=[], width=15, font=("Consolas", 11))
curr_from.pack(pady=5)

# To Currency
Label(converter_frame, text="To Currency:", font=("Consolas", 12, "bold"), 
      bg="#1a1a2e", fg="#ffffff").pack(pady=5)
curr_to = ttk.Combobox(converter_frame, values=[], width=15, font=("Consolas", 11))
curr_to.pack(pady=5)

# Convert Button
convert_btn = Button(converter_frame, text="💱 Convert Currency", command=lambda: convert_currency(),
                     bg="#e94560", fg="#ffffff", font=("Consolas", 12, "bold"), width=20, height=1)
convert_btn.pack(pady=15)

# Result Label
curr_result = Label(converter_frame, text="", font=("Consolas", 14, "bold"), 
                    bg="#1a1a2e", fg="#00d4ff")
curr_result.pack(pady=10)

# ===== TAB 2: MANAGE EXCHANGE RATES =====
rates_tab = Frame(currency_tabs, bg="#1a1a2e")
currency_tabs.add(rates_tab, text="💰 Manage Exchange Rates")

rates_frame = Frame(rates_tab, bg="#1a1a2e")
rates_frame.pack(padx=20, pady=20, fill="both", expand=True)

Label(rates_frame, text="Exchange Rate Manager", font=("Consolas", 14, "bold"), 
      bg="#1a1a2e", fg="#00ff88").pack(pady=10)
Label(rates_frame, text="Set exchange rates relative to USD (1 USD = ?)", 
      font=("Consolas", 10), bg="#1a1a2e", fg="#888888").pack()

# Create scrollable frame for rates
rates_canvas = Canvas(rates_frame, bg="#1a1a2e", height=300, highlightthickness=0)
rates_scrollbar = Scrollbar(rates_frame, orient="vertical", command=rates_canvas.yview)
rates_scrollable_frame = Frame(rates_canvas, bg="#1a1a2e")

rates_scrollable_frame.bind(
    "<Configure>",
    lambda e: rates_canvas.configure(scrollregion=rates_canvas.bbox("all"))
)

rates_canvas.create_window((0, 0), window=rates_scrollable_frame, anchor="nw")
rates_canvas.configure(yscrollcommand=rates_scrollbar.set)

rates_canvas.pack(side="left", fill="both", expand=True)
rates_scrollbar.pack(side="right", fill="y")

# Store rate entries
rate_entries = {}

# ==================================================
# CURRENT REAL-TIME EXCHANGE RATES (as of May 2026)
# ==================================================

# List of currencies with their codes and names
currencies_info = [
    ("USD", "US Dollar"), ("EUR", "Euro"), ("GBP", "British Pound"), 
    ("JPY", "Japanese Yen"), ("INR", "Indian Rupee"), ("CAD", "Canadian Dollar"),
    ("AUD", "Australian Dollar"), ("CHF", "Swiss Franc"), ("CNY", "Chinese Yuan"),
    ("SGD", "Singapore Dollar"), ("BRL", "Brazilian Real"), ("ZAR", "South African Rand"),
    ("RUB", "Russian Ruble"), ("KRW", "South Korean Won"), ("MXN", "Mexican Peso"),
    ("AED", "UAE Dirham"), ("SAR", "Saudi Riyal"), ("TRY", "Turkish Lira"),
    ("NZD", "New Zealand Dollar"), ("HKD", "Hong Kong Dollar"), ("THB", "Thai Baht"),
    ("MYR", "Malaysian Ringgit"), ("PHP", "Philippine Peso"), ("IDR", "Indonesian Rupiah")
]

# Current real-time exchange rates (relative to USD)
# Updated with current market rates
default_rates = {
    "USD": 1.00, 
    "EUR": 0.87,    # 1 USD = 0.93 EUR
    "GBP": 0.75,    # 1 USD = 0.79 GBP
    "JPY": 161,  # 1 USD = 149.50 JPY
    "INR": 94.33,   # 1 USD = 83.50 INR (Updated from 74.50)
    "CAD": 1.41,    # 1 USD = 1.35 CAD
    "AUD": 1.42,    # 1 USD = 1.52 AUD
    "CHF": 0.80,    # 1 USD = 0.88 CHF
    "CNY": 6.78,    # 1 USD = 7.24 CNY
    "SGD": 1.29,    # 1 USD = 1.34 SGD
    "BRL": 5.16,    # 1 USD = 4.97 BRL
    "ZAR": 16.47,   # 1 USD = 19.20 ZAR
    "RUB": 73.25,   # 1 USD = 92.50 RUB
    "KRW": 1530.00, # 1 USD = 1330.00 KRW
    "MXN": 17.34,   # 1 USD = 16.80 MXN
    "AED": 3.67,    # 1 USD = 3.67 AED
    "SAR": 3.75,    # 1 USD = 3.75 SAR
    "TRY": 46.42,   # 1 USD = 32.00 TRY
    "NZD": 1.74,    # 1 USD = 1.63 NZD
    "HKD": 7.83,    # 1 USD = 7.82 HKD
    "THB": 32.86,   # 1 USD = 36.20 THB
    "MYR": 4.13,    # 1 USD = 4.73 MYR
    "PHP": 60.73,   # 1 USD = 56.50 PHP
    "IDR": 17797.00 # 1 USD = 15600.00 IDR
}

# Load saved rates from file
def load_rates():
    try:
        import json
        import os
        if os.path.exists("exchange_rates.json"):
            with open("exchange_rates.json", "r") as f:
                return json.load(f)
    except:
        pass
    return default_rates.copy()

# Load initial rates
exchange_rates = load_rates()

# ===== FUNCTION DEFINITIONS =====

def reset_rate(code):
    """Reset individual currency rate to default"""
    default_val = default_rates.get(code, 1.0)
    if code in rate_entries:
        rate_entries[code].delete(0, END)
        rate_entries[code].insert(0, str(default_val))
    # Update exchange_rates dictionary
    exchange_rates[code] = default_val
    update_currency_lists()
    update_examples()
    messagebox.showinfo("Reset", f"{code} rate reset to {default_val}")

def reset_all_rates():
    """Reset all rates to default values"""
    for code, entry in rate_entries.items():
        default_val = default_rates.get(code, 1.0)
        entry.delete(0, END)
        entry.insert(0, str(default_val))
        exchange_rates[code] = default_val
    
    update_currency_lists()
    update_examples()
    messagebox.showinfo("Reset", "All exchange rates reset to default values!")

def save_rates():
    """Save all rates to file"""
    try:
        import json
        current_rates = {}
        for code, entry in rate_entries.items():
            try:
                current_rates[code] = float(entry.get())
            except:
                current_rates[code] = default_rates.get(code, 1.0)
        with open("exchange_rates.json", "w") as f:
            json.dump(current_rates, f)
        messagebox.showinfo("Success", "Exchange rates saved successfully!")
        update_currency_lists()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save rates: {str(e)}")

def load_latest_rates():
    """Load rates from saved file"""
    try:
        import json
        import os
        if os.path.exists("exchange_rates.json"):
            with open("exchange_rates.json", "r") as f:
                saved_rates = json.load(f)
            
            for code, entry in rate_entries.items():
                if code in saved_rates:
                    entry.delete(0, END)
                    entry.insert(0, str(saved_rates[code]))
                    exchange_rates[code] = saved_rates[code]
            
            update_currency_lists()
            update_examples()
            messagebox.showinfo("Success", "Latest saved rates loaded!")
        else:
            messagebox.showinfo("Info", "No saved rates found. Using default rates.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load rates: {str(e)}")

def update_currency_lists():
    """Update currency lists in converter tab"""
    # Update exchange_rates dictionary from entries
    for code, entry in rate_entries.items():
        try:
            exchange_rates[code] = float(entry.get())
        except:
            exchange_rates[code] = default_rates.get(code, 1.0)
    
    # Update combobox values
    currency_list = list(exchange_rates.keys())
    curr_from['values'] = currency_list
    curr_to['values'] = currency_list
    
    # Set default selections if not set
    if not curr_from.get():
        curr_from.set("USD")
    if not curr_to.get():
        curr_to.set("INR")  # Changed to INR as default target

def update_examples():
    """Update quick examples based on current rates"""
    examples_text.delete(1.0, END)
    
    examples_text.insert(END, "="*60 + "\n")
    examples_text.insert(END, "QUICK CONVERSION EXAMPLES (1 USD = ?)\n")
    examples_text.insert(END, "="*60 + "\n\n")
    
    # Show top 10 currencies
    count = 0
    for code, name in currencies_info[:10]:
        rate = exchange_rates.get(code, default_rates.get(code, 1.0))
        examples_text.insert(END, f"💰 1 USD = {rate:.4f} {code} ({name})\n")
        examples_text.insert(END, f"   • 10 USD = {rate*10:.2f} {code}\n")
        examples_text.insert(END, f"   • 100 USD = {rate*100:.2f} {code}\n")
        examples_text.insert(END, f"   • 1000 USD = {rate*1000:.2f} {code}\n\n")
        count += 1
        if count >= 8:
            break
    
    examples_text.insert(END, "="*60 + "\n")
    examples_text.insert(END, "💡 Tip: Update rates in 'Manage Exchange Rates' tab\n")
    examples_text.insert(END, "   to see real-time conversion examples!\n")
    examples_text.insert(END, "="*60)

def convert_currency():
    """Convert currency using current exchange rates"""
    try:
        # Update rates from entries
        for code, entry in rate_entries.items():
            try:
                exchange_rates[code] = float(entry.get())
            except:
                pass
        
        amount = float(curr_amount.get())
        from_curr = curr_from.get()
        to_curr = curr_to.get()
        
        if from_curr not in exchange_rates or to_curr not in exchange_rates:
            messagebox.showerror("Error", "Please select valid currencies!")
            return
        
        # Convert to USD first, then to target currency
        usd_amount = amount / exchange_rates[from_curr]
        converted = usd_amount * exchange_rates[to_curr]
        
        # Format result
        result_text = f"{amount:,.2f} {from_curr} = {converted:,.2f} {to_curr}"
        curr_result.config(text=result_text, font=("Consolas", 16, "bold"), fg="#00d4ff")
                   
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid amount!")
    except Exception as e:
        messagebox.showerror("Error", f"Conversion failed: {str(e)}")

def auto_update_rates(event=None):
    """Auto-update rates from entries"""
    for code, entry in rate_entries.items():
        try:
            exchange_rates[code] = float(entry.get())
        except:
            pass
    update_examples()

# ===== CREATE RATE INPUT FIELDS =====

# Headers with dark theme
Label(rates_scrollable_frame, text="Currency", font=("Consolas", 10, "bold"), 
      bg="#1a1a2e", fg="#00ff88").grid(row=0, column=0, padx=10, pady=5, sticky="w")
Label(rates_scrollable_frame, text="Rate (1 USD = ?)", font=("Consolas", 10, "bold"), 
      bg="#1a1a2e", fg="#00ff88").grid(row=0, column=1, padx=10, pady=5, sticky="w")
Label(rates_scrollable_frame, text="Actions", font=("Consolas", 10, "bold"), 
      bg="#1a1a2e", fg="#00ff88").grid(row=0, column=2, padx=10, pady=5, sticky="w")

row = 1
for code, name in currencies_info:
    # Currency label
    Label(rates_scrollable_frame, text=f"{code} - {name}", font=("Consolas", 9), 
          bg="#1a1a2e", fg="#ffffff").grid(row=row, column=0, padx=10, pady=3, sticky="w")
    
    # Rate entry
    rate_entry = Entry(rates_scrollable_frame, width=15, font=("Consolas", 9),
                       bg="#0f0f1a", fg="#00ff88", insertbackground="#00ff88")
    rate_entry.grid(row=row, column=1, padx=10, pady=3)
    rate_entry.insert(0, str(exchange_rates.get(code, default_rates.get(code, 1.0))))
    rate_entries[code] = rate_entry
    
    # Reset button
    reset_btn = Button(rates_scrollable_frame, text="Reset", 
                       command=lambda c=code: reset_rate(c),
                       bg="#533483", fg="#ffffff", font=("Consolas", 8), width=6)
    reset_btn.grid(row=row, column=2, padx=10, pady=3)
    
    row += 1

# ===== BUTTONS =====
rate_button_frame = Frame(rates_frame, bg="#1a1a2e")
rate_button_frame.pack(pady=15, fill="x")

# Create a sub-frame for centering
button_container = Frame(rate_button_frame, bg="#1a1a2e")
button_container.pack()

# Button 1: Save All Rates
btn_save = Button(button_container, text="💾 Save All Rates", command=save_rates,
                  bg="#00b894", fg="#ffffff", font=("Consolas", 11, "bold"), 
                  width=30, height=1, relief="raised", bd=2)
btn_save.pack(pady=4)

# Button 2: Reset All to Default
btn_reset = Button(button_container, text="🔄 Reset All to Default", command=reset_all_rates,
                   bg="#ff6b6b", fg="#ffffff", font=("Consolas", 11, "bold"), 
                   width=30, height=1, relief="raised", bd=2)
btn_reset.pack(pady=4)

# Button 3: Load Latest Rates
btn_load = Button(button_container, text="📥 Load Latest Rates", command=load_latest_rates,
                  bg="#533483", fg="#ffffff", font=("Consolas", 11, "bold"), 
                  width=30, height=1, relief="raised", bd=2)
btn_load.pack(pady=4)


# ===== STATUS BAR =====
status_frame = Frame(currency_main_frame, bg="#0f0f1a", height=25)
status_frame.pack(fill="x", side="bottom")
status_label = Label(status_frame, text="✅ Ready | Rates can be updated anytime", 
                     bg="#0f0f1a", fg="#00ff88", font=("Consolas", 9))
status_label.pack(side="left", padx=10, pady=3)

def update_status():
    """Update status bar with current rate info"""
    usd_inr = exchange_rates.get("INR", 83.50)
    usd_eur = exchange_rates.get("EUR", 0.93)
    status_label.config(text=f"💱 Live Mode | 1 USD = {usd_inr:.2f} INR | 1 USD = {usd_eur:.2f} EUR | Rates can be updated in 'Manage Exchange Rates' tab")

update_status()

# =========================
# HISTORY PAGE
# =========================

history_page = Frame(content, bg="#1a1a2e")
pages["History"] = history_page

history_box = Listbox(history_page, width=90, height=20, font=("Courier", 10),
                      bg="#0f0f1a", fg="#00ff88", selectbackground="#533483")
history_box.pack(padx=20, pady=20, expand=True, fill=BOTH)

def refresh_history():
    history_box.delete(0, END)
    conn = sqlite3.connect("calculator_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT calculation, result, timestamp FROM history ORDER BY id DESC LIMIT 50")
    for row in cursor.fetchall():
        history_box.insert(END, f"{row[2]} | {row[0]} = {row[1]}")
    conn.close()

def clear_history():
    conn = sqlite3.connect("calculator_history.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history")
    conn.commit()
    conn.close()
    refresh_history()
    messagebox.showinfo("Success", "History Cleared!")

Button(history_page, text="Refresh History", command=refresh_history, 
       bg="#533483", fg="#ffffff").pack(pady=5)
Button(history_page, text="Clear History", command=clear_history, 
       bg="#ff6b6b", fg="#ffffff").pack(pady=5)

# =========================
# SIDEBAR BUTTONS
# =========================

modules = [
    ("🧮  Basic Calculator", "Basic Calculator"),
    ("🔬  Scientific", "Scientific"),
    ("📊  Statistics", "Statistics"),
    ("💰  Finance", "Finance"),
    ("⚖️  BMI", "BMI"),
    ("📅  Age Calculator", "Age Calculator"),
    ("📏  Unit Converter", "Unit Converter"),
    ("💱  Currency", "Currency"),
    ("📜  History", "History"),
]

for display_text, page_name in modules:
    btn = Button(sidebar, text=display_text, width=18, height=2, 
                 bg="#0f0f1a", fg="#ffffff",
                 font=("Segoe UI", 10, "bold"), anchor="w",
                 activebackground="#2d2d44", activeforeground="#ffffff",
                 command=lambda x=page_name: show_page(x))
    btn.pack(pady=3, padx=5, fill=X)

# =========================
# APPLY INITIAL THEME
# =========================

apply_theme("dark")
update_theme_label()
show_page("Basic Calculator")
refresh_history()
root.mainloop()