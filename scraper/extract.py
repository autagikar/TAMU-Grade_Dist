import os
import pdfplumber  # library that reads PDF files and extracts text/tables
import re          # library for pattern matching with regular expressions
import json        # library for reading/writing JSON files


def format_instructor(raw):
    # The PDF stores instructor names as "LASTNAME FIRSTNAME_INITIAL" (e.g. "TAKACHI TOMITA J")
    # This converts it to a readable format like "J. Takachi Tomita"
    if not raw:
        return ""
    parts = raw.split()
    initial = parts[-1].title()                            # last token is the first initial
    last_name = " ".join(p.title() for p in parts[:-1])   # everything before is the last name
    return f"{initial}. {last_name}"


def parse_section_id(section_id):
    # Section IDs in the PDF look like "AERO-201-500"
    # We split off the last part as the section number and keep the rest as the course code
    # e.g. "AERO-201-500" → course="AERO-201", section="500"
    parts = section_id.split("-")
    section = parts[-1]
    course = "-".join(parts[:-1])
    return course, section


def is_data_row(line):
    # A data row starts with a course code like "AERO-201-500" followed by a number
    # The regex checks: one or more uppercase letters, a dash, digits, optional extra dash/word chars, then whitespace and a digit
    return bool(re.match(r'^[A-Z]+-\d+[-\w]*\s+\d+', line))


def is_percentage_row(line):
    # Percentage rows follow each data row and look like "30.77% 46.15% ..."
    # We skip these since the raw counts are more useful for our DB
    return bool(re.match(r'^\d+\.\d+%', line))


def parse_data_row(line, college, department, semester):
    # Split the line into individual tokens (words/numbers separated by spaces)
    tokens = line.split()

    # A valid data row needs at least 14 tokens — skip anything shorter
    if len(tokens) < 14:
        return None

    course, section = parse_section_id(tokens[0])

    # The instructor name is everything after token 13 (the total count)
    instructor = format_instructor(" ".join(tokens[14:])) if len(tokens) > 14 else ""

    try:
        return {
            "semester":   semester,
            "college":    college,
            "department": department,
            "course":     course,       # e.g. "AERO-201"
            "section":    section,      # e.g. "500"
            "instructor": instructor,
            "a":          int(tokens[1]),
            "b":          int(tokens[2]),
            "c":          int(tokens[3]),
            "d":          int(tokens[4]),
            "f":          int(tokens[5]),
            "a_to_f":     int(tokens[6]),   # total of A+B+C+D+F grades
            # GPA is validated to be between 0 and 4.0 — anything outside that range
            # means the row parsed incorrectly and we store None instead of bad data
            "gpa":        float(tokens[7]) if 0 <= float(tokens[7]) <= 4.0 else None,
            "i":          int(tokens[8]),   # incomplete
            "s":          int(tokens[9]),   # satisfactory
            "u":          int(tokens[10]),  # unsatisfactory
            "q":          int(tokens[11]),  # dropped
            "x":          int(tokens[12]),  # absent from final
            "total":      int(tokens[13]),  # total enrolled
        }
    except (ValueError, IndexError):
        # If any token can't be converted to the expected type, skip this row silently
        return None


def semester_from_filename(filename):
    # Our downloaded PDFs are named like "2026_SPRING_EN.pdf"
    # We extract the year and term to build a human-readable semester string
    # e.g. "2026_SPRING_EN.pdf" → "Spring 2026"
    parts = os.path.basename(filename).replace(".pdf", "").split("_")
    year = parts[0]
    term = parts[1].title()  # "SPRING" → "Spring"
    return f"{term} {year}"


def extract(pdf_path):
    records = []
    college = ""
    department = ""
    semester = semester_from_filename(pdf_path)

    with pdfplumber.open(pdf_path) as pdf:
        # Loop through every page in the PDF
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue  # skip blank pages

            # Process each line of text on the page
            for line in text.splitlines():
                line = line.strip()

                # Context headers appear at the top of each department section
                # We track them so every data row below knows which college/department it belongs to
                if line.startswith("COLLEGE:"):
                    college = line.replace("COLLEGE:", "").strip()
                elif line.startswith("DEPARTMENT:"):
                    department = line.replace("DEPARTMENT:", "").strip()

                # "COURSE TOTAL:" rows are aggregate summaries — skip them, we have the individual sections
                elif line.startswith("COURSE TOTAL:"):
                    continue

                # Skip the percentage rows that follow each data row
                elif is_percentage_row(line):
                    continue

                # If this looks like a section data row, parse it into a dict
                elif is_data_row(line):
                    record = parse_data_row(line, college, department, semester)
                    if record:
                        records.append(record)

    return records


if __name__ == "__main__":
    # When run directly, accepts an optional PDF path as a command-line argument
    # Falls back to a default path if none is provided
    # Usage: python3 extract.py raw_data/pdfs/2026_SPRING_EN.pdf
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "raw_data/pdfs/2026_SPRING_EN.pdf"
    records = extract(path)
    print(f"Extracted {len(records)} section(s)")

    output_path = "raw_data/extracted.json"
    with open(output_path, "w") as f:
        json.dump(records, f, indent=2)
    print(f"Saved to {output_path}")

    print("\nSample (first 3 records):")
    for r in records[:3]:
        print(json.dumps(r, indent=2))
