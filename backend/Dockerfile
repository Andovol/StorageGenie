# SG-041: production image — the one service that serves both the JSON API and
# the built UI on a single port. Build context is the repo root.
FROM node:20-alpine AS frontend-build
WORKDIR /ui
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
ARG VITE_API_BASE=https://storagegenie.dynv6.net
ENV VITE_API_BASE=${VITE_API_BASE}
RUN npm run build

FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl tesseract-ocr libzbar0 && rm -rf /var/lib/apt/lists/*
COPY backend/pyproject.toml backend/requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock
COPY backend/ ./
RUN pip install --no-cache-dir "hatchling==1.32.0" "editables==0.6"
RUN pip install --no-cache-dir --no-build-isolation --no-deps -e .
COPY --from=frontend-build /ui/dist ./static
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
