from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
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
