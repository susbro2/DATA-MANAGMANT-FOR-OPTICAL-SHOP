import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import sqlite3
from datetime import date, datetime
import os
import time
import shutil
import threading
import pandas as pd
import platform
from PIL import Image, ImageTk, ImageDraw  # Add PIL for image handling

class AnimatedButton(tk.Button):
    """Custom animated button class with hover effects"""
    def __init__(self, master=None, **kwargs):
        bg_color = kwargs.pop('bg_color', "#3498db")
        hover_color = kwargs.pop('hover_color', "#2ecc71")
        text_color = kwargs.pop('text_color', "white")
        hover_text_color = kwargs.pop('hover_text_color', "white")
        
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hover_text_color = hover_text_color
        
        tk.Button.__init__(self, master, bg=bg_color, fg=text_color, 
                         relief=tk.RAISED, bd=0, **kwargs)
        
        # Set button font and dimensions
        self.configure(
            font=('Arial', 11, 'bold'),
            padx=15,
            pady=8,
            cursor="hand2",
            activebackground=hover_color,
            activeforeground=hover_text_color
        )
        
        # Bind events for animation
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
    
    def on_enter(self, event):
        """Mouse enters button - animate to hover state"""
        self.config(bg=self.hover_color)
        
        # Add subtle growth animation
        current_padx = int(self.cget('padx'))
        current_pady = int(self.cget('pady'))
        self.config(padx=current_padx+2, pady=current_pady+1)
    
    def on_leave(self, event):
        """Mouse leaves button - animate back to normal state"""
        self.config(bg=self.bg_color)
        
        # Revert size
        self.config(padx=15, pady=8)
    
    def on_press(self, event):
        """Button is pressed - show pressed state"""
        self.config(relief=tk.SUNKEN)
    
    def on_release(self, event):
        """Button is released - return to normal state"""
        self.config(relief=tk.RAISED)

class ShivamOpticals:
    def __init__(self, root):
        self.root = root
        self.root.title("Shivam Opticals")
        
        # Configure high-DPI scaling
        self.configure_dpi_scaling()
        
        # Get screen dimensions for responsive layout
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set default size based on screen (80% of screen size)
        default_width = int(screen_width * 0.85)  # Increased from 0.8 to 0.85
        default_height = int(screen_height * 0.85)  # Increased from 0.8 to 0.85
        
        # Ensure minimum window size
        default_width = max(default_width, 1200)  # Increased from 1100 to 1200
        default_height = max(default_height, 820)  # Increased from 780 to 820
        
        # Set window geometry
        self.root.geometry(f"{default_width}x{default_height}")
        
        # Enable window resizing
        self.root.minsize(1000, 700)
        
        # Set theme colors
        self.primary_color = "#3498db"  # Blue
        self.secondary_color = "#2ecc71"  # Green
        self.bg_color = "#f9f9f9"  # Light gray
        self.text_color = "#2c3e50"  # Dark blue/gray
        self.heading_color = "#1a5276"  # Darker blue for headings
        self.hover_color = "#2980b9"  # Darker blue for hover effects
        self.accent_color = "#e74c3c"  # Red accent color
        
        # Store canvas references for scrolling
        self.form_canvas = None
        self.list_canvas = None
        
        # Database connection
        self.conn = None
        self.cursor = None
        
        # Set custom fonts with high DPI support
        self.setup_fonts()
        
        # Configure styles
        self.configure_styles()
        
        # Configure the root window background
        self.root.configure(bg=self.bg_color)
        
        # Try to set window icon
        try:
            if os.path.exists("icon.png"):
                img = Image.open("icon.png")
                img = img.resize((64, 64), Image.LANCZOS)  # Higher resolution icon
                icon = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, icon)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Initialize database
        self.setup_database()
        
        # Start database maintenance schedule
        self.schedule_database_maintenance()
        
        # Create header with logo
        self.setup_header()
        
        # Create tab control
        self.tab_control = ttk.Notebook(root)
        
        # Create tabs
        self.customer_tab = ttk.Frame(self.tab_control)
        self.list_tab = ttk.Frame(self.tab_control)
        self.tools_tab = ttk.Frame(self.tab_control)  # New tools tab
        
        self.tab_control.add(self.customer_tab, text="Add Customer")
        self.tab_control.add(self.list_tab, text="Customer List")
        self.tab_control.add(self.tools_tab, text="Tools & Utilities")  # Add tools tab
        
        self.tab_control.pack(expand=1, fill="both", padx=20, pady=10)
        
        # Set up the customer form
        self.setup_customer_form()
        
        # Set up the customer list
        self.setup_customer_list()
        
        # Set up the tools tab
        self.setup_tools_tab()
        
        # Initialize scrolling for the first tab
        self.root.update()
        self.setup_scrolling(self.form_canvas)
        
        # Set up application closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bind resize event
        self.root.bind("<Configure>", self.on_window_resize)
    
    def configure_dpi_scaling(self):
        """Configure high-DPI scaling based on platform"""
        system = platform.system()
        
        # Set DPI awareness on Windows
        if system == "Windows":
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)  # Process is system DPI aware
            except Exception as e:
                print(f"Failed to set DPI awareness: {e}")
        
        # Set scaling factor for Tk
        scaling_factor = 1.2  # Default scaling factor
        
        # Adjust scaling based on screen resolution
        screen_width = self.root.winfo_screenwidth()
        if screen_width > 2500:  # For very high-res screens
            scaling_factor = 1.5
        elif screen_width > 1900:  # For typical HD/FHD screens
            scaling_factor = 1.3
            
        # Apply scaling - use the native tk scaling mechanism
        self.root.tk.call('tk', 'scaling', scaling_factor)
    
    def setup_fonts(self):
        """Set up custom fonts with appropriate sizes for high-DPI displays"""
        default_font_size = 11  # Increased from 10 to 11
        
        # Scale font sizes based on screen resolution
        screen_width = self.root.winfo_screenwidth()
        if screen_width > 2500:  # For very high-res screens
            default_font_size = 13  # Increased from 12 to 13
        elif screen_width > 1900:  # For typical HD/FHD screens
            default_font_size = 12  # Increased from 11 to 12
            
        # Store font configurations
        self.fonts = {
            'default': font.Font(family='Arial', size=default_font_size),
            'heading': font.Font(family='Arial', size=default_font_size+8, weight='bold'),
            'subheading': font.Font(family='Arial', size=default_font_size+4, weight='bold'),
            'bold': font.Font(family='Arial', size=default_font_size, weight='bold'),
            'large': font.Font(family='Arial', size=default_font_size+2),
            'small': font.Font(family='Arial', size=default_font_size-1),
            'italic': font.Font(family='Arial', size=default_font_size, slant='italic'),
        }
        
        # Override default font
        self.root.option_add('*Font', self.fonts['default'])
    
    def on_window_resize(self, event):
        """Handle window resize events to adjust UI elements"""
        # Only process if it's the main window that's being resized
        if event.widget == self.root:
            # You might want to adjust UI elements based on new window size
            pass
    
    def configure_styles(self):
        """Configure ttk styles for a consistent look with high-DPI support"""
        style = ttk.Style()
        
        # Configure TFrame
        style.configure("TFrame", background=self.bg_color)
        
        # Configure TLabel
        style.configure("TLabel", 
                      background=self.bg_color, 
                      foreground=self.text_color, 
                      font=self.fonts['default'])
        
        # Configure TButton with animation-like effect
        style.configure("TButton", 
                      background=self.primary_color, 
                      foreground="white", 
                      font=self.fonts['bold'],
                      padding=(15, 10))  # Increased padding
        style.map("TButton", 
                background=[('active', self.secondary_color), ('pressed', self.hover_color)],
                relief=[('pressed', 'sunken'), ('!pressed', 'raised')],
                borderwidth=[('pressed', 2), ('!pressed', 1)])
        
        # Configure Animated.TButton - a more animated version
        style.configure("Animated.TButton",
                      padding=(18, 12),  # Larger padding
                      font=self.fonts['bold'],
                      background=self.primary_color,
                      foreground="white")
        style.map("Animated.TButton",
                background=[('active', self.secondary_color), ('pressed', self.hover_color)],
                relief=[('pressed', 'sunken'), ('!pressed', 'raised')],
                borderwidth=[('pressed', 3), ('!pressed', 1)])
        
        # Configure heading style
        style.configure("Heading.TLabel", 
                      font=self.fonts['heading'], 
                      foreground=self.heading_color)
        
        # Configure subheading style
        style.configure("Subheading.TLabel", 
                      font=self.fonts['subheading'], 
                      foreground=self.primary_color)
        
        # Configure section header style
        style.configure("SectionHeader.TLabel", 
                      font=self.fonts['bold'], 
                      foreground=self.primary_color)
        
        # Configure Treeview for higher resolution
        style.configure("Treeview", 
                      background="white", 
                      fieldbackground="white", 
                      foreground=self.text_color,
                      font=self.fonts['default'],
                      rowheight=int(self.fonts['default'].metrics('linespace') * 1.8))  # Increased row height
        style.configure("Treeview.Heading", 
                      font=self.fonts['bold'], 
                      foreground=self.heading_color)
        style.map("Treeview", background=[('selected', self.primary_color)])
        
        # Configure tab style
        style.configure("TNotebook.Tab", 
                      font=self.fonts['bold'],
                      padding=(15, 8))  # Increased padding
        
        # Configure labelframe
        style.configure("TLabelframe", 
                      font=self.fonts['bold'])
        style.configure("TLabelframe.Label", 
                     font=self.fonts['bold'], 
                     foreground=self.primary_color)
        
        # Configure entries with larger padding for better touch targets
        style.configure("TEntry", 
                      padding=(8, 8),  # Increased padding
                      font=self.fonts['default'])
    
    def setup_header(self):
        """Create a header with logo and title"""
        header_frame = tk.Frame(self.root, bg=self.primary_color, height=100)  # Increased height
        header_frame.pack(fill="x", pady=(0, 15))
        
        # Center content in header
        center_frame = tk.Frame(header_frame, bg=self.primary_color)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Try to load logo
        logo_img = None
        try:
            if os.path.exists("icon.png"):
                img = Image.open("icon.png")
                img = img.resize((80, 80), Image.LANCZOS)  # Larger logo
                logo_img = ImageTk.PhotoImage(img)
                logo_label = tk.Label(center_frame, image=logo_img, bg=self.primary_color)
                logo_label.image = logo_img  # Keep a reference
                logo_label.pack(side="left", padx=15)
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        # App title with larger, more readable text
        title_label = tk.Label(
            center_frame, 
            text="SHIVAM OPTICALS", 
            font=self.fonts['heading'], 
            fg="white", 
            bg=self.primary_color
        )
        title_label.pack(side="left", padx=15)
    
    def setup_database(self):
        try:
            # Create database directory if it doesn't exist
            db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            db_path = os.path.join(db_dir, "optical_shop.db")
            
            # Connect to database (will create if it doesn't exist)
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
            self.conn.execute("PRAGMA journal_mode = WAL")  # Use Write-Ahead Logging for better concurrency
            self.cursor = self.conn.cursor()
            
            # Create tables if they don't exist
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS prescriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER,
                    right_sph TEXT,
                    right_cyl TEXT,
                    right_axe TEXT,
                    right_add TEXT,
                    left_sph TEXT,
                    left_cyl TEXT,
                    left_axe TEXT,
                    left_add TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER,
                    frame_name TEXT,
                    lens_name TEXT,
                    frame_cost REAL,
                    lens_cost REAL,
                    total_cost REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
                )
            ''')
            
            # Create trigger to update the updated_at timestamp
            for table in ['customers', 'prescriptions', 'products']:
                self.cursor.execute(f'''
                    CREATE TRIGGER IF NOT EXISTS update_{table}_timestamp
                    AFTER UPDATE ON {table}
                    BEGIN
                        UPDATE {table} SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                    END
                ''')
            
            # Create index on frequently searched fields
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_customer_name ON customers(name)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_customer_phone ON customers(phone)')
            
            self.conn.commit()
            
            # Create backups directory
            backup_dir = os.path.join(db_dir, "backups")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
            raise
    
    def backup_database(self):
        """Create a backup of the database"""
        try:
            # Get paths
            db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
            db_path = os.path.join(db_dir, "optical_shop.db")
            backup_dir = os.path.join(db_dir, "backups")
            
            # Format timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"optical_shop_backup_{timestamp}.db")
            
            # Close current connection
            if self.conn:
                self.conn.close()
            
            # Copy database file
            shutil.copy2(db_path, backup_path)
            
            # Reconnect to database
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.conn.execute("PRAGMA journal_mode = WAL")
            self.cursor = self.conn.cursor()
            
            # Clean old backups (keep only 10 most recent)
            self.clean_old_backups(backup_dir)
            
            return True, backup_path
        except Exception as e:
            print(f"Backup error: {e}")
            # Reconnect to database in case of error
            try:
                db_path = os.path.join(db_dir, "optical_shop.db")
                self.conn = sqlite3.connect(db_path, check_same_thread=False)
                self.conn.execute("PRAGMA foreign_keys = ON")
                self.conn.execute("PRAGMA journal_mode = WAL")
                self.cursor = self.conn.cursor()
            except Exception as e2:
                print(f"Reconnection error: {e2}")
            
            return False, str(e)
    
    def clean_old_backups(self, backup_dir, max_backups=10):
        """Remove old backups, keeping only the most recent ones"""
        try:
            # Get list of backup files
            backup_files = [f for f in os.listdir(backup_dir) if f.startswith("optical_shop_backup_") and f.endswith(".db")]
            
            # Sort by filename (which includes timestamp)
            backup_files.sort(reverse=True)
            
            # Remove old backups
            if len(backup_files) > max_backups:
                for old_file in backup_files[max_backups:]:
                    os.remove(os.path.join(backup_dir, old_file))
        except Exception as e:
            print(f"Error cleaning old backups: {e}")
    
    def schedule_database_maintenance(self):
        """Schedule regular database maintenance tasks"""
        # Run maintenance in a separate thread
        maintenance_thread = threading.Thread(target=self.run_maintenance)
        maintenance_thread.daemon = True  # Thread will exit when main program exits
        maintenance_thread.start()
    
    def run_maintenance(self):
        """Run maintenance tasks periodically"""
        # Run every 2 hours
        while True:
            try:
                # Create backup
                self.backup_database()
                
                # Run VACUUM to optimize database
                if self.conn:
                    self.conn.execute("VACUUM")
                    self.conn.commit()
                
                # Check database integrity
                if self.conn:
                    integrity_check = self.conn.execute("PRAGMA integrity_check").fetchone()
                    if integrity_check[0] != "ok":
                        print(f"Database integrity issue: {integrity_check}")
            except Exception as e:
                print(f"Maintenance error: {e}")
            
            # Sleep for 2 hours
            time.sleep(7200)
    
    def on_closing(self):
        """Handle application closing"""
        try:
            # Close database connection properly
            if self.conn:
                self.conn.close()
        except Exception as e:
            print(f"Error during closing: {e}")
        
        # Close the application
        self.root.destroy()
    
    def setup_customer_form(self):
        # Create a main frame with scrolling capability
        main_frame = ttk.Frame(self.customer_tab)
        main_frame.pack(fill="both", expand=True)
        
        # Create a canvas for scrolling
        canvas = tk.Canvas(main_frame, bg=self.bg_color, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        
        # Store canvas reference
        self.form_canvas = canvas
        
        # Add a vertical scrollbar
        v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        v_scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Create a frame inside the canvas for the form content
        form_frame = ttk.Frame(canvas, padding=30)  # Increased padding from 25 to 30
        canvas_window = canvas.create_window((0, 0), window=form_frame, anchor="nw", tags="form_frame")
        
        # Configure canvas scrolling
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        form_frame.bind("<Configure>", configure_scroll_region)
        
        # Make sure the canvas window stays the width of the canvas
        def configure_canvas_window(event):
            canvas.itemconfig("form_frame", width=event.width)
        
        canvas.bind("<Configure>", configure_canvas_window)
        
        # Enable mousewheel scrolling when this tab is selected
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Center the content within the form
        center_frame = ttk.Frame(form_frame)
        center_frame.pack(expand=True)
        
        # Title with graphic decoration
        title_frame = ttk.Frame(center_frame)
        title_frame.grid(column=0, row=0, columnspan=4, pady=20)  # Increased padding from 15 to 20
        
        # Decorative line before title with animation
        line_canvas1 = tk.Canvas(title_frame, width=120, height=3, bg=self.primary_color, highlightthickness=0)
        line_canvas1.pack(side="left", padx=15)
        
        # Animate line on hover
        def animate_line_enter(event):
            line_canvas1.config(width=140, height=4)
            line_canvas2.config(width=140, height=4)
        
        def animate_line_leave(event):
            line_canvas1.config(width=120, height=3)
            line_canvas2.config(width=120, height=3)
        
        title_label = ttk.Label(title_frame, text="Customer Data", style="Heading.TLabel")
        title_label.pack(side="left")
        title_label.bind("<Enter>", animate_line_enter)
        title_label.bind("<Leave>", animate_line_leave)
        
        # Decorative line after title
        line_canvas2 = tk.Canvas(title_frame, width=120, height=3, bg=self.primary_color, highlightthickness=0)
        line_canvas2.pack(side="left", padx=15)
        
        # Date field with better spacing
        date_frame = ttk.Frame(center_frame)
        date_frame.grid(column=0, row=1, columnspan=4, pady=12)  # Increased padding
        
        ttk.Label(date_frame, text="Date:", font=self.fonts['bold']).pack(side="left", padx=10)  # Increased padding
        self.date_entry = ttk.Entry(date_frame, width=18, font=self.fonts['default'])  # Increased width from 15 to 18
        self.date_entry.pack(side="left", padx=10)  # Increased padding
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        # Customer details - centered with better spacing
        details_frame = ttk.LabelFrame(center_frame, text="Customer Information", padding=20)
        details_frame.grid(column=0, row=2, columnspan=4, pady=15, sticky=tk.W+tk.E)
        
        name_frame = ttk.Frame(details_frame)
        name_frame.pack(fill="x", pady=8)
        ttk.Label(name_frame, text="Name:", width=12, font=self.fonts['bold']).pack(side="left")
        self.name_entry = ttk.Entry(name_frame, width=30, font=self.fonts['default'])
        self.name_entry.pack(side="left", padx=8, expand=True, fill="x")
        
        phone_frame = ttk.Frame(details_frame)
        phone_frame.pack(fill="x", pady=8)
        ttk.Label(phone_frame, text="Phone No:", width=12, font=self.fonts['bold']).pack(side="left")
        self.phone_entry = ttk.Entry(phone_frame, width=20, font=self.fonts['default'])
        self.phone_entry.pack(side="left", padx=8, expand=True, fill="x")
        
        # Prescription section with visual improvements
        prescription_frame = ttk.LabelFrame(center_frame, text="Prescription Details", padding=20)
        prescription_frame.grid(column=0, row=4, columnspan=4, pady=15, sticky=tk.W+tk.E)
        
        # Add decorative elements for eye sections
        right_eye_frame = ttk.Frame(prescription_frame)
        right_eye_frame.grid(column=1, row=0, pady=8)
        
        # Eye icon for right eye (simulated with a circle)
        eye_canvas_r = tk.Canvas(right_eye_frame, width=25, height=25, highlightthickness=0)
        eye_canvas_r.create_oval(2, 2, 23, 23, fill=self.primary_color, outline="")
        eye_canvas_r.pack(side="left", padx=4)
        
        ttk.Label(right_eye_frame, text="Right Eye (R.E)", font=self.fonts['bold']).pack(side="left")
        
        left_eye_frame = ttk.Frame(prescription_frame)
        left_eye_frame.grid(column=2, row=0, pady=8)
        
        # Eye icon for left eye (simulated with a circle)
        eye_canvas_l = tk.Canvas(left_eye_frame, width=25, height=25, highlightthickness=0)
        eye_canvas_l.create_oval(2, 2, 23, 23, fill=self.secondary_color, outline="")
        eye_canvas_l.pack(side="left", padx=4)
        
        ttk.Label(left_eye_frame, text="Left Eye (L.E)", font=self.fonts['bold']).pack(side="left")
        
        # Prescription fields with better spacing
        prescription_types = ["SPH", "CYL", "AXE", "Add"]
        self.prescription_entries = {}
        
        for i, p_type in enumerate(prescription_types):
            row_frame = ttk.Frame(prescription_frame)
            row_frame.grid(column=0, row=i+1, columnspan=3, pady=8, sticky=tk.W+tk.E)
            
            # Type label with colored background
            type_label = tk.Label(row_frame, text=p_type, width=8, bg=self.primary_color, fg="white",
                                  font=self.fonts['bold'])
            type_label.pack(side="left", padx=12)
            
            # Right eye entry
            right_frame = ttk.Frame(row_frame)
            right_frame.pack(side="left", expand=True, fill="x", padx=12)
            
            self.prescription_entries[f"right_{p_type.lower()}"] = ttk.Entry(right_frame, width=12, font=self.fonts['default'])
            self.prescription_entries[f"right_{p_type.lower()}"].pack(side="top", pady=3)
            
            # Left eye entry
            left_frame = ttk.Frame(row_frame)
            left_frame.pack(side="left", expand=True, fill="x", padx=12)
            
            self.prescription_entries[f"left_{p_type.lower()}"] = ttk.Entry(left_frame, width=12, font=self.fonts['default'])
            self.prescription_entries[f"left_{p_type.lower()}"].pack(side="top", pady=3)
        
        # Product details with visual enhancements
        product_frame = ttk.LabelFrame(center_frame, text="Product Details", padding=20)
        product_frame.grid(column=0, row=5, columnspan=4, pady=15, sticky=tk.W+tk.E)
        
        # Frame info - centered
        frame_row = ttk.Frame(product_frame)
        frame_row.pack(fill="x", pady=5)
        
        frame_icon = tk.Canvas(frame_row, width=20, height=20, highlightthickness=0)
        frame_icon.create_rectangle(2, 5, 18, 15, outline=self.primary_color, width=2)
        frame_icon.pack(side="left", padx=5)
        
        ttk.Label(frame_row, text="Frame Name:").pack(side="left", padx=5)
        self.frame_name_entry = ttk.Entry(frame_row, width=30, font=self.fonts['default'])
        self.frame_name_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        # Lens info - centered
        lens_row = ttk.Frame(product_frame)
        lens_row.pack(fill="x", pady=5)
        
        lens_icon = tk.Canvas(lens_row, width=20, height=20, highlightthickness=0)
        lens_icon.create_oval(2, 2, 18, 18, outline=self.secondary_color, width=2)
        lens_icon.pack(side="left", padx=5)
        
        ttk.Label(lens_row, text="Lens Name:").pack(side="left", padx=5)
        self.lens_name_entry = ttk.Entry(lens_row, width=30, font=self.fonts['default'])
        self.lens_name_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        # Cost details with visual elements
        cost_frame = ttk.LabelFrame(center_frame, text="Cost Details", padding=20)
        cost_frame.grid(column=0, row=6, columnspan=4, pady=15, sticky=tk.W+tk.E)
        
        # Graphical cost display
        costs_row = ttk.Frame(cost_frame)
        costs_row.pack(fill="x", pady=5)
        
        # Frame cost
        frame_cost_frame = ttk.Frame(costs_row)
        frame_cost_frame.pack(side="left", expand=True, fill="x", padx=10)
        
        frame_cost_icon = tk.Canvas(frame_cost_frame, width=20, height=20, highlightthickness=0)
        frame_cost_icon.create_rectangle(3, 3, 17, 17, fill=self.primary_color)
        frame_cost_icon.pack(side="left", padx=5)
        
        ttk.Label(frame_cost_frame, text="Frame Cost:").pack(side="left")
        self.frame_cost_entry = ttk.Entry(frame_cost_frame, width=10, font=self.fonts['default'])
        self.frame_cost_entry.pack(side="left", padx=5)
        
        # Lens cost
        lens_cost_frame = ttk.Frame(costs_row)
        lens_cost_frame.pack(side="left", expand=True, fill="x", padx=10)
        
        lens_cost_icon = tk.Canvas(lens_cost_frame, width=20, height=20, highlightthickness=0)
        lens_cost_icon.create_oval(3, 3, 17, 17, fill=self.secondary_color)
        lens_cost_icon.pack(side="left", padx=5)
        
        ttk.Label(lens_cost_frame, text="Lens Cost:").pack(side="left")
        self.lens_cost_entry = ttk.Entry(lens_cost_frame, width=10, font=self.fonts['default'])
        self.lens_cost_entry.pack(side="left", padx=5)
        
        # Total cost with visual highlight
        total_frame = ttk.Frame(cost_frame)
        total_frame.pack(fill="x", pady=10)
        
        # Decorative elements for total
        total_canvas = tk.Canvas(total_frame, width=30, height=30, highlightthickness=0)
        total_canvas.create_oval(5, 5, 25, 25, fill="#e74c3c")  # Red circle
        total_canvas.create_text(15, 15, text="₹", fill="white", font=("Arial", 12, "bold"))
        total_canvas.pack(side="left", padx=5)
        
        ttk.Label(total_frame, text="Total Cost:", font=self.fonts['bold']).pack(side="left")
        self.total_cost_entry = ttk.Entry(total_frame, width=10, font=self.fonts['default'], state="readonly")
        self.total_cost_entry.pack(side="left", padx=5)
        
        # Add cost calculation events
        self.frame_cost_entry.bind("<FocusOut>", self.calculate_total)
        self.lens_cost_entry.bind("<FocusOut>", self.calculate_total)
        
        # Buttons in a centered frame with improved styling and animation
        button_frame = ttk.Frame(center_frame)
        button_frame.grid(column=0, row=7, columnspan=4, pady=20)  # Increased padding
        
        # Save button with icon and animation
        save_button_frame = ttk.Frame(button_frame)
        save_button_frame.pack(side="left", padx=15)  # Increased padding
        
        save_icon = tk.Canvas(save_button_frame, width=25, height=25, highlightthickness=0)  # Increased size
        save_icon.create_rectangle(4, 4, 21, 21, fill=self.secondary_color)
        save_icon.create_line(8, 13, 13, 18, width=2, fill="white")
        save_icon.create_line(13, 18, 19, 7, width=2, fill="white")
        save_icon.pack(side="left", padx=5)
        
        save_button = self.create_animated_button(
            save_button_frame, 
            text="Save Customer", 
            command=self.save_customer,
            bg_color=self.primary_color,
            hover_color=self.secondary_color
        )
        save_button.pack(side="left")
        
        # Clear button with icon and animation
        clear_button_frame = ttk.Frame(button_frame)
        clear_button_frame.pack(side="left", padx=15)  # Increased padding
        
        clear_icon = tk.Canvas(clear_button_frame, width=25, height=25, highlightthickness=0)  # Increased size
        clear_icon.create_rectangle(4, 4, 21, 21, outline=self.primary_color, width=2)
        clear_icon.create_line(8, 8, 17, 17, width=2, fill=self.primary_color)
        clear_icon.create_line(8, 17, 17, 8, width=2, fill=self.primary_color)
        clear_icon.pack(side="left", padx=5)
        
        clear_button = self.create_animated_button(
            clear_button_frame, 
            text="Clear Form", 
            command=self.clear_form,
            bg_color="#e74c3c",  # Red color for clear button
            hover_color="#c0392b"  # Darker red for hover
        )
        clear_button.pack(side="left")
    
    def setup_customer_list(self):
        # Create a main frame with scrolling capability
        main_frame = ttk.Frame(self.list_tab)
        main_frame.pack(fill="both", expand=True)
        
        # Create a canvas for scrolling
        canvas = tk.Canvas(main_frame, bg=self.bg_color, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        
        # Store canvas reference
        self.list_canvas = canvas
        
        # Add a vertical scrollbar
        v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        v_scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Create a frame inside the canvas for the list content
        list_frame = ttk.Frame(canvas, padding=25)  # Increased padding
        canvas_window = canvas.create_window((0, 0), window=list_frame, anchor="nw", tags="list_frame")
        
        # Configure canvas scrolling
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        list_frame.bind("<Configure>", configure_scroll_region)
        
        # Make sure the canvas window stays the width of the canvas
        def configure_canvas_window(event):
            canvas.itemconfig("list_frame", width=event.width)
        
        canvas.bind("<Configure>", configure_canvas_window)
        
        # Title with graphic decoration
        title_frame = ttk.Frame(list_frame)
        title_frame.pack(fill="x", pady=15)  # Increased padding
        
        # Center the title
        center_title = ttk.Frame(title_frame)
        center_title.pack(expand=True)
        
        # Decorative line before title
        line_canvas1 = tk.Canvas(center_title, width=100, height=3, bg=self.primary_color, highlightthickness=0)
        line_canvas1.pack(side="left", padx=15)
        
        title_label = ttk.Label(center_title, text="Customer Records", style="Heading.TLabel")
        title_label.pack(side="left")
        
        # Decorative line after title
        line_canvas2 = tk.Canvas(center_title, width=100, height=3, bg=self.primary_color, highlightthickness=0)
        line_canvas2.pack(side="left", padx=15)
        
        # Search section with improved visuals
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill="x", pady=15)  # Increased padding
        
        # Center the search controls
        center_search = ttk.Frame(search_frame)
        center_search.pack(expand=True)
        
        # Add an explanatory label
        search_header = ttk.Frame(center_search)
        search_header.pack(fill="x", pady=(0, 8))  # Increased padding
        
        # Create an info icon with better visual
        info_icon = tk.Canvas(search_header, width=20, height=20, highlightthickness=0)
        info_icon.create_oval(0, 0, 20, 20, fill=self.primary_color)
        info_icon.create_text(10, 10, text="i", fill="white", font=self.fonts['bold'])
        info_icon.pack(side="left", padx=8)
        
        ttk.Label(search_header, 
                 text="Search by name or phone to find customers. Exact matches will show details automatically.", 
                 font=self.fonts['italic']).pack(side="left")
        
        # Search controls with animated buttons
        search_controls = ttk.Frame(center_search)
        search_controls.pack(fill="x", pady=8)
        
        # Search icon (magnifying glass) - larger
        search_icon = tk.Canvas(search_controls, width=25, height=25, highlightthickness=0)
        search_icon.create_oval(5, 5, 20, 20, outline=self.primary_color, width=2)
        search_icon.create_line(18, 18, 24, 24, width=2, fill=self.primary_color)
        search_icon.pack(side="left", padx=8)
        
        ttk.Label(search_controls, text="Search:", font=self.fonts['bold']).pack(side="left", padx=8)
        self.search_entry = ttk.Entry(search_controls, width=35, font=self.fonts['default'])
        self.search_entry.pack(side="left", padx=8)
        
        # Bind Enter key to search function
        self.search_entry.bind("<Return>", lambda event: self.search_customers())
        
        # Animated search button
        search_button = self.create_animated_button(
            search_controls, 
            text="Search Customers", 
            command=self.search_customers,
            bg_color=self.primary_color,
            hover_color=self.secondary_color
        )
        search_button.pack(side="left", padx=8)
        
        # Animated clear button
        clear_button = self.create_animated_button(
            search_controls, 
            text="Clear", 
            command=lambda: [self.search_entry.delete(0, tk.END), self.refresh_customer_list()],
            bg_color="#e74c3c",  # Red color
            hover_color="#c0392b"  # Darker red for hover
        )
        clear_button.pack(side="left", padx=8)
        
        # Treeview for customer list with visual enhancements
        self.tree_frame = ttk.Frame(list_frame)
        self.tree_frame.pack(fill="both", expand=True, pady=15)  # Increased padding
        
        # Create a container for stats display
        stats_frame = ttk.Frame(self.tree_frame)
        stats_frame.pack(fill="x", pady=(0, 10))
        
        # Add simple statistics display
        self.stats_label = ttk.Label(stats_frame, text="Total Records: 0", 
                                  font=self.fonts['italic'])
        self.stats_label.pack(side="right", padx=15)
        
        # Container for treeview and scrollbar
        tree_container = ttk.Frame(self.tree_frame)
        tree_container.pack(fill="both", expand=True)
        
        columns = ("id", "name", "phone", "date", "frame", "total")
        self.customer_tree = ttk.Treeview(tree_container, columns=columns, show="headings")
        
        # Define headings with center alignment and improved visibility
        self.customer_tree.heading("id", text="ID", anchor="center")
        self.customer_tree.heading("name", text="Name", anchor="center")
        self.customer_tree.heading("phone", text="Phone", anchor="center")
        self.customer_tree.heading("date", text="Date", anchor="center")
        self.customer_tree.heading("frame", text="Frame", anchor="center")
        self.customer_tree.heading("total", text="Total Cost", anchor="center")
        
        # Column widths and alignment - adjusted for higher resolution
        screen_width = self.root.winfo_screenwidth()
        width_factor = 1.0
        if screen_width > 1900:
            width_factor = 1.3
        elif screen_width > 2500:
            width_factor = 1.5
            
        self.customer_tree.column("id", width=int(60 * width_factor), anchor="center")
        self.customer_tree.column("name", width=int(180 * width_factor), anchor="center")
        self.customer_tree.column("phone", width=int(150 * width_factor), anchor="center")
        self.customer_tree.column("date", width=int(120 * width_factor), anchor="center")
        self.customer_tree.column("frame", width=int(180 * width_factor), anchor="center")
        self.customer_tree.column("total", width=int(120 * width_factor), anchor="center")
        
        # Add horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.customer_tree.xview)
        self.customer_tree.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Add vertical scrollbar
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.customer_tree.yview)
        self.customer_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Pack tree and scrollbar
        self.customer_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        
        # Add visual cue for double-click action with improved visibility
        tip_frame = ttk.Frame(list_frame)
        tip_frame.pack(fill="x", pady=(15, 0))  # Increased padding
        
        tip_icon = tk.Canvas(tip_frame, width=25, height=25, highlightthickness=0)
        tip_icon.create_text(12, 12, text="i", fill=self.primary_color, font=self.fonts['bold'])
        tip_icon.create_oval(2, 2, 22, 22, outline=self.primary_color, width=2)
        tip_icon.pack(side="left", padx=8)
        
        tip_label = ttk.Label(tip_frame, text="Double-click on any customer to view full details", 
                           font=self.fonts['italic'])
        tip_label.pack(side="left")
        
        # Bind double-click to view details
        self.customer_tree.bind("<Double-1>", self.view_customer_details)
        
        # Load customers
        self.refresh_customer_list()
    
    def calculate_total(self, event=None):
        try:
            frame_cost = float(self.frame_cost_entry.get()) if self.frame_cost_entry.get() else 0
            lens_cost = float(self.lens_cost_entry.get()) if self.lens_cost_entry.get() else 0
            total = frame_cost + lens_cost
            
            # Update the total field - need to make it writable temporarily
            self.total_cost_entry.configure(state="normal")
            self.total_cost_entry.delete(0, tk.END)
            self.total_cost_entry.insert(0, f"{total:.2f}")
            self.total_cost_entry.configure(state="readonly")
        except ValueError:
            # Invalid number format
            pass
    
    def save_customer(self):
        # Validate required fields
        if not self.name_entry.get().strip():
            messagebox.showwarning("Validation Error", "Please enter the customer name")
            return
        
        try:
            # Start transaction
            self.conn.execute("BEGIN")
            
            # Insert customer
            self.cursor.execute(
                "INSERT INTO customers (name, phone, date) VALUES (?, ?, ?)",
                (self.name_entry.get(), self.phone_entry.get(), self.date_entry.get())
            )
            
            # Get customer ID
            customer_id = self.cursor.lastrowid
            
            # Insert prescription
            self.cursor.execute(
                '''INSERT INTO prescriptions 
                   (customer_id, right_sph, right_cyl, right_axe, right_add,
                    left_sph, left_cyl, left_axe, left_add)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    customer_id,
                    self.prescription_entries["right_sph"].get(),
                    self.prescription_entries["right_cyl"].get(),
                    self.prescription_entries["right_axe"].get(),
                    self.prescription_entries["right_add"].get(),
                    self.prescription_entries["left_sph"].get(),
                    self.prescription_entries["left_cyl"].get(),
                    self.prescription_entries["left_axe"].get(),
                    self.prescription_entries["left_add"].get()
                )
            )
            
            # Get cost values
            try:
                frame_cost = float(self.frame_cost_entry.get()) if self.frame_cost_entry.get() else 0
                lens_cost = float(self.lens_cost_entry.get()) if self.lens_cost_entry.get() else 0
                total_cost = float(self.total_cost_entry.get()) if self.total_cost_entry.get() else 0
            except ValueError:
                raise ValueError("Invalid cost values. Please enter numeric values only.")
            
            # Insert product details
            self.cursor.execute(
                '''INSERT INTO products
                   (customer_id, frame_name, lens_name, frame_cost, lens_cost, total_cost)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (
                    customer_id,
                    self.frame_name_entry.get(),
                    self.lens_name_entry.get(),
                    frame_cost,
                    lens_cost,
                    total_cost
                )
            )
            
            # Commit transaction
            self.conn.commit()
            
            # Show success message
            messagebox.showinfo("Success", "Customer saved successfully!")
            
            # Clear form for next entry
            self.clear_form()
            
            # Refresh customer list
            self.refresh_customer_list()
            
        except Exception as e:
            # Roll back transaction in case of error
            self.conn.rollback()
            messagebox.showerror("Error", f"Failed to save customer: {e}")
            print(f"Error saving customer: {e}")
    
    def clear_form(self):
        # Reset date to today
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        # Clear other fields
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.frame_name_entry.delete(0, tk.END)
        self.lens_name_entry.delete(0, tk.END)
        self.frame_cost_entry.delete(0, tk.END)
        self.lens_cost_entry.delete(0, tk.END)
        
        # Clear total cost
        self.total_cost_entry.configure(state="normal")
        self.total_cost_entry.delete(0, tk.END)
        self.total_cost_entry.configure(state="readonly")
        
        # Clear prescription fields
        for entry in self.prescription_entries.values():
            entry.delete(0, tk.END)
    
    def refresh_customer_list(self, search_term=""):
        # Clear existing items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        try:
            # Build query based on whether we're searching
            if search_term:
                query = '''
                    SELECT c.id, c.name, c.phone, c.date, p.frame_name, p.total_cost
                    FROM customers c
                    LEFT JOIN products p ON c.id = p.customer_id
                    WHERE c.name LIKE ? OR c.phone LIKE ? OR p.frame_name LIKE ?
                    ORDER BY c.date DESC
                '''
                like_term = f"%{search_term}%"
                self.cursor.execute(query, (like_term, like_term, like_term))
            else:
                query = '''
                    SELECT c.id, c.name, c.phone, c.date, p.frame_name, p.total_cost
                    FROM customers c
                    LEFT JOIN products p ON c.id = p.customer_id
                    ORDER BY c.date DESC
                '''
                self.cursor.execute(query)
            
            # Get and display results
            results = self.cursor.fetchall()
            for row in results:
                customer_id, name, phone, date_str, frame, total = row
                
                # Handle NULL values from database
                if total is None:
                    total = 0
                
                self.customer_tree.insert("", "end", values=(
                    customer_id,
                    name if name else "",
                    phone if phone else "",
                    date_str if date_str else "",
                    frame if frame else "",
                    f"{total:.2f}" if total else "0.00"
                ))
            
            # Update statistics
            count = len(results)
            self.stats_label.configure(text=f"Total Records: {count}")
            
            # Add alternating row colors for better readability
            for i, item in enumerate(self.customer_tree.get_children()):
                if i % 2 == 0:
                    self.customer_tree.item(item, tags=("evenrow",))
                else:
                    self.customer_tree.item(item, tags=("oddrow",))
            
            # Configure tag colors
            self.customer_tree.tag_configure("evenrow", background="#f0f0f0")
            self.customer_tree.tag_configure("oddrow", background="white")
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error refreshing customer list: {e}")
    
    def search_customers(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            # If search is empty, just refresh the list with all customers
            self.refresh_customer_list()
            return
            
        # First check if we have an exact match on name or phone
        try:
            query = '''
                SELECT c.id
                FROM customers c
                WHERE c.name = ? OR c.phone = ?
                LIMIT 1
            '''
            self.cursor.execute(query, (search_term, search_term))
            exact_match = self.cursor.fetchone()
            
            if exact_match:
                # If we have an exact match, directly show that customer's details
                customer_id = exact_match[0]
                self.show_customer_details(customer_id)
                # Also highlight this record in the list
                self.highlight_customer_in_list(customer_id)
                return
                
            # If no exact match, let's check for a single partial match
            query = '''
                SELECT c.id, COUNT(*) as count
                FROM customers c
                WHERE c.name LIKE ? OR c.phone LIKE ?
            '''
            like_term = f"%{search_term}%"
            self.cursor.execute(query, (like_term, like_term))
            match_count = self.cursor.fetchone()
            
            if match_count and match_count[1] == 1:
                # If there's only one partial match, show it directly
                customer_id = match_count[0]
                self.show_customer_details(customer_id)
                # Also highlight this record in the list
                self.highlight_customer_in_list(customer_id)
                # Still refresh the list to show the single result
                self.refresh_customer_list(search_term)
                return
                
            # If we have multiple matches or no matches, just refresh the list
            self.refresh_customer_list(search_term)
            
        except sqlite3.Error as e:
            messagebox.showerror("Search Error", f"Error during search: {e}")
            self.refresh_customer_list()
    
    def highlight_customer_in_list(self, customer_id):
        """Highlight a specific customer in the list view"""
        # First make sure we have the customer in the visible list
        self.refresh_customer_list()
        
        # Find and select the customer in the tree
        for item in self.customer_tree.get_children():
            item_values = self.customer_tree.item(item, "values")
            if item_values and str(item_values[0]) == str(customer_id):
                # Select this item
                self.customer_tree.selection_set(item)
                # Ensure it's visible by scrolling to it
                self.customer_tree.see(item)
                # Highlight with a special tag
                self.customer_tree.item(item, tags=("highlight",))
                # Configure the highlight color
                self.customer_tree.tag_configure("highlight", background="#ffeb99")  # Light yellow
                break
    
    def show_customer_details(self, customer_id):
        """Show customer details - extracted for reuse from view_customer_details"""
        try:
            # Query customer details
            query = '''
                SELECT c.*, 
                       pr.right_sph, pr.right_cyl, pr.right_axe, pr.right_add,
                       pr.left_sph, pr.left_cyl, pr.left_axe, pr.left_add,
                       p.frame_name, p.lens_name, p.frame_cost, p.lens_cost, p.total_cost
                FROM customers c
                LEFT JOIN prescriptions pr ON c.id = pr.customer_id
                LEFT JOIN products p ON c.id = p.customer_id
                WHERE c.id = ?
            '''
            self.cursor.execute(query, (customer_id,))
            customer = self.cursor.fetchone()
            
            if not customer:
                messagebox.showerror("Error", "Customer not found")
                return
            
            # Get screen dimensions for responsive window size
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Set detail window size based on screen (50% of screen size)
            window_width = int(screen_width * 0.5)
            window_height = int(screen_height * 0.8)
            
            # Ensure minimum window size
            window_width = max(window_width, 700)  # Increased from 650 to 700
            window_height = max(window_height, 750)  # Increased from 700 to 750
            
            # Create detail window with enhanced visuals
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"Customer Details")
            detail_window.geometry(f"{window_width}x{window_height}")
            detail_window.configure(bg=self.bg_color)
            detail_window.grab_set()  # Make the window modal
            
            # Header with customer ID
            header_frame = tk.Frame(detail_window, bg=self.primary_color, height=70)  # Increased height
            header_frame.pack(fill="x", pady=(0, 25))
            
            header_label = tk.Label(
                header_frame, 
                text=f"Customer #{customer_id} Details", 
                font=self.fonts['heading'],
                bg=self.primary_color,
                fg="white"
            )
            header_label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Add subtle animation to header
            def animate_header():
                """Pulse animation for header"""
                current_bg = header_frame.cget("bg")
                if current_bg == self.primary_color:
                    header_frame.config(bg=self.hover_color)
                else:
                    header_frame.config(bg=self.primary_color)
                # Repeat animation
                detail_window.after(3000, animate_header)  # Every 3 seconds
            
            # Start header animation
            detail_window.after(2000, animate_header)  # Start after 2 seconds
            
            # Create a frame with scrolling
            main_canvas = tk.Canvas(detail_window, bg=self.bg_color, highlightthickness=0)
            main_canvas.pack(side="left", fill="both", expand=True, padx=30, pady=(0, 30))  # Increased padding
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(detail_window, orient="vertical", command=main_canvas.yview)
            scrollbar.pack(side="right", fill="y")
            
            main_canvas.configure(yscrollcommand=scrollbar.set)
            main_canvas.bind('<Configure>', lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
            
            # Create a frame inside the canvas for all content
            main_frame = ttk.Frame(main_canvas, padding=20)  # Increased from 15 to 20
            main_canvas.create_window((0, 0), window=main_frame, anchor="nw")
            
            # Basic info section with graphical elements and enhanced visuals
            basic_frame = ttk.LabelFrame(main_frame, text="Basic Information", padding=25)  # Increased padding
            basic_frame.pack(fill="x", pady=15)
            
            # Animate sections on hover
            def animate_section_enter(event, frame):
                """Animate section on mouse enter"""
                # Add subtle highlight
                for child in frame.winfo_children():
                    if isinstance(child, tk.Canvas):
                        child.config(width=30, height=30)  # Grow icons
            
            def animate_section_leave(event, frame):
                """Animate section on mouse leave"""
                # Remove highlight
                for child in frame.winfo_children():
                    if isinstance(child, tk.Canvas):
                        child.config(width=25, height=25)  # Shrink icons back
            
            # Add hover animation to section
            basic_frame.bind("<Enter>", lambda e: animate_section_enter(e, basic_frame))
            basic_frame.bind("<Leave>", lambda e: animate_section_leave(e, basic_frame))
            
            # Customer name with icon
            name_frame = ttk.Frame(basic_frame)
            name_frame.pack(fill="x", pady=10)  # Increased padding
            
            name_icon = tk.Canvas(name_frame, width=25, height=25, highlightthickness=0)
            name_icon.create_oval(2, 2, 23, 23, fill=self.primary_color)
            name_icon.create_text(12, 12, text="N", fill="white", font=self.fonts['bold'])
            name_icon.pack(side="left", padx=10)  # Increased padding
            
            ttk.Label(name_frame, text="Name:", width=10, font=self.fonts['bold']).pack(side="left")
            customer_name_label = ttk.Label(name_frame, text=customer[1] or "", font=self.fonts['large'])
            customer_name_label.pack(side="left")
            
            # Phone with icon
            phone_frame = ttk.Frame(basic_frame)
            phone_frame.pack(fill="x", pady=10)  # Increased padding
            
            phone_icon = tk.Canvas(phone_frame, width=25, height=25, highlightthickness=0)
            phone_icon.create_oval(2, 2, 23, 23, fill=self.secondary_color)
            phone_icon.create_text(12, 12, text="P", fill="white", font=self.fonts['bold'])
            phone_icon.pack(side="left", padx=10)  # Increased padding
            
            ttk.Label(phone_frame, text="Phone:", width=10, font=self.fonts['bold']).pack(side="left")
            ttk.Label(phone_frame, text=customer[2] or "", font=self.fonts['default']).pack(side="left")
            
            # Date with icon
            date_frame = ttk.Frame(basic_frame)
            date_frame.pack(fill="x", pady=10)  # Increased padding
            
            date_icon = tk.Canvas(date_frame, width=25, height=25, highlightthickness=0)
            date_icon.create_rectangle(3, 3, 22, 22, fill="#e67e22")  # Orange
            date_icon.pack(side="left", padx=10)  # Increased padding
            
            ttk.Label(date_frame, text="Date:", width=10, font=self.fonts['bold']).pack(side="left")
            ttk.Label(date_frame, text=customer[3] or "", font=self.fonts['default']).pack(side="left")
            
            # Prescription sections with visual separation for right and left eye
            prescription_frame = ttk.LabelFrame(main_frame, text="Prescription Details", padding=25)  # Increased padding
            prescription_frame.pack(fill="x", pady=15)
            
            # Add hover animation to section
            prescription_frame.bind("<Enter>", lambda e: animate_section_enter(e, prescription_frame))
            prescription_frame.bind("<Leave>", lambda e: animate_section_leave(e, prescription_frame))
            
            # ... rest of the existing customer details implementation ...

            # Close button with animation
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(pady=20)  # Increased padding
            
            close_button_frame = ttk.Frame(button_frame)
            close_button_frame.pack()
            
            close_icon = tk.Canvas(close_button_frame, width=25, height=25, highlightthickness=0)  # Increased size
            close_icon.create_rectangle(4, 4, 21, 21, fill="#e74c3c")
            close_icon.create_line(8, 8, 17, 17, width=2, fill="white")
            close_icon.create_line(8, 17, 17, 8, width=2, fill="white")
            close_icon.pack(side="left", padx=5)
            
            # Use animated button
            close_button = self.create_animated_button(
                close_button_frame, 
                text="Close", 
                command=detail_window.destroy,
                bg_color="#e74c3c",
                hover_color="#c0392b"
            )
            close_button.pack(side="left")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error retrieving customer details: {e}")
    
    def view_customer_details(self, event):
        # Get selected item
        selected_item = self.customer_tree.selection()
        if not selected_item:
            return
        
        # Get customer ID
        customer_id = self.customer_tree.item(selected_item[0], "values")[0]
        
        # Show the details
        self.show_customer_details(customer_id)
    
    def add_detail_row(self, parent, label_text, value_text):
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill="x", pady=2)
        ttk.Label(row_frame, text=label_text, width=8).pack(side="left")
        ttk.Label(row_frame, text=value_text).pack(side="left", padx=5)

    def on_tab_changed(self, event):
        """Handle tab changes and set up proper scrolling for active tab"""
        # Unbind all mousewheel events
        self.root.unbind_all("<MouseWheel>")
        self.root.unbind_all("<Button-4>")
        self.root.unbind_all("<Button-5>")
        
        # Get the currently selected tab
        selected_tab = self.tab_control.index(self.tab_control.select())
        
        # Set up proper scrolling for the active tab
        if selected_tab == 0:  # Customer form tab
            self.setup_scrolling(self.form_canvas)
        else:  # Customer list tab
            self.setup_scrolling(self.list_canvas)
    
    def setup_scrolling(self, canvas):
        """Set up mousewheel scrolling for a specific canvas"""
        if not canvas:
            return
            
        # Function to handle mousewheel events
        def _on_mousewheel(event):
            # Handle Windows mousewheel
            if hasattr(event, 'delta') and event.delta:
                if event.delta < 0:
                    canvas.yview_scroll(1, "units")
                else:
                    canvas.yview_scroll(-1, "units")
            # Handle Linux mousewheel
            elif hasattr(event, 'num'):
                if event.num == 5:
                    canvas.yview_scroll(1, "units")
                elif event.num == 4:
                    canvas.yview_scroll(-1, "units")
        
        # Bind mousewheel events to root so it works regardless of focus
        self.root.bind_all("<MouseWheel>", _on_mousewheel)  # Windows
        self.root.bind_all("<Button-4>", _on_mousewheel)    # Linux scroll up
        self.root.bind_all("<Button-5>", _on_mousewheel)    # Linux scroll down

    def setup_tools_tab(self):
        """Create the tools and utilities tab"""
        # Create a main frame with scrolling capability
        main_frame = ttk.Frame(self.tools_tab)
        main_frame.pack(fill="both", expand=True)
        
        # Create a canvas for scrolling
        canvas = tk.Canvas(main_frame, bg=self.bg_color, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        
        # Add a vertical scrollbar
        v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        v_scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Create a frame inside the canvas for the form content
        tools_frame = ttk.Frame(canvas, padding=20)
        canvas_window = canvas.create_window((0, 0), window=tools_frame, anchor="nw", tags="tools_frame")
        
        # Configure canvas scrolling
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        tools_frame.bind("<Configure>", configure_scroll_region)
        
        # Make sure the canvas window stays the width of the canvas
        def configure_canvas_window(event):
            canvas.itemconfig("tools_frame", width=event.width)
        
        canvas.bind("<Configure>", configure_canvas_window)
        
        # Title with graphic decoration
        title_frame = ttk.Frame(tools_frame)
        title_frame.pack(fill="x", pady=10)
        
        center_title = ttk.Frame(title_frame)
        center_title.pack(expand=True)
        
        # Decorative line before title
        line_canvas1 = tk.Canvas(center_title, width=80, height=2, bg=self.primary_color, highlightthickness=0)
        line_canvas1.pack(side="left", padx=10)
        
        title_label = ttk.Label(center_title, text="Tools & Utilities", font=self.fonts['heading'], 
                              foreground=self.primary_color)
        title_label.pack(side="left")
        
        # Decorative line after title
        line_canvas2 = tk.Canvas(center_title, width=80, height=2, bg=self.primary_color, highlightthickness=0)
        line_canvas2.pack(side="left", padx=10)
        
        # Data Export Section
        export_frame = ttk.LabelFrame(tools_frame, text="Data Export", padding=15)
        export_frame.pack(fill="x", pady=10)
        
        # Excel export icon and description
        excel_icon_frame = ttk.Frame(export_frame)
        excel_icon_frame.pack(fill="x", pady=10)
        
        # Excel icon
        excel_canvas = tk.Canvas(excel_icon_frame, width=40, height=40, highlightthickness=0)
        excel_canvas.create_rectangle(5, 5, 35, 35, fill="#1D6F42")  # Excel green color
        excel_canvas.create_text(20, 20, text="X", fill="white", font=("Arial", 16, "bold"))
        excel_canvas.pack(side="left", padx=10)
        
        # Export description
        export_desc_frame = ttk.Frame(excel_icon_frame)
        export_desc_frame.pack(side="left", fill="x", expand=True, padx=10)
        
        ttk.Label(export_desc_frame, 
                 text="Export customer data to Excel", 
                 font=self.fonts['bold']).pack(anchor="w")
        
        ttk.Label(export_desc_frame, 
                 text="Export all your customer records, including prescriptions and product details to Excel format.", 
                 wraplength=400).pack(anchor="w", pady=5)
        
        # Export options
        options_frame = ttk.Frame(export_frame)
        options_frame.pack(fill="x", pady=10)
        
        # Export type selection
        export_type_frame = ttk.Frame(options_frame)
        export_type_frame.pack(fill="x", pady=5)
        
        ttk.Label(export_type_frame, text="Export Data:").pack(side="left", padx=5)
        
        self.export_type = tk.StringVar(value="all")
        ttk.Radiobutton(export_type_frame, text="All Customers", 
                      variable=self.export_type, value="all").pack(side="left", padx=10)
        ttk.Radiobutton(export_type_frame, text="Current Search Results", 
                      variable=self.export_type, value="search").pack(side="left", padx=10)
        
        # Export button with animation
        export_button_frame = ttk.Frame(export_frame)
        export_button_frame.pack(pady=10)
        
        export_button = self.create_animated_button(
            export_button_frame, 
            text="Export to Excel", 
            command=self.export_to_excel,
            bg_color=self.primary_color,
            hover_color="#1D6F42"  # Excel green
        )
        export_button.pack(padx=10)
        
        # Database Management Section
        db_frame = ttk.LabelFrame(tools_frame, text="Database Management", padding=15)
        db_frame.pack(fill="x", pady=10)
        
        # Backup database icon and description
        backup_icon_frame = ttk.Frame(db_frame)
        backup_icon_frame.pack(fill="x", pady=10)
        
        # Backup icon
        backup_canvas = tk.Canvas(backup_icon_frame, width=40, height=40, highlightthickness=0)
        backup_canvas.create_rectangle(5, 5, 35, 35, fill="#3498db")  # Blue
        backup_canvas.create_text(20, 20, text="B", fill="white", font=("Arial", 16, "bold"))
        backup_canvas.pack(side="left", padx=10)
        
        # Backup description
        backup_desc_frame = ttk.Frame(backup_icon_frame)
        backup_desc_frame.pack(side="left", fill="x", expand=True, padx=10)
        
        ttk.Label(backup_desc_frame, 
                 text="Database Backup & Maintenance", 
                 font=self.fonts['bold']).pack(anchor="w")
        
        ttk.Label(backup_desc_frame, 
                 text="Create a backup of your database or run maintenance tasks to optimize performance.", 
                 wraplength=400).pack(anchor="w", pady=5)
        
        # Backup buttons with animation
        backup_buttons_frame = ttk.Frame(db_frame)
        backup_buttons_frame.pack(pady=10)
        
        backup_button = self.create_animated_button(
            backup_buttons_frame, 
            text="Create Backup Now", 
            command=self.manual_backup,
            bg_color=self.primary_color,
            hover_color=self.secondary_color
        )
        backup_button.pack(side="left", padx=10)
        
        optimize_button = self.create_animated_button(
            backup_buttons_frame, 
            text="Optimize Database", 
            command=self.optimize_database,
            bg_color="#3498db",
            hover_color="#2980b9"
        )
        optimize_button.pack(side="left", padx=10)
        
        # Status info section
        status_frame = ttk.Frame(db_frame)
        status_frame.pack(fill="x", pady=10)
        
        # Show when last backup was created
        self.last_backup_label = ttk.Label(status_frame, text="Automatic backups are created every 2 hours.")
        self.last_backup_label.pack(anchor="w", padx=10)
    
    def manual_backup(self):
        """Manually create a database backup"""
        try:
            success, result = self.backup_database()
            
            if success:
                messagebox.showinfo("Backup Complete", 
                                   f"Database backup created successfully at:\n{result}")
            else:
                messagebox.showerror("Backup Failed", 
                                    f"Failed to create backup: {result}")
        except Exception as e:
            messagebox.showerror("Backup Error", f"An error occurred: {e}")
    
    def optimize_database(self):
        """Run database optimization tasks"""
        try:
            # Perform VACUUM operation
            if self.conn:
                self.conn.execute("VACUUM")
                self.conn.commit()
                
                # Check integrity
                integrity_check = self.conn.execute("PRAGMA integrity_check").fetchone()
                if integrity_check[0] == "ok":
                    messagebox.showinfo("Optimization Complete", 
                                       "Database has been optimized successfully.")
                else:
                    messagebox.showwarning("Optimization Warning", 
                                         f"Database optimization completed but integrity check found issues: {integrity_check}")
            else:
                messagebox.showerror("Optimization Failed", 
                                    "No database connection available.")
        except Exception as e:
            messagebox.showerror("Optimization Error", f"An error occurred: {e}")
    
    def export_to_excel(self):
        """Export customer data to Excel file"""
        try:
            # Determine what to export based on selection
            export_type = self.export_type.get()
            search_term = ""
            
            if export_type == "search":
                # Get the current search term from the search entry
                search_term = self.search_entry.get().strip()
            
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Save Excel Export As"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Show progress dialog
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Exporting Data")
            progress_window.geometry("300x100")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            progress_label = ttk.Label(progress_window, text="Exporting data to Excel...", padding=10)
            progress_label.pack()
            
            progress_bar = ttk.Progressbar(progress_window, mode="indeterminate")
            progress_bar.pack(fill="x", padx=20, pady=10)
            progress_bar.start()
            
            # Function to perform the export
            def do_export():
                try:
                    # Fetch customer data
                    if export_type == "all" or not search_term:
                        query = '''
                            SELECT c.id, c.name, c.phone, c.date, c.created_at
                            FROM customers c
                            ORDER BY c.date DESC
                        '''
                        customers = pd.read_sql_query(query, self.conn)
                    else:
                        # Export search results
                        query = '''
                            SELECT c.id, c.name, c.phone, c.date, c.created_at
                            FROM customers c
                            WHERE c.name LIKE ? OR c.phone LIKE ? OR c.id IN (
                                SELECT customer_id FROM products WHERE frame_name LIKE ?
                            )
                            ORDER BY c.date DESC
                        '''
                        like_term = f"%{search_term}%"
                        customers = pd.read_sql_query(query, self.conn, params=(like_term, like_term, like_term))
                    
                    # Fetch prescription data
                    query = '''
                        SELECT customer_id, right_sph, right_cyl, right_axe, right_add,
                               left_sph, left_cyl, left_axe, left_add
                        FROM prescriptions
                    '''
                    prescriptions = pd.read_sql_query(query, self.conn)
                    
                    # Fetch product data
                    query = '''
                        SELECT customer_id, frame_name, lens_name, frame_cost, lens_cost, total_cost
                        FROM products
                    '''
                    products = pd.read_sql_query(query, self.conn)
                    
                    # Create Excel writer
                    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                        # Write customers sheet
                        customers.to_excel(writer, sheet_name='Customers', index=False)
                        
                        # Write prescriptions sheet
                        prescriptions.to_excel(writer, sheet_name='Prescriptions', index=False)
                        
                        # Write products sheet
                        products.to_excel(writer, sheet_name='Products', index=False)
                        
                        # Create a summary sheet
                        summary_data = {
                            'Category': ['Total Customers', 'Total Revenue'],
                            'Count': [len(customers), products['total_cost'].sum()]
                        }
                        summary_df = pd.DataFrame(summary_data)
                        summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    
                    # Close progress window and show success
                    progress_window.destroy()
                    messagebox.showinfo("Export Complete", 
                                       f"Data has been exported to:\n{file_path}")
                
                except Exception as e:
                    progress_window.destroy()
                    messagebox.showerror("Export Error", f"An error occurred during export: {e}")
            
            # Run export in a separate thread
            export_thread = threading.Thread(target=do_export)
            export_thread.daemon = True
            export_thread.start()
            
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred: {e}")

    def create_animated_button(self, parent, text, command, bg_color=None, hover_color=None):
        """Create an animated button with hover effects"""
        if bg_color is None:
            bg_color = self.primary_color
        if hover_color is None:
            hover_color = self.secondary_color
            
        button = AnimatedButton(
            parent,
            text=text,
            command=command,
            bg_color=bg_color,
            hover_color=hover_color
        )
        return button

def main():
    # Configure high-DPI awareness for Windows
    if platform.system() == "Windows":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception as e:
            print(f"Failed to set DPI awareness: {e}")
    
    # Create a dummy icon if it doesn't exist
    if not os.path.exists("icon.png"):
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple icon
            img = Image.new('RGBA', (256, 256), (255, 255, 255, 0))  # Larger icon for high-DPI
            draw = ImageDraw.Draw(img)
            
            # Draw a circle
            draw.ellipse((20, 20, 236, 236), fill="#3498db")
            
            # Draw glasses shape
            draw.ellipse((50, 90, 110, 150), outline="white", width=6)
            draw.ellipse((146, 90, 206, 150), outline="white", width=6)
            draw.line((110, 120, 146, 120), fill="white", width=6)
            
            # Save the icon
            img.save("icon.png")
            print("Created default icon.png")
        except Exception as e:
            print(f"Could not create icon: {e}")
    
    root = tk.Tk()
    app = ShivamOpticals(root)
    root.mainloop()

if __name__ == "__main__":
    main() 