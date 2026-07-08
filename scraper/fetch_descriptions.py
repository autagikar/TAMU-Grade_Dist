"""
Scrapes course descriptions from the TAMU undergraduate and graduate catalogs
and loads them into the course_descriptions table in PostgreSQL/Supabase.

Run once (or once per semester when the catalog updates):
    DATABASE_URL="postgresql://..." python3 fetch_descriptions.py

Requires: requests, beautifulsoup4, psycopg2-binary
    python3 -m pip install requests beautifulsoup4 psycopg2-binary
"""

import os
import re
import time
import psycopg2
import requests
from bs4 import BeautifulSoup

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    DB_CONFIG = {
        "host": "localhost",
        "port": 5432,
        "dbname": "grades",
        "user": "tamu",
        "password": "devpassword",
    }
else:
    DB_CONFIG = DATABASE_URL

CATALOG_BASES = [
    "https://catalog.tamu.edu/undergraduate/course-descriptions/{prefix}/",
    "https://catalog.tamu.edu/graduate/course-descriptions/{prefix}/",
]

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS course_descriptions (
    course_code   TEXT PRIMARY KEY,
    title         TEXT,
    credits       TEXT,
    lecture_hours TEXT,
    lab_hours     TEXT,
    description   TEXT,
    prerequisites TEXT
);
"""

UPSERT_SQL = """
INSERT INTO course_descriptions
    (course_code, title, credits, lecture_hours, lab_hours, description, prerequisites)
VALUES
    (%(course_code)s, %(title)s, %(credits)s, %(lecture_hours)s, %(lab_hours)s,
     %(description)s, %(prerequisites)s)
ON CONFLICT (course_code) DO UPDATE SET
    title         = EXCLUDED.title,
    credits       = EXCLUDED.credits,
    lecture_hours = EXCLUDED.lecture_hours,
    lab_hours     = EXCLUDED.lab_hours,
    description   = EXCLUDED.description,
    prerequisites = EXCLUDED.prerequisites;
"""


def get_prefixes(cur):
    cur.execute("""
        SELECT DISTINCT SPLIT_PART(course, '-', 1)
        FROM sections
        WHERE course LIKE '%-%'
        ORDER BY 1
    """)
    return [row[0].lower() for row in cur.fetchall()]


def parse_credits(text):
    m = re.search(r'(\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?)\s*Credit', text, re.IGNORECASE)
    return m.group(1).strip() if m else None


def parse_hours(label, text):
    m = re.search(rf'(\d+(?:\.\d+)?)\s*{label}\s*Hour', text, re.IGNORECASE)
    return m.group(1).strip() if m else None


def scrape_prefix(prefix):
    """Returns a dict of course_code -> record for all courses under this prefix."""
    results = {}
    headers = {"User-Agent": "Mozilla/5.0 (research scraper)"}

    for base in CATALOG_BASES:
        url = base.format(prefix=prefix)
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                continue
        except requests.RequestException as e:
            print(f"    Request failed for {url}: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        blocks = soup.select("div.courseblock")
        if not blocks:
            continue

        for block in blocks:
            title_el = block.select_one(".courseblocktitle")
            if not title_el:
                continue

            title_text = title_el.get_text(" ", strip=True)

            # Course code is always the first token(s) before the period-terminated title.
            # Format: "BMEN 291 Some Title. 3 Credit Hours. 2 Lecture Hours. 1 Lab Hour."
            code_match = re.match(r'^([A-Z]+)\s+(\d+\w*)', title_text)
            if not code_match:
                continue
            course_code = f"{code_match.group(1)}-{code_match.group(2)}"

            # Title = everything between the course number and the first ". Credits" chunk
            after_code = title_text[code_match.end():].strip().lstrip(".")
            title_only = re.split(r'\.\s*\d', after_code)[0].strip().strip(".")

            credits       = parse_credits(title_text)
            lecture_hours = parse_hours("Lecture", title_text)
            lab_hours     = parse_hours("Lab(?:oratory)?", title_text)

            # Description: first .courseblockdesc paragraph
            desc_el = block.select_one(".courseblockdesc")
            description = desc_el.get_text(" ", strip=True) if desc_el else None

            # Prerequisites: any .courseblockextra paragraph that starts with "Prerequisite"
            prerequisites = None
            for extra in block.select(".courseblockextra"):
                t = extra.get_text(" ", strip=True)
                if re.match(r'Prerequisite', t, re.IGNORECASE):
                    # Strip the leading label
                    prerequisites = re.sub(r'^Prerequisite[s]?\s*:\s*', '', t, flags=re.IGNORECASE).strip()
                    break

            # Graduate catalog may already have the course; don't overwrite with a
            # worse/duplicate record if the undergrad entry came first.
            if course_code not in results:
                results[course_code] = {
                    "course_code":   course_code,
                    "title":         title_only or None,
                    "credits":       credits,
                    "lecture_hours": lecture_hours,
                    "lab_hours":     lab_hours,
                    "description":   description,
                    "prerequisites": prerequisites,
                }

        time.sleep(0.3)  # be polite between pages

    return results


def main():
    conn = psycopg2.connect(DB_CONFIG) if isinstance(DB_CONFIG, str) else psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print("Creating course_descriptions table if it doesn't exist...")
    cur.execute(CREATE_TABLE_SQL)
    conn.commit()

    print("Fetching course prefixes from sections table...")
    prefixes = get_prefixes(cur)
    print(f"Found {len(prefixes)} prefixes: {', '.join(p.upper() for p in prefixes[:10])}{'...' if len(prefixes) > 10 else ''}\n")

    total = 0
    for prefix in prefixes:
        print(f"  Scraping {prefix.upper()}...", end=" ", flush=True)
        records = scrape_prefix(prefix)
        if records:
            cur.executemany(UPSERT_SQL, list(records.values()))
            conn.commit()
            print(f"{len(records)} courses")
            total += len(records)
        else:
            print("no data found")

    cur.close()
    conn.close()
    print(f"\nDone. Loaded {total} course descriptions.")


if __name__ == "__main__":
    main()
