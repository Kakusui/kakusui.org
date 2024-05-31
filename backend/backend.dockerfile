## Backend Dockerfile
FROM python:3.11-slim

## Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

## Install dependencies
RUN python3 setup.py local

## Copy the application code
COPY . /app

## Expose the port
EXPOSE 8000

## Start the server
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
