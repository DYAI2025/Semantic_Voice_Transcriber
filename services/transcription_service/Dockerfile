FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY services/transcription_service /app/services/transcription_service

ENV SVT_BASE_PATH=/app
CMD ["uvicorn", "services.transcription_service.api:app", "--host", "0.0.0.0", "--port", "8000"]
