import pandas as pd
import tkinter as tk
from tkinter import filedialog, Scrollbar, ttk

class CSVViewerApp:
    def __init__(self, root):

        self.root = root
        self.root.iconbitmap('sketch.ico')
        self.root.title("CSV Viewer")

        # Pencere boyutunu ve konumunu ayarla
        window_width = 800
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        self.load_button = tk.Button(self.root, text="CSV Dosyası Yükle", command=self.load_csv)
        self.load_button.pack()

        self.show_tooltip_var = tk.IntVar(value=0)  # Tooltip kontrolü için değişken
        self.show_tooltip_checkbox = tk.Checkbutton(self.root, text="Tooltip Göster", variable=self.show_tooltip_var, command=self.toggle_tooltip)
        self.show_tooltip_checkbox.pack()

        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(expand=True, fill=tk.BOTH)

        self.table = None
        self.scrollbar_x = None  # Yatay kaydırma çubuğu
        self.scrollbar_y = None  # Dikey kaydırma çubuğu
        self.tooltip = None
        self.tooltip_visible = False


    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Dosyaları", "*.csv")])
        if file_path:
            try:
                df = pd.read_csv(file_path)
                self.display_dataframe(df)
            except Exception as e:
                self.clear_table()
                self.show_message(f"Dosya yüklenirken bir hata oluştu:\n{e}")

    def display_dataframe(self, df):
        self.clear_table()

        columns = list(df.columns)
        self.table = ttk.Treeview(self.table_frame, columns=columns, show="headings")

        for column in columns:
            self.table.heading(column, text=column)
            self.table.column(column, width=100)  # Sabit sütun genişliği

        self.scrollbar_x = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL, command=self.table.xview)
        self.table.configure(xscrollcommand=self.scrollbar_x.set)

        self.scrollbar_y = Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=self.scrollbar_y.set)

        self.scrollbar_x.pack(fill=tk.X)
        self.scrollbar_y.pack(fill=tk.Y, side=tk.RIGHT)
        self.table.pack(side="top", fill="both", expand=True)

        for index, row in df.iterrows():
            values = [value if pd.notna(value) else "NULL" for value in row]
            self.table.insert("", index, values=values)

        self.table.bind("<Motion>", self.show_tooltip)
        self.tooltip = None

    def clear_table(self):
        if self.table is not None:
            for child in self.table.get_children():
                self.table.delete(child)

    def show_message(self, message):
        message_box = tk.messagebox.showerror("Hata", message)

    def toggle_tooltip(self):
        if self.show_tooltip_var.get():
            self.table.bind("<Motion>", self.show_tooltip)
        else:
            self.table.unbind("<Motion>")
            self.hide_tooltip()

    def show_tooltip(self, event):
        item = self.table.identify("item", event.x, event.y)
        if item and self.show_tooltip_var.get():  # Eğer tooltip açıkken işlem yapılacak
            column = self.table.identify("column", event.x, event.y)
            column_name = self.table.heading(column)["text"]
            value = self.table.item(item, "values")[self.table["columns"].index(column_name)]
            if len(str(value)) > 25:
                if self.tooltip:
                    self.tooltip.destroy()
                x_offset = event.x_root + 10
                y_offset = event.y_root + 10
                if x_offset + 300 > self.root.winfo_screenwidth():
                    x_offset = self.root.winfo_screenwidth() - 310
                self.tooltip = tk.Toplevel(self.root)
                self.tooltip.geometry("+{}+{}".format(x_offset, y_offset))
                tk.Label(self.tooltip, text=value, justify="left", relief="solid", borderwidth=1, wraplength=300).pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    # Yeni metin filtreleme işlevi
    def apply_filter(self):
        filter_text = self.filter_entry.get().lower()
        self.filtered_keywords = filter_text.split()  # Filtrelenen kelimeleri ayırarak listeye ekle
        for row_id in self.table.get_children():
            values = self.table.item(row_id, 'values')
            if all(any(keyword in str(value).lower() for value in values) for keyword in self.filtered_keywords):
                self.table.item(row_id, tags=('visible',))
            else:
                self.table.item(row_id, tags=('hidden',))
        self.table.tag_configure('visible', background='white')
        self.table.tag_configure('hidden', background='lightgray')




if __name__ == "__main__":
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.mainloop()
