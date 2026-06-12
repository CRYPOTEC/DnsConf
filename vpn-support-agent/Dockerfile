FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Config is provided via environment variables (see .env.example).
CMD ["python", "main.py"]
