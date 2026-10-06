import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import time

st.set_page_config(
    page_title="Institutional Trading Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# عنوان الصفحة وإعدادات الهيدر
st.title("⚡ Institutional Algorithmic Execution Terminal")
st.caption("نظام التداول الكمي عالي السرعة - مراقبة التدفق والسيولة الحية")

# شريط المؤشرات السريعة (KPI Highlights)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("رأس المال القائم", "$104,250.00", "+4.25%")
with col2:
    st.metric("OFI (Order Flow Imbalance)", "+420.5", "Bullish Flow", delta_color="normal")
with col3:
    st.metric("متوسط زمن التنفيذ (Latency)", "1.24 ms", "-0.15 ms", delta_color="inverse")
with col4:
    st.metric("النسبة العظمى للتراجع (Max DD)", "1.12%", "Safe")

st.divider()

# توليد بيانات محاكاة تفاعلية
@st.cache_data(ttl=1)
def generate_live_data():
    dates = pd.date_range(end=pd.Timestamp.now(), periods=50, freq="1s")
    df = pd.DataFrame({
        "timestamp": dates,
        "price": np.random.randn(50).cumsum() + 150.0,
        "ofi": np.random.randn(50) * 100,
        "equity": np.linspace(100000, 104250, 50) + np.random.randn(50)*100
    })
    return df

data = generate_live_data()

# تقسيم الشاشة إلى عمودين للرسومات البيانية
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("📈 سعر السهم ومؤشر تدفق الأوامر (Level 2 OFI)")
    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(x=data["timestamp"], y=data["price"], mode="lines", name="Price", line=dict(color="#00FFA3", width=2)))
    fig_price.update_layout(template="plotly_dark", height=380, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_price, use_container_width=True)

    st.subheader("📊 صافي عدم توازن تدفق الطلبات (OFI)")
    fig_ofi = px.bar(data, x="timestamp", y="ofi", color="ofi", color_continuous_scale="RdYlGn")
    fig_ofi.update_layout(template="plotly_dark", height=220, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_ofi, use_container_width=True)

with right_col:
    st.subheader("🎯 صفقات النظام والقرارات الحية")
    st.dataframe(
        pd.DataFrame({
            "Symbol": ["NVDA", "AAPL", "EUR/USD", "BTC/USD"],
            "Action": ["BUY", "HOLD", "BUY", "SELL"],
            "Kelly Alloc": ["$12,400", "$0", "$8,500", "$5,100"],
            "Confidence": ["91%", "45%", "84%", "78%"]
        }),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("⚙️ حالة خدمات النظام (Health Check)")
    st.success("✅ QuestDB Time-Series DB: Connected")
    st.success("✅ Capital.com WebSocket: 12ms Latency")
    st.info("ℹ️ RL Execution Agent: Model Updated (PPO)")

# إمكانية التحديث الآلي للواجهة
if st.checkbox("تفعيل البث المباشر (Auto-Refresh)", value=True):
    time.sleep(1)
    st.rerun()
