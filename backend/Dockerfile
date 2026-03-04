FROM python:3.12-slim

WORKDIR /app

# System deps (small essentials)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --default-timeout=300 --retries=10 -r /app/requirements.txt

# App code
COPY app /app/app

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
