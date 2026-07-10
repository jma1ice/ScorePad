FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_ENV=production

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scorepad.py .
COPY templates/ ./templates/
COPY static/ ./static/
COPY dictionary/ ./dictionary/

EXPOSE 2283

CMD ["python", "scorepad.py"]
