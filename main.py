import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import uuid
import os

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Metadata Remover")
        self.root.geometry("950x750")

        self.images = []
        self.thumbnails = []
        self.image_rotations = {}  # Track rotation angle for each image path
        
        # Top frame for buttons and controls
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10, padx=10, fill=tk.X)

        self.select_button = tk.Button(top_frame, text="Select Images", command=self.select_images, font=("Arial", 10))
        self.select_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(top_frame, text="Clear All", command=self.clear_images, font=("Arial", 10))
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.image_count_label = tk.Label(top_frame, text="No images selected", font=("Arial", 10))
        self.image_count_label.pack(side=tk.LEFT, padx=20)

        # Metadata options frame
        options_frame = tk.LabelFrame(root, text="Metadata Removal Options", padx=10, pady=10)
        options_frame.pack(pady=10, padx=10, fill=tk.X)

        self.remove_all_var = tk.BooleanVar(value=True)
        self.remove_exif_var = tk.BooleanVar(value=True)
        self.remove_icc_var = tk.BooleanVar(value=True)
        self.remove_xmp_var = tk.BooleanVar(value=True)

        tk.Checkbutton(options_frame, text="Select All Metadata", variable=self.remove_all_var, 
                      command=self.toggle_all_metadata, font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        tk.Checkbutton(options_frame, text="EXIF Data (camera settings, date, location)", 
                      variable=self.remove_exif_var, font=("Arial", 9)).grid(row=1, column=0, sticky=tk.W, padx=20)
        tk.Checkbutton(options_frame, text="ICC Profile (color profile)", 
                      variable=self.remove_icc_var, font=("Arial", 9)).grid(row=2, column=0, sticky=tk.W, padx=20)
        tk.Checkbutton(options_frame, text="XMP Data (additional metadata)", 
                      variable=self.remove_xmp_var, font=("Arial", 9)).grid(row=3, column=0, sticky=tk.W, padx=20)

        # Resize options frame
        resize_frame = tk.LabelFrame(root, text="Resize Options", padx=10, pady=10)
        resize_frame.pack(pady=10, padx=10, fill=tk.X)

        self.resize_enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(resize_frame, text="Enable Resize", variable=self.resize_enabled_var, 
                      font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W)

        tk.Label(resize_frame, text="Target width (px):", font=("Arial", 9)).grid(row=0, column=1, padx=10)
        self.width_entry = tk.Entry(resize_frame, width=10)
        self.width_entry.grid(row=0, column=2)
        self.width_entry.insert(0, "800")

        # Output options frame
        output_frame = tk.LabelFrame(root, text="Output Options", padx=10, pady=10)
        output_frame.pack(pady=10, padx=10, fill=tk.X)

        self.randomize_names_var = tk.BooleanVar(value=True)
        tk.Checkbutton(output_frame, text="Randomize Filenames (UUID)", variable=self.randomize_names_var, 
                      font=("Arial", 10)).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        tk.Label(output_frame, text="(Uncheck to keep original filenames)", 
                font=("Arial", 8), fg="gray").grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=20)

        # Output format selection
        tk.Label(output_frame, text="Output Format:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        self.output_format_var = tk.StringVar(value="PNG")
        
        format_frame = tk.Frame(output_frame)
        format_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=20)
        
        formats = [
            ("PNG", "Lossless, larger files, supports transparency"),
            ("JPEG", "Lossy compression, smaller files, no transparency"),
            ("WebP", "Modern format, good compression, supports transparency"),
            ("BMP", "Uncompressed, very large files, high quality"),
            ("TIFF", "Lossless, large files, professional archival")
        ]
        
        for idx, (fmt, description) in enumerate(formats):
            rb = tk.Radiobutton(format_frame, text=f"{fmt}", variable=self.output_format_var, 
                               value=fmt, font=("Arial", 9))
            rb.grid(row=idx, column=0, sticky=tk.W)
            
            desc_label = tk.Label(format_frame, text=f"- {description}", 
                                 font=("Arial", 8), fg="gray")
            desc_label.grid(row=idx, column=1, sticky=tk.W, padx=5)

        # Image grid frame with scrollbar
        grid_frame = tk.LabelFrame(root, text="Image Preview (Click to view full size)", padx=5, pady=5)
        grid_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(grid_frame, bg="white")
        scrollbar = tk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Convert button
        self.convert_button = tk.Button(root, text="Convert & Save", command=self.convert_images, 
                                       font=("Arial", 12, "bold"), bg="lightgray")
        self.convert_button.pack(pady=10)

        # Enable drag and drop for files
        try:
            self.root.drop_target_register('DND_Files')
            self.root.dnd_bind('<<Drop>>', self.drop_images)
        except:
            pass

    def toggle_all_metadata(self):
        """Toggle all metadata checkboxes"""
        select_all = self.remove_all_var.get()
        self.remove_exif_var.set(select_all)
        self.remove_icc_var.set(select_all)
        self.remove_xmp_var.set(select_all)

    def clear_images(self):
        """Clear all selected images"""
        self.images = []
        self.thumbnails = []
        self.image_rotations = {}
        self.display_image_grid()
        self.image_count_label.config(text="No images selected")

    def select_images(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp *.tiff")]
        )
        if files:
            self.images = list(files)
            # Initialize rotation angles for new images
            for img_path in self.images:
                if img_path not in self.image_rotations:
                    self.image_rotations[img_path] = 0
            self.image_count_label.config(text=f"{len(self.images)} image(s) selected")
            self.display_image_grid()

    def drop_images(self, event):
        files = self.root.splitlist(event.data)
        valid_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff'))]
        if valid_files:
            self.images = valid_files
            # Initialize rotation angles for new images
            for img_path in self.images:
                if img_path not in self.image_rotations:
                    self.image_rotations[img_path] = 0
            self.image_count_label.config(text=f"{len(self.images)} image(s) dropped")
            self.display_image_grid()

    def rotate_image(self, image_path, degrees):
        """Rotate an image by the specified degrees"""
        if image_path not in self.image_rotations:
            self.image_rotations[image_path] = 0
        
        self.image_rotations[image_path] = (self.image_rotations[image_path] + degrees) % 360
        self.display_image_grid()

    def display_image_grid(self):
        """Display images in a 5-column grid"""
        # Clear existing thumbnails
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.thumbnails = []

        if not self.images:
            tk.Label(self.scrollable_frame, text="No images to display", 
                    font=("Arial", 12), bg="white").pack(pady=50)
            return

        # Create thumbnails in a grid
        columns = 5
        thumbnail_size = 150

        for idx, image_path in enumerate(self.images):
            row = idx // columns
            col = idx % columns

            try:
                # Create thumbnail
                img = Image.open(image_path)
                
                # Apply rotation if set
                rotation = self.image_rotations.get(image_path, 0)
                if rotation != 0:
                    img = img.rotate(-rotation, expand=True)
                
                img.thumbnail((thumbnail_size, thumbnail_size), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.thumbnails.append(photo)

                # Create frame for each image
                frame = tk.Frame(self.scrollable_frame, bg="white", relief=tk.RAISED, borderwidth=2)
                frame.grid(row=row, column=col, padx=5, pady=5)

                # Image label (clickable)
                img_label = tk.Label(frame, image=photo, cursor="hand2", bg="white")
                img_label.pack()
                img_label.bind("<Button-1>", lambda e, path=image_path: self.show_full_image(path))

                # Rotation controls frame
                rotation_frame = tk.Frame(frame, bg="white")
                rotation_frame.pack(pady=2)

                # Rotate left button
                left_btn = tk.Button(rotation_frame, text="↺ 90°", 
                                    command=lambda p=image_path: self.rotate_image(p, -90),
                                    font=("Arial", 7), width=5)
                left_btn.pack(side=tk.LEFT, padx=2)

                # Rotation angle display
                angle_display = tk.Label(rotation_frame, text=f"{rotation}°", 
                                        font=("Arial", 7), bg="white", width=4)
                angle_display.pack(side=tk.LEFT, padx=2)

                # Rotate right button
                right_btn = tk.Button(rotation_frame, text="↻ 90°", 
                                     command=lambda p=image_path: self.rotate_image(p, 90),
                                     font=("Arial", 7), width=5)
                right_btn.pack(side=tk.LEFT, padx=2)

                # Filename label
                filename = os.path.basename(image_path)
                if len(filename) > 20:
                    filename = filename[:17] + "..."
                name_label = tk.Label(frame, text=filename, font=("Arial", 8), bg="white")
                name_label.pack()

            except Exception as e:
                print(f"Error loading thumbnail for {image_path}: {e}")

    def show_full_image(self, image_path):
        """Show full size image in a new window"""
        preview_window = tk.Toplevel(self.root)
        preview_window.title(f"Preview: {os.path.basename(image_path)}")
        
        # Load and display image
        img = Image.open(image_path)
        original_size = img.size
        
        # Apply rotation if set
        rotation = self.image_rotations.get(image_path, 0)
        if rotation != 0:
            img = img.rotate(-rotation, expand=True)
        
        # Resize if too large for screen
        max_width = 1200
        max_height = 800
        
        if img.width > max_width or img.height > max_height:
            ratio = min(max_width / img.width, max_height / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        
        photo = ImageTk.PhotoImage(img)
        
        # Display image
        label = tk.Label(preview_window, image=photo)
        label.image = photo  # Keep a reference
        label.pack(padx=10, pady=10)
        
        # Add image info
        info_text = f"Path: {image_path}\nOriginal Dimensions: {original_size[0]} x {original_size[1]} px\nRotation: {rotation}°"
        info_label = tk.Label(preview_window, text=info_text, font=("Arial", 9))
        info_label.pack(pady=5)
        
        # Close button
        close_btn = tk.Button(preview_window, text="Close", command=preview_window.destroy)
        close_btn.pack(pady=10)

    def convert_images(self):
        if not self.images:
            messagebox.showerror("Error", "No images selected.")
            return

        # Validate resize width if enabled
        if self.resize_enabled_var.get():
            try:
                target_width = int(self.width_entry.get())
                if target_width <= 0:
                    messagebox.showerror("Error", "Width must be a positive number.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Width must be a valid number.")
                return

        output_dir = filedialog.askdirectory(title="Select Output Folder")
        if not output_dir:
            return

        success_count = 0
        error_count = 0

        for image_path in self.images:
            try:
                img = Image.open(image_path)
                
                # Apply rotation if set
                rotation = self.image_rotations.get(image_path, 0)
                if rotation != 0:
                    img = img.rotate(-rotation, expand=True)
                
                # Resize if enabled
                if self.resize_enabled_var.get():
                    w_percent = (target_width / float(img.size[0]))
                    target_height = int((float(img.size[1]) * float(w_percent)))
                    img = img.resize((target_width, target_height), Image.LANCZOS)

                # Handle metadata removal based on user selection
                remove_all = self.remove_all_var.get()
                remove_exif = self.remove_exif_var.get() or remove_all
                remove_icc = self.remove_icc_var.get() or remove_all
                remove_xmp = self.remove_xmp_var.get() or remove_all

                if remove_exif or remove_icc or remove_xmp:
                    # Create a new image without metadata
                    clean_img = Image.new(img.mode, img.size)
                    clean_img.putdata(list(img.getdata()))
                    
                    # Preserve ICC profile if user wants to keep it
                    if not remove_icc and 'icc_profile' in img.info:
                        clean_img.info['icc_profile'] = img.info['icc_profile']
                    
                    img = clean_img

                # Get selected output format
                output_format = self.output_format_var.get()
                file_extension = output_format.lower()
                if file_extension == "jpeg":
                    file_extension = "jpg"
                
                # Generate output filename
                if self.randomize_names_var.get():
                    # Use UUID for random filename
                    new_filename = f"{uuid.uuid4()}.{file_extension}"
                else:
                    # Keep original filename but change extension
                    original_name = os.path.splitext(os.path.basename(image_path))[0]
                    new_filename = f"{original_name}.{file_extension}"
                
                output_path = os.path.join(output_dir, new_filename)
                
                # Handle filename conflicts when keeping original names
                if not self.randomize_names_var.get() and os.path.exists(output_path):
                    counter = 1
                    while os.path.exists(output_path):
                        new_filename = f"{original_name}_{counter}.{file_extension}"
                        output_path = os.path.join(output_dir, new_filename)
                        counter += 1
                
                # Prepare save parameters
                save_kwargs = {"format": output_format}
                
                # Format-specific options
                if output_format == "JPEG":
                    save_kwargs["quality"] = 95
                    save_kwargs["optimize"] = True
                    # Convert RGBA to RGB for JPEG (no transparency support)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = background
                elif output_format == "WebP":
                    save_kwargs["quality"] = 90
                    save_kwargs["method"] = 6
                elif output_format == "PNG":
                    save_kwargs["optimize"] = True
                
                # Save with or without metadata
                if remove_exif and remove_icc and remove_xmp:
                    # Complete metadata removal
                    img.save(output_path, **save_kwargs)
                else:
                    # Partial metadata preservation
                    if not remove_exif and 'exif' in img.info:
                        save_kwargs['exif'] = img.info.get('exif', b'')
                    img.save(output_path, **save_kwargs)
                
                success_count += 1

            except Exception as e:
                error_count += 1
                print(f"Error converting {image_path}: {e}")

        # Show summary
        if error_count > 0:
            messagebox.showwarning("Conversion Complete", 
                f"Successfully converted: {success_count}\nFailed: {error_count}")
        else:
            messagebox.showinfo("Success", 
                f"All {success_count} image(s) converted successfully!\n\nSaved to: {output_dir}")

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
