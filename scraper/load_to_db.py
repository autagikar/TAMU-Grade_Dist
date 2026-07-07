import os
import psycopg2        # Python driver for connecting to PostgreSQL
from extract import extract  # our PDF parsing function from extract.py

# Directory containing all downloaded PDFs
PDF_DIR = "raw_data/pdfs"

# If the DATABASE_URL environment variable is set (e.g. when loading into Railway),
# use it directly. Otherwise fall back to the local Docker config.
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # psycopg2 can connect using a full URL string directly
    DB_CONFIG = DATABASE_URL
else:
    # Local Docker defaults from docker-compose.yml
    DB_CONFIG = {
        "host": "localhost",
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

# Set this to a filename to skip everything before it (useful after a mid-run crash).
# Set to None to process all files from the beginning.
START_FROM = None
END_AT = None

# Get a sorted list of all PDF files in the directory
all_pdfs = sorted(f for f in os.listdir(PDF_DIR) if f.endswith(".pdf"))
if START_FROM and END_AT:
    pdfs = [f for f in all_pdfs if START_FROM <= f <= END_AT]
elif START_FROM:
    pdfs = [f for f in all_pdfs if f >= START_FROM]
else:
    pdfs = all_pdfs
print(f"Found {len(pdfs)} PDFs to process\n")

# Open one database connection and reuse it for all files
conn = psycopg2.connect(DB_CONFIG) if isinstance(DB_CONFIG, str) else psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

total_loaded = 0
failed = 0

for filename in pdfs:
    path = os.path.join(PDF_DIR, filename)

    records = extract(path)

    if records:
        try:
            # Insert all records for this PDF as one batch
            cur.executemany(INSERT_SQL, records)
            conn.commit()
            total_loaded += len(records)
            print(f"  {filename}: {len(records)} records")
        except Exception as e:
            failed += 1
            print(f"  {filename}: FAILED — {e}")
            # Try to roll back; if the connection dropped, reconnect so the
            # remaining files can still be processed
            try:
                conn.rollback()
            except Exception:
                print("  Connection lost — reconnecting...")
                try:
                    conn = psycopg2.connect(DB_CONFIG) if isinstance(DB_CONFIG, str) else psycopg2.connect(**DB_CONFIG)
                    cur = conn.cursor()
                    print("  Reconnected.")
                except Exception as reconnect_err:
                    print(f"  FATAL: could not reconnect — {reconnect_err}")
                    break
    else:
        print(f"  {filename}: no records extracted")

cur.close()
conn.close()

print(f"\nDone. Loaded: {total_loaded} records | Failed batches: {failed}")
