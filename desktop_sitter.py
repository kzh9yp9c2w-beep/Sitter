import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import webbrowser
import os
import sys

# Files to permanently save your data
LINKS_FILE = "sitter_links.txt"
POSITION_FILE = "sitter_position.txt"

# HELPER FUNCTION: Tells the code where to look for assets whether running raw or compiled
def resource_path(relative_path):
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DesktopSitter:
    def __init__(self, root):
        self.root = root
        
        # Configure a borderless, always-on-top window
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.config(bg="white")
        
        # Make the white background transparent (Windows only)
        self.root.wm_attributes("-transparentcolor", "white")
        
        # Automatically look for the image across common formats using resource_path
        possible_extensions = [".png", ".jpg", ".jpeg", ".webp"]
        image_path = None
        
        for ext in possible_extensions:
            test_path = resource_path(f"sitter{ext}")
            if os.path.exists(test_path):
                image_path = test_path
                break
                
        if not image_path and os.path.exists(resource_path("sitter")):
            image_path = resource_path("sitter")
            
        # Load and resize the character image
        if image_path:
            try:
                self.img = Image.open(image_path)
                self.img = self.img.resize((100, 100), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(self.img)
            except Exception as e:
                messagebox.showerror("Error", f"Could not read the image file: {e}")
                self.root.destroy()
                return
        else:
            messagebox.showerror("Error", "Could not find your 'sitter' image file inside assets.")
            self.root.destroy()
            return
            
        # Create a label to hold the image
        self.label = tk.Label(self.root, image=self.photo, bg="white", bd=0)
        self.label.pack()
        
        # Set default position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        default_x = screen_width - 150
        default_y = screen_height - 150
        
        if os.path.exists(POSITION_FILE):
            try:
                with open(POSITION_FILE, "r") as f:
                    pos_text = f.read().strip()
                    saved_x, saved_y = map(int, pos_text.split(","))
                    if 0 <= saved_x < screen_width and 0 <= saved_y < screen_height:
                        default_x = saved_x
                        default_y = saved_y
            except:
                pass
                
        self.root.geometry(f"100x100+{default_x}+{default_y}")
        
        # Bind mouse events for dragging and clicking
        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.drag)
        self.label.bind("<ButtonRelease-1>", self.end_drag)
        
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Exit", command=self.root.destroy)
        self.label.bind("<Button-3>", self.show_menu)
        
        self.drag_data = {"x": 0, "y": 0}
        self.is_dragging = False
        
    def start_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.is_dragging = False
        
    def drag(self, event):
        if abs(event.x - self.drag_data["x"]) > 2 or abs(event.y - self.drag_data["y"]) > 2:
            self.is_dragging = True
            deltax = event.x - self.drag_data["x"]
            deltay = event.y - self.drag_data["y"]
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")
            
    def end_drag(self, event):
        if self.is_dragging:
            current_x = self.root.winfo_x()
            current_y = self.root.winfo_y()
            with open(POSITION_FILE, "w") as f:
                f.write(f"{current_x},{current_y}")
        else:
            self.open_link_box()
            
    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)
        
    def open_link_box(self):
        self.box = tk.Toplevel(self.root)
        self.box.title("Sitter")
        box_width = 450
        box_height = 320
        
        sitter_x = self.root.winfo_x()
        sitter_y = self.root.winfo_y()
        box_x = (sitter_x + 50) - (box_width // 2)
        box_y = sitter_y - box_height - 15
        
        if box_y < 0:
            box_y = sitter_y + 115
        if box_x < 0:
            box_x = 10
            
        self.box.geometry(f"{box_width}x{box_height}+{box_x}+{box_y}")
        self.box.attributes("-topmost", True)
        
        lbl = tk.Label(self.box, text="Your Links:", font=("Arial", 10, "bold"))
        lbl.pack(pady=5)
        
        self.text_area = tk.Text(self.box, wrap="none", height=10)
        self.text_area.pack(padx=10, pady=5, fill="both", expand=True)
        
        if os.path.exists(LINKS_FILE):
            with open(LINKS_FILE, "r") as f:
                self.text_area.insert("1.0", f.read())
                
        btn_frame = tk.Frame(self.box)
        btn_frame.pack(pady=10)
        
        save_btn = tk.Button(btn_frame, text="Save Links", command=self.save_links, bg="#4CAF50", fg="white")
        save_btn.pack(side="left", padx=5)
        
        single_btn = tk.Button(btn_frame, text="Open Selected Link", command=self.launch_single_link, bg="#9C27B0", fg="white")
        single_btn.pack(side="left", padx=5)
        
        launch_btn = tk.Button(btn_frame, text="Open All Links", command=self.launch_links, bg="#2196F3", fg="white")
        launch_btn.pack(side="left", padx=5)
        
    def save_links(self):
        links_content = self.text_area.get("1.0", "end-1c")
        with open(LINKS_FILE, "w") as f:
            f.write(links_content)
        messagebox.showinfo("Saved", "Your links have been saved successfully!")
        
    def clean_url(self, url):
        url = url.strip()
        if not url or url.startswith(("-", "#", "=", "*")) or "." not in url:
            return None
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url
        
    def launch_single_link(self):
        try:
            current_line = self.text_area.get("insert linestart", "insert lineend")
            url = self.clean_url(current_line)
            if url:
                webbrowser.open(url)
            else:
                messagebox.showwarning("Invalid", "The line your cursor is on does not contain a valid web link.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open link: {e}")
            
    def launch_links(self):
        links_content = self.text_area.get("1.0", "end-1c")
        lines = links_content.split("\n")
        opened_count = 0
        for line in lines:
            url = self.clean_url(line)
            if url:
                webbrowser.open(url)
                opened_count += 1
        if opened_count == 0:
            messagebox.showwarning("Empty", "No valid links found to open.")

if __name__ == "__main__":
    window = tk.Tk()
    app = DesktopSitter(window)
    window.mainloop()