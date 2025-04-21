import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, Text, END, WORD, CENTER, X, Y, BOTH, LEFT, RIGHT, W, E, BOTTOM, DISABLED, Frame, Label, Button, Entry
import mysql.connector  # MySQL Connector for connecting to XAMPP's MySQL

# Color scheme - Modern Dark Theme
# Coffee-inspired color theme
BACKGROUND_COLOR = "#F5EEDC"   # Soft coffee-cream background
FOREGROUND_COLOR = "#3E2723"   # Dark coffee text
ACCENT_COLOR     = "#795548"   # Coffee brown accent
COMMENT_COLOR    = "#D7CCC8"   # Light beige for inputs
GREEN_COLOR      = "#8BC34A"   # Success/Add button (light green)
YELLOW_COLOR     = "#FFCA28"   # Edit/Update button (amber yellow)
RED_COLOR        = "#F44336"   # Delete button (light red)
CYAN_COLOR       = "#03A9F4"   # View button (cyan)
ORANGE_COLOR     = "#FF7043"   # Filter buttons (orange)

# Font styles and sizes for clarity and readability
TITLE_FONT       = ("Helvetica", 28, "bold")
HEADER_FONT      = ("Helvetica", 22, "bold")
BUTTON_FONT      = ("Arial", 14)
BUTTON_FONT_BOLD = ("Arial", 14, "bold")
TEXT_FONT        = ("Arial", 13)
QUOTE_FONT       = ("Times New Roman", 20, "italic")
AUTHOR_FONT      = ("Times New Roman", 16)
CATEGORY_FONT    = ("Verdana", 13)

# --- Unique fonts for specialized windows ---
# For the Categories window:
CATEGORIES_HEADER_FONT = ("Helvetica", 22, "bold italic")
CATEGORIES_ITEM_FONT   = ("Verdana", 14, "italic")
CATEGORIES_SUBTITLE_FONT = ("Verdana", 12, "bold")
# For the Authors window:
AUTHORS_HEADER_FONT  = ("Helvetica", 22, "bold italic")
AUTHORS_ITEM_FONT    = ("Verdana", 14, "italic")
AUTHORS_SUBTITLE_FONT = ("Verdana", 12, "bold")

# Global references (used later for the main app)
app_root = None
app_tree = None
app_status_label = None
app_quote_count_label = None


# ------------------------------------------------------------------------------
# Database Connection & Initialization Functions
# ------------------------------------------------------------------------------
def get_connection():
    """Returns a connection to the MySQL database 'quotes_keeper'."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Default XAMPP password; change if needed.
        database="quotes_keeper"
    )


def initialize_database():
    """
    Connects to MySQL, creates the database 'quotes_keeper' if it doesn't exist,
    and then creates the 'users' and 'quotes' tables.
    """
    # First, create the database if not exists.
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS quotes_keeper")
    conn.commit()
    cursor.close()
    conn.close()
    # Now, connect to the 'quotes_keeper' database and create tables.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            quote_text TEXT NOT NULL,
            author VARCHAR(255) NOT NULL,
            category VARCHAR(255) NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


def create_table():
    # Minimal change: simply ensure database initialization.
    initialize_database()


def add_quote(quote, author, category, tree):
    """Insert a new quote into the MySQL database and update the tree view."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO quotes (quote_text, author, category) VALUES (%s, %s, %s)",
                   (quote, author, category))
    conn.commit()  # Save changes to the database.
    cursor.close()
    conn.close()
    load_quotes(tree)
    return True


def update_quote(quote_id, quote_text, author, category, tree):
    """Update an existing quote in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE quotes SET quote_text=%s, author=%s, category=%s WHERE id=%s",
                   (quote_text, author, category, quote_id))
    conn.commit()
    cursor.close()
    conn.close()
    load_quotes(tree)
    return True


def get_quote_by_id(quote_id):
    """Retrieve a quote from the database by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quote_text, author, category FROM quotes WHERE id=%s", (quote_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def load_quotes(tree):
    """Load quotes from the database into the Treeview control."""
    tree.delete(*tree.get_children())
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quotes")
    quotes = cursor.fetchall()
    cursor.close()
    conn.close()
    for quote in quotes:
        tree.insert("", "end", values=quote)
    update_quote_count()


def delete_quote(tree):
    """Remove the selected quote from the database."""
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a quote to delete")
        return
    quote_id = tree.item(selected[0])['values'][0]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quotes WHERE id=%s", (quote_id,))
    conn.commit()
    cursor.close()
    conn.close()
    tree.delete(selected[0])
    messagebox.showinfo("Deleted", "Quote deleted successfully.")
    update_quote_count()


def get_all_authors():
    """Get list of all unique authors from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT author FROM quotes ORDER BY author")
    authors = [author[0] for author in cursor.fetchall()]
    cursor.close()
    conn.close()
    return authors


def get_all_categories():
    """Get list of all unique categories from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM quotes ORDER BY category")
    categories = [category[0] for category in cursor.fetchall()]
    cursor.close()
    conn.close()
    return categories


def filter_quotes_by_author(tree, author):
    """Filter the quotes in the treeview by a specific author."""
    tree.delete(*tree.get_children())
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quotes WHERE author=%s ORDER BY id", (author,))
    quotes = cursor.fetchall()
    cursor.close()
    conn.close()
    for quote in quotes:
        tree.insert("", "end", values=quote)
    update_quote_count()


def filter_quotes_by_category(tree, category):
    """Filter the quotes in the treeview by a specific category."""
    tree.delete(*tree.get_children())
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quotes WHERE category=%s ORDER BY id", (category,))
    quotes = cursor.fetchall()
    cursor.close()
    conn.close()
    for quote in quotes:
        tree.insert("", "end", values=quote)
    update_quote_count()


def update_quote_count():
    if app_tree and app_quote_count_label:
        count = len(app_tree.get_children())
        app_quote_count_label.config(text=f"Total Quotes: {count}")


# ------------------------------------------------------------------------------
# Custom Entry with Placeholder
# ------------------------------------------------------------------------------
class PlaceholderEntry(Entry):
    def __init__(self, master, placeholder, **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = COMMENT_COLOR
        self.default_fg_color = FOREGROUND_COLOR
        self.insert(0, self.placeholder)
        self.config(fg=self.placeholder_color)
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, event):
        if self.get() == self.placeholder:
            self.delete(0, END)
            self.config(fg=self.default_fg_color)

    def _add_placeholder(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)

    def get_text(self):
        if self.get() == self.placeholder:
            return ""
        return self.get()


# ------------------------------------------------------------------------------
# Theme and UI Helpers
# ------------------------------------------------------------------------------
def setup_theme():
    style = ttk.Style()
    style.theme_use('clam')
    # Treeview overall style - card-like rows with padding and subtle shadows
    style.configure("Treeview",
                    background=BACKGROUND_COLOR,
                    foreground=FOREGROUND_COLOR,
                    fieldbackground=BACKGROUND_COLOR,
                    font=TEXT_FONT,
                    rowheight=80,  # Spacious rows for better readability
                    borderwidth=0,  # Remove outer border for cleaner look
                    relief="flat")
    # Add a style map to highlight selected rows with accent color and white text
    style.map("Treeview",
              background=[('selected', ACCENT_COLOR)],
              foreground=[('selected', BACKGROUND_COLOR)])
    # Treeview heading style - solid background with subtle border and bold font
    style.configure("Treeview.Heading",
                    background=COMMENT_COLOR,
                    foreground=FOREGROUND_COLOR,
                    font=BUTTON_FONT_BOLD,
                    borderwidth=1,
                    relief="solid")
    # Scrollbar styling to match theme
    style.configure("Vertical.TScrollbar",
                    background=COMMENT_COLOR,
                    troughcolor=BACKGROUND_COLOR,
                    arrowcolor=FOREGROUND_COLOR,
                    bordercolor=COMMENT_COLOR,
                    lightcolor=COMMENT_COLOR,
                    darkcolor=COMMENT_COLOR)
    style.configure("Horizontal.TScrollbar",
                    background=COMMENT_COLOR,
                    troughcolor=BACKGROUND_COLOR,
                    arrowcolor=FOREGROUND_COLOR,
                    bordercolor=COMMENT_COLOR,
                    lightcolor=COMMENT_COLOR,
                    darkcolor=COMMENT_COLOR)


def create_rounded_button(parent, text, bg_color, fg_color, command, bold=False):
    font_choice = BUTTON_FONT_BOLD if bold else BUTTON_FONT
    button = Button(parent, text=text, font=font_choice,
                    bg=bg_color, fg=fg_color,
                    command=command, bd=0, cursor="hand2",
                    activebackground=bg_color, activeforeground=fg_color,
                    highlightthickness=0, padx=20, pady=8,
                    relief="flat")
    return button


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


# ------------------------------------------------------------------------------
# Main Window and Sub-Windows
# ------------------------------------------------------------------------------
def create_main_window():
    global tree  # Make the Treeview variable global so callbacks can access it.
    root = tk.Tk()
    root.title("QuoteKeeper")
    root.geometry("1000x700")
    root.configure(bg=BACKGROUND_COLOR)
    root.minsize(800, 600)
    center_window(root, 1000, 700)
    setup_theme()

    # Header
    header_frame = Frame(root, bg=BACKGROUND_COLOR, padx=30, pady=20)
    header_frame.pack(fill=X)
    app_title_label = Label(header_frame, text="QuoteKeeper", font=TITLE_FONT, bg=BACKGROUND_COLOR, fg=ACCENT_COLOR)
    app_title_label.pack(side=LEFT)

    # Search Frame
    search_frame = Frame(header_frame, bg=BACKGROUND_COLOR)
    search_frame.pack(side=RIGHT)
    search_entry = PlaceholderEntry(search_frame,
                                    placeholder="Search quotes, authors or categories...",
                                    width=30, font=TEXT_FONT, bg=COMMENT_COLOR, fg=FOREGROUND_COLOR,
                                    insertbackground=FOREGROUND_COLOR, relief="flat")
    search_entry.pack(side=LEFT, ipady=8, padx=(0, 10))
    search_button = create_rounded_button(search_frame, "Search", ACCENT_COLOR, BACKGROUND_COLOR,
                                          lambda: search_quotes(tree, search_entry.get_text()))
    search_button.pack(side=LEFT)

    # Main Content Frame
    content_frame = Frame(root, bg=BACKGROUND_COLOR, padx=30, pady=20)
    content_frame.pack(fill=BOTH, expand=True)
    # Toolbar Buttons
    buttons_frame = Frame(content_frame, bg=BACKGROUND_COLOR, pady=15)
    buttons_frame.pack(fill=X)
    # Left Side Buttons
    left_buttons = Frame(buttons_frame, bg=BACKGROUND_COLOR)
    left_buttons.pack(side=LEFT)
    add_button = create_rounded_button(left_buttons, "Add Quote", "#8B5A36", BACKGROUND_COLOR,
                                       lambda: create_add_quote_window(tree))
    add_button.pack(side=LEFT, padx=(0, 10))
    edit_button = create_rounded_button(left_buttons, "Edit Quote", "#8B5A36", BACKGROUND_COLOR,
                                        lambda: open_edit_quote_window(tree))
    edit_button.pack(side=LEFT, padx=(0, 10))
    delete_button = create_rounded_button(left_buttons, "Delete Quote", "#8B5A36", BACKGROUND_COLOR,
                                          lambda: delete_quote(tree))
    delete_button.pack(side=LEFT, padx=(0, 10))
    """view_button = create_rounded_button(left_buttons, "View Quote", "#5D4037", BACKGROUND_COLOR,
                                        lambda: view_quote_details(tree))
    view_button.pack(side=LEFT)"""

    # Right Side Buttons
    right_buttons = Frame(buttons_frame, bg=BACKGROUND_COLOR)
    right_buttons.pack(side=RIGHT)
    authors_button = create_rounded_button(right_buttons, "Authors", ORANGE_COLOR, BACKGROUND_COLOR,
                                           lambda: list_authors(tree))
    authors_button.pack(side=RIGHT, padx=(10, 0))
    categories_button = create_rounded_button(right_buttons, "Categories", ORANGE_COLOR, BACKGROUND_COLOR,
                                              lambda: list_categories(tree))
    categories_button.pack(side=RIGHT)

    # Treeview with Scrollbars
    tree_frame = Frame(content_frame, bg=COMMENT_COLOR, pady=1, padx=1)
    tree_frame.pack(fill=BOTH, expand=True, pady=(15, 10))
    inner_tree_frame = Frame(tree_frame, bg=BACKGROUND_COLOR)
    inner_tree_frame.pack(fill=BOTH, expand=True, padx=1, pady=1)
    v_scrollbar = ttk.Scrollbar(inner_tree_frame, orient="vertical")
    h_scrollbar = ttk.Scrollbar(inner_tree_frame, orient="horizontal")
    tree = ttk.Treeview(inner_tree_frame,
                        columns=("ID", "Quote", "Author", "Category"),
                        show="headings",
                        yscrollcommand=v_scrollbar.set,
                        xscrollcommand=h_scrollbar.set)
    v_scrollbar.configure(command=tree.yview)
    h_scrollbar.configure(command=tree.xview)
    tree.heading("ID", text="")
    tree.heading("Quote", text="Quote")
    tree.heading("Author", text="Author")
    tree.heading("Category", text="Category")
    tree.column("ID", width=50, minwidth=50, anchor=CENTER)
    tree.column("Quote", width=600, minwidth=300)
    tree.column("Author", width=200, minwidth=150)
    tree.column("Category", width=150, minwidth=100)
    v_scrollbar.pack(side=RIGHT, fill=Y)
    h_scrollbar.pack(side=BOTTOM, fill=X)
    tree.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
    tree.bind("<Double-1>", lambda event: view_quote_details(tree))

    # Status Bar
    status_frame = Frame(root, bg=COMMENT_COLOR, height=30)
    status_frame.pack(fill=X, side=BOTTOM)
    status_label = Label(status_frame, text="Ready", bg=COMMENT_COLOR, fg=FOREGROUND_COLOR, anchor=W, padx=15, pady=5)
    status_label.pack(side=LEFT)
    quote_count_label = Label(status_frame, text="Total Quotes: 0", bg=COMMENT_COLOR, fg=FOREGROUND_COLOR, anchor=E, padx=15, pady=5)
    quote_count_label.pack(side=RIGHT)
    return root, tree, status_label, quote_count_label


def create_add_quote_window(tree):
    add_window = Toplevel()
    add_window.title("QuoteKeeper - Add New Quote")
    add_window.geometry("450x400")
    add_window.configure(bg=BACKGROUND_COLOR)
    add_window.transient()
    add_window.grab_set()
    center_window(add_window, 450, 400)
    title_frame = Frame(add_window, bg=BACKGROUND_COLOR, padx=20, pady=15)
    title_frame.pack(fill=X)
    title_label = Label(title_frame, text="✨ Add New Quote", font=HEADER_FONT, bg=BACKGROUND_COLOR, fg=ACCENT_COLOR)
    title_label.pack(side=LEFT)
    input_frame = Frame(add_window, bg=BACKGROUND_COLOR, padx=20, pady=10)
    input_frame.pack(fill=BOTH, expand=True)
    quote_label = Label(input_frame, text="Quote Text", font=TEXT_FONT, bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
    quote_label.pack(anchor=W, pady=(0, 5))
    quote_frame = Frame(input_frame, bg=COMMENT_COLOR, padx=2, pady=2)
    quote_frame.pack(fill=X, pady=(0, 10))
    quote_text = Text(quote_frame, height=4, font=TEXT_FONT, bg=COMMENT_COLOR, fg=FOREGROUND_COLOR,
                      insertbackground=FOREGROUND_COLOR, bd=0, padx=8, pady=8)
    quote_text.pack(fill=X, expand=True)
    author_label = Label(input_frame, text="Author", font=TEXT_FONT, bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
    author_label.pack(anchor=W, pady=(0, 5))
    author_entry = Entry(input_frame, font=TEXT_FONT, bg=COMMENT_COLOR, fg=FOREGROUND_COLOR,
                         insertbackground=FOREGROUND_COLOR, bd=0)
    author_entry.pack(fill=X, ipady=6, pady=(0, 10))
    category_label = Label(input_frame, text="Category", font=TEXT_FONT, bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
    category_label.pack(anchor=W, pady=(0, 5))
    category_entry = Entry(input_frame, font=TEXT_FONT, bg=COMMENT_COLOR, fg=FOREGROUND_COLOR,
                           insertbackground=FOREGROUND_COLOR, bd=0)
    category_entry.pack(fill=X, ipady=6)
    button_frame = Frame(add_window, bg=BACKGROUND_COLOR, padx=20, pady=15)
    button_frame.pack(fill=X)

    def save_quote():
        quote_content = quote_text.get("1.0", END).strip()
        author_content = author_entry.get().strip()
        category_content = category_entry.get().strip()
        if not quote_content or not author_content or not category_content:
            messagebox.showerror("Error", "All fields are required")
            return
        if add_quote(quote_content, author_content, category_content, tree):
            add_window.destroy()

    # Setting both "Save" and "Cancel" buttons to dark brown (#5D4037)
    save_button = create_rounded_button(button_frame, "Save", "#5D4037", BACKGROUND_COLOR, save_quote, bold=True)
    save_button.pack(side=LEFT)
    cancel_button = create_rounded_button(button_frame, "Cancel", "#5D4037", BACKGROUND_COLOR, add_window.destroy)
    cancel_button.pack(side=RIGHT)


def view_quote_details(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a quote to view")
        return
    quote_id = tree.item(selected[0])['values'][0]
    quote_data = get_quote_by_id(quote_id)
    if not quote_data:
        messagebox.showerror("Error", "Quote not found")
        return
    view_window = Toplevel()
    view_window.title("QuoteKeeper - Quote Details")
    view_window.geometry("450x350")
    view_window.configure(bg=BACKGROUND_COLOR)
    view_window.transient()
    center_window(view_window, 450, 350)
    top_bar = Frame(view_window, bg=ACCENT_COLOR, height=5)
    top_bar.pack(fill=X)
    main_frame = Frame(view_window, bg=BACKGROUND_COLOR, padx=20, pady=20)
    main_frame.pack(fill=BOTH, expand=True)
    quote_frame = Frame(main_frame, bg=BACKGROUND_COLOR)
    quote_frame.pack(fill=BOTH, expand=True)
    quote_text_widget = Text(quote_frame, font=QUOTE_FONT, bg="Black", fg="white",
                              wrap=WORD, bd=0, padx=0, pady=0, highlightthickness=0)
    quote_text_widget.pack(fill=BOTH, expand=True)
    quote_text_widget.insert(END, f'"{quote_data[0]}"\n\n')
    quote_text_widget.insert(END, f"— {quote_data[1]}", "author")
    quote_text_widget.insert(END, f"\n\nCategory: {quote_data[2]}", "category")
    quote_text_widget.tag_configure("author", font=AUTHOR_FONT, foreground="white")
    quote_text_widget.tag_configure("category", font=CATEGORY_FONT, foreground="white")
    quote_text_widget.config(state=DISABLED)
    button_frame = Frame(main_frame, bg=BACKGROUND_COLOR, pady=10)
    button_frame.pack(fill=X)
    edit_button = create_rounded_button(button_frame, "Edit", YELLOW_COLOR, BACKGROUND_COLOR,
                                        lambda: [view_window.destroy(), open_edit_quote_window(tree)])
    edit_button.pack(side=LEFT)
    close_button = create_rounded_button(button_frame, "Close", COMMENT_COLOR, FOREGROUND_COLOR,
                                         view_window.destroy)
    close_button.pack(side=RIGHT)


def open_edit_quote_window(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a quote to edit")
        return
    quote_id = tree.item(selected[0])['values'][0]
    quote_data = get_quote_by_id(quote_id)
    if not quote_data:
        messagebox.showerror("Error", "Quote not found")
        return
    edit_window = Toplevel()
    edit_window.title("QuoteKeeper - Edit Quote")
    edit_window.geometry("450x400")
    edit_window.configure(bg=BACKGROUND_COLOR)
    edit_window.transient()
    edit_window.grab_set()
    center_window(edit_window, 450, 400)
    title_frame = Frame(edit_window, bg=BACKGROUND_COLOR, padx=20, pady=15)
    title_frame.pack(fill=X)
    title_label = Label(title_frame, text="✏️ Edit Quote", font=HEADER_FONT, bg=BACKGROUND_COLOR, fg=YELLOW_COLOR)
    title_label.pack(side=LEFT)
    input_frame = Frame(edit_window, bg=BACKGROUND_COLOR, padx=20, pady=10)
    input_frame.pack(fill=BOTH, expand=True)
    quote_label = Label(input_frame, text="Quote Text", font=TEXT_FONT, bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
    quote_label.pack(anchor=W, pady=(0, 5))
    quote_frame = Frame(input_frame, bg=COMMENT_COLOR, padx=2, pady=2)
    quote_frame.pack(fill=X, pady=(0, 10))
    quote_text = Text(quote_frame, height=4, font=TEXT_FONT, bg=COMMENT_COLOR, fg=FOREGROUND_COLOR,
                      insertbackground=FOREGROUND_COLOR, bd=0, padx=8, pady=8)
    quote_text.pack(fill=X, expand=True)
    quote_text.insert(END, quote_data[0])
    author_label = Label(input_frame, text="Author", font=TEXT_FONT, bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
    author_label.pack(anchor=W, pady=(0, 5))
    author_entry = Entry(input_frame, font=TEXT_FONT, bg=COMMENT_COLOR, fg=FOREGROUND_COLOR,
                         insertbackground=FOREGROUND_COLOR, bd=0)
    author_entry.pack(fill=X, ipady=6, pady=(0, 10))
    author_entry.insert(0, quote_data[1])
    category_label = Label(input_frame, text="Category", font=TEXT_FONT, bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
    category_label.pack(anchor=W, pady=(0, 5))
    category_entry = Entry(input_frame, font=TEXT_FONT, bg=COMMENT_COLOR, fg=FOREGROUND_COLOR,
                           insertbackground=FOREGROUND_COLOR, bd=0)
    category_entry.pack(fill=X, ipady=6)
    category_entry.insert(0, quote_data[2])
    button_frame = Frame(edit_window, bg=BACKGROUND_COLOR, padx=20, pady=15)
    button_frame.pack(fill=X)

    def save_edited_quote():
        quote_content = quote_text.get("1.0", END).strip()
        author_content = author_entry.get().strip()
        category_content = category_entry.get().strip()
        if not quote_content or not author_content or not category_content:
            messagebox.showerror("Error", "All fields are required")
            return
        if update_quote(quote_id, quote_content, author_content, category_content, tree):
            messagebox.showinfo("Success", "Quote updated successfully!")
            edit_window.destroy()

    update_button = create_rounded_button(button_frame, "Update Quote", YELLOW_COLOR, BACKGROUND_COLOR,
                                          save_edited_quote, bold=True)
    update_button.pack(side=LEFT)
    cancel_button = create_rounded_button(button_frame, "Cancel", COMMENT_COLOR, FOREGROUND_COLOR,
                                          edit_window.destroy)
    cancel_button.pack(side=RIGHT)


def list_categories(tree):
    """Display a window with a list of all categories with extra features.
    Includes a search field, sort toggle, and category counts.
    Each category is clickable."""
    window = Toplevel()
    window.title("QuoteKeeper - Categories")
    window.geometry("400x600")
    window.configure(bg=BACKGROUND_COLOR)
    window.transient()
    center_window(window, 400, 600)
    # Header Frame with title and sort toggle
    header_frame = Frame(window, bg=BACKGROUND_COLOR, padx=30, pady=10)
    header_frame.pack(fill=X)
    title_label = Label(header_frame, text="🏷️ Categories", font=CATEGORIES_HEADER_FONT, bg=BACKGROUND_COLOR, fg=ORANGE_COLOR)
    title_label.pack(side=LEFT)
    sort_frame = Frame(header_frame, bg=BACKGROUND_COLOR)
    sort_frame.pack(side=RIGHT)
    sort_order = tk.StringVar(value="Asc")
    sort_btn = create_rounded_button(sort_frame, "Sort: Asc", ORANGE_COLOR, BACKGROUND_COLOR, command=lambda: None)
    sort_btn.pack()
    # Search Frame for filtering categories
    search_frame = Frame(window, bg=BACKGROUND_COLOR, padx=30, pady=10)
    search_frame.pack(fill=X)
    search_entry = Entry(search_frame, font=TEXT_FONT, bg=COMMENT_COLOR, fg=FOREGROUND_COLOR,
                         insertbackground=FOREGROUND_COLOR, bd=0)
    search_entry.pack(fill=X, ipady=8)
    # Frame for listing categories with scrollbar
    list_frame = Frame(window, bg=BACKGROUND_COLOR, padx=30, pady=10)
    list_frame.pack(fill=BOTH, expand=True)
    canvas = tk.Canvas(list_frame, bg=BACKGROUND_COLOR, highlightthickness=0)
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, bg=BACKGROUND_COLOR)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def get_quote_count_by_category(category):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM quotes WHERE category=%s", (category,))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count

    def update_category_list():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        conn = get_connection()
        cursor = conn.cursor()
        if sort_order.get() == "Asc":
            cursor.execute("SELECT DISTINCT category FROM quotes ORDER BY category ASC")
        else:
            cursor.execute("SELECT DISTINCT category FROM quotes ORDER BY category DESC")
        categories = [cat[0] for cat in cursor.fetchall()]
        cursor.close()
        conn.close()
        search_text = search_entry.get().lower()
        if search_text:
            categories = [cat for cat in categories if search_text in cat.lower()]
        for category in categories:
            count = get_quote_count_by_category(category)
            category_text = f"{category} ({count})"
            cat_frame = Frame(scrollable_frame, bg=BACKGROUND_COLOR, pady=6)
            cat_frame.pack(fill=X)
            cat_label = Label(cat_frame, text=category_text, font=CATEGORIES_ITEM_FONT, bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR, cursor="hand2")
            cat_label.pack(side=LEFT)
            cat_label.bind("<Button-1>", lambda event, c=category: (filter_quotes_by_category(tree, c), window.destroy()))
            cat_frame.bind("<Button-1>", lambda event, c=category: (filter_quotes_by_category(tree, c), window.destroy()))
    search_entry.bind("<KeyRelease>", lambda event: update_category_list())

    def toggle_sort():
        if sort_order.get() == "Asc":
            sort_order.set("Desc")
        else:
            sort_order.set("Asc")
        sort_btn.config(text=f"Sort: {sort_order.get()}")
        update_category_list()

    sort_btn.config(command=toggle_sort)
    update_category_list()  # initial population

    button_frame = Frame(window, bg=BACKGROUND_COLOR, padx=30, pady=10)
    button_frame.pack(fill=X)
    show_all_button = create_rounded_button(button_frame, "Show All Quotes", GREEN_COLOR, BACKGROUND_COLOR,
                                            lambda: [load_quotes(tree), window.destroy()])
    show_all_button.pack(side=LEFT, padx=(0, 10))
    close_button = create_rounded_button(button_frame, "Close", COMMENT_COLOR, FOREGROUND_COLOR,
                                         window.destroy)
    close_button.pack(side=RIGHT)


def list_authors(tree):
    """
    Display a window with a list of all authors with extra features.
    Includes a search field, sort toggle, and author counts.
    Each author is clickable to filter quotes.
    """
    window = Toplevel()
    window.title("QuoteKeeper - Authors")
    window.geometry("400x600")
    window.configure(bg=BACKGROUND_COLOR)
    window.transient()
    center_window(window, 400, 600)
    header_frame = Frame(window, bg=BACKGROUND_COLOR, padx=30, pady=10)
    header_frame.pack(fill=X)
    title_label = Label(header_frame, text="📚 Authors", font=AUTHORS_HEADER_FONT, bg=BACKGROUND_COLOR, fg=ORANGE_COLOR)
    title_label.pack(side=LEFT)
    sort_frame = Frame(header_frame, bg=BACKGROUND_COLOR)
    sort_frame.pack(side=RIGHT)
    sort_order = tk.StringVar(value="Asc")
    sort_btn = create_rounded_button(sort_frame, "Sort: Asc", ORANGE_COLOR, BACKGROUND_COLOR, command=lambda: None)
    sort_btn.pack()
    search_frame = Frame(window, bg=BACKGROUND_COLOR, padx=30, pady=10)
    search_frame.pack(fill=X)
    search_entry = Entry(search_frame, font=TEXT_FONT, bg=COMMENT_COLOR, fg=FOREGROUND_COLOR,
                         insertbackground=FOREGROUND_COLOR, bd=0)
    search_entry.pack(fill=X, ipady=8)
    list_frame = Frame(window, bg=BACKGROUND_COLOR, padx=30, pady=10)
    list_frame.pack(fill=BOTH, expand=True)
    canvas = tk.Canvas(list_frame, bg=BACKGROUND_COLOR, highlightthickness=0)
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, bg=BACKGROUND_COLOR)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def get_quote_count_by_author(author):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM quotes WHERE author=%s", (author,))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count

    def update_author_list():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        conn = get_connection()
        cursor = conn.cursor()
        if sort_order.get() == "Asc":
            cursor.execute("SELECT DISTINCT author FROM quotes ORDER BY author ASC")
        else:
            cursor.execute("SELECT DISTINCT author FROM quotes ORDER BY author DESC")
        authors = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        search_text = search_entry.get().lower()
        if search_text:
            authors = [auth for auth in authors if search_text in auth.lower()]
        for author in authors:
            count = get_quote_count_by_author(author)
            author_text = f"{author} ({count})"
            row_frame = Frame(scrollable_frame, bg=BACKGROUND_COLOR, pady=6)
            row_frame.pack(fill=X)
            auth_label = Label(row_frame, text=author_text, font=AUTHORS_ITEM_FONT, bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR, cursor="hand2")
            auth_label.pack(side=LEFT)
            auth_label.bind("<Button-1>", lambda event, a=author: (filter_quotes_by_author(tree, a), window.destroy()))
    search_entry.bind("<KeyRelease>", lambda event: update_author_list())

    def toggle_sort():
        if sort_order.get() == "Asc":
            sort_order.set("Desc")
        else:
            sort_order.set("Asc")
        sort_btn.config(text=f"Sort: {sort_order.get()}")
        update_author_list()

    sort_btn.config(command=toggle_sort)
    update_author_list()
    button_frame = Frame(window, bg=BACKGROUND_COLOR, padx=30, pady=10)
    button_frame.pack(fill=X)
    show_all_button = create_rounded_button(button_frame, "Show All Quotes", GREEN_COLOR, BACKGROUND_COLOR,
                                            lambda: [load_quotes(tree), window.destroy()])
    show_all_button.pack(side=LEFT, padx=(0, 10))
    close_button = create_rounded_button(button_frame, "Close", COMMENT_COLOR, FOREGROUND_COLOR,
                                         window.destroy)
    close_button.pack(side=RIGHT)


def search_quotes(tree, query):
    """Search quotes by content, author or category."""
    if not query:
        load_quotes(tree)
        return
    tree.delete(*tree.get_children())
    conn = get_connection()
    cursor = conn.cursor()
    search_term = f"%{query}%"
    query_str = (
        "SELECT * FROM quotes "
        "WHERE quote_text LIKE %s "
        "OR author LIKE %s "
        "OR category LIKE %s"
    )
    cursor.execute(query_str, (search_term, search_term, search_term))
    quotes = cursor.fetchall()
    cursor.close()
    conn.close()
    for quote in quotes:
        tree.insert("", "end", values=quote)
    if app_status_label:
        app_status_label.config(text=f"Found {len(quotes)} results for '{query}'")
    update_quote_count()


# ------------------------------------------------------------------------------
# Sign Up and Authentication Functions
# ------------------------------------------------------------------------------
def open_signup_window():
    signup_window = Toplevel()
    signup_window.title("QuoteKeeper - Sign Up")
    signup_window.geometry("400x300")
    signup_window.configure(bg=BACKGROUND_COLOR)
    center_window(signup_window, 400, 300)
    frame = Frame(signup_window, bg=BACKGROUND_COLOR, padx=20, pady=20)
    frame.pack(expand=True, fill=BOTH)
    title = Label(frame, text="Sign Up", font=HEADER_FONT, bg=BACKGROUND_COLOR, fg=ACCENT_COLOR)
    title.pack(pady=(0, 20))
    username_label = Label(frame, text="Username", font=TEXT_FONT, bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
    username_label.pack(anchor=W)
    username_entry = Entry(frame, font=TEXT_FONT, bg=COMMENT_COLOR, fg=FOREGROUND_COLOR,
                           insertbackground=FOREGROUND_COLOR, bd=0)
    username_entry.pack(fill=X, pady=(0, 10))
    password_label = Label(frame, text="Password", font=TEXT_FONT, bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
    password_label.pack(anchor=W)
    password_entry = Entry(frame, font=TEXT_FONT, show="*", bg=COMMENT_COLOR, fg=FOREGROUND_COLOR,
                           insertbackground=FOREGROUND_COLOR, bd=0)
    password_entry.pack(fill=X, pady=(0, 10))

    def signup_action():
        uname = username_entry.get().strip()
        pwd = password_entry.get().strip()
        if not uname or not pwd:
            messagebox.showerror("Error", "All fields are required")
            return
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (uname, pwd))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
            signup_window.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Username already exists or error occurred: {err}")
        finally:
            cursor.close()
            conn.close()

    signup_button = create_rounded_button(frame, "Sign Up", GREEN_COLOR, BACKGROUND_COLOR, signup_action, bold=True)
    signup_button.pack(pady=(10, 0))


def authenticate(username, password, auth_window):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        auth_window.destroy()
        root, tree, status_label, quote_count_label = create_main_window()
        create_table()  # Ensure tables exist
        load_quotes(tree)  # Load quotes from the database
        update_quote_count()
        global app_root, app_tree, app_status_label, app_quote_count_label
        app_root, app_tree, app_status_label, app_quote_count_label = root, tree, status_label, quote_count_label
        root.mainloop()
    else:
        messagebox.showerror("Error", "Invalid username or password")


def create_login_window():
    auth_window = tk.Tk()
    auth_window.title("QuoteKeeper - Login")
    auth_window.geometry("500x600")
    auth_window.configure(bg=BACKGROUND_COLOR)
    auth_window.resizable(False, False)
    center_window(auth_window, 500, 600)
    welcome_frame = Frame(auth_window, bg=BACKGROUND_COLOR, padx=40, pady=40)
    welcome_frame.pack(expand=True, fill=BOTH)
    # Logo
    logo_frame = Frame(welcome_frame, bg=BACKGROUND_COLOR)
    logo_frame.pack(pady=(30, 0))
    logo_bg = Label(logo_frame, text="📚", font=("Arial", 65), bg=BACKGROUND_COLOR, fg=COMMENT_COLOR)
    logo_bg.place(x=3, y=3)
    logo_label = Label(logo_frame, text="📚", font=("Arial", 65), bg=BACKGROUND_COLOR, fg=ACCENT_COLOR)
    logo_label.pack()
    # Title
    title_frame = Frame(welcome_frame, bg=BACKGROUND_COLOR)
    title_frame.pack(pady=(20, 30))
    app_title_label = Label(title_frame, text="QuoteKeeper", font=TITLE_FONT, bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
    app_title_label.pack()
    # Entry Fields
    entry_frame = Frame(welcome_frame, bg=BACKGROUND_COLOR)
    entry_frame.pack(fill=X)
    username_label = Label(entry_frame, text="Username", font=TEXT_FONT, bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
    username_label.pack(anchor=W, pady=(0, 5))
    username_entry = Entry(entry_frame, font=TEXT_FONT, bg=COMMENT_COLOR, fg=FOREGROUND_COLOR,
                           insertbackground=FOREGROUND_COLOR, bd=0)
    username_entry.pack(fill=X, ipady=8, pady=(0, 15))
    password_label = Label(entry_frame, text="Password", font=TEXT_FONT, bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
    password_label.pack(anchor=W, pady=(0, 5))
    password_entry = Entry(entry_frame, font=TEXT_FONT, show="*", bg=COMMENT_COLOR, fg=FOREGROUND_COLOR,
                           insertbackground=FOREGROUND_COLOR, bd=0)
    password_entry.pack(fill=X, ipady=8, pady=(0, 25))
    login_button = create_rounded_button(entry_frame, "Login", ACCENT_COLOR, BACKGROUND_COLOR,
                                          lambda: authenticate(username_entry.get(), password_entry.get(), auth_window), bold=True)
    login_button.pack(pady=(0, 15))
    bottom_frame = Frame(welcome_frame, bg=BACKGROUND_COLOR)
    bottom_frame.pack(side=BOTTOM, fill=X, pady=(10, 20))
    message_label = Label(bottom_frame, text="Don't have an account?", font=TEXT_FONT, bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
    message_label.pack(side=LEFT)
    signup_button = Button(bottom_frame, text="Sign up", font=BUTTON_FONT_BOLD, bg=BACKGROUND_COLOR, fg=ACCENT_COLOR,
                           bd=0, cursor="hand2", activebackground=BACKGROUND_COLOR, activeforeground=ACCENT_COLOR,
                           highlightthickness=0, relief="flat", command=open_signup_window)
    signup_button.pack(side=RIGHT)
    return auth_window, username_entry, password_entry


if __name__ == "__main__":
    initialize_database()
    auth_window, username_entry, password_entry = create_login_window()
    auth_window.mainloop()
