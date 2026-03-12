# Technical Architecture

The solution is designed with separation of concerns in mind.

## Class Overview

### 1. `FileManager` (src/file_manager.py)
*   **Responsibility**: Interacting with the Windows file system.
*   **Logic**: Scans the network drive. It uses Regex to filter out files that are already named correctly (`Produktion Pxxxxx.pdf`) so the expensive OCR process is only run on new files.

### 2. `OCRExtractor` (src/image_processor.py)
*   **Responsibility**: Computer Vision and Text Extraction.
*   **Logic**:
    1.  Converts the **first page** of the PDF to an image using `pdf2image`.
    2.  Crops the image to the top 25% (Header) to reduce noise.
    3.  Applies image pre-processing (Grayscale -> High Contrast -> Thresholding) to isolate handwritten ink.
    4.  Uses `pytesseract` to read the text.
    5.  Parses the text for the `Pxxxxx` pattern.

### 3. `AppConfig` (src/config.py)
*   **Responsibility**: Configuration Management.
*   **Logic**: A frozen dataclass storing paths and constants. This ensures strict typing and immutability of settings during runtime.