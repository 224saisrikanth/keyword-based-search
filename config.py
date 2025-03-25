import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# PDF directory (where PDFs are stored)
PDF_DIR = os.path.join(BASE_DIR, 'pdfs')

# Extracted data directory
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Search index directory
INDEX_DIR = os.path.join(BASE_DIR, 'index')

# Create directories if they don't exist
for directory in [PDF_DIR, DATA_DIR, INDEX_DIR]:
    os.makedirs(directory, exist_ok=True) 