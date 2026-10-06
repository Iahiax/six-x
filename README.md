# ⚡ six-x: Capital-AI-X Institutional Trading Engine

نظام تداول كمي مؤتمت بالكامل مع:
- 🤖 محرك إجماع متعدد الوكلاء (Multi-Agent Consensus)
- 🧪 اختبار تاريخي شامل (Backtest Engine)
- 📊 واجهة Streamlit تفاعلية
- 💬 بوت Telegram للتحكم والمراقبة
- ⚠️ إدارة مخاطر مؤسسية
- 🔐 وضع DEMO آمن افتراضي

## 🎯 الوضع الافتراضي: DEMO

**الحالة الآمنة الافتراضية:**
- جميع الصفقات افتراضية
- لا توجد أموال حقيقية معرضة
- مثالي للاختبار والتطوير
- يمكن التبديل إلى LIVE يدويًا بعد التحقق الكامل

## 📋 المتطلبات

- Python 3.11+
- pip أو conda
- Docker (اختياري)
- توكن Telegram Bot (اختياري)
- بيانات Capital.com API (للتشغيل الحقيقي)

## 🚀 التثبيت السريع

### الطريقة 1: التثبيت المباشر

```bash
# 1. استنساخ المشروع
git clone https://github.com/Iahiax/six-x.git
cd six-x

# 2. تشغيل سكريبت الإعداد
chmod +x setup.sh
./setup.sh

# 3. تعديل البيئة
cp .env.example .env
# ثم قم بتحرير .env وأضف قيمك الحقيقية

# 4. التشغيل
python main.py
```

### الطريقة 2: Docker

```bash
# 1. تثبيت المتطلبات
chmod +x setup.sh
./setup.sh

# 2. التشغيل
docker-compose up --build
```

## ⚙️ إعدادات البيئة

عدّل ملف `.env` بقيمك الخاصة:

```env
# Capital.com API
CAPITAL_API_KEY=your_key
CAPITAL_IDENTIFIER=your_email
CAPITAL_PASSWORD=your_password
CAPITAL_MODE=DEMO  # أو LIVE بعد الاختبار

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# وضع التداول (افتراضي: DEMO)
TRADING_MODE=DEMO
```

## 🎮 استخدام البوت

### الأوامر الأساسية

```
/start          - عرض القائمة الرئيسية
/status         - حالة النظام الحالية
/portfolio      - تفاصيل المحفظة
/risk           - تقرير المخاطر
/mode           - التبديل بين DEMO و LIVE
/kill           - إيقاف طارئ
/resume         - استئناف التشغيل
/backtest       - تشغيل اختبار تاريخي
/help           - مساعدة شاملة
```

### التبديل بين DEMO و LIVE

1. اكتب `/mode`
2. اختر:
   - 🟢 DEMO (آمن - افتراضي)
   - 🔴 LIVE (حقيقي - خطير!)

## 🧪 الاختبار التاريخي

```
/backtest
```

سيظهر خيارات لاختيار الأصل والفترة الزمنية، ثم ينفذ:
- تحميل البيانات التاريخية
- تطبيق الإشارات
- حساب العوائد والمؤشرات
- محاكاة مونتي كارلو

## 📊 التشغيل

### تشغيل النظام الرئيسي

```bash
python main.py
```

سيبدأ في:
- وضع DEMO الآمن
- تشغيل بوت Telegram تلقائيًا
- نشر التنبيهات
- معالجة الأوامر من البوت

### تشغيل البوت منفصل

```bash
python telegram_control_bot.py
```

### تشغيل واجهة Streamlit

```bash
streamlit run app.py
```

## 🔐 نقاط الأمان المهمة

✅ **الوضع الافتراضي آمن:**
- DEMO هو الخيار الافتراضي
- لا توجد صفقات حقيقية تلقائيًا
- يمكن الاختبار بدون مخاطر

⚠️ **قبل التشغيل الحقيقي:**
1. اختبر النظام بالكامل في وضع DEMO
2. تحقق من صلاحية API Key و Password
3. تأكد من توكن Telegram والـ Chat ID
4. راجع جميع إعدادات المخاطر
5. ابدأ بمبالغ صغيرة في LIVE

🛑 **إيقاف طارئ:**
- اكتب `/kill` في البوت لإيقاف فوري
- هذا يفعّل Circuit Breaker ويجمّد جميع العمليات

## 📁 هيكل المشروع

```
six-x/
├── main.py                      # برنامج التشغيل الرئيسي
├── telegram_control_bot.py       # بوت Telegram
├── config.py                     # التكوين المركزي
├── app.py                        # واجهة Streamlit
│
├── # محركات العمل
├── broker_client.py              # عميل Capital.com
├── massive_indicators.py         # المؤشرات الفنية
├── llm_agent_consensus.py        # محرك الإجماع
├── portfolio_allocator.py        # توزيع المحفظة
├── risk_and_execution.py         # إدارة المخاطر
├── backtest_engine.py            # الاختبار التاريخي
│
├── # ملفات الإعداد
├── .env.example                  # مثال متغيرات البيئة
├── requirements.txt              # المتطلبات
├── docker-compose.yml            # Docker Compose
├── Dockerfile                    # Docker Image
├── setup.sh                      # سكريبت الإعداد
│
└── logs/                         # ملفات السجلات
```

## 🔧 الإعدادات المتقدمة

### حدود المخاطر

```env
MAX_DAILY_DRAWDOWN_PCT=0.05      # أقصى انجراف يومي (5%)
MAX_POSITION_SIZE_PCT=0.05       # أقصى وزن أصل (5%)
CONFIDENCE_THRESHOLD=0.80        # عتبة الثقة
MAX_SLIPPAGE_POINTS=0.5          # أقصى انزلاق سعري
```

### إعدادات المحفظة

```env
DEFAULT_CAPITAL=100000           # رأس المال الافتراضي
MAX_LEVERAGE=2.0                 # أقصى رفع مالي
MAX_ASSET_WEIGHT=0.35            # أقصى وزن لأصل
CONSENSUS_THRESHOLD=0.65         # عتبة الإجماع
```

## 📚 التوثيق الإضافي

جميع الملفات موثقة بالعربية مع تعليقات واضحة:
- `massive_indicators.py` - شرح كل مؤشر
- `broker_client.py` - شرح واجهة API
- `llm_agent_consensus.py` - شرح محرك الإجماع

## 🚨 استكشاف الأخطاء

### الخطأ: `ModuleNotFoundError`

```bash
pip install -r requirements.txt
```

### الخطأ: `TELEGRAM_BOT_TOKEN not set`

```bash
# تأكد من وجود .env بقيم صحيحة
cat .env | grep TELEGRAM
```

### الخطأ: `Connection refused`

تأكد من اتصالك بالإنترنت وصحة بيانات API.

## 📞 الدعم والمساهمة

للمشاكل والاستفسارات:
- 📧 فتح issue على GitHub
- 💬 اطلب مساعدة في المشروع

## 📄 الترخيص

MIT License - استخدم بحرية

---

**تذكر دائمًا:**
- DEMO = آمن وافتراضي ✅
- LIVE = بعد اختبار كامل فقط ⚠️
- /kill = إيقاف طارئ في أي وقت 🛑

**Happy Trading! 🚀**
