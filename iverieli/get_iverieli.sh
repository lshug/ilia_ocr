#!/bin/bash
echo "Scraping URLs..."
python3 scrap_pdf_urls.py
echo "Converting PDFs to images..."
EXTRACT_NO=10000 python3 convert_pdfs.py
echo "Extracting characters..."
python3 shuffle.py
echo "Done."
