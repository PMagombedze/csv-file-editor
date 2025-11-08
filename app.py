import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
import csv
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CSVEditor(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("CSV File Editor")
        self.geometry("1000x600")
        
        self.data = []
        self.headers = []
        self.current_file = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Top button frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkButton(btn_frame, text="Open CSV", command=self.open_file, width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Save CSV", command=self.save_file, width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Add Row", command=self.add_row, width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Add Column", command=self.add_column, width=100).pack(side="left", padx=5)
        
        self.file_label = ctk.CTkLabel(btn_frame, text="No file loaded", font=("Arial", 12))
        self.file_label.pack(side="left", padx=20)
        
        # Container frame for scrollable area
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Create canvas
        self.canvas = tk.Canvas(container, bg="#2b2b2b", highlightthickness=0)
        
        # Create CustomTkinter scrollbars (they're dark themed)
        v_scrollbar = ctk.CTkScrollbar(container, orientation="vertical", command=self.canvas.yview)
        h_scrollbar = ctk.CTkScrollbar(container, orientation="horizontal", command=self.canvas.xview)
        
        # Configure canvas
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for scrollbars and canvas
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Create frame inside canvas
        self.table_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
        
        # Bind events
        self.table_frame.bind("<Configure>", self.on_frame_configure)
        
        # Bind mouse wheel
        self.bind_mousewheel()
        
    def bind_mousewheel(self):
        """Bind mouse wheel events"""
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        def on_shift_mousewheel(event):
            self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
        
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<Shift-MouseWheel>", on_shift_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<Shift-MouseWheel>"))
        
    def on_frame_configure(self, event=None):
        """Update scroll region when frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    
                    if rows:
                        self.headers = rows[0]
                        self.data = rows[1:]
                        self.current_file = file_path
                        self.file_label.configure(text=f"File: {os.path.basename(file_path)}")
                        self.display_table()
                    else:
                        messagebox.showwarning("Empty File", "The CSV file is empty.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")
    
    def save_file(self):
        if not self.headers:
            messagebox.showwarning("No Data", "No data to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save CSV File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=os.path.basename(self.current_file) if self.current_file else "untitled.csv"
        )
        
        if file_path:
            try:
                # Collect current data from entries
                self.collect_data_from_entries()
                
                with open(file_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.headers)
                    writer.writerows(self.data)
                
                self.current_file = file_path
                self.file_label.configure(text=f"File: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
    
    def collect_data_from_entries(self):
        """Collect data from entry widgets back into data structure"""
        if not hasattr(self, 'entry_widgets'):
            return
        
        # Update headers
        for col, entry in enumerate(self.header_entries):
            self.headers[col] = entry.get()
        
        # Update data - rebuild data array from entry widgets
        self.data = []
        for row_entries in self.entry_widgets:
            row_data = [entry.get() for entry in row_entries]
            self.data.append(row_data)
    
    def display_table(self):
        # Clear existing table
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        if not self.headers:
            return
        
        self.entry_widgets = []
        self.header_entries = []
        
        # Display headers (editable)
        for col, header in enumerate(self.headers):
            entry = ctk.CTkEntry(self.table_frame, width=120, font=("Arial", 12, "bold"))
            entry.grid(row=0, column=col, padx=2, pady=2, sticky="ew")
            entry.insert(0, header)
            self.header_entries.append(entry)
        
        # Display data (editable)
        for row_idx, row in enumerate(self.data):
            row_entries = []
            for col_idx, cell in enumerate(row):
                entry = ctk.CTkEntry(self.table_frame, width=120)
                entry.grid(row=row_idx+1, column=col_idx, padx=2, pady=2, sticky="ew")
                entry.insert(0, cell)
                row_entries.append(entry)
            self.entry_widgets.append(row_entries)
        
        # Update scroll region
        self.table_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def add_row(self):
        if not self.headers:
            messagebox.showwarning("No Headers", "Please load a CSV file first.")
            return
        
        # Collect current data first
        self.collect_data_from_entries()
        
        # Find maximum number of columns from headers and first 3 rows
        max_cols = len(self.headers)
        
        # Check first 3 rows for maximum columns
        for i in range(min(3, len(self.data))):
            if len(self.data[i]) > max_cols:
                max_cols = len(self.data[i])
        
        # Ensure headers match max columns
        while len(self.headers) < max_cols:
            self.headers.append(f"Column_{len(self.headers) + 1}")
        
        # Ensure each existing row has the correct number of columns
        for row in self.data:
            while len(row) < max_cols:
                row.append("")
        
        # Add new empty row with correct number of columns
        new_row = [""] * max_cols
        self.data.append(new_row)
        
        # Refresh display
        self.display_table()
    
    def add_column(self):
        if not self.headers:
            messagebox.showwarning("No Headers", "Please load a CSV file first.")
            return
        
        # Collect current data first
        self.collect_data_from_entries()
        
        # Ask for column name
        dialog = ctk.CTkInputDialog(text="Enter column name:", title="Add Column")
        col_name = dialog.get_input()
        
        if col_name:
            self.headers.append(col_name)
            
            # Add empty cell to each row
            for row in self.data:
                row.append("")
            
            # Refresh display
            self.display_table()

if __name__ == "__main__":
    app = CSVEditor()
    app.mainloop()