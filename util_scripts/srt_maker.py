import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
from itertools import takewhile
from dataclasses import dataclass

REGEXP_PHRASE = r"(.*?[.!?,;:])"
REGEXP_SENTENCE = r"(.*?[.!?])"

AI_SUGGESTION_COUNT = 3
BUTTONS_SUGGESTION_COUNT = AI_SUGGESTION_COUNT + 2
    
@dataclass
class Suggestion:
    phrase: str
    score: float

class SRTManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SRT Manager [q - replace selected, w - clear selected, e - select next phrase, r - select next sentence]")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)
        self.root.rowconfigure(2, weight=0)
        
        self.srt_data = []  # Store original SRT content with timings and text
        self.model = None  # Lazy initialization of model
        self.tokenizer = None  # Lazy initialization of tokenizer
        self.suggestions = []  # Store suggestions for buttons

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

        self.srt_table.bind("<<TreeviewSelect>>", self.restore_textbox_focus)
        self.srt_table.bind("<Double-1>", self.edit_table_cell)
        
        self.srt_table.tag_configure("mismatch", background="#CCFFCC")
        
        self.suggestions_frame = ttk.Frame(root)
        self.paned_window.add(self.suggestions_frame)
        #self.suggestions_frame.grid(row=2, column=0, pady=5, sticky="nsew")
        self.suggestions_frame.columnconfigure(0, weight=1)
        self.suggestion_buttons = []
        for i in range(BUTTONS_SUGGESTION_COUNT):
            #button = ttk.Button(self.suggestions_frame, text=f"Option {i+1}", command=lambda idx=i: self.select_suggestion(idx))
            button = self.create_text_button(self.suggestions_frame, f"Option {i+1}", lambda idx=i: self.select_suggestion(idx))
            button.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            self.suggestions_frame.rowconfigure(i, weight=1)
            self.suggestion_buttons.append(button)  
            
            
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

        self.paned_window.add(self.textbox_frame)
        
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

        self.root.bind("<q>", self.handle_hotkey)
        self.root.bind("<w>", self.clear_selected_row)
        self.root.bind("<e>", self.highlight_next_phrase)
        self.root.bind("<r>", self.highlight_next_sentence)
        
    def create_text_button(self, parent, text, command):
        """Создает текстовый виджет с поведением кнопки."""
        button = tk.Text(parent, height=1, width=30, bg="lightblue", fg="black", font=("Arial", 12), relief="raised", bd=2, wrap="none")
        button.insert("1.0", text)
        button.configure(state="normal")  # Разрешаем выделение текста
        button.is_pressed = False
        button.callback = command

        def on_press(event):
            button.is_pressed = True

        def on_release(event):
            if button.is_pressed:
                x, y = event.x, event.y
                width, height = button.winfo_width(), button.winfo_height()
                if 0 <= x <= width and 0 <= y <= height:
                    button.callback()
            button.is_pressed = False

        def on_leave(event):
            button.is_pressed = False

        button.bind("<ButtonPress-1>", on_press)
        button.bind("<ButtonRelease-1>", on_release)
        button.bind("<Leave>", on_leave)
        return button

    def lazy_load_model(self):
        """Lazy load the tokenizer and model when first required."""
        if self.model is None or self.tokenizer is None:
            from transformers import AutoTokenizer, AutoModel
            import torch
            self.tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
            self.model = AutoModel.from_pretrained("bert-base-multilingual-cased")
            self.model.eval()

    def generate_phrases(self, text, start_pos):
        """Generate phrases starting from a specific position in the text."""
        remaining_text = text[start_pos:]
        words = remaining_text.split()
        max_length = min(32, len(words))
        phrases = list(
            takewhile(lambda phrase: "." not in phrase, 
                (" ".join(words[:i]) for i in range(1, max_length + 1)))
        )
        return phrases

    def flat_to_tk_index(self, text, char_index):
        """Convert a flat character index to a Tkinter text index (line.char)."""
        current_char_count = 0
        for line_num, line in enumerate(text.split("\n"), start=1):
            line_length = len(line) + 1  # +1 for the newline character
            if current_char_count + line_length > char_index:
                char_in_line = char_index - current_char_count
                return f"{line_num}.{char_in_line}"
            current_char_count += line_length
        return f"end"
            
    def get_current_and_previous_subs(self):
        selected_item = self.srt_table.selection()
        if not selected_item:
            return None, None

        children = self.srt_table.get_children()
        if not children:
            return None, None

        current_index = children.index(selected_item[0])
        if current_index == 0:
            return None, None
            
        #TODO: previous_item/current_item need to be argument of function
        previous_item = children[current_index - 1]
        previous_text = self.srt_table.item(previous_item, "values")[1] #get previous_item translated - to search it in text
        
        current_item = children[current_index]
        current_text = self.srt_table.item(current_item, "values")[0] #get current_item non-translated - to match it with ai
        return current_text, previous_text
        
    def highlight_by_regexp(self, regexp_str):
        _, selected_text = self.get_current_and_previous_subs()
        if not selected_text:
            return

        text_content = self.textbox.get("1.0", tk.END)
        current_match = re.search(re.escape(selected_text), text_content, re.DOTALL)
        if not current_match:
            return

        start_pos = current_match.end()
        next_phrase_match = re.search(regexp_str, text_content[start_pos:], re.DOTALL)
        if not next_phrase_match:
            return

        next_phrase = next_phrase_match.group(1)
        start_char_index = start_pos + next_phrase_match.start()
        end_char_index = start_pos + next_phrase_match.end()

        start_index = self.textbox.index(f"1.0+{start_char_index}c")
        end_index = self.textbox.index(f"1.0+{end_char_index}c")

        self.textbox.tag_remove(tk.SEL, "1.0", tk.END)
        self.textbox.mark_set("insert", start_index)
        self.textbox.mark_set("anchor", end_index)
        self.textbox.tag_add(tk.SEL, start_index, end_index)
        self.textbox.focus_set()
        self.textbox.see(start_index)

    def highlight_next_phrase(self, event=None):
        self.highlight_by_regexp(REGEXP_PHRASE)
        
    def highlight_next_sentence(self, event=None):
        self.highlight_by_regexp(REGEXP_SENTENCE)
        
    def restore_textbox_focus(self, event):
        if self.textbox.tag_ranges(tk.SEL):
            self.textbox.focus_set()
        self.srt_table.focus()

    def load_srt(self):
        file_path = filedialog.askopenfilename(filetypes=[("SRT Files", "*.srt")])
        if not file_path:
            return
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.srt_data = []
        matches = re.findall(r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n((?:.+\n?)+)", content)
        for _, timing, text in matches:
            text = text.strip().replace("\n", " ")
            self.srt_data.append({"timing": timing, "text": text, "selected_text": text})

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
        self.suggestions = []

        phrase_result = self.find_by_regexp(REGEXP_PHRASE)
        if phrase_result:
            self.suggestions.append(Suggestion(phrase = phrase_result, score = 100.0))

        sentence_result = self.find_by_regexp(REGEXP_SENTENCE)
        if sentence_result and sentence_result != phrase_result:
            self.suggestions.append(Suggestion(phrase = sentence_result, score = 100.0))

        best_suggestions = self.get_topk_best_phrases(k=AI_SUGGESTION_COUNT)
        for suggestion in best_suggestions:
            if suggestion.phrase != phrase_result and suggestion.phrase != sentence_result:
                self.suggestions.append(suggestion)
            
        self.update_suggestion_buttons()
        
    def update_suggestion_buttons(self):
        for i, button in enumerate(self.suggestion_buttons):
            if i < len(self.suggestions):
                button.configure(state="normal")
                button.delete("1.0", tk.END)
                button.insert("1.0", f"{self.suggestions[i].phrase} [{self.suggestions[i].score:.2f}]")
                button.configure(state="disabled") 
            else:
                button.configure(state="normal")
                button.delete("1.0", tk.END)
                button.insert("1.0", "")
                button.configure(state="disabled")
                
    def select_suggestion(self, idx):
        """Handle selection of a suggestion by index."""
        if idx >= len(self.suggestions):
            return

        button = self.suggestion_buttons[idx]
        try:
            selected_text = button.get("sel.first", "sel.last").strip()
            if selected_text:
                suggestion = selected_text
            else:
                suggestion = self.suggestions[idx].phrase
        except tk.TclError:
            suggestion = self.suggestions[idx].phrase
        
        
        text_content = self.textbox.get("1.0", tk.END).strip()
        match = re.search(re.escape(suggestion), text_content, re.DOTALL)
        if not match:
            return

        start_char_index = match.start()
        end_char_index = match.end()

        start_index = self.textbox.index(f"1.0+{start_char_index}c")
        end_index = self.textbox.index(f"1.0+{end_char_index}c")

        self.textbox.tag_remove(tk.SEL, "1.0", tk.END)
        self.textbox.mark_set("insert", start_index)
        self.textbox.mark_set("anchor", end_index)
        self.textbox.tag_add(tk.SEL, start_index, end_index)
        self.textbox.focus_set()
        self.textbox.see(start_index)
        
        self.handle_hotkey()
            
    def find_by_regexp(self, regexp_str):
        """Helper method to find a match using a regular expression."""
        _, selected_text = self.get_current_and_previous_subs()
        if not selected_text:
            return None

        text_content = self.textbox.get("1.0", tk.END)
        current_match = re.search(re.escape(selected_text), text_content, re.DOTALL)
        if not current_match:
            return None

        start_pos = current_match.end()
        next_phrase_match = re.search(regexp_str, text_content[start_pos:], re.DOTALL)
        if next_phrase_match:
            return next_phrase_match.group(1).strip()
        return None

    def get_topk_best_phrases(self, k):
        self.lazy_load_model()  # Ensure the model is loaded

        current_row_text, previous_text = self.get_current_and_previous_subs()
        if not previous_text:
            return []

        # Get text content from the textbox
        text_content = self.textbox.get("1.0", tk.END).strip()
        if not text_content:
            return []

        flat_text_content = text_content.replace("\n", " ")
        current_match = re.search(re.escape(previous_text), flat_text_content, re.DOTALL)
        if not current_match:
            return []
        start_pos = current_match.end()

        # Generate candidate phrases starting from the end of the selected text
        tgt_phrases = self.generate_phrases(flat_text_content, start_pos)

        # Tokenize and compute embeddings
        import torch
        token_src = self.tokenizer([current_row_text], return_tensors="pt", padding=True, truncation=True)
        token_tgt = self.tokenizer(tgt_phrases, return_tensors="pt", padding=True, truncation=True)

        with torch.no_grad():
            #emb_src = self.model(**token_src).last_hidden_state.mean(dim=1)
            #emb_tgt = self.model(**token_tgt).last_hidden_state.mean(dim=1)
            emb_src = self.model(**token_src).last_hidden_state[:, 0, :] #full token instead of mean
            emb_tgt = self.model(**token_tgt).last_hidden_state[:, 0, :]

        scores = torch.matmul(emb_src, emb_tgt.T).squeeze()
        
        if scores.dim() == 0:
            return []
        
        k = min(k, len(scores))
        topk_scores, topk_indices = torch.topk(scores, k=k)

        topk_phrases = [Suggestion(phrase = tgt_phrases[idx], score = score) for (idx, score) in zip(topk_indices.tolist(), topk_scores.tolist())]
        return topk_phrases
        
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
