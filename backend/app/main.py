from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import sections

app = FastAPI(title="TAMU Grade Distribution API")

# CORS (Cross-Origin Resource Sharing) allows the Vue frontend (running on
# localhost:5173) to make requests to this API (running on localhost:8000)
# Without this, browsers block cross-origin requests by default
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default dev server port
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Register the sections router — this wires up all the /api/... endpoints
app.include_router(sections.router)


@app.get("/health")
def health():
    # Simple health check endpoint to confirm the API is running
    return {"status": "ok"}
