FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV TRADING_MODE=DEMO

RUN mkdir -p logs

CMD ["python", "main.py"]
