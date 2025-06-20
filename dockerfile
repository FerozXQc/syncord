FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Run both FastAPI (without reload) and bot.py in parallel
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port 8000"]
