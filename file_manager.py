import re
import os
import shutil
from pathlib import Path
from typing import Iterator, List
from pypdf import PdfReader, PdfWriter
from config import settings

class FileManager:
    """
    Manages file system operations: scanning directories and renaming files.
    """
    
    def __init__(self, target_folder: Path):
        self.target_folder = target_folder
        self.archive_folder = settings.ARCHIVE_FOLDER
        self.archive_folder.mkdir(exist_ok=True)

    def get_unsorted_pdfs(self) -> Iterator[Path]:
        """
        Yields PDF files in the target folder that match the pattern of all digits (e.g., 20260312131314.pdf).
        Only these files will be processed for renaming.
        """
        if not self.target_folder.exists():
            raise FileNotFoundError(f"Directory not found: {self.target_folder}")

        digit_pattern = re.compile(r'^\d+\.pdf$', re.IGNORECASE)
        for file_path in self.target_folder.glob("*.pdf"):
            if digit_pattern.match(file_path.name):
                yield file_path

    def _is_already_processed(self, filename: str) -> bool:
        """Checks if filename matches 'Produktion Pxxxxx.pdf'."""
        return bool(re.match(settings.PROCESSED_FILE_PATTERN, filename, re.IGNORECASE))

    def rename_file(self, current_path: Path, p_number: str) -> bool:
        """
        Renames the file to the standard format.
        Returns True if successful, False otherwise.
        """
        new_filename = f"Produktion {p_number}.pdf"
        new_path = self.target_folder / new_filename

        if new_path.exists():
            print(f" -> SKIP: Target '{new_filename}' already exists.")
            return False

        try:
            current_path.rename(new_path)
            print(f" -> SUCCESS: Renamed to '{new_filename}'")
            return True
        except OSError as e:
            print(f" -> ERROR: Could not rename file. {e}")
            return False

    def extract_pages_to_new_pdf(self, source_path: Path, page_indices: List[int], p_number: str):
        """
        Extracts specific pages from source_path and saves them as a new PDF.
        """
        new_filename = f"Produktion {p_number}.pdf"
        output_path = self.target_folder / new_filename

        if output_path.exists():
            print(f"   -> Warning: File {new_filename} already exists. Appending timestamp.")
            import time
            new_filename = f"Produktion {p_number}_{int(time.time())}.pdf"
            output_path = self.target_folder / new_filename

        try:
            reader = PdfReader(str(source_path))
            writer = PdfWriter()
            
            for page_idx in page_indices:
                writer.add_page(reader.pages[page_idx])
                
            with open(output_path, "wb") as f:
                writer.write(f)
            print(f"   -> Created: {new_filename} ({len(page_indices)} pages)")
        except Exception as e:
            print(f"   -> Error creating PDF {new_filename}: {e}")

    def archive_original(self, file_path: Path):
        """Moves the original processed file to the archive folder."""
        try:
            destination = self.archive_folder / file_path.name
            if destination.exists():
                import time
                destination = self.archive_folder / f"{file_path.stem}_{int(time.time())}{file_path.suffix}"
            
            shutil.move(str(file_path), str(destination))
            print(f" -> Archived original to: {destination.name}")
        except Exception as e:
            print(f" -> Error archiving file: {e}")