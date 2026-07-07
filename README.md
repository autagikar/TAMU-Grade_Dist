# TAMU Grade Distribution

A full-stack web app that lets you explore Texas A&M grade distribution data scraped from official PDF reports. Search courses and professors, compare them side by side, and save courses to a personal list.

## Tech Stack

| Layer | Technology |
|---|---|
| Scraper | Python 3 + pdfplumber |
| Database | PostgreSQL 16 (Docker) |
| Backend API | FastAPI + SQLAlchemy (Docker) |
| Frontend | Vue 3 + Vite + Pinia + Chart.js |

---

## Prerequisites

Make sure the following are installed before you start:

- [Python 3.10+](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Node.js 20.12+](https://nodejs.org/) (comes with npm)

---

## First-Time Setup (from a fresh clone)

### Step 1 — Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/tamu-grade-dist.git
cd tamu-grade-dist
```

### Step 2 — Create a Python virtual environment

This isolates project dependencies from your system Python.

```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

> You need to run `source venv/bin/activate` every time you open a new terminal session.

### Step 3 — Install Python dependencies

```bash
pip install pdfplumber psycopg2-binary
```

### Step 4 — Start the database and backend with Docker

```bash
docker compose up -d
```

This starts two containers:
- **db** — PostgreSQL 16 on port 5432, with a named volume (`pgdata`) so data persists across restarts
- **backend** — FastAPI on port 8000, connected to the database

Verify both are running:

```bash
docker compose ps
```

### Step 5 — Create the database table

Connect to the running Postgres container and create the `sections` table:

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
\q
```

### Step 6 — Download grade distribution PDFs

With the virtual environment active, run from the `scraper/` directory:

```bash
cd scraper
python3 download_pdfs.py
```

This downloads PDFs for all years (2021–2026), all terms (Spring/Summer/Fall), and all college codes into `scraper/raw_data/pdfs/`. It skips files that already exist so it is safe to re-run. This may take several minutes.

### Step 7 — Load the PDFs into the database

```bash
python3 load_to_db.py
```

This reads every PDF in `raw_data/pdfs/`, parses it with pdfplumber, and inserts all section rows into the `sections` table. Expect ~99,000+ records and a few minutes of processing time.

### Step 8 — Install and run the frontend

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
```

---

## Project Structure

```
tamu_grade_dist/
├── scraper/
│   ├── download_pdfs.py      # downloads all PDFs from TAMU website
│   ├── get_college_codes.py  # scrapes college code list from TAMU website
│   ├── inspect_pdf.py        # dev tool for inspecting raw PDF structure
│   ├── extract.py            # PDF parser — converts pages to section dicts
│   ├── load_to_db.py         # loads all parsed PDFs into PostgreSQL
│   └── raw_data/pdfs/        # downloaded PDFs (gitignored)
│
├── backend/
│   └── app/
│       ├── main.py           # FastAPI app setup + CORS middleware
│       ├── database.py       # SQLAlchemy engine + session factory
│       ├── models.py         # Section ORM model (maps to sections table)
│       ├── schemas.py        # Pydantic response schema
│       └── routers/
│           └── sections.py   # all /api/* endpoints
│
├── frontend/
│   └── src/
│       ├── App.vue           # root layout (hero + navbar + RouterView)
│       ├── main.js           # Vue app bootstrap
│       ├── api/index.js      # all axios HTTP calls to the backend
│       ├── router/index.js   # Vue Router route definitions
│       ├── stores/           # Pinia state management stores
│       │   ├── grades.js         # Course Search page state
│       │   ├── professor.js      # Professor Lookup page state
│       │   ├── compare.js        # Compare Courses page state
│       │   ├── compareProfessor.js # Compare Professors page state
│       │   └── myCourses.js      # My Courses saved list + stats
│       ├── components/       # reusable UI components
│       │   ├── NavBar.vue
│       │   ├── CourseSearch.vue
│       │   ├── InstructorSearch.vue
│       │   ├── GradeChart.vue
│       │   ├── GpaTrendChart.vue
│       │   ├── SectionsTable.vue
│       │   ├── ProfessorSectionsTable.vue
│       │   ├── CompareSearch.vue
│       │   ├── CompareProfessorSearch.vue
│       │   ├── CompareBarChart.vue
│       │   ├── CompareTrendChart.vue
│       │   └── MyCoursesChart.vue
│       └── views/            # page-level components (one per route)
│           ├── HomeView.vue
│           ├── ProfessorView.vue
│           ├── CompareView.vue
│           ├── CompareProfessorView.vue
│           └── MyCoursesView.vue
│
├── docker-compose.yml
├── documentation/
│   ├── python_scripts.txt    # detailed explanation of all Python code
│   └── vue_frontend.txt      # detailed explanation of all Vue/JS code
└── README.md
```

---

## Pages

| URL | Page | Description |
|---|---|---|
| `/` | Course Search | Search any course, filter by semester/instructor, view charts and sections |
| `/professor` | Professor Lookup | Search any professor, view their stats, courses taught, and GPA trend |
| `/compare` | Compare Courses | Side-by-side stats, grade distribution, and GPA trend for two courses |
| `/compare-professor` | Compare Professors | Side-by-side comparison of two professors |
| `/my-courses` | My Courses | Saved course list (persisted to localStorage) with a multi-line GPA trend and summary table |
