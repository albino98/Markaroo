import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import simpledialog
from tkhtmlview import HTMLLabel
from datetime import datetime
from templates import TEMPLATES

MD_DIR = "markdown_files"

if not os.path.exists(MD_DIR):
    os.makedirs(MD_DIR)

class MarkdownEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown File Manager")
        self.root.geometry("1800x700")
        
        # Carica il tema azure correttamente
        theme_path = os.path.abspath("azure.tcl")
        self.root.tk.call("source", theme_path)
        self.root.tk.call("set_theme", "azure")

        self.files = []
        self.current_file = None
        self.sort_by = "name"
        self.markdown_mode = True
        self.create_widgets()
        self.load_files()

    def create_widgets(self):
        style = ttk.Style(self.root)
        style.configure("TButton", padding=6, relief="flat", font=("Segoe UI", 10))
        style.configure("TFrame", background="#f8f8f8")
        style.configure("TLabel", background="#f8f8f8", font=("Segoe UI", 10))

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(paned_window, width=250)
        right_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        paned_window.add(right_frame, weight=4)

        self.file_listbox = tk.Listbox(
            left_frame,
            bg="#ffffff", fg="#333333",
            selectbackground="#6ca0dc", selectforeground="white",
            relief=tk.FLAT, font=("Segoe UI", 10), activestyle="none"
        )
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)

        self.sort_button = ttk.Button(left_frame, text="Sort by Date", command=self.toggle_sort)
        self.sort_button.pack(fill=tk.X, padx=5, pady=2)

        self.new_file_button = ttk.Button(left_frame, text="New File", command=self.create_new_file)
        self.new_file_button.pack(fill=tk.X, padx=5, pady=2)

        ttk.Button(left_frame, text="New To-Do List", command=lambda: self.create_template_file("To-Do List")).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(left_frame, text="New Daily Log", command=lambda: self.create_template_file("Daily Activity Log")).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(left_frame, text="New Dev Notes", command=lambda: self.create_template_file("Dev Notes")).pack(fill=tk.X, padx=5, pady=2)

        self.text = tk.Text(
            right_frame,
            bg="#fcfcfc", fg="#222222",
            insertbackground="#444444",
            font=("Consolas", 11),
            padx=10, pady=10,
            relief=tk.FLAT
        )
        self.text.pack(fill=tk.BOTH, expand=True)

        self.html_view = HTMLLabel(right_frame, html="")
        self.html_view.pack_forget()

        bottom_frame = ttk.Frame(right_frame)
        bottom_frame.pack(fill=tk.X)

        ttk.Button(bottom_frame, text="Save", command=self.save_file).pack(side=tk.LEFT)
        self.toggle_view_btn = ttk.Button(bottom_frame, text="Render Markdown", command=self.toggle_markdown_view)
        self.toggle_view_btn.pack(side=tk.LEFT, padx=5)

    def toggle_sort(self):
        self.sort_by = "date" if self.sort_by == "name" else "name"
        self.sort_button.config(text=f"Sort by {'Name' if self.sort_by == 'date' else 'Date'}")
        self.load_files()

    def load_files(self):
        files = [f for f in os.listdir(MD_DIR) if f.endswith(".md")]

        if self.sort_by == "name":
            files.sort(key=lambda x: x.lower())
        else:
            files.sort(key=lambda x: os.path.getmtime(os.path.join(MD_DIR, x)), reverse=True)

        self.files = files
        self.file_listbox.delete(0, tk.END)
        for f in files:
            mtime = os.path.getmtime(os.path.join(MD_DIR, f))
            mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            display_text = f"{f}    ({mtime_str})"
            self.file_listbox.insert(tk.END, display_text)

        if self.files:
            idx = 0 if not self.current_file or self.current_file not in self.files else self.files.index(self.current_file)
            self.file_listbox.select_set(idx)
            self.current_file = self.files[idx]
            self.load_file_content(self.current_file)

    def on_file_select(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            idx = selection[0]
            self.current_file = self.files[idx]
            self.load_file_content(self.current_file)

    def load_file_content(self, filename):
        path = os.path.join(MD_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, content)
        self.text.pack(fill=tk.BOTH, expand=True)
        self.html_view.pack_forget()
        self.markdown_mode = True
        self.toggle_view_btn.config(text="Render Markdown")

    def save_file(self):
        if self.current_file:
            path = os.path.join(MD_DIR, self.current_file)
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", tk.END))
            self.load_files()
            messagebox.showinfo("Saved", f"File '{self.current_file}' saved successfully.")

    def toggle_markdown_view(self):
        import markdown
        if self.markdown_mode:
            content = self.text.get("1.0", tk.END)
            html = markdown.markdown(content)
            self.html_view.set_html(html)
            self.text.pack_forget()
            self.html_view.pack(fill=tk.BOTH, expand=True)
            self.toggle_view_btn.config(text="Edit Markdown")
        else:
            self.html_view.pack_forget()
            self.text.pack(fill=tk.BOTH, expand=True)
            self.toggle_view_btn.config(text="Render Markdown")
        self.markdown_mode = not self.markdown_mode

    def create_new_file(self):
        filename = simpledialog.askstring("New File", "Enter file name (without extension):")
        if filename:
            if not filename.endswith(".md"):
                filename += ".md"
            path = os.path.join(MD_DIR, filename)
            if os.path.exists(path):
                messagebox.showerror("Error", f"File '{filename}' already exists.")
                return
            with open(path, "w", encoding="utf-8") as f:
                f.write("# New Markdown File\n")
            self.load_files()
            idx = self.files.index(filename)
            self.file_listbox.select_clear(0, tk.END)
            self.file_listbox.select_set(idx)
            self.current_file = filename
            self.load_file_content(filename)

    def create_template_file(self, template_name):
        base_name = template_name.lower().replace(" ", "_")
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{base_name}_{date_str}.md"
        path = os.path.join(MD_DIR, filename)

        if os.path.exists(path):
            messagebox.showerror("Error", f"File '{filename}' already exists.")
            return

        content = TEMPLATES[template_name]
        if "{date}" in content:
            content = content.format(date=datetime.now().strftime("%Y-%m-%d"))

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self.load_files()
        idx = self.files.index(filename)
        self.file_listbox.select_clear(0, tk.END)
        self.file_listbox.select_set(idx)
        self.current_file = filename
        self.load_file_content(filename)

if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownEditor(root)
    root.mainloop()
