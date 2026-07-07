// Central API module — all HTTP calls go through here.
// Using a single axios instance with a shared baseURL means we only need to
// change one line if the backend URL ever changes (e.g. deploying to a server).

import axios from 'axios'

// All requests go to the FastAPI backend running in Docker on port 8000.
// The /api prefix matches the router prefix defined in backend/app/routers/sections.py.
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
})

// Returns a list of matching course codes (e.g. ["CSCE-121", "CSCE-221"])
// Used by the autocomplete search inputs on Course Search and Compare pages.
export const searchCourses = (q) =>
  api.get('/courses/search', { params: { q } })

// Returns a list of matching instructor names (e.g. ["J. Smith", "J. Jones"])
// Used by the autocomplete on Professor Lookup and Compare Professors.
export const searchInstructors = (q) =>
  api.get('/instructors/search', { params: { q } })

// Fetches all section rows that match the given filters.
// At least one of course or instructor must be provided — the API enforces this.
// Spread syntax drops null/undefined params so they don't appear in the query string.
export const getSections = (course = null, semester = null, instructor = null) =>
  api.get('/sections', {
    params: {
      ...(course && { course }),
      ...(semester && { semester }),
      ...(instructor && { instructor }),
    },
  })

// Returns the list of all semesters that exist in the database,
// used to populate the "All Semesters" filter dropdown.
export const getSemesters = () =>
  api.get('/semesters')
