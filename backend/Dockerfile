FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so Docker can cache this layer
# If only app code changes, Docker won't re-install packages on rebuild
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the app code
COPY . .

# Start the FastAPI server on all interfaces so Docker can route traffic to it
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
