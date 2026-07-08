# TAMU Grade Distribution

A publicly deployed full-stack web app for exploring Texas A&M grade distribution data scraped from official PDF reports. Search courses and professors, compare them side by side, view department rankings, heatmaps, GPA trends, and save courses to a personal list.

**Live site:** [your-deployed-url-here]

## Tech Stack

| Layer | Technology |
|---|---|
| Scraper | Python 3 + pdfplumber + requests + BeautifulSoup4 |
| Database | PostgreSQL 16 (Docker locally, Supabase in production) |
| Backend API | FastAPI + SQLAlchemy (Docker locally, Railway in production) |
| Frontend | Vue 3 + Vite + Pinia + Chart.js (Vercel in production) |

---

## Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Node.js 20.12+](https://nodejs.org/)

---

## First-Time Setup (from a fresh clone)

### Step 1 — Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/tamu-grade-dist.git
cd tamu-grade-dist
```

### Step 2 — Create a Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

> Run `source venv/bin/activate` every time you open a new terminal session.

### Step 3 — Install Python dependencies

```bash
pip install pdfplumber psycopg2-binary requests beautifulsoup4
```

### Step 4 — Start the database and backend with Docker

```bash
docker compose up -d
```

This starts two containers:
- **db** — PostgreSQL 16 on port 5432 with a named volume (`pgdata`) so data persists across restarts
- **backend** — FastAPI on port 8000, connected to the database

Verify both are running:

```bash
docker compose ps
```

### Step 5 — Create the database tables

Connect to the running Postgres container:

```bash
docker exec -it tamu_grade_dist-db-1 psql -U tamu -d grades
```

Then run this SQL:

```sql
CREATE TABLE sections (
    id         SERIAL PRIMARY KEY,
    semester   VARCHAR,
    college    VARCHAR,
    department VARCHAR,
    course     VARCHAR,
    section    VARCHAR,
    instructor VARCHAR,
    gpa        NUMERIC(6,3),
    a          INTEGER,
    b          INTEGER,
    c          INTEGER,
    d          INTEGER,
    f          INTEGER,
    a_to_f     INTEGER,
    i          INTEGER,
    s          INTEGER,
    u          INTEGER,
    q          INTEGER,
    x          INTEGER,
    total      INTEGER
);

CREATE TABLE course_descriptions (
    course_code   TEXT PRIMARY KEY,
    title         TEXT,
    credits       NUMERIC(4,1),
    lecture_hours SMALLINT,
    lab_hours     SMALLINT,
    description   TEXT,
    prerequisites TEXT
);

\q
```

### Step 6 — Download grade distribution PDFs

```bash
cd scraper
python3 download_pdfs.py
```

Downloads all PDFs (2021–2026, all terms and colleges) into `scraper/raw_data/pdfs/`. Safe to re-run — skips files that already exist. Takes several minutes.

### Step 7 — Load grade data into the database

```bash
python3 load_to_db.py
```

Parses every PDF with pdfplumber and inserts all section rows into the `sections` table. Expect ~99,000+ records.

### Step 8 — Scrape course descriptions from the TAMU catalog

```bash
python3 fetch_descriptions.py
```

Discovers all course prefixes from the `sections` table, scrapes both the undergraduate and graduate TAMU course catalogs, and loads title, credits, lecture hours, lab hours, description, and prerequisites into the `course_descriptions` table. Safe to re-run — uses upsert so existing rows are updated.

### Step 9 — Install and run the frontend

```bash
cd ../frontend
npm install
npm run dev
```

The app is now running at **http://localhost:5173**.
The backend API is at **http://localhost:8000**.

---

## Daily Usage (after first-time setup)

```bash
# Start containers (if not already running)
docker compose up -d

# Start frontend dev server
cd frontend
npm run dev
```

---

## Docker Commands Reference

```bash
docker compose up -d        # start db + backend in background
docker compose down         # stop containers (data volume is preserved)
docker compose down -v      # stop containers AND delete all data (full reset)
docker compose logs backend # view backend logs
docker exec -it tamu_grade_dist-db-1 psql -U tamu -d grades  # open psql shell
```

---

## Project Structure

```
tamu_grade_dist/
├── scraper/
│   ├── download_pdfs.py        # downloads all PDFs from TAMU website
│   ├── get_college_codes.py    # scrapes college code list from TAMU website
│   ├── inspect_pdf.py          # dev tool for inspecting raw PDF structure
│   ├── extract.py              # PDF parser — converts pages to section dicts
│   ├── load_to_db.py           # loads all parsed PDFs into PostgreSQL
│   ├── fetch_descriptions.py   # scrapes TAMU catalog and loads course_descriptions table
│   └── raw_data/pdfs/          # downloaded PDFs (gitignored)
│
├── backend/
│   └── app/
│       ├── main.py             # FastAPI app setup + CORS middleware
│       ├── database.py         # SQLAlchemy engine + session factory
│       ├── models.py           # Section + CourseDescription ORM models
│       ├── schemas.py          # Pydantic response schema
│       └── routers/
│           └── sections.py     # all /api/* endpoints
│
├── frontend/
│   └── src/
│       ├── App.vue             # root layout + CSS variables (light/dark mode)
│       ├── main.js             # Vue app bootstrap
│       ├── api/index.js        # all axios HTTP calls to the backend
│       ├── router/index.js     # Vue Router route definitions
│       ├── stores/             # Pinia state management stores
│       │   ├── grades.js           # Course Search page state
│       │   ├── professor.js        # Professor Lookup page state
│       │   ├── compare.js          # Compare Courses page state
│       │   ├── compareProfessor.js # Compare Professors page state
│       │   ├── myCourses.js        # My Courses saved list + stats + description data
│       │   ├── rankings.js         # Department Rankings page state
│       │   ├── courseRankings.js   # Course Rankings page state
│       │   └── theme.js            # Dark mode toggle + localStorage persistence
│       ├── components/         # reusable UI components
│       │   ├── NavBar.vue              # top navigation bar with dark mode toggle
│       │   ├── CourseSearch.vue        # autocomplete course search input
│       │   ├── InstructorSearch.vue    # autocomplete professor search input
│       │   ├── CompareSearch.vue       # autocomplete search for compare courses
│       │   ├── CompareProfessorSearch.vue
│       │   ├── GradeChart.vue          # horizontal bar chart for grade distribution
│       │   ├── GpaTrendChart.vue       # multi-line GPA trend chart
│       │   ├── SectionsTable.vue       # paginated section breakdown table
│       │   ├── ProfessorSectionsTable.vue
│       │   ├── CompareBarChart.vue     # side-by-side grade distribution bars
│       │   ├── CompareTrendChart.vue   # overlapping GPA trend lines
│       │   ├── MyCoursesChart.vue      # multi-course GPA trend chart
│       │   ├── ScoreRing.vue           # circular score indicator for professor score
│       │   ├── ShareButton.vue         # copies current URL to clipboard
│       │   ├── GradePredictor.vue      # A/B/C/D/F probability bars per instructor
│       │   └── CourseInfoCard.vue      # catalog info card with hyperlinked prerequisites
│       └── views/              # page-level components (one per route)
│           ├── HomeView.vue            # Course Search page
│           ├── ProfessorView.vue       # Professor Lookup page
│           ├── CompareView.vue         # Compare Courses page
│           ├── CompareProfessorView.vue
│           ├── RankingsView.vue        # Department Rankings + professor heatmap
│           ├── CourseRankingsView.vue  # Course Rankings + difficulty heatmap
│           └── MyCoursesView.vue       # My Courses saved list
│
├── docker-compose.yml
├── documentation/
│   ├── python_scripts.txt      # detailed explanation of all Python code
│   └── vue_frontend.txt        # detailed explanation of all Vue/JS code
└── README.md
```

---

## Pages

| URL | Page | Description |
|---|---|---|
| `/` | Course Search | Search any course, filter by semester/instructor, view catalog info, charts, grade predictor, and section breakdown |
| `/professor` | Professor Lookup | Search any professor, view score ring, stats, courses taught, GPA trend, and similar professors |
| `/compare` | Compare Courses | Side-by-side grade distribution and GPA trend for two courses with shareable URL |
| `/compare-professor` | Compare Professors | Side-by-side comparison of two professors with shareable URL |
| `/rankings` | Department Rankings | Professors in a department ranked by score with sortable table and heatmap |
| `/course-rankings` | Course Rankings | Courses in a department ranked by difficulty with sortable table and heatmap |
| `/my-courses` | My Courses | Saved course list with credits/hours summary, multi-line GPA trend, and grade breakdown table |

---

## Features

- **Dark mode** — toggle in the navbar, persisted to localStorage
- **Share button** — copies the current page URL to clipboard on any results page
- **Course info card** — shows catalog title, credits, lecture/lab hours, description, and hyperlinked prerequisites
- **Grade predictor** — shows A/B/C/D/F probability bars when an instructor is selected
- **S/U grading detection** — courses graded Satisfactory/Unsatisfactory are flagged with a badge and banner
- **Heatmaps** — department course difficulty heatmap and professor score heatmap, colored on a dynamic red→green scale
- **Pagination** — all tables paginate at 20 rows with arrow controls
- **Deep linking** — course and professor pages sync state to the URL query string
