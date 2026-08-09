# ==========================================
# STAGE 1: Build Angular Frontend with Node
# ==========================================
FROM node:20-slim AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npx ng build

# ==========================================
# STAGE 2: Serve Full-Stack App with Python
# ==========================================
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install psycopg2-binary

# Copy backend codebase
COPY . .

# Ensure clean app/static and copy freshly built Angular static bundle
RUN rm -rf ./app/static && mkdir -p ./app/static
COPY --from=frontend-builder /frontend/dist/expensify-angular/browser ./app/static

EXPOSE 8000

# Run uvicorn server with dynamic PORT support for Render
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
