from sqlalchemy import Column, Integer, String, Numeric, Text
from app.database import Base


class Section(Base):
    # This class maps to the "sections" table we created in PostgreSQL
    # Each attribute corresponds to a column in the table
    __tablename__ = "sections"

    id         = Column(Integer, primary_key=True)
    semester   = Column(String)
    college    = Column(String)
    department = Column(String)
    course     = Column(String)   # e.g. "AERO-201"
    section    = Column(String)   # e.g. "500"
    instructor = Column(String)
    gpa        = Column(Numeric)
    a          = Column(Integer)
    b          = Column(Integer)
    c          = Column(Integer)
    d          = Column(Integer)
    f          = Column(Integer)
    a_to_f     = Column(Integer)
    i          = Column(Integer)  # incomplete
    s          = Column(Integer)  # satisfactory
    u          = Column(Integer)  # unsatisfactory
    q          = Column(Integer)  # dropped
    x          = Column(Integer)  # absent from final
    total      = Column(Integer)


class CourseDescription(Base):
    __tablename__ = "course_descriptions"

    course_code   = Column(String, primary_key=True)
    title         = Column(Text)
    credits       = Column(Numeric(4, 1))
    lecture_hours = Column(Integer)
    lab_hours     = Column(Integer)
    description   = Column(Text)
    prerequisites = Column(Text)
