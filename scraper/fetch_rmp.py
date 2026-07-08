"""
fetch_rmp.py — Match TAMU professors to RateMyProfessors profiles.

Usage:
    DATABASE_URL='postgresql://...' python3 fetch_rmp.py

Outputs two files in the same directory:
    rmp_matches.csv    — professors where a confident match was found
    rmp_no_match.csv   — professors where no confident match was found
"""

import os
import csv
import time
import re
from difflib import SequenceMatcher

import psycopg2
import requests

# ── Config ──────────────────────────────────────────────────────────────────

DATABASE_URL = os.environ.get("DATABASE_URL", "")

# TAMU's school ID on RMP (base64 of "School-1003")
TAMU_SCHOOL_ID = "U2Nob29sLTEwMDM="

RMP_URL = "https://www.ratemyprofessors.com/graphql"

# The unofficial RMP GraphQL API accepts this header
RMP_HEADERS = {
    "Authorization": "Basic dGVzdDp0ZXN0",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
}

# Match confidence threshold — below this the result is written to no-match file
CONFIDENCE_THRESHOLD = 0.72

# Seconds to wait between RMP requests (be polite)
REQUEST_DELAY = 0.4

# ── GraphQL query ────────────────────────────────────────────────────────────

SEARCH_QUERY = """
query NewSearchTeachersQuery($text: String!, $schoolID: ID!) {
  newSearch {
    teachers(query: {text: $text, schoolID: $schoolID}) {
      edges {
        node {
          legacyId
          firstName
          lastName
          avgRating
          numRatings
          wouldTakeAgainPercent
          department
        }
      }
    }
  }
}
"""

# ── Name parsing ─────────────────────────────────────────────────────────────

def parse_name(raw: str) -> tuple[str, str]:
    """
    Return (first, last) from common TAMU name formats:
      "LASTNAME, FIRSTNAME MIDDLE"  →  ("Firstname", "Lastname")
      "FIRSTNAME LASTNAME"          →  ("Firstname", "Lastname")
      "F. LASTNAME"                 →  ("F.", "Lastname")
    """
    raw = raw.strip()

    if "," in raw:
        last_part, first_part = raw.split(",", 1)
        last = last_part.strip().title()
        first_tokens = first_part.strip().split()
        first = first_tokens[0].title() if first_tokens else ""
        return first, last

    tokens = raw.split()
    if len(tokens) >= 2:
        return tokens[0].title(), tokens[-1].title()

    return "", raw.title()


def normalize(s: str) -> str:
    """Lowercase and strip punctuation for comparison."""
    return re.sub(r"[^a-z ]", "", s.lower()).strip()


# ── RMP API ──────────────────────────────────────────────────────────────────

def search_rmp(query_text: str) -> list[dict]:
    payload = {
        "query": SEARCH_QUERY,
        "variables": {"text": query_text, "schoolID": TAMU_SCHOOL_ID},
    }
    resp = requests.post(RMP_URL, json=payload, headers=RMP_HEADERS, timeout=10)
    resp.raise_for_status()
    edges = (
        resp.json()
        .get("data", {})
        .get("newSearch", {})
        .get("teachers", {})
        .get("edges", [])
    )
    return [e["node"] for e in edges]


# ── Matching ─────────────────────────────────────────────────────────────────

def score_match(db_first: str, db_last: str, rmp_node: dict) -> float:
    """
    Compute a confidence score 0-1 between a DB name and an RMP result.
    Weights last-name similarity heavily since first names often differ
    (e.g. "J." in the DB vs "John" on RMP).
    """
    rmp_first = rmp_node["firstName"] or ""
    rmp_last  = rmp_node["lastName"]  or ""

    last_sim  = SequenceMatcher(None, normalize(db_last),  normalize(rmp_last)).ratio()
    first_sim = SequenceMatcher(None, normalize(db_first), normalize(rmp_first)).ratio()

    # If the DB entry is just an initial, check whether the initial matches
    if len(db_first.replace(".", "")) == 1:
        initial_match = (
            1.0 if rmp_first and rmp_first[0].lower() == db_first[0].lower() else 0.0
        )
        first_sim = max(first_sim, initial_match * 0.8)

    # 65% weight on last name, 35% on first
    return last_sim * 0.65 + first_sim * 0.35


def find_best_match(db_name: str, candidates: list[dict]) -> tuple[dict | None, float]:
    if not candidates:
        return None, 0.0

    db_first, db_last = parse_name(db_name)
    best_node, best_score = None, 0.0

    for node in candidates:
        s = score_match(db_first, db_last, node)
        if s > best_score:
            best_score = s
            best_node = node

    return best_node, best_score


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not DATABASE_URL:
        print("ERROR: Set the DATABASE_URL environment variable.")
        return

    # Fetch all unique instructor names from the DB
    conn = psycopg2.connect(DATABASE_URL)
    cur  = conn.cursor()
    cur.execute(
        "SELECT DISTINCT instructor FROM sections "
        "WHERE instructor IS NOT NULL AND instructor != '' "
        "ORDER BY instructor"
    )
    instructors = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()

    print(f"Found {len(instructors)} unique instructors in DB.\n")

    matches    = []
    no_matches = []
    errors     = []

    for i, name in enumerate(instructors, 1):
        db_first, db_last = parse_name(name)

        # Search RMP by last name (more precise than full name for partial initials)
        search_term = db_last if db_last else name
        try:
            candidates = search_rmp(search_term)
        except Exception as e:
            print(f"  [{i}/{len(instructors)}] ERROR searching '{name}': {e}")
            errors.append({"db_name": name, "error": str(e)})
            time.sleep(REQUEST_DELAY * 2)
            continue

        best_node, confidence = find_best_match(name, candidates)

        if best_node and confidence >= CONFIDENCE_THRESHOLD:
            rmp_id  = best_node["legacyId"]
            rmp_url = f"https://www.ratemyprofessors.com/professor/{rmp_id}"
            row = {
                "db_name":     name,
                "rmp_name":    f"{best_node['firstName']} {best_node['lastName']}",
                "confidence":  round(confidence, 3),
                "rmp_id":      rmp_id,
                "rmp_url":     rmp_url,
                "avg_rating":  best_node["avgRating"],
                "num_ratings": best_node["numRatings"],
                "would_take_again_pct": best_node["wouldTakeAgainPercent"],
                "rmp_department": best_node["department"],
            }
            matches.append(row)
            print(
                f"  [{i}/{len(instructors)}] ✓ '{name}' → "
                f"{best_node['firstName']} {best_node['lastName']} "
                f"(conf={confidence:.2f}, rating={best_node['avgRating']}, "
                f"n={best_node['numRatings']})"
            )
        else:
            row = {
                "db_name":    name,
                "best_rmp":   f"{best_node['firstName']} {best_node['lastName']}" if best_node else "—",
                "confidence": round(confidence, 3) if best_node else 0.0,
                "candidates": len(candidates),
            }
            no_matches.append(row)
            print(
                f"  [{i}/{len(instructors)}] ✗ '{name}' — "
                f"best guess: {row['best_rmp']} (conf={row['confidence']:.2f})"
            )

        time.sleep(REQUEST_DELAY)

    # ── Write outputs ─────────────────────────────────────────────────────────
    out_dir = os.path.dirname(os.path.abspath(__file__))

    match_path = os.path.join(out_dir, "rmp_matches.csv")
    with open(match_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "db_name", "rmp_name", "confidence", "rmp_id", "rmp_url",
            "avg_rating", "num_ratings", "would_take_again_pct", "rmp_department",
        ])
        writer.writeheader()
        writer.writerows(matches)

    no_match_path = os.path.join(out_dir, "rmp_no_match.csv")
    with open(no_match_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["db_name", "best_rmp", "confidence", "candidates"])
        writer.writeheader()
        writer.writerows(no_matches)

    print(f"\n{'─'*60}")
    print(f"  Matched:    {len(matches):>5}  → {match_path}")
    print(f"  No match:   {len(no_matches):>5}  → {no_match_path}")
    print(f"  Errors:     {len(errors):>5}")
    print(f"  Total:      {len(instructors):>5}")
    print(f"  Match rate: {len(matches)/len(instructors)*100:.1f}%")


if __name__ == "__main__":
    main()
