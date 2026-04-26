import os
import shutil
from datetime import datetime
from tkinter import Tk, Label, Button, filedialog, Text, Scrollbar, END, StringVar, OptionMenu
from PIL import Image
from PIL.ExifTags import TAGS

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')

def get_exif_date(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == "DateTimeOriginal":
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return None

def get_file_modification_date(file_path):
    timestamp = os.path.getmtime(file_path)
    return datetime.fromtimestamp(timestamp)

class PhotoOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Organizer (by Year)")
        self.root.geometry("600x400")

        self.folder_path = ""

        # UI Elements
        Label(root, text="Select Folder:").pack(pady=5)

        Button(root, text="Browse", command=self.browse_folder).pack(pady=5)

        self.folder_label = Label(root, text="No folder selected", fg="blue")
        self.folder_label.pack(pady=5)

        Label(root, text="Operation Mode:").pack(pady=5)

        self.mode = StringVar(value="Move")
        OptionMenu(root, self.mode, "Move", "Copy").pack(pady=5)

        Button(root, text="Start Organizing", command=self.organize).pack(pady=10)

        # Log box with scrollbar
        self.log_box = Text(root, height=15)
        self.log_box.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        scrollbar = Scrollbar(root, command=self.log_box.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_box.config(yscrollcommand=scrollbar.set)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = folder
            self.folder_label.config(text=folder)

    def log(self, message):
        self.log_box.insert(END, message + "\n")
        self.log_box.see(END)

    def organize(self):
        if not self.folder_path:
            self.log("❌ Please select a folder first.")
            return

        mode = self.mode.get()

        for filename in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, filename)

            if not os.path.isfile(file_path):
                continue

            if not filename.lower().endswith(IMAGE_EXTENSIONS):
                continue

            # Get date
            date_taken = get_exif_date(file_path)
            if not date_taken:
                date_taken = get_file_modification_date(file_path)

            year = str(date_taken.year)

            year_folder = os.path.join(self.folder_path, year)
            os.makedirs(year_folder, exist_ok=True)

            destination = os.path.join(year_folder, filename)

            try:
                if mode == "Move":
                    shutil.move(file_path, destination)
                    self.log(f"Moved: {filename} → {year}/")
                else:
                    shutil.copy2(file_path, destination)
                    self.log(f"Copied: {filename} → {year}/")
            except Exception as e:
                self.log(f"Error processing {filename}: {e}")

        self.log("✅ Done organizing photos!")

if __name__ == "__main__":
    root = Tk()
    app = PhotoOrganizerApp(root)
    root.mainloop()