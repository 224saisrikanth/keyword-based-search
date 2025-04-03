import os
import json
import fitz  # PyMuPDF
from pathlib import Path

class PDFExtractor:
    def __init__(self, pdf_dir):
        self.pdf_dir = pdf_dir
        
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file page by page."""
        try:
            document = fitz.open(pdf_path)
            text_data = {
                "filename": os.path.basename(pdf_path),
                "total_pages": len(document),
                "pages": {}
            }
            
            for page_num in range(len(document)):
                page = document.load_page(page_num)
                text = page.get_text()
                text_data["pages"][page_num] = text
                
            return text_data
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return None
        
    def extract_all_pdfs(self):
        """Extract text from all PDFs in the directory."""
        extracted_data = []
        
        for filename in os.listdir(self.pdf_dir):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(self.pdf_dir, filename)
                data = self.extract_text_from_pdf(pdf_path)
                if data:
                    extracted_data.append(data)
        
        return extracted_data 

    def process_pdf(self, filename):
        """Process a PDF file to extract text content"""
        try:
            file_path = os.path.join(self.pdf_dir, filename)
            
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return None
            
            print(f"Processing PDF: {filename}")
            pdf_document = fitz.open(file_path)
            
            # Extract pages
            pages = {}
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text = page.get_text()
                
                # Only add pages with actual content
                if text and text.strip():
                    pages[page_num] = text
            
            pdf_document.close()
            
            # Skip if no text extracted
            if not pages:
                print(f"Warning: No text content extracted from {filename}")
                return None
                
            # Create document object
            document = {
                "filename": filename,
                "pages": pages,
                "page_count": len(pages)
            }
            
            print(f"Extracted {len(pages)} pages with text from {filename}")
            return document
            
        except Exception as e:
            print(f"Error processing PDF {filename}: {str(e)}")
            return None 