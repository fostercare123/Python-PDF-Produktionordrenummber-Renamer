# Production Order Renamer

Automated tool for scanning, splitting, and renaming production order PDFs based on handwritten or printed P-numbers using OCR.

## Features
- Scans a folder for PDF files with production orders
- Uses Tesseract OCR and Poppler to extract handwritten/printed P-numbers
- Splits and renames files to `Produktion Pxxxxx.pdf`
- Designed for manufacturing/production environments

## Requirements
- Python 3.10+
- Tesseract OCR (installed and in PATH)
- Poppler (installed and in PATH)

## Setup
1. Clone this repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Edit `config.py` to set your folder paths and Poppler/Tesseract locations

## Usage
Run the main script:
```bash
python rename_production_orders.py
```

## Confidentiality
**Do not commit any PDF, PNG, or confidential files to this repository.**

## License
MIT