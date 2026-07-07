import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import sections

app = FastAPI(title="TAMU Grade Distribution API")

# CORS (Cross-Origin Resource Sharing) allows the Vue frontend to make requests
# to this API. Without it, browsers block cross-origin requests by default.
# In production, FRONTEND_URL is set as an environment variable on Railway
# pointing to the deployed Vercel frontend. Localhost is kept for local dev.
origins = [
    "http://localhost:5173",
    os.environ.get("FRONTEND_URL", ""),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in origins if o],  # filter out empty strings
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Register the sections router — this wires up all the /api/... endpoints
app.include_router(sections.router)


@app.get("/health")
def health():
    # Simple health check endpoint to confirm the API is running
    return {"status": "ok"}
