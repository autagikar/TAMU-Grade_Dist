import urllib.request  # built-in Python library for making HTTP requests
import urllib.error    # built-in library for handling HTTP errors
import time            # used for adding a delay between requests
import os              # used for file/directory operations

# Where to save the downloaded PDFs
OUTPUT_DIR = "raw_data/pdfs"

# Base URL pattern for TAMU grade distribution PDFs
# We fill in year, term, and college code to get each specific PDF
BASE_URL = "https://web-as.tamu.edu/gradereports/Report"

# All years we want to download (site only goes back to 2021)
YEARS = [2021, 2022, 2023, 2024, 2025, 2026]

# The three academic terms TAMU offers
TERMS = ["SPRING", "SUMMER", "FALL"]

# All college codes found on the grade reports page (from get_college_codes.py)
# Not every combination of year/term/college exists — we handle missing ones gracefully below
COLLEGE_CODES = [
    "AD", "AE", "AG", "AR", "AC", "AP", "AT", "GB", "BA",
    "DN", "DN_PROF", "DT", "DT_PROF",
    "ED", "EH", "EN",
    "GV", "GE", "GS",
    "SL", "SL_PROF",
    "LA", "MD", "MD_PROF", "MN", "MN_PROF",
    "MS", "NU", "CP_PROF", "PM_PROF", "PH",
    "QT", "SC", "PV",
    "VM", "VM_PROF", "VT", "VT_PROF",
    "EX",
]

# Create the output directory if it doesn't already exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

total = len(YEARS) * len(TERMS) * len(COLLEGE_CODES)
downloaded = 0
skipped = 0
missing = 0

print(f"Starting download — {total} combinations to check\n")

# Loop over every combination of year, term, and college
for year in YEARS:
    for term in TERMS:
        for college in COLLEGE_CODES:
            # Build the filename from the three variables so we know what's in each file later
            filename = f"{year}_{term}_{college}.pdf"
            filepath = os.path.join(OUTPUT_DIR, filename)

            # If the file already exists, skip it — makes the script safe to re-run
            if os.path.exists(filepath):
                skipped += 1
                continue

            # Build the full URL for this specific year/term/college combination
            url = f"{BASE_URL}?year={year}&term={term}&college={college}"

            try:
                with urllib.request.urlopen(url, timeout=15) as response:
                    content = response.read()

                # Validate the response is actually a PDF:
                # - must be larger than 1KB (empty/error pages are small)
                # - must start with "%PDF" (the standard PDF file signature)
                if len(content) < 1000 or not content.startswith(b"%PDF"):
                    missing += 1
                    print(f"  no data: {filename}")
                    continue

                # Write the PDF bytes to disk
                with open(filepath, "wb") as f:
                    f.write(content)
                downloaded += 1
                print(f"  saved:   {filename} ({len(content) // 1024} KB)")

            except urllib.error.HTTPError as e:
                # Server returned an error code (e.g. 404 Not Found)
                missing += 1
                print(f"  error {e.code}: {filename}")
            except Exception as e:
                # Any other error (timeout, network issue, etc.)
                missing += 1
                print(f"  failed:  {filename} — {e}")

            # Small delay between requests so we don't hammer the TAMU server
            time.sleep(0.3)

print(f"\nDone. Downloaded: {downloaded} | Already existed: {skipped} | No data: {missing}")
