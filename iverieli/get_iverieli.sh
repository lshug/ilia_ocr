#!/bin/bash
echo "Scraping URLs..."
python3 scrap_pdf_urls.py
echo "Converting PDFs to images..."
python3 convert_pdfs.py
echo "Extracting characters..."
python3 shuffle.py
echo "Done."
