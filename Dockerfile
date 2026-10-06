FROM python:3.11-slim

# تثبيت المكونات الأساسية للنظام
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نسخ ملف متطلبات المكتبات
COPY requirements.txt .

# تثبيت المكتبات الكمية ومحرك Polars
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كافة سكريبتات المشروع
COPY . .

# تعيين المتغيرات البيئية لاستغلال أقصى قدرات الأنوية
ENV PYTHONUNBUFFERED=1 \
    POLARS_MAX_THREADS=8

EXPOSE 8501 8000

CMD ["python", "main_v2_institutional.py"]
