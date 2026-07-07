import os
import psycopg2        # Python driver for connecting to PostgreSQL
from extract import extract  # our PDF parsing function from extract.py

# Directory containing all downloaded PDFs
PDF_DIR = "raw_data/pdfs"

# Connection details for the PostgreSQL database running in Docker
# These match what we set in docker-compose.yml
DB_CONFIG = {
    "host": "localhost",    # Docker maps the container's port to localhost
    "port": 5432,
    "dbname": "grades",
    "user": "tamu",
    "password": "devpassword",
}

# SQL template for inserting one record into the sections table
# The %(key)s placeholders are filled in by psycopg2 from each record dict —
# this prevents SQL injection and handles type conversion automatically
INSERT_SQL = """
    INSERT INTO sections (
        semester, college, department, course, section,
        instructor, gpa, a, b, c, d, f, a_to_f,
        i, s, u, q, x, total
    ) VALUES (
        %(semester)s, %(college)s, %(department)s, %(course)s, %(section)s,
        %(instructor)s, %(gpa)s, %(a)s, %(b)s, %(c)s, %(d)s, %(f)s, %(a_to_f)s,
        %(i)s, %(s)s, %(u)s, %(q)s, %(x)s, %(total)s
    )
"""

# Get a sorted list of all PDF files in the directory
pdfs = sorted(f for f in os.listdir(PDF_DIR) if f.endswith(".pdf"))
print(f"Found {len(pdfs)} PDFs to process\n")

# Open one database connection and reuse it for all files
# Opening a new connection per file would be slow — this is much more efficient
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()  # a cursor is the object we use to send SQL commands

total_loaded = 0

for filename in pdfs:
    path = os.path.join(PDF_DIR, filename)

    # extract() parses the PDF and returns a list of dicts, one per section row
    records = extract(path)

    if records:
        # executemany runs the INSERT for every record in the list in one batch
        cur.executemany(INSERT_SQL, records)
        # commit() saves this batch to the DB — without this, changes are temporary
        conn.commit()
        total_loaded += len(records)
        print(f"  {filename}: {len(records)} records")
    else:
        print(f"  {filename}: no records extracted")

# Always close the cursor and connection when done to free up DB resources
cur.close()
conn.close()

print(f"\nDone. Total records loaded: {total_loaded}")
