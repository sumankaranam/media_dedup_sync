from tkinter import Tk, Frame, Button, Entry, Listbox, Scrollbar, END, filedialog, Label, StringVar, OptionMenu, Canvas
from PIL import Image, ImageTk
import os
import mimetypes
import sys
import shutil
import tkinter as tk
from tkinter import ttk

# Ensure src is in sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.exif_utils import extract_exif_data
from src.utils.hash_utils import generate_hash
from src.database.db_manager import DBManager  # You must implement this

class AppUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Media EXIF Scanner")
        self.master.state('zoomed')  # Full screen on Windows

        self.db = DBManager()

        self.mode = StringVar(value="Scan")
        self.mode_menu = OptionMenu(self.master, self.mode, "Scan", "Deduplication", command=self.switch_mode)
        self.mode_menu.pack(pady=5)

        self.notebook = ttk.Notebook(self.master)
        self.scan_tab = Frame(self.notebook, bg="#eaf6fb")
        self.dedupe_tab = Frame(self.notebook, bg="#f7f7f7")
        self.notebook.add(self.scan_tab, text="Scan")
        self.notebook.add(self.dedupe_tab, text="Deduplication")
        self.notebook.pack(fill="both", expand=True)

        # Add colored headers for each mode
        self.scan_header = Label(self.scan_tab, text="Scan Mode", font=("Arial", 18, "bold"), bg="#1e90ff", fg="white", pady=10)
        self.scan_header.pack(fill="x")
        self.dedupe_header = Label(self.dedupe_tab, text="Deduplication Mode", font=("Arial", 18, "bold"), bg="#ffb347", fg="white", pady=10)
        self.dedupe_header.pack(fill="x")

        self.setup_scan_mode(parent=self.scan_tab)
        self.setup_dedupe_mode(parent=self.dedupe_tab)

        self.media_listbox = Listbox(self.scan_tab, width=120)
        self.media_listbox.pack(pady=10, fill="both", expand=True)
        self.scrollbar = Scrollbar(self.scan_tab)
        self.scrollbar.pack(side="right", fill="y")
        self.media_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.media_listbox.yview)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def switch_mode(self, *args):
        self.media_listbox.delete(0, END)
        self.clear_main_frame()
        if self.mode.get() == "Scan":
            self.setup_scan_mode()
        else:
            self.setup_dedupe_mode()

    # --- Scan Mode ---
    def setup_scan_mode(self, parent):
        self.disk_entries = []
        self.disk_frame = Frame(parent)
        self.disk_frame.pack(pady=10)
        self.create_disk_entry(parent=self.disk_frame)

        add_disk_button = Button(parent, text="+", command=lambda: self.create_disk_entry(parent=self.disk_frame))
        add_disk_button.pack(pady=5)
        extract_button = Button(parent, text="Extract EXIF & Hash", command=self.extract_exif_and_hash)
        extract_button.pack(pady=5)

    def create_disk_entry(self, parent):
        row_frame = Frame(parent)
        entry = Entry(row_frame, width=60)
        entry.pack(side="left", padx=5, pady=5)
        browse_button = Button(row_frame, text="Browse", command=lambda: self.browse_folder(entry))
        browse_button.pack(side="left", padx=2)
        remove_button = Button(row_frame, text="-", command=lambda: self.remove_disk_entry(row_frame, entry))
        remove_button.pack(side="left", padx=2)
        row_frame.pack(anchor="w")
        self.disk_entries.append(entry)

    def browse_folder(self, entry):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            entry.delete(0, END)
            entry.insert(0, folder_selected)

    def remove_disk_entry(self, row_frame, entry):
        row_frame.destroy()
        if entry in self.disk_entries:
            self.disk_entries.remove(entry)

    def extract_exif_and_hash(self):
        self.media_listbox.delete(0, END)
        for entry in self.disk_entries:
            path = entry.get()
            if not os.path.exists(path):
                self.media_listbox.insert(END, f"Invalid path: {path}")
                continue
            total_files = 0
            exif_copied = 0
            skipped = 0
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    mime_type, _ = mimetypes.guess_type(file_path)
                    if not (mime_type and (mime_type.startswith('image/') or mime_type.startswith('video/'))):
                        continue  # Not a media file, don't count
                    total_files += 1
                    try:
                        hash_value = generate_hash(file_path)
                        # --- SKIP if already in DB ---
                        if self.db.file_exists(file_path, hash_value):
                            continue
                        exif_data = extract_exif_data(file_path) if mime_type and mime_type.startswith('image/') else {}
                        exif_data = self.clean_exif_data(exif_data)
                        if exif_data:
                            exif_copied += 1
                        print(f"Saving: {file_path}, hash: {hash_value}, exif: {str(exif_data)[:100]}")
                        self.db.add_media_file(
                            disk_name=os.path.splitdrive(file_path)[0],
                            file_name=file,
                            file_path=file_path,
                            exif_data=exif_data,
                            hash_value=hash_value
                        )
                    except Exception as e:
                        skipped += 1
                        print(f"Error processing {file_path}: {e}")
                        continue
            self.media_listbox.insert(
                END,
                f"Path: {path}\n  Total media files: {total_files} | EXIF copied: {exif_copied} | Skipped: {skipped}"
            )

    def browse_metadata(self):
        self.media_listbox.delete(0, END)
        files = self.db.get_all_files()
        if not files:
            self.media_listbox.insert(END, "No metadata found in the database.")
            return

        # Table header
        header = f"{'File Name':30} | {'Path':40} | {'Hash':64} | {'EXIF Keys':20}"
        self.media_listbox.insert(END, header)
        self.media_listbox.insert(END, "-" * len(header))

        for f in files[:10]:
            exif_keys = ", ".join(f['exif_data'].keys()) if isinstance(f['exif_data'], dict) else ""
            row = f"{f['file_name'][:30]:30} | {f['file_path'][:40]:40} | {f['hash_value'][:64]:64} | {exif_keys[:20]:20}"
            self.media_listbox.insert(END, row)

    # --- Deduplication Mode ---
    def setup_dedupe_mode(self, parent=None):
        if parent is None:
            parent = self.master

        # Get all unique paths from DB
        paths = self.db.get_all_paths()
        self.selected_path = StringVar(value="All")
        path_options = ["All"] + paths
        path_menu = OptionMenu(parent, self.selected_path, *path_options)
        path_menu.pack(pady=5)
        dedupe_button = Button(parent, text="Find Duplicates", command=self.run_deduplication)
        dedupe_button.pack(pady=5)

        self.duplicate_groups = []
        self.duplicate_page = 0
        self.duplicates_per_page = 10

        self.thumb_canvas = None
        self.thumb_frame = None
        self.page_label = None
        self.prev_btn = None
        self.next_btn = None

        browse_meta_button = Button(parent, text="Browse Metadata", command=self.browse_metadata)
        browse_meta_button.pack(pady=5)

    def run_deduplication(self):
        self.media_listbox.delete(0, END)
        path = self.selected_path.get()
        if path == "All":
            files = self.db.get_all_files()
        else:
            files = self.db.get_files_by_path(path)
        # Group by hash
        hash_map = {}
        for info in files:
            h = info["hash_value"]
            if h:
                hash_map.setdefault(h, []).append(info)
        self.duplicate_groups = [group for group in hash_map.values() if len(group) > 1]
        self.duplicate_page = 0
        self.show_duplicate_page()

    def show_duplicate_page(self):
        # Remove old thumbnail frame if exists
        if hasattr(self, "v_scroll") and self.v_scroll:
            self.v_scroll.destroy()
        if self.thumb_canvas:
            self.thumb_canvas.destroy()
        if self.page_label:
            self.page_label.destroy()
        if self.prev_btn:
            self.prev_btn.destroy()
        if self.next_btn:
            self.next_btn.destroy()
        if hasattr(self, "purge_btn") and self.purge_btn:
            self.purge_btn.destroy()
        if hasattr(self, "nav_frame") and self.nav_frame:
            self.nav_frame.destroy()

        # Navigation and purge buttons at the top
        self.nav_frame = Frame(self.dedupe_tab, bg="#ffb347")
        self.nav_frame.pack(fill="x", pady=(5, 0))
        total_pages = max(1, (len(self.duplicate_groups) + self.duplicates_per_page - 1) // self.duplicates_per_page)
        self.page_label = Label(self.nav_frame, text=f"Page {self.duplicate_page+1} of {total_pages}", font=("Arial", 12, "bold"), bg="#ffb347")
        self.page_label.pack(side="left", padx=10)
        self.prev_btn = Button(self.nav_frame, text="Previous", command=self.prev_duplicate_page, bg="#fff", font=("Arial", 10, "bold"))
        self.prev_btn.pack(side="left", padx=10)
        self.next_btn = Button(self.nav_frame, text="Next", command=self.next_duplicate_page, bg="#fff", font=("Arial", 10, "bold"))
        self.next_btn.pack(side="left", padx=10)
        self.purge_btn = Button(self.nav_frame, text="Keep Selected & Purge Duplicates", command=self.purge_selected_duplicates, bg="#d9534f", fg="white", font=("Arial", 11, "bold"))
        self.purge_btn.pack(side="right", padx=10)

        # Canvas with vertical scrollbar for thumbnails
        self.thumb_canvas = Canvas(self.dedupe_tab, width=1600, height=700, bg="#f7f7f7", highlightthickness=0)
        self.thumb_canvas.pack(pady=10, fill="both", expand=True, side="left")
        self.v_scroll = Scrollbar(self.dedupe_tab, orient="vertical", command=self.thumb_canvas.yview)
        self.v_scroll.pack(side="right", fill="y")
        self.thumb_canvas.configure(yscrollcommand=self.v_scroll.set)

        self.thumb_frame = Frame(self.thumb_canvas, bg="#f7f7f7")
        self.thumb_canvas.create_window((0, 0), window=self.thumb_frame, anchor='nw')

        # Show only 10 groups per page
        self.duplicates_per_page = 10
        start = self.duplicate_page * self.duplicates_per_page
        end = start + self.duplicates_per_page
        groups = self.duplicate_groups[start:end]

        self.thumbnails = []
        self.keep_vars = []
        self.group_file_refs = []

        # Grid layout: 2 columns, 5 rows (adjust cols as needed)
        cols = 2
        for idx, group in enumerate(groups):
            row = idx // cols
            col = idx % cols
            group_card = Frame(self.thumb_frame, bd=2, relief="groove", padx=5, pady=5, bg="#fffbe6")
            group_card.grid(row=row, column=col, padx=16, pady=16, sticky="n")

            group_label = Label(group_card, text=f"Group {start+idx+1} (hash: {group[0]['hash_value'][:8]}...)", font=("Arial", 11, "bold"), bg="#fffbe6")
            group_label.pack(anchor="w", pady=(0, 4))

            thumbs_row = Frame(group_card, bg="#fffbe6")
            thumbs_row.pack(anchor="w", pady=2)
            names_row = Frame(group_card, bg="#fffbe6")
            names_row.pack(anchor="w", pady=(0,2))

            keep_var = tk.IntVar(value=0)
            self.keep_vars.append(keep_var)
            file_refs = []
            for j, f in enumerate(group):
                is_duplicate = f.get("is_duplicate", False)
                if is_duplicate:
                    thumb = self.get_thumbnail(None, purged=True)
                else:
                    thumb = self.get_thumbnail(f['file_path'], gray=False)
                thumb_label = Label(thumbs_row, image=thumb, bg="#fffbe6", bd=2, relief="ridge")
                thumb_label.image = thumb
                thumb_label.grid(row=0, column=j, padx=8, pady=2)
                file_label = Label(names_row, text=f['file_name'], wraplength=120, font=("Arial", 9), bg="#fffbe6")
                file_label.grid(row=0, column=j, padx=8, pady=(0, 6))
                rb = tk.Radiobutton(
                    thumbs_row, variable=keep_var, value=j,
                    state="disabled" if is_duplicate else "normal",
                    bg="#fffbe6"
                )
                rb.grid(row=1, column=j, pady=(2, 0))
                file_refs.append(f)
            self.group_file_refs.append(file_refs)

        self.thumb_frame.update_idletasks()
        self.thumb_canvas.config(scrollregion=self.thumb_canvas.bbox("all"))

    def get_thumbnail(self, file_path, size=(100, 100), gray=False, purged=False):
        from PIL import ImageDraw, ImageFont
        if purged:
            # Create a gray rectangle with "Purged" text
            img = Image.new('RGB', size, color='#cccccc')
            draw = ImageDraw.Draw(img)
            text = "Purged"
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except Exception:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(((size[0]-w)//2, (size[1]-h)//2), text, fill="black", font=font)
            thumb = ImageTk.PhotoImage(img)
            self.thumbnails.append(thumb)
            return thumb
        try:
            img = Image.open(file_path)
            img.thumbnail(size)
            if gray:
                img = img.convert("LA").convert("RGB")
            thumb = ImageTk.PhotoImage(img)
            self.thumbnails.append(thumb)
            return thumb
        except Exception:
            # Return a blank image if error
            img = Image.new('RGB', size, color='gray')
            thumb = ImageTk.PhotoImage(img)
            self.thumbnails.append(thumb)
            return thumb

    def next_duplicate_page(self):
        total_pages = max(1, (len(self.duplicate_groups) + self.duplicates_per_page - 1) // self.duplicates_per_page)
        if self.duplicate_page < total_pages - 1:
            self.duplicate_page += 1
            self.show_duplicate_page()

    def prev_duplicate_page(self):
        if self.duplicate_page > 0:
            self.duplicate_page -= 1
            self.show_duplicate_page()

    def purge_selected_duplicates(self):
        # For each group, keep the selected, mark others as duplicate and copy them
        dest_folder = r"C:\duplicate_pics"
        os.makedirs(dest_folder, exist_ok=True)
        for group_idx, keep_var in enumerate(self.keep_vars):
            keep_idx = keep_var.get()
            files = self.group_file_refs[group_idx]
            for idx, f in enumerate(files):
                if idx != keep_idx and not f.get("is_duplicate", False):
                    # Mark as duplicate in DB
                    self.db.mark_as_duplicate(f['file_path'])
                    # Copy file to dest_folder
                    try:
                        shutil.copy2(f['file_path'], dest_folder)
                    except Exception as e:
                        print(f"Failed to copy {f['file_path']}: {e}")
        # Refresh page to gray out purged files
        self.run_deduplication()

    def clean_exif_data(self, exif_data):
        """Recursively convert bytes and non-JSON-serializable EXIF data to strings or floats."""
        import numbers

        # Import IFDRational from PIL if available
        try:
            from PIL.TiffImagePlugin import IFDRational
        except ImportError:
            IFDRational = None

        if isinstance(exif_data, dict):
            return {k: self.clean_exif_data(v) for k, v in exif_data.items()}
        elif isinstance(exif_data, (list, tuple)):
            return [self.clean_exif_data(v) for v in exif_data]
        elif isinstance(exif_data, bytes):
            try:
                return exif_data.decode(errors="replace")
            except Exception:
                return str(exif_data)
        elif IFDRational and isinstance(exif_data, IFDRational):
            # Convert IFDRational to float
            return float(exif_data)
        elif isinstance(exif_data, numbers.Number):
            return exif_data
        else:
            return str(exif_data)

if __name__ == "__main__":
    root = Tk()
    app = AppUI(root)
    root.mainloop()