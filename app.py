import streamlit as st
import asyncio
import threading
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# استيراد الوحدة والأنظمة المطورة
from macro_news_brain import MacroEconomicBrain
from market_session_timer import MarketSessionTimer
from portfolio_allocator import InstitutionalPortfolioAllocator
from super_ai_self_improving_brain import SuperAISelfImprovingBrain

st.set_page_config(page_title="Super-Intelligent Institutional Trading Brain", layout="wide")

# 1. تهيئة النظام الشامل في الذاكرة
@st.cache_resource
def init_institutional_system():
    macro_brain = MacroEconomicBrain()
    session_timer = MarketSessionTimer()
    allocator = InstitutionalPortfolioAllocator(total_capital=100000.0)
    ai_core = SuperAISelfImprovingBrain()
    return macro_brain, session_timer, allocator, ai_core

macro_brain, session_timer, allocator, ai_core = init_institutional_system()

# أصول التداول المستهدفة
TARGET_SYMBOLS = {
    "NVDA": "US_EQUITIES",
    "AAPL": "US_EQUITIES",
    "EUR/USD": "FOREX",
    "BTC/USD": "CRYPTO"
}

if "live_state" not in st.session_state:
    st.session_state.live_state = {
        "last_sync": "Initializing...",
        "allocations": {},
        "market_statuses": {},
        "system_logs": []
    }

# 2. حلقة التداول والتقييم الخفية المستمرة (Background Thread)
def autonomous_execution_loop():
    while True:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            macro_eval = macro_brain.evaluate_macro_regime()
            
            signals = {}
            biases = {}
            vols = {}
            statuses = {}

            # تقييم كل أصل مالي على حدة بناءً على حالة سوقه
            for symbol, asset_class in TARGET_SYMBOLS.items():
                is_open, status_name, seconds_left = session_timer.is_market_open(asset_class)
                statuses[symbol] = {
                    "is_open": is_open,
                    "status": status_name,
                    "seconds_left": seconds_left
                }

                if is_open and not macro_eval["blackout_active"]:
                    # حساب بيانات السعر الافتراضية
                    micro_eval = ai_core.evaluate_microstructure_vpin_and_microprice([150.0], [150.1], [100.0], [120.0])
                    score, debate_summary = ai_core.multi_agent_llm_debate(symbol, macro_eval, micro_eval)
                    
                    signals[symbol] = score
                    biases[symbol] = macro_eval["macro_bias"]
                    vols[symbol] = 0.02
                else:
                    signals[symbol] = 0.0
                    biases[symbol] = 0.0
                    vols[symbol] = 0.01

            # حساب توزيع المحفظة متعددة الأصول
            dummy_returns = pd.DataFrame(np.random.randn(50, len(TARGET_SYMBOLS)) * 0.01, columns=list(TARGET_SYMBOLS.keys()))
            allocations = allocator.calculate_portfolio_allocations(
                symbols=list(TARGET_SYMBOLS.keys()),
                returns_df=dummy_returns,
                signal_strengths=signals,
                macro_biases=biases,
                volatilities=vols
            )

            # تحديث الحالة العامة
            st.session_state.live_state["last_sync"] = timestamp
            st.session_state.live_state["allocations"] = allocations
            st.session_state.live_state["market_statuses"] = statuses

            # تنفيذ دورة التعلم والتطوير الذاتي برؤية النتائج
            ai_core.self_healing_optimization_loop(ai_core.trade_history_performance)

        except Exception as e:
            print(f"Error in continuous core execution: {e}")

        time.sleep(10) # تحديث مستمر كل 10 ثوانٍ

@st.cache_resource
def start_core_thread():
    t = threading.Thread(target=autonomous_execution_loop, daemon=True)
    t.start()
    return t

start_core_thread()

# --- 3. واجهة المستخدم والتفاعل الحية (Streamlit Dashboard) ---
st.title("🧠 Autonomous Multi-Asset Institutional Engine")
st.caption("النظام التداولي الفائق: إدارة المحفظة متعددة الأصول، مؤقت جلسات البورصة، والتعلم الذاتي")

# شريط حالة الجلسات المؤقتة
st.subheader("⏰ مؤقتات جلسات البورصة وحالة الأسواق الحية")
session_cols = st.columns(len(TARGET_SYMBOLS))

for idx, (symbol, asset_class) in enumerate(TARGET_SYMBOLS.items()):
    status_info = st.session_state.live_state["market_statuses"].get(symbol, {"is_open": False, "status": "CHECKING", "seconds_left": 0})
    with session_cols[idx]:
        if status_info["is_open"]:
            st.success(f"**{symbol}**\n🟢 مفتوح ({status_info['status']})")
        else:
            mins_left = status_info['seconds_left'] // 60
            st.error(f"**{symbol}**\n🛑 مغلق ({status_info['status']})\nيفتح خلال: {mins_left} دقيقة")

st.divider()

# شريط التوزيع المالي والمخاطر
col_alloc, col_params = st.columns([2, 1])

with col_alloc:
    st.subheader("⚖️ توزيع رأس المال المستهدف عبر المحفظة (Portfolio Allocation)")
    alloc_data = st.session_state.live_state["allocations"]
    if alloc_data:
        df_alloc = pd.DataFrame.from_dict(alloc_data, orient="index")
        st.dataframe(df_alloc, use_container_width=True)
        
        # رسم بياني لتوزيع الأوزان
        fig_bar = go.Figure(go.Bar(
            x=list(alloc_data.keys()),
            y=[v["allocated_capital_usd"] for v in alloc_data.values()],
            marker_color=["#00FFA3" if v["allocated_capital_usd"] > 0 else "#FF4B4B" for v in alloc_data.values()]
        ))
        fig_bar.update_layout(title="توزيع رأس المال القائم ($)", template="plotly_dark", height=280)
        st.plotly_chart(fig_bar, use_container_width=True)

with col_params:
    st.subheader("🧬 معامل التكيّف والتعلم الذاتي (Hyperparameters)")
    st.json(ai_core.hyperparameters)
    st.metric("آخر تزامن كلي", st.session_state.live_state["last_sync"])

st.info("💡 يتم تحديث الصفقات وأوزان المحفظة أوتوماتيكياً في الخلفية. يتوقف النظام فوراً عند إغلاق جلسة الأصل أو تفعيل درع الأخبار.")
