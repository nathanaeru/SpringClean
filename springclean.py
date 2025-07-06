import os
import shutil
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import sv_ttk
import darkdetect
import pywinstyles

# Define file type categories
FILE_CATEGORIES = {
    "DOCUMENTS": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"],
    "IMAGES": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp", ".avif", ".ico", ".heic", ".heif"],
    "VIDEOS": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mpeg", ".mpg", ".3gp", ".m4v", ".hevc",],
    "AUDIO": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".opus", ".alac"],
    "CODE": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".h", ".php", ".rb", ".go", ".rs", ".ts", ".swift", ".kt", ".sh", ".bat"],
    "APPS": [".exe", ".msi", ".apk", ".dmg", ".pkg", ".app", ".deb", ".rpm", ".jar", ".war", ".iso"],
    "ARCHIVES": [".zip", ".rar", ".tar", ".gz", ".7z", ".bz2", ".xz", ".tar.gz", ".tar.bz2", ".tar.xz"],
}

# Function to apply theme to the title bar (Windows 11 and 10 only)
def apply_theme_to_titlebar(root):
    version = sys.getwindowsversion()

    if version.major == 10 and version.build >= 22000:
        # Set the title bar color to the background color on Windows 11 for better appearance
        pywinstyles.change_header_color(root, "#1c1c1c" if darkdetect.isDark() else "#fafafa")
    elif version.major == 10:
        # For Windows 10
        pywinstyles.apply_style(root, "dark" if darkdetect.isDark() else "normal")
        root.wm_attributes("-alpha", 0.99)
        root.wm_attributes("-alpha", 1)

# Function to get the category of a file based on its extension
def get_category(extension):
    for category, extensions in FILE_CATEGORIES.items():
        if extension.lower() in extensions:
            return category
    return "OTHERS"

# Main class for the GUI application
class FileOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SpringClean")
        self.root.iconbitmap("icon.ico")
        self.root.geometry("600x600")
        self.root.resizable(True, True)
        
        # Configure style
        apply_theme_to_titlebar(self.root) if sys.platform == "win32" else None
        sv_ttk.set_theme(darkdetect.theme())
        
        self.selected_folder = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="SpringClean - Organize Your Files", 
                               font=("Segoe UI", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Folder selection frame
        folder_frame = ttk.LabelFrame(main_frame, text="Select Folder to Organize", padding="10")
        folder_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Folder path entry
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.selected_folder, 
                                     width=50, state="readonly")
        self.folder_entry.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        
        # Browse button
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_folder)
        browse_btn.grid(row=0, column=1)
        
        # File categories frame
        categories_frame = ttk.LabelFrame(main_frame, text="File Categories", padding="10")
        categories_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Display file categories
        row = 0
        for category, extensions in FILE_CATEGORIES.items():
            category_label = ttk.Label(categories_frame, text=f"{category}:", 
                                     font=("Segoe UI", 10, "bold"))
            category_label.grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
            
            ext_label = ttk.Label(categories_frame, text=", ".join(extensions))
            ext_label.grid(row=row, column=1, sticky=tk.W)
            row += 1
        
        # Control buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        # Organize button
        self.organize_btn = ttk.Button(buttons_frame, text="Organize Files", 
                                      command=self.start_organizing, state="disabled")
        self.organize_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Clear button
        clear_btn = ttk.Button(buttons_frame, text="Clear", command=self.clear_selection)
        clear_btn.grid(row=0, column=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log text with scrollbar
        self.log_text = tk.Text(log_frame, height=50, wrap=tk.WORD, font=("Segoe UI", 10))
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        folder_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    # Display folder selection dialog
    def browse_folder(self):
        folder_path = filedialog.askdirectory(title="Select folder to organize")
        if folder_path:
            self.selected_folder.set(folder_path)
            self.organize_btn.config(state="normal")
            self.log_message(f"Selected folder: {folder_path}")
    
    # Clear the selected folder and reset UI
    def clear_selection(self):
        self.selected_folder.set("")
        self.organize_btn.config(state="disabled")
        self.log_text.delete(1.0, tk.END)
    
    # Log messages in the text widget
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    # Start organizing files in the selected folder
    def start_organizing(self):
        if not self.selected_folder.get():
            messagebox.showwarning("Warning", "Please select a folder first!")
            return
        
        # Disable the organize button and start progress bar
        self.organize_btn.config(state="disabled")
        self.progress.start()
        
        # Run organization in a separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.organize_files_threaded)
        thread.daemon = True
        thread.start()
    
    # Organize files in the selected folder
    def organize_files_threaded(self):
        try:
            # Get the selected folder path
            folder_path = self.selected_folder.get()
            self.log_message("Starting file organization...")
            
            files_moved = 0
            errors = 0
            
            # Check if the folder exists
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                
                # Skip directories
                if os.path.isfile(file_path):
                    ext = os.path.splitext(filename)[1]
                    category = get_category(ext)
                    
                    target_dir = os.path.join(folder_path, category)
                    os.makedirs(target_dir, exist_ok=True)
                    
                    # Move the file to the appropriate category folder
                    try:
                        shutil.move(file_path, os.path.join(target_dir, filename))
                        self.log_message(f"✓ Moved: {filename} → {category}")
                        files_moved += 1
                    except Exception as e:
                        self.log_message(f"✗ Error moving {filename}: {e}")
                        errors += 1
            
            # Show completion message
            self.log_message(f"\n=== Organization Complete ===")
            self.log_message(f"Files moved: {files_moved}")
            self.log_message(f"Errors: {errors}")
            
            # Show success dialog
            self.root.after(0, lambda: messagebox.showinfo(
                "Complete", 
                f"File organization completed!\n\nFiles moved: {files_moved}\nErrors: {errors}"
            ))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
            self.log_message(f"✗ Fatal error: {e}")
        
        finally:
            # Re-enable button and stop progress bar
            self.root.after(0, self.finish_organizing)
    
    def finish_organizing(self):
        self.progress.stop()
        self.organize_btn.config(state="normal")


def organize_downloads(path):
    """Legacy function for backward compatibility"""
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
