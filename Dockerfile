# استخدام صورة Python خفيفة ومستقرة
FROM python:3.11-slim

# منع كتابة ملفات pyc وتفعيل الطباعة المباشرة في السجلات (Logs)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# تثبيت الحزم الأساسية للنظام ودعم التوقيت العالمي
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مستخدم بغير صلاحيات root (مترتب حسب متطلبات Hugging Face: UID 1000)
RUN useradd -m -u 1000 user
USER user

# ضبط مسار العمل ضمن مجلد المستخدم
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# نسخ ملف المكتبات أولاً للاستفادة من الكاش الخاص بـ Docker
COPY --chown=user:user requirements.txt .

# تثبيت المكتبات مع تفعيل خيار --no-cache-dir لتقليل حجم الحاوية
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# نسخ باقي أكواد المشروع مع ضبط الصلاحيات للمستخدم
COPY --chown=user:user . .

# فتح المنفذ المخصص لمنصة Hugging Face Spaces
EXPOSE 7860

# تشغيل Streamlit على المنفذ 7860 وعنوان IP الشامل
CMD ["streamlit", "run", "app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false"]
