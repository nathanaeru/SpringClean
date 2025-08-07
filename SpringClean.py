import os
import shutil
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
import json
import sv_ttk
import darkdetect
import pywinstyles

# Default file type categories (basic - for typical Windows users)
DEFAULT_FILE_CATEGORIES = {
    "DOCUMENTS": [".pdf", ".doc", ".docx", ".txt", ".rtf"],
    "SPREADSHEETS": [".xls", ".xlsx", ".csv"],
    "PRESENTATIONS": [".ppt", ".pptx"],
    "IMAGES": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "VIDEOS": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
    "AUDIO": [".mp3", ".wav", ".m4a", ".wma"],
    "PROGRAMS": [".exe", ".msi"],
    "COMPRESSED": [".zip", ".rar", ".7z"]
}

def load_file_categories(json_path=None):
    """Load file categories from JSON file or return defaults."""
    try:
        if json_path and os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                categories = json.load(f)
                return categories
        else:
            # Return hardcoded defaults without creating files
            return DEFAULT_FILE_CATEGORIES.copy()
    except Exception as e:
        print(f"Error loading file categories from {json_path}: {e}")
        return DEFAULT_FILE_CATEGORIES.copy()

def save_file_categories(categories, json_path="file_categories.json"):
    """Save file categories to JSON file."""
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(categories, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving file categories: {e}")
        return False

# Global variable for file categories (starts with defaults)
FILE_CATEGORIES = DEFAULT_FILE_CATEGORIES.copy()

# Default configuration settings
DEFAULT_CONFIG = {
    "theme": "auto",
    "categories_file": "",  # Empty means use built-in defaults
    "window_geometry": "600x600",
    "last_selected_folder": ""
}

def load_config(config_path="config.json"):
    """Load configuration from JSON file."""
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Ensure all required keys are present
                for key, default_value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = default_value
                return config
        else:
            # Create default config file if it doesn't exist
            save_config(DEFAULT_CONFIG, config_path)
            return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config, config_path="config.json"):
    """Save configuration to JSON file."""
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

# Global variable for configuration
APP_CONFIG = load_config()

def apply_theme_to_titlebar(root, mode):
    """Apply theme to the title bar for Windows systems."""
    version = sys.getwindowsversion()
    if version.major == 10 and version.build >= 22000:
        # Windows 11: Set title bar color to match background
        pywinstyles.change_header_color(root, "#1c1c1c" if mode == "dark" else "#fafafa")
    elif version.major == 10:
        # Windows 10: Apply style and refresh alpha for proper rendering
        pywinstyles.apply_style(root, "dark" if mode == "dark" else "normal")
        root.wm_attributes("-alpha", 0.99)
        root.wm_attributes("-alpha", 1)


def set_theme(root, mode="auto"):
    """Set the theme for the application."""
    if mode == "auto":
        mode = "dark" if darkdetect.isDark() else "light"
    if sys.platform == "win32":
        apply_theme_to_titlebar(root, mode)
    sv_ttk.set_theme(mode)

def toggle_theme(root):
    """Toggle the theme between light and dark."""
    current_theme = sv_ttk.get_theme()
    new_theme = "dark" if current_theme == "light" else "light"
    set_theme(root, new_theme)

def get_category(extension):
    """Get the category of a file based on its extension."""
    for category, extensions in FILE_CATEGORIES.items():
        if extension.lower() in extensions:
            return category
    return "OTHERS"

# Settings window class
class SettingsWindow:
    """Settings window for theme and file categories configuration."""
    
    def __init__(self, parent, main_app):
        """Initialize the settings window."""
        self.parent = parent
        self.main_app = main_app
        self.current_theme = getattr(main_app, 'current_theme', 'auto')
        
        # Create the settings window
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.iconbitmap("icon.ico")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window on parent
        self.center_window()
        
        self.create_widgets()

        set_theme(self.window, self.current_theme)
    
    def center_window(self):
        """Center the settings window on the parent window."""
        self.window.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.window.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Create and configure all settings widgets."""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Settings", font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Theme settings
        theme_frame = ttk.LabelFrame(main_frame, text="Theme Settings", padding="10")
        theme_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(theme_frame, text="Theme:").pack(anchor=tk.W)
        
        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, 
                                  values=["auto", "light", "dark"], 
                                  state="readonly", width=30)
        theme_combo.pack(anchor=tk.W, pady=(5, 0))
        theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)
        
        # File categories settings
        categories_frame = ttk.LabelFrame(main_frame, text="File Categories", padding="10")
        categories_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        ttk.Label(categories_frame, text="Load custom file categories from JSON file:").pack(anchor=tk.W)
        
        file_frame = ttk.Frame(categories_frame)
        file_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Get current categories file from config
        current_categories_file = self.main_app.config.get("categories_file", "")
        if not current_categories_file:
            current_categories_file = "[Built-in Defaults]"
        self.categories_file_var = tk.StringVar(value=current_categories_file)
        self.file_entry = ttk.Entry(file_frame, textvariable=self.categories_file_var, 
                                   width=40, state="readonly")
        self.file_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        browse_file_btn = ttk.Button(file_frame, text="Browse", command=self.browse_categories_file)
        browse_file_btn.pack(side=tk.LEFT)
        
        load_file_btn = ttk.Button(categories_frame, text="Load Categories File", 
                                  command=self.load_categories_file)
        load_file_btn.pack(pady=(10, 0))
        
        # Use defaults button
        defaults_btn = ttk.Button(categories_frame, text="Use Built-in Defaults", 
                                 command=self.use_builtin_defaults)
        defaults_btn.pack(pady=(5, 0))
        
        # Current categories info
        info_label = ttk.Label(categories_frame, text=f"Current categories: {len(FILE_CATEGORIES)} loaded")
        info_label.pack(pady=(10, 0))
        
        # Configuration info
        config_info_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_info_frame.pack(fill=tk.X, pady=(0, 20))
        
        config_file_label = ttk.Label(config_info_frame, text=f"Config file: config.json")
        config_file_label.pack(anchor=tk.W)
        
        categories_file_display = self.main_app.config.get('categories_file', '')
        if not categories_file_display:
            categories_file_display = "[Built-in Defaults]"
        categories_file_label = ttk.Label(config_info_frame, 
                                         text=f"Categories file: {categories_file_display}")
        categories_file_label.pack(anchor=tk.W)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        # Reset to defaults button
        reset_btn = ttk.Button(buttons_frame, text="Reset to Defaults", command=self.reset_to_defaults)
        reset_btn.pack(side=tk.LEFT)
        
        ttk.Button(buttons_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT)
    
    def on_theme_change(self, event=None):
        """Handle theme change from dropdown."""
        new_theme = self.theme_var.get()
        self.current_theme = new_theme
        self.main_app.current_theme = new_theme
        
        # Save theme to config
        self.main_app.config["theme"] = new_theme
        self.main_app.save_current_config()
        
        set_theme(self.parent, new_theme)
        set_theme(self.window, new_theme)
        
        # Update theme button in main window
        if hasattr(self.main_app, 'update_theme_button'):
            self.main_app.update_theme_button()
    
    def browse_categories_file(self):
        """Browse for a JSON file containing file categories."""
        file_path = filedialog.askopenfilename(
            title="Select File Categories JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.categories_file_var.set(file_path)
    
    def load_categories_file(self):
        """Load the selected categories file."""
        file_path = self.categories_file_var.get()
        
        # Handle the built-in defaults case
        if file_path == "[Built-in Defaults]":
            messagebox.showinfo("Info", "Please select a JSON file to load custom categories.")
            return
            
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid JSON file.")
            return
        
        try:
            global FILE_CATEGORIES
            new_categories = load_file_categories(file_path)
            FILE_CATEGORIES = new_categories
            
            # Save categories file path to config
            self.main_app.config["categories_file"] = file_path
            self.main_app.save_current_config()
            
            # Update the main app's category display
            self.main_app.refresh_categories_display()
            
            messagebox.showinfo("Success", f"Loaded {len(FILE_CATEGORIES)} categories from {os.path.basename(file_path)}")
            
            # Update the file entry to show the loaded file
            self.categories_file_var.set(file_path)
            
            # Update info label
            for widget in self.window.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame) and "File Categories" in child.cget("text"):
                            for subchild in child.winfo_children():
                                if isinstance(subchild, ttk.Label) and "Current categories:" in subchild.cget("text"):
                                    subchild.config(text=f"Current categories: {len(FILE_CATEGORIES)} loaded")
                                    break
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load categories file: {e}")
    
    def use_builtin_defaults(self):
        """Switch to using built-in default categories."""
        global FILE_CATEGORIES
        FILE_CATEGORIES = DEFAULT_FILE_CATEGORIES.copy()
        
        # Clear categories file from config
        self.main_app.config["categories_file"] = ""
        self.main_app.save_current_config()
        
        # Update display
        self.categories_file_var.set("[Built-in Defaults]")
        self.main_app.refresh_categories_display()
        
        # Update info label
        for widget in self.window.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.LabelFrame) and "File Categories" in child.cget("text"):
                        for subchild in child.winfo_children():
                            if isinstance(subchild, ttk.Label) and "Current categories:" in subchild.cget("text"):
                                subchild.config(text=f"Current categories: {len(FILE_CATEGORIES)} loaded")
                                break
        
        messagebox.showinfo("Success", f"Switched to built-in default categories ({len(FILE_CATEGORIES)} categories)")
    
    def reset_to_defaults(self):
        """Reset all settings to default values."""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            # Reset theme
            self.theme_var.set("auto")
            self.on_theme_change()
            
            # Reset categories file to built-in defaults
            self.categories_file_var.set("[Built-in Defaults]")
            
            # Reset main app config
            self.main_app.config.update(DEFAULT_CONFIG)
            self.main_app.save_current_config()
            
            # Reload default categories
            global FILE_CATEGORIES
            FILE_CATEGORIES = DEFAULT_FILE_CATEGORIES.copy()
            self.main_app.refresh_categories_display()
            
            # Update info label
            for widget in self.window.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame) and "File Categories" in child.cget("text"):
                            for subchild in child.winfo_children():
                                if isinstance(subchild, ttk.Label) and "Current categories:" in subchild.cget("text"):
                                    subchild.config(text=f"Current categories: {len(FILE_CATEGORIES)} loaded")
                                    break
            
            messagebox.showinfo("Settings Reset", "All settings have been reset to defaults.")

# Main class for the GUI application
class FileOrganizerGUI:
    """GUI class for the SpringClean file organizer application."""
    
    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("SpringClean")
        self.root.iconbitmap("icon.ico")
        
        # Load configuration
        global APP_CONFIG
        self.config = APP_CONFIG
        
        # Set window geometry from config
        geometry = self.config.get("window_geometry", "600x600")
        self.root.geometry(geometry)
        self.root.resizable(True, True)
        
        # Load categories file from config if specified
        categories_file = self.config.get("categories_file", "")
        if categories_file and os.path.exists(categories_file):
            global FILE_CATEGORIES
            FILE_CATEGORIES = load_file_categories(categories_file)
        # Otherwise, FILE_CATEGORIES already contains the defaults
        
        # Theme setting from config
        self.current_theme = self.config.get("theme", "auto")
        set_theme(self.root, self.current_theme)
        
        self.selected_folder = tk.StringVar()
        
        # Set last selected folder from config if it exists
        last_folder = self.config.get("last_selected_folder", "")
        if last_folder and os.path.exists(last_folder):
            self.selected_folder.set(last_folder)
        
        self.create_widgets()
        
        # Update organize button state based on folder selection
        if self.selected_folder.get():
            self.organize_btn.config(state="normal")
            self.log_message(f"Restored folder selection: {self.selected_folder.get()}")
        
        # Bind window close event to save config
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """Create and configure all GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title label
        title_label = ttk.Label(main_frame, text="SpringClean - Organize Your Files", 
                               font=("Segoe UI", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Settings button
        self.settings_btn = ttk.Button(main_frame, text="⚙", command=self.open_settings, width=3)
        self.settings_btn.grid(row=0, column=1, sticky=tk.E, padx=(0, 10), pady=(0, 20))

        # Folder selection frame
        folder_frame = ttk.LabelFrame(main_frame, text="Select Folder to Organize", padding="10")
        folder_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Folder path entry (read-only)
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.selected_folder, 
                                     width=50, state="readonly")
        self.folder_entry.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        
        # Browse folder button
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_folder)
        browse_btn.grid(row=0, column=1)
        
        # File categories display frame
        self.categories_frame = ttk.LabelFrame(main_frame, text="File Categories", padding="10")
        self.categories_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Create scrollable categories display
        self.create_categories_display()
        
        # Control buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        # Organize files button (disabled by default)
        self.organize_btn = ttk.Button(buttons_frame, text="Organize Files", 
                                      command=self.start_organizing, state="disabled")
        self.organize_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Clear selection button
        clear_btn = ttk.Button(buttons_frame, text="Clear", command=self.clear_selection)
        clear_btn.grid(row=0, column=1)
        
        # Progress bar for organization process
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log display frame
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log text area with scrollbar
        self.log_text = tk.Text(log_frame, height=50, wrap=tk.WORD, font=("Segoe UI", 10))
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights for responsive resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        folder_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def create_categories_display(self):
        """Create the scrollable display for file categories."""
        # Clear existing widgets
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
        
        # Create a frame to contain canvas and scrollbar
        container_frame = ttk.Frame(self.categories_frame)
        container_frame.pack(fill="both", expand=True)
        
        # Create a canvas and scrollbar for scrolling
        canvas = tk.Canvas(container_frame, height=120)
        scrollbar = ttk.Scrollbar(container_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display supported file categories and extensions
        row = 0
        for category, extensions in FILE_CATEGORIES.items():
            category_label = ttk.Label(scrollable_frame, text=f"{category}:", 
                                     font=("Segoe UI", 10, "bold"))
            category_label.grid(row=row, column=0, sticky=tk.W, padx=(0, 10), pady=1)
            
            # Truncate extensions list if too long for better display
            ext_text = ", ".join(extensions)
            if len(ext_text) > 70:
                ext_text = ext_text[:67] + "..."
            
            ext_label = ttk.Label(scrollable_frame, text=ext_text)
            ext_label.grid(row=row, column=1, sticky=tk.W, pady=1)
            row += 1
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Only bind mousewheel when mouse is over the canvas
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_mousewheel)
        canvas.bind('<Leave>', _unbind_mousewheel)
    
    def refresh_categories_display(self):
        """Refresh the categories display after loading new categories."""
        self.create_categories_display()
    
    def open_settings(self):
        """Open the settings window."""
        SettingsWindow(self.root, self)
    
    def update_theme_button(self):
        """Update theme button (placeholder for compatibility)."""
        pass
    
    def save_current_config(self):
        """Save current application configuration."""
        try:
            self.config["theme"] = self.current_theme
            self.config["window_geometry"] = self.root.geometry()
            self.config["last_selected_folder"] = self.selected_folder.get()
            
            global APP_CONFIG
            APP_CONFIG = self.config
            save_config(self.config)
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def on_closing(self):
        """Handle application closing event."""
        self.save_current_config()
        self.root.destroy()
    
    def browse_folder(self):
        """Display folder selection dialog and update UI."""
        folder_path = filedialog.askdirectory(title="Select folder to organize")
        if folder_path:
            self.selected_folder.set(folder_path)
            self.organize_btn.config(state="normal")
            self.log_message(f"Selected folder: {folder_path}")
            
            # Save the selected folder to config
            self.config["last_selected_folder"] = folder_path
            self.save_current_config()
    
    def clear_selection(self):
        """Clear the selected folder and reset UI elements."""
        self.selected_folder.set("")
        self.organize_btn.config(state="disabled")
        self.log_text.delete(1.0, tk.END)
    
    def log_message(self, message):
        """Log messages to the text widget and auto-scroll to bottom."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_organizing(self):
        """Start the file organization process in a separate thread."""
        if not self.selected_folder.get():
            messagebox.showwarning("Warning", "Please select a folder first!")
            return
        
        # Disable organize button and reset progress bar
        self.organize_btn.config(state="disabled")
        self.progress['value'] = 0
        
        # Run organization in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.organize_files_threaded)
        thread.daemon = True
        thread.start()
    
    def organize_files_threaded(self):
        """Organize files in the selected folder (runs in separate thread)."""
        try:
            folder_path = self.selected_folder.get()
            self.log_message("Starting file organization...")
            
            # First, count the total number of files to process
            total_files = 0
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    total_files += 1
            
            if total_files == 0:
                self.log_message("No files found to organize.")
                self.root.after(0, lambda: messagebox.showinfo("Info", "No files found to organize in the selected folder."))
                return
            
            # Set progress bar maximum
            self.root.after(0, lambda: self.progress.config(maximum=total_files))
            self.log_message(f"Found {total_files} files to organize...")
            
            files_moved = 0
            errors = 0
            processed = 0
            
            # Process each file in the selected folder
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                
                # Only process files, skip directories
                if os.path.isfile(file_path):
                    processed += 1
                    ext = os.path.splitext(filename)[1]
                    category = get_category(ext)
                    
                    target_dir = os.path.join(folder_path, category)
                    os.makedirs(target_dir, exist_ok=True)
                    
                    # Move file to appropriate category folder
                    try:
                        shutil.move(file_path, os.path.join(target_dir, filename))
                        self.log_message(f"✓ Moved: {filename} → {category}")
                        files_moved += 1
                    except Exception as e:
                        self.log_message(f"✗ Error moving {filename}: {e}")
                        errors += 1
                    
                    # Update progress bar smoothly
                    def update_progress(value):
                        self.progress['value'] = value
                        self.root.update_idletasks()
                    
                    self.root.after(0, lambda v=processed: update_progress(v))
                    
                    # Small delay for smooth visual feedback (only for larger operations)
                    if total_files > 10:
                        import time
                        time.sleep(0.05)  # 50ms delay for smoother animation
            
            # Display completion summary
            self.log_message(f"\n=== Organization Complete ===")
            self.log_message(f"Files moved: {files_moved}")
            self.log_message(f"Errors: {errors}")
            
            # Show success dialog in main thread
            self.root.after(0, lambda: messagebox.showinfo(
                "Complete", 
                f"File organization completed!\n\nFiles moved: {files_moved}\nErrors: {errors}"
            ))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
            self.log_message(f"✗ Fatal error: {e}")
        
        finally:
            # Re-enable UI elements in main thread
            self.root.after(0, self.finish_organizing)
    
    def finish_organizing(self):
        """Re-enable UI elements after organization completes."""
        self.progress['value'] = self.progress['maximum']  # Ensure progress bar shows 100%
        self.organize_btn.config(state="normal")


def organize_downloads(path):
    """Legacy function for backward compatibility."""
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)

        if os.path.isfile(file_path):
            ext = os.path.splitext(filename)[1]
            category = get_category(ext)

            target_dir = os.path.join(path, category)
            os.makedirs(target_dir, exist_ok=True)

            try:
                shutil.move(file_path, os.path.join(target_dir, filename))
                print(f"Moved: {filename} → {category}")
            except Exception as e:
                print(f"Error moving {filename}: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerGUI(root)
    root.mainloop()
