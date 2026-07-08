from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.models import Section
from app.schemas import SectionResponse

# All routes in this file are prefixed with /api
# e.g. get_colleges is reachable at GET /api/colleges
router = APIRouter(prefix="/api")


@router.get("/colleges")
def get_colleges(db: Session = Depends(get_db)):
    # Returns all distinct college names, alphabetically sorted.
    # Used to confirm data loaded correctly — not consumed by the frontend.
    rows = db.query(Section.college).distinct().order_by(Section.college).all()
    return [r.college for r in rows]


@router.get("/departments")
def get_departments(college: Optional[str] = None, db: Session = Depends(get_db)):
    # Returns distinct department names, optionally filtered by college.
    # Not currently consumed by the frontend.
    query = db.query(Section.department).distinct()
    if college:
        query = query.filter(Section.college == college)
    rows = query.order_by(Section.department).all()
    return [r.department for r in rows]


@router.get("/semesters")
def get_semesters(db: Session = Depends(get_db)):
    # Returns all distinct semester strings (e.g. "Spring 2026") in the database.
    # The frontend sorts these by chronological key after receiving them.
    rows = db.query(Section.semester).distinct().order_by(Section.semester).all()
    return [r.semester for r in rows]


@router.get("/courses/search")
def search_courses(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    # Autocomplete endpoint for course names.
    # Normalizes input (uppercase, spaces→dashes) before searching so that
    # "csce 121" and "CSCE-121" both match the stored "CSCE-121" format.
    normalized = q.strip().upper().replace(" ", "-")
    rows = (
        db.query(Section.course)
        .distinct()
        .filter(Section.course.ilike(f"%{normalized}%"))
        .order_by(Section.course)
        .all()
    )
    return [r.course for r in rows]


@router.get("/instructors/search")
def search_instructors(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    # Autocomplete endpoint for instructor names.
    # Names are stored as "J. Takachi Tomita" — ilike does a case-insensitive
    # substring search so partial matches like "smith" or "J. Smith" both work.
    rows = (
        db.query(Section.instructor)
        .distinct()
        .filter(Section.instructor.ilike(f"%{q.strip()}%"))
        .order_by(Section.instructor)
        .all()
    )
    # Filter out any rows where instructor is NULL or empty string
    return [r.instructor for r in rows if r.instructor]


@router.get("/sections", response_model=list[SectionResponse])
def get_sections(
    course: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    instructor: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    # Main data endpoint — returns every section row matching the given filters.
    # At least one of course or instructor is required to prevent accidentally
    # returning the entire 99k-row table in one response.
    if not course and not instructor:
        raise HTTPException(status_code=400, detail="Provide at least course or instructor.")

    query = db.query(Section)

    if course:
        # Normalize the course code the same way as the search endpoint
        normalized = course.strip().upper().replace(" ", "-")
        query = query.filter(Section.course == normalized)
    if semester:
        query = query.filter(Section.semester == semester)
    if instructor:
        # Exact match on instructor name — the frontend always sends the full
        # formatted name selected from the autocomplete, never a partial string
        query = query.filter(Section.instructor == instructor)

    # Order by semester then section so the data arrives in a sensible default order
    return query.order_by(Section.semester, Section.section).all()


@router.get("/rankings")
def get_department_rankings(department: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    # Returns one row per professor in the given department with aggregated stats.
    # Only includes professors with at least 2 sections to filter out one-off visitors.
    results = (
        db.query(
            Section.instructor,
            (func.sum(Section.gpa * Section.a_to_f) / func.sum(Section.a_to_f)).label("avg_gpa"),
            func.sum(Section.total).label("total_students"),
            func.count(Section.id).label("sections_count"),
            # Multiply by 1.0 to force float division instead of integer division
            (func.sum(Section.a * 1.0) / func.sum(Section.a_to_f)).label("a_percent"),
        )
        .filter(
            Section.department == department,
            Section.instructor != None,
            Section.a_to_f > 0,
            Section.gpa != None,
            Section.gpa > 0,
        )
        .group_by(Section.instructor)
        .having(func.count(Section.id) >= 2)
        .all()
    )

    rankings = []
    for r in results:
        avg_gpa = float(r.avg_gpa) if r.avg_gpa is not None else None
        a_percent = float(r.a_percent) if r.a_percent is not None else 0.0
        score = (
            min(100, round((avg_gpa / 4.0) * 70 + a_percent * 30))
            if avg_gpa is not None else None
        )
        rankings.append({
            "instructor": r.instructor,
            "avg_gpa": round(avg_gpa, 3) if avg_gpa is not None else None,
            "total_students": int(r.total_students),
            "sections_count": int(r.sections_count),
            "a_percent": round(a_percent * 100, 1),
            "score": score,
        })

    # Default sort: highest score first, nulls last
    return sorted(rankings, key=lambda x: x["score"] or 0, reverse=True)


@router.get("/course-rankings")
def get_course_rankings(department: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    # Returns one row per course in the given department with aggregated stats.
    # Difficulty is computed on the frontend from avg_gpa and f_percent.
    results = (
        db.query(
            Section.course,
            (func.sum(Section.gpa * Section.a_to_f) / func.sum(Section.a_to_f)).label("avg_gpa"),
            func.sum(Section.total).label("total_students"),
            func.count(Section.id).label("sections_count"),
            (func.sum(Section.a * 1.0) / func.sum(Section.a_to_f)).label("a_percent"),
            (func.sum(Section.f * 1.0) / func.sum(Section.a_to_f)).label("f_percent"),
            # Q-drop % uses total enrolled as denominator since Q students never received a grade
            (func.sum(Section.q * 1.0) / func.sum(Section.total)).label("q_percent"),
        )
        .filter(
            Section.department == department,
            Section.a_to_f > 0,
            Section.gpa != None,
            Section.gpa > 0,
        )
        .group_by(Section.course)
        .all()
    )

    courses = []
    for r in results:
        avg_gpa = float(r.avg_gpa) if r.avg_gpa is not None else None
        a_pct = float(r.a_percent) if r.a_percent is not None else 0.0
        f_pct = float(r.f_percent) if r.f_percent is not None else 0.0
        q_pct = float(r.q_percent) if r.q_percent is not None else 0.0
        courses.append({
            "course": r.course,
            "avg_gpa": round(avg_gpa, 3) if avg_gpa is not None else None,
            "total_students": int(r.total_students),
            "sections_count": int(r.sections_count),
            "a_percent": round(a_pct * 100, 1),
            "f_percent": round(f_pct * 100, 1),
            "q_percent": round(q_pct * 100, 1),
        })

    # Default sort: lowest avg GPA first (hardest courses at the top)
    return sorted(courses, key=lambda x: x["avg_gpa"] or 4.0)
