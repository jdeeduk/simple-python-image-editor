import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import uuid
import os

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Converter")
        self.root.geometry("400x250")

        self.label = tk.Label(root, text="Drag and drop images here or click 'Select Images'")
        self.label.pack(pady=10)

        self.select_button = tk.Button(root, text="Select Images", command=self.select_images)
        self.select_button.pack(pady=5)

        self.images = []

        self.width_label = tk.Label(root, text="Set target width (px):")
        self.width_label.pack(pady=5)

        self.width_entry = tk.Entry(root)
        self.width_entry.pack(pady=5)
        self.width_entry.insert(0, "800")

        self.convert_button = tk.Button(root, text="Convert", command=self.convert_images)
        self.convert_button.pack(pady=10)

        # Enable drag and drop for files
        self.root.drop_target_register('DND_Files')
        self.root.dnd_bind('<<Drop>>', self.drop_images)

    def select_images(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp *.tiff")]
        )
        if files:
            self.images = list(files)
            self.label.config(text=f"{len(self.images)} image(s) selected")

    def drop_images(self, event):
        files = self.root.splitlist(event.data)
        valid_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff'))]
        if valid_files:
            self.images = valid_files
            self.label.config(text=f"{len(self.images)} image(s) dropped")

    def convert_images(self):
        if not self.images:
            messagebox.showerror("Error", "No images selected.")
            return

        try:
            target_width = int(self.width_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Width must be a number.")
            return

        output_dir = filedialog.askdirectory(title="Select Output Folder")
        if not output_dir:
            return

        for image_path in self.images:
            try:
                img = Image.open(image_path)
                w_percent = (target_width / float(img.size[0]))
                target_height = int((float(img.size[1]) * float(w_percent)))
                img = img.resize((target_width, target_height), Image.LANCZOS)

                # Strip metadata by creating a new image object
                clean_img = Image.new(img.mode, img.size)
                clean_img.putdata(list(img.getdata()))

                new_filename = f"{uuid.uuid4()}.png"
                output_path = os.path.join(output_dir, new_filename)
                clean_img.save(output_path, format="PNG")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to convert {image_path}\n{e}")

        messagebox.showinfo("Done", "Conversion complete.")

if __name__ == "__main__":
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
    except ImportError:
        # Fallback if tkinterdnd2 is not installed
        root = tk.Tk()
        messagebox.showwarning(
            "Drag and Drop Disabled",
            "Install 'tkinterdnd2' to enable drag and drop support:\n\npip install tkinterdnd2"
        )

    app = ImageConverterApp(root)
    root.mainloop()
