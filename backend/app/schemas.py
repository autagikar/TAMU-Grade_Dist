from pydantic import BaseModel
from typing import Optional


# Pydantic schemas define the shape of data that goes IN and OUT of the API
# They handle validation and automatic JSON serialization


class SectionResponse(BaseModel):
    # The full data for one section row, returned by the API
    id:         int
    semester:   str
    college:    str
    department: str
    course:     str
    section:    str
    instructor: Optional[str]
    gpa:        Optional[float]
    a:          int
    b:          int
    c:          int
    d:          int
    f:          int
    a_to_f:     int
    i:          int
    s:          int
    u:          int
    q:          int
    x:          int
    total:      int

    class Config:
        # Tells Pydantic to read data from SQLAlchemy model attributes
        # instead of expecting a plain dictionary
        from_attributes = True
