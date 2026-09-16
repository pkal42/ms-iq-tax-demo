FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PORT=8080

WORKDIR /app
COPY src ./src

EXPOSE 8080
CMD ["sh", "-c", "uvicorn meridian_iq.web:app --host 0.0.0.0 --port ${PORT}"]
