FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY run.py .
COPY app/ app/
COPY usuaris.txt /tmp/usuaris.txt

RUN mkdir -p /app/data

EXPOSE 5000

CMD ["python", "run.py"]
