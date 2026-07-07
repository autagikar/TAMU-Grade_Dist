import pdfplumber  # library that reads PDF files and extracts text/tables

# Path to the single-page PDF we use for development/testing
# Using the 1-page version keeps output small while we figure out the PDF structure
PDF_PATH = "raw_data/TAMU_Spring_2026_Grade_Dist_p1.pdf"

with pdfplumber.open(PDF_PATH) as pdf:
    page = pdf.pages[0]  # grab the first (and only) page

    # extract_text() reads all the text from the page as one big string
    # This tells us if the PDF is text-based (readable) or scanned (would need OCR)
    print("=== RAW TEXT ===")
    print(page.extract_text())
    print()

    # extract_tables() tries to detect table structures using line/border detection
    # If it finds tables, we can use them directly instead of parsing raw text
    print("=== TABLES ===")
    tables = page.extract_tables()
    print(f"Found {len(tables)} table(s)")
    for i, table in enumerate(tables):
        print(f"\n--- Table {i} ---")
        for row in table:
            print(row)
