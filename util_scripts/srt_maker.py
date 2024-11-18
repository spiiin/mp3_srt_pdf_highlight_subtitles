import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re


class SRTManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SRT Manager [q - replace selected, w - clear selected]")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)
        
        self.srt_data = []  # Store original SRT content with timings and text

        self.paned_window = ttk.PanedWindow(root, orient=tk.VERTICAL)
        self.paned_window.grid(row=0, column=0, sticky="nsew")

        self.treeview_frame = ttk.Frame(self.paned_window)
        self.treeview_frame.rowconfigure(0, weight=1)
        self.treeview_frame.columnconfigure(0, weight=1)
        self.srt_table = ttk.Treeview(self.treeview_frame, columns=("SRT Lines", "Selected Lines"), show="headings")
        self.srt_table.heading("SRT Lines", text="SRT Lines")
        self.srt_table.heading("Selected Lines", text="Selected Lines")
        self.srt_table.grid(row=0, column=0, sticky="nsew")
       
        self.scrollbar = ttk.Scrollbar(self.treeview_frame, orient="vertical", command=self.srt_table.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.srt_table.configure(yscrollcommand=self.scrollbar.set)

        self.treeview_frame.rowconfigure(0, weight=1)
        self.treeview_frame.columnconfigure(0, weight=1)

        self.paned_window.add(self.treeview_frame)

        self.textbox_frame = ttk.Frame(self.paned_window)
        self.textbox_frame.rowconfigure(0, weight=1)
        self.textbox_frame.columnconfigure(0, weight=1)
        self.textbox = tk.Text(self.textbox_frame, wrap="word", height=5, state="disabled")
        self.textbox.grid(row=0, column=0, sticky="nsew")

        self.textbox_frame.rowconfigure(0, weight=1)
        self.textbox_frame.columnconfigure(0, weight=1)
        
        self.textbox_scrollbar = ttk.Scrollbar(self.textbox_frame, orient="vertical", command=self.textbox.yview)
        self.textbox_scrollbar.grid(row=0, column=1, sticky="ns")
        self.textbox.configure(yscrollcommand=self.textbox_scrollbar.set)

        # Add Textbox frame to PanedWindow
        self.paned_window.add(self.textbox_frame)

        # Buttons
        self.buttons_frame = ttk.Frame(root)
        self.buttons_frame.grid(row=1, column=0, pady=5, sticky="ew")
        self.buttons_frame.columnconfigure(0, weight=1)
        self.buttons_frame.columnconfigure(1, weight=1)
        self.buttons_frame.columnconfigure(2, weight=1)

        self.load_text_button = ttk.Button(self.buttons_frame, text="Load Text File", command=self.load_text)
        self.load_text_button.grid(row=0, column=0, padx=5, sticky="ew")

        self.load_srt_button = ttk.Button(self.buttons_frame, text="Load SRT", command=self.load_srt)
        self.load_srt_button.grid(row=0, column=1, padx=5, sticky="ew")

        self.export_srt_button = ttk.Button(self.buttons_frame, text="Export SRT", command=self.export_srt)
        self.export_srt_button.grid(row=0, column=2, padx=5, sticky="ew")

        self.srt_table.bind("<<TreeviewSelect>>", self.restore_textbox_focus)
        self.srt_table.bind("<Double-1>", self.edit_table_cell)
        
        # Define Treeview tags
        self.srt_table.tag_configure("mismatch", background="#CCFFCC")
        
        self.buttons_frame.columnconfigure(0, weight=1)
        self.buttons_frame.columnconfigure(1, weight=1)
        self.buttons_frame.columnconfigure(2, weight=1)

        # Hotkey setup
        self.root.bind("<q>", self.handle_hotkey)
        self.root.bind("<w>", self.clear_selected_row)
        
    def restore_textbox_focus(self, event):
        if self.textbox.tag_ranges(tk.SEL):
            self.textbox.focus_set()
        self.srt_table.focus()

    def load_srt(self):
        file_path = filedialog.askopenfilename(filetypes=[("SRT Files", "*.srt")])
        if not file_path:
            return
        
        # Load SRT content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse SRT and store lines with timings
        self.srt_data = []
        matches = re.findall(r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n((?:.+\n?)+)", content)
        for _, timing, text in matches:
            text = text.strip().replace("\n", " ")
            self.srt_data.append({"timing": timing, "text": text, "selected_text": text})

        # Display text content in the table
        self.srt_table.delete(*self.srt_table.get_children())

        for entry in self.srt_data:
            self.srt_table.insert("", "end", values=(entry["text"], entry["selected_text"]))

    def load_text(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not file_path:
            return
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.set_textbox_content(content)

    def set_textbox_content(self, text):
        self.textbox.config(state="normal")
        self.textbox.delete("1.0", tk.END)
        self.textbox.insert("1.0", text)
        self.textbox.config(state="disabled")

    def replace_selected_line(self):
        selected_item = self.srt_table.selection()
        if not selected_item:
            return
        try:
            selected_text = self.textbox.get("sel.first", "sel.last").strip().replace("\n", " ")
        except tk.TclError:
            return

        for item in selected_item:
            values = self.srt_table.item(item, "values")
            self.srt_table.item(item, values=(values[0], selected_text), tags=("mismatch",))

    def select_next_row(self):        
        children = self.srt_table.get_children()
        if not children:
            return
        selected_item = self.srt_table.selection()
        if not selected_item:
            self.srt_table.selection_set(children[0])
        else:
            current_index = children.index(selected_item[0])
            next_index = (current_index + 1) % len(children)
            self.srt_table.selection_set(children[next_index])
            self.srt_table.see(children[next_index])
            
    def handle_hotkey(self, event=None):
        self.replace_selected_line()
        self.select_next_row()
        
    def clear_selected_row(self, event=None):
        selected_item = self.srt_table.selection()
        if not selected_item:
            return

        for item in selected_item:
            values = self.srt_table.item(item, "values")
            self.srt_table.item(item, values=(values[0], ""), tags=("mismatch",))

    def export_srt(self):
        """Export the updated table content to an SRT file."""
        if not self.srt_data:
            messagebox.showerror("Error", "No SRT file loaded.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".srt", filetypes=[("SRT Files", "*.srt")])
        if not file_path:
            return

        updated_lines = [self.srt_table.item(item)["values"][1] for item in self.srt_table.get_children()]
        srt_content = ""
        for i, entry in enumerate(self.srt_data):
            text = updated_lines[i] if i < len(updated_lines) else entry["text"]
            srt_content += f"{i + 1}\n{entry['timing']}\n{text}\n\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
            
    def edit_table_cell(self, event):
        region = self.srt_table.identify_region(event.x, event.y)
        if region != "cell":
            return

        row_id = self.srt_table.identify_row(event.y)
        column_id = self.srt_table.identify_column(event.x)

        if column_id != "#2":  # Only allow editing the second column
            return

        current_value = self.srt_table.item(row_id, "values")[1]

        x, y, width, height = self.srt_table.bbox(row_id, column_id)
        self.entry = tk.Entry(self.srt_table)
        self.entry.place(x=x, y=y, width=width, height=height)
        self.entry.insert(0, current_value)
        self.entry.focus_set()

        self.entry.bind("<FocusOut>", lambda e: self.save_table_edit(row_id))
        self.entry.bind("<Return>", lambda e: self.save_table_edit(row_id))
        
    def save_table_edit(self, row_id):
        """Save the edited value back to the table."""
        new_value = self.entry.get()
        current_values = self.srt_table.item(row_id, "values")
        self.srt_table.item(row_id, values=(current_values[0], new_value), tags=("mismatch",))
        self.entry.destroy()
        self.entry = None

root = tk.Tk()
app = SRTManagerApp(root)
root.mainloop()
