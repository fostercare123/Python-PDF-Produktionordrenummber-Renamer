import re
import pytesseract
from pathlib import Path
from typing import Optional
from PIL import Image, ImageEnhance, ImageOps
from pdf2image import convert_from_path
from config import settings

class OCRExtractor:
    """
    Handles the extraction of text data from PDF documents using OCR.
    """
    
    def __init__(self):
        # Initialize Tesseract configuration on instantiation
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Applies grayscale, contrast enhancement, and binarization 
        to improve OCR accuracy on handwriting.
        """
        # 1. Grayscale
        gray_image = ImageOps.grayscale(image)
        
        # 2. Contrast
        enhancer = ImageEnhance.Contrast(gray_image)
        contrast_image = enhancer.enhance(settings.CONTRAST_FACTOR)
        
        # 3. Binarize (Thresholding)
        binary_image = contrast_image.point(
            lambda x: 0 if x < settings.THRESHOLD_VALUE else 255, '1'
        )
        return binary_image

    def extract_p_number_from_image(self, page_img: Image.Image) -> Optional[str]:
        """
        Analyzes a single PIL Image (PDF page) to find the P-number.
        Tries header first, then the whole page if not found.
        Prints the raw OCR text for debugging.
        """
        try:
            width, height = page_img.size
            # 1. Try header crop
            header_crop = page_img.crop((0, 0, width, int(height * 0.25)))
            clean_header = self._preprocess_image(header_crop)
            text_header = pytesseract.image_to_string(clean_header, config='--psm 6')
            print("\n--- OCR DEBUG OUTPUT (Header) ---\n" + text_header + "\n-------------------------------\n")
            p_number = self._parse_text_for_p_number(text_header)
            if p_number:
                return p_number
            # 2. Try the whole page if not found
            clean_full = self._preprocess_image(page_img)
            text_full = pytesseract.image_to_string(clean_full, config='--psm 6')
            print("\n--- OCR DEBUG OUTPUT (Full Page) ---\n" + text_full + "\n-------------------------------\n")
            return self._parse_text_for_p_number(text_full)
        except Exception as e:
            print(f"OCR Error: {e}")
            return None

    def _parse_text_for_p_number(self, text: str) -> Optional[str]:
        """Robustly parses OCR output for the P-number after 'Produktionsordrenummer:'.
        Handles spaces, common OCR errors, and separated digits/letters. Uses difflib for fuzzy matching if a list of valid P-numbers is provided."""
        import re
        import difflib
        # Generate all valid P-numbers in the range P20000–P29999
        valid_p_numbers = [f"P{n}" for n in range(20000, 30000)]
        # Find the line with 'Produktionsordrenummer:'
        lines = text.splitlines()
        for line in lines:
            if 'Produktionsordrenummer' in line:
                after = line.split(':', 1)[-1] if ':' in line else line.split('Produktionsordrenummer', 1)[-1]
                cleaned = re.sub(r'[^A-Za-z0-9]', '', after)
                cleaned = cleaned.upper().replace('I', '1').replace('L', '1').replace('O', '0')
                cleaned = cleaned.replace('S', 'P').replace('B', '8').replace('b', '6')
                # Look for P followed by 5 digits
                match = re.search(r'P(\d{5})', cleaned)
                if match:
                    candidate = f"P{match.group(1)}"
                    # Fuzzy match to valid list
                    close = difflib.get_close_matches(candidate, valid_p_numbers, n=1, cutoff=0.7)
                    if close:
                        return close[0]
                    return candidate
        # Fallback: try to find a P-number anywhere in the text, robustly
        cleaned_text = re.sub(r'[^A-Za-z0-9]', '', text)
        cleaned_text = cleaned_text.upper().replace('I', '1').replace('L', '1').replace('O', '0')
        cleaned_text = cleaned_text.replace('S', 'P').replace('B', '8').replace('b', '6')
        match = re.search(r'P(\d{5})', cleaned_text)
        if match:
            candidate = f"P{match.group(1)}"
            close = difflib.get_close_matches(candidate, valid_p_numbers, n=1, cutoff=0.7)
            if close:
                return close[0]
            return candidate
        return None