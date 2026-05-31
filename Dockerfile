FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --default-timeout=120 --retries 5 -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT ["sh", "-c", "sed 's/\\r$//' entrypoint.sh | sh"]