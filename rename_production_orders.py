"""
Main entry point for the Production Order Renaming System.
"""
from config import settings
from file_manager import FileManager
from image_processor import OCRExtractor
from pdf2image import convert_from_path
from collections import defaultdict
import os
import sys
import shutil

# --- Pre-installation check for Poppler and Tesseract ---
def check_external_dependencies():
    errors = []
    # Check Poppler
    poppler_path = getattr(settings, 'POPPLER_PATH', r'C:\Poppler\bin')
    if not shutil.which(os.path.join(poppler_path, 'pdftoppm.exe')):
        errors.append(f"Poppler not found at {poppler_path}. Please install Poppler and set POPPLER_PATH in config.py.")
    # Check Tesseract
    tesseract_path = shutil.which('tesseract')
    if not tesseract_path:
        errors.append("Tesseract-OCR is not installed or not in PATH. Please install Tesseract and add it to your PATH.")
    if errors:
        print("\n\n--- Dependency Check Failed ---")
        for err in errors:
            print(err)
        print("\nExiting due to missing dependencies.\n")
        sys.exit(1)

def main():
    check_external_dependencies()
    print("Initializing Production Order Renamer...")
    print(f"Target Directory: {settings.TARGET_FOLDER}")
    
    # Initialize Services
    file_manager = FileManager(settings.TARGET_FOLDER)
    ocr_engine = OCRExtractor()
    
    # Process Cycle
    for file_path in file_manager.get_unsorted_pdfs():
        print(f"Scanning: {file_path.name}...")
        
        try:
            # 1. Convert ALL pages to images to find split points
            # Using thread_count for speed if possible
            images = convert_from_path(
                file_path, 
                dpi=settings.DPI, 
                poppler_path=settings.POPPLER_PATH
            )
        except Exception as e:
            print(f" -> Error reading PDF {file_path.name}: {e}")
            continue

        if not images:
            continue

        # 2. Analyze pages to group them
        # Structure: { "P12345": [0, 1], "P67890": [2] }
        document_map = defaultdict(list)
        current_p_number = None
        
        for i, page_img in enumerate(images):
            # Check if this page has a new header
            found_number = ocr_engine.extract_p_number_from_image(page_img)
            
            if found_number:
                current_p_number = found_number
                print(f"   -> Page {i+1}: Start of {current_p_number}")
            
            if current_p_number:
                document_map[current_p_number].append(i)
            else:
                print(f"   -> Page {i+1}: No P-number found (and no previous P-number). Skipping page.")

        # 3. Split and Save
        if document_map:
            for p_num, pages in document_map.items():
                file_manager.extract_pages_to_new_pdf(file_path, pages, p_num)
            
            # 4. Archive original file so it's not processed again
            file_manager.archive_original(file_path)
    
if __name__ == "__main__":
    main()