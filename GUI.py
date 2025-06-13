import tkinter as tk
from tkinter import END, messagebox, simpledialog
import save_load
import webbrowser
from collections import Counter

class BibliographyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Bibliography")
        self.paper_list = save_load.load_papers()
        self.filtered_list = None  # To keep track of filtered results
        self.current_keyword = None

        # --- Main Frame ---
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Keyword Column ---
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.keyword_listbox = tk.Listbox(left_frame, width=25)
        self.keyword_listbox.pack(fill=tk.Y, expand=True)
        self.keyword_listbox.bind('<<ListboxSelect>>', self.filter_by_selected_keyword)

        self.reset_button = tk.Button(left_frame, text="Reset Filter", command=self.show_all)
        self.reset_button.pack(pady=(10, 0))

        # --- Paper List and Details ---
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(right_frame, width=80)
        self.listbox.pack(padx=10, pady=10, fill=tk.X)
        self.listbox.bind('<<ListboxSelect>>', self.show_details)

        self.details = tk.Text(right_frame, width=100, height=10, wrap='word')
        self.details.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.details.tag_configure("hyperlink", foreground="blue", underline=True)
        self.details.tag_bind("hyperlink", "<Button-1>", self.open_url)

        self.current_url = None

        # --- Button Row ---
        button_frame = tk.Frame(right_frame)
        button_frame.pack(pady=5)

        self.add_button = tk.Button(button_frame, text="Add Paper", command=self.add_paper_dialog)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.edit_button = tk.Button(button_frame, text="Edit", command=self.edit_selected_paper)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        self.export_button = tk.Button(button_frame, text="Export BibTeX", command=self.export_bibtex)
        self.export_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(button_frame, text="Delete Paper", command=self.delete_selected_paper)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        # --- Populate lists ---
        self.refresh_keyword_list()
        self.refresh_list()

    def refresh_keyword_list(self):
        # Count all keywords
        keywords = []
        for p in self.paper_list:
            keywords.extend([k.lower() for k in p.get_keywords()])
        keyword_counts = Counter(keywords)
        sorted_keywords = sorted(keyword_counts.items())
        self.keyword_listbox.delete(0, END)
        for kw, count in sorted_keywords:
            self.keyword_listbox.insert(END, f"{kw} ({count})")

    def filter_by_selected_keyword(self, event):
        selection = self.keyword_listbox.curselection()
        if not selection:
            return
        kw_with_count = self.keyword_listbox.get(selection[0])
        keyword = kw_with_count.split(" (")[0]
        self.filtered_list = [p for p in self.paper_list if keyword in [k.lower() for k in p.get_keywords()]]
        self.current_keyword = keyword
        self.refresh_list()

    def show_all(self):
        self.filtered_list = None
        self.current_keyword = None
        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, END)
        papers_to_show = self.filtered_list if self.filtered_list is not None else self.paper_list
        for p in papers_to_show:
            self.listbox.insert(END, f"{p.show_id()} | {p.show_title()}")
        self.refresh_keyword_list()

    def show_details(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        papers_to_show = self.filtered_list if self.filtered_list is not None else self.paper_list
        p = papers_to_show[idx]
        self.details.delete(1.0, END)
        self.details.insert(END, f"{p.show_title()}\n", "hyperlink")
        self.current_url = p.show_url()
        self.details.insert(END, f"Keywords: {', '.join(p.get_keywords())}\n")
        self.details.insert(END, f"{p.show_abs()}\n")

    def open_url(self, event):
        if self.current_url:
            webbrowser.open(self.current_url)

    def add_paper_dialog(self):
        arxiv_id = simpledialog.askstring("Add Paper", "Enter arXiv ID:")
        if not arxiv_id:
            return
        # Duplicate detection
        if any(p.show_id() == arxiv_id for p in self.paper_list):
            messagebox.showwarning("Duplicate", f"A paper with arXiv ID {arxiv_id} already exists.")
            return
        import papers
        new_paper = papers.paper(arxiv_id)
        new_paper.get_arxiv_metadata_by_id()
        keywords = simpledialog.askstring("Add Keywords", "Enter keywords (comma separated):")
        if keywords:
            for kw in [k.strip() for k in keywords.split(",") if k.strip()]:
                new_paper.add_keyword(kw)
        self.paper_list.append(new_paper)
        save_load.save_papers(self.paper_list)
        self.show_all()

    def edit_selected_paper(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Edit Paper", "No paper selected.")
            return
        idx = selection[0]
        papers_to_show = self.filtered_list if self.filtered_list is not None else self.paper_list
        p = papers_to_show[idx]

        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Paper")

    # Title
        tk.Label(edit_win, text="Title:").grid(row=0, column=0, sticky="e")
        title_var = tk.StringVar(value=p.show_title())
        tk.Entry(edit_win, textvariable=title_var, width=60).grid(row=0, column=1)

    # Authors
        tk.Label(edit_win, text="Authors (comma separated):").grid(row=1, column=0, sticky="e")
        authors_var = tk.StringVar(value=', '.join(p.authors))
        tk.Entry(edit_win, textvariable=authors_var, width=60).grid(row=1, column=1)

    # Keywords
        tk.Label(edit_win, text="Keywords (comma separated):").grid(row=2, column=0, sticky="e")
        keywords_var = tk.StringVar(value=', '.join(p.get_keywords()))
        tk.Entry(edit_win, textvariable=keywords_var, width=60).grid(row=2, column=1)

    # Journal
        tk.Label(edit_win, text="Journal:").grid(row=3, column=0, sticky="e")
        journal_var = tk.StringVar(value=p.journal)
        tk.Entry(edit_win, textvariable=journal_var, width=60).grid(row=3, column=1)

    # DOI
        tk.Label(edit_win, text="DOI:").grid(row=4, column=0, sticky="e")
        doi_var = tk.StringVar(value=p.doi)
        tk.Entry(edit_win, textvariable=doi_var, width=60).grid(row=4, column=1)

    # Year
        tk.Label(edit_win, text="Year:").grid(row=5, column=0, sticky="e")
        year_var = tk.StringVar(value=p.year)
        tk.Entry(edit_win, textvariable=year_var, width=60).grid(row=5, column=1)

    # Abstract
        tk.Label(edit_win, text="Abstract:").grid(row=6, column=0, sticky="ne")
        abs_text = tk.Text(edit_win, width=60, height=6)
        abs_text.insert("1.0", p.abs)
        abs_text.grid(row=6, column=1)

        def save_changes():
            p.title = title_var.get()
            p.authors = [a.strip() for a in authors_var.get().split(",") if a.strip()]
            p.keywords = [k.strip() for k in keywords_var.get().split(",") if k.strip()]
            p.journal = journal_var.get()
            p.doi = doi_var.get()
            p.year = year_var.get()
            p.abs = abs_text.get("1.0", "end").strip()
            save_load.save_papers(self.paper_list)
            self.refresh_list()
            self.show_details(None)
            edit_win.destroy()

        tk.Button(edit_win, text="Save", command=save_changes).grid(row=7, column=0, columnspan=2, pady=10)

        edit_win.grab_set()  # Modal dialog

    def export_bibtex(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Export BibTeX", "No paper selected.")
            return
        idx = selection[0]
        papers_to_show = self.filtered_list if self.filtered_list is not None else self.paper_list
        p = papers_to_show[idx]
        bibtex_str = p.to_bibtex()
        # Copy to clipboard
        self.root.clipboard_clear()
        self.root.clipboard_append(bibtex_str)
        messagebox.showinfo("Export BibTeX", "BibTeX entry copied to clipboard!")

    def delete_selected_paper(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Delete Paper", "No paper selected.")
            return
        idx = selection[0]
        papers_to_show = self.filtered_list if self.filtered_list is not None else self.paper_list
        p = papers_to_show[idx]
        if messagebox.askyesno("Delete Paper", f"Are you sure you want to delete:\n\n{p.show_title()}"):
            self.paper_list.remove(p)
            save_load.save_papers(self.paper_list)
            self.show_all()


if __name__ == "__main__":
    root = tk.Tk()
    app = BibliographyGUI(root)
    root.mainloop()