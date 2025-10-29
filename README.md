# Image Metadata Remover

A feature-rich GUI tool to remove metadata from images, resize them, and save with randomized filenames. Includes an intuitive preview grid and selective metadata removal options.

## Features

- **Image Preview Grid**: View all selected images in a 5-column thumbnail grid
- **Click to Preview**: Click any thumbnail to view the full-size image in a separate window
- **Individual Image Rotation**: Rotate each image independently with 90° left/right controls
- **Selective Metadata Removal**: Choose which metadata to remove:
  - EXIF Data (camera settings, date, location, GPS)
  - ICC Profile (color profile information)
  - XMP Data (additional metadata)
  - "Select All" option for convenience
- **Batch Processing**: Convert multiple images at once
- **Optional Resize**: Enable/disable image resizing with custom width
- **Smart Resizing**: Height adjusted automatically to maintain aspect ratio
- **Flexible Naming**: Choose between UUID random filenames or keep original names
- **Multiple Output Formats**: Save as PNG, JPEG, WebP, BMP, or TIFF with format descriptions
- **Drag and Drop**: Drag images directly into the window (optional feature)
- **Multiple Input Formats**: Supports JPG, PNG, BMP, WebP, and TIFF input formats

## Requirements

```bash
pip install pillow
pip install tkinterdnd2  # Optional: for drag-and-drop support
```

## How to Run

1. Install dependencies:
```bash
pip install pillow tkinterdnd2
```

2. Run the application:
```bash
python main.py
```

## Usage

1. **Load Images**: Click "Select Images" or drag and drop image files into the window
2. **Preview & Rotate**: 
   - View all images in the preview grid
   - Use ↺ 90° and ↻ 90° buttons to rotate each image individually
   - Click any image to see it full-size with current rotation
3. **Select Metadata Options**: 
   - Use "Select All Metadata" to remove everything
   - Or individually choose which metadata types to remove
4. **Configure Resize** (optional):
   - Check/uncheck "Enable Resize"
   - Set target width in pixels (default: 800px)
5. **Configure Output**:
   - Check "Randomize Filenames" for UUID-based names (privacy)
   - Uncheck to keep original filenames
   - Select output format:
     - **PNG**: Lossless, larger files, supports transparency (default)
     - **JPEG**: Lossy compression, smaller files, no transparency
     - **WebP**: Modern format, good compression, supports transparency
     - **BMP**: Uncompressed, very large files, high quality
     - **TIFF**: Lossless, large files, professional archival
6. **Convert**: Click "Convert & Save"
7. **Choose Output Folder**: Select where to save the processed images

## Notes

- The application maintains the aspect ratio when resizing
- You can disable resizing if you only want to remove metadata
- **Rotation**: Each image can be rotated individually in 90° increments; rotation is applied before resizing
- Preview window shows original image dimensions, file path, and current rotation angle
- Success/failure summary is displayed after batch conversion
- When keeping original filenames, conflicts are automatically resolved by appending a number (e.g., `image_1.jpg`)
- **JPEG output**: Images are saved at 95% quality for optimal balance; transparency is converted to white background
- **WebP output**: Images are saved at 90% quality with maximum compression efficiency
- **PNG output**: Images are optimized for smaller file size while maintaining lossless quality

