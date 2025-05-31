from tkinter import Tk, Frame, Label, Button, Entry, Listbox, Scrollbar, END, filedialog
import os

class AppUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Media EXIF Scanner")
        self.master.geometry("600x400")

        self.disk_frame = Frame(self.master)
        self.disk_frame.pack(pady=10)

        self.disk_entries = []
        self.create_disk_entry()

        self.add_disk_button = Button(self.master, text="+", command=self.create_disk_entry)
        self.add_disk_button.pack(pady=5)

        self.scan_button = Button(self.master, text="Scan Media", command=self.scan_media)
        self.scan_button.pack(pady=5)

        self.media_listbox = Listbox(self.master, width=80)
        self.media_listbox.pack(pady=10)

        self.scrollbar = Scrollbar(self.master)
        self.scrollbar.pack(side="right", fill="y")
        self.media_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.media_listbox.yview)

    def create_disk_entry(self):
        entry = Entry(self.disk_frame, width=50)
        entry.pack(padx=5, pady=5)
        self.disk_entries.append(entry)

    def scan_media(self):
        self.media_listbox.delete(0, END)
        for entry in self.disk_entries:
            path = entry.get()
            if os.path.exists(path):
                self.media_listbox.insert(END, f"Scanning: {path}")
                # Here you would call the media scanning logic
            else:
                self.media_listbox.insert(END, f"Invalid path: {path}")

if __name__ == "__main__":
    root = Tk()
    app = AppUI(root)
    root.mainloop()