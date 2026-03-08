## Dockerfile for the FastAPI backend service.
##
## This container will run the City Congestion Tracker API using Uvicorn.

FROM python:3.11-slim

WORKDIR /app

COPY ../requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ../backend /app/backend

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

