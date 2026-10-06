import streamlit as st
import threading
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# استيراد المحركات المطورة
from microstructure_engine import MicrostructureQuantEngine, MarketTick
from portfolio_optimizer import InstitutionalPortfolioOptimizer
from market_session_engine import AdvancedMarketSessionTimer
from macro_surprise_engine import EconomicSurpriseMacroEngine
from self_improving_core import SelfImprovingAdaptiveCore

st.set_page_config(page_title="Institutional Autonomous Engine", layout="wide")

# 1. تهيئة النظام الكامل
@st.cache_resource
def build_integrated_quant_system():
    micro = MicrostructureQuantEngine()
    portfolio = InstitutionalPortfolioOptimizer()
    timer = AdvancedMarketSessionTimer()
    macro = EconomicSurpriseMacroEngine()
    ai_core = SelfImprovingAdaptiveCore()
    return micro, portfolio, timer, macro, ai_core

micro_eng, portfolio_eng, timer_eng, macro_eng, ai_core_eng = build_integrated_quant_system()

TARGET_ASSETS = {
    "NVDA": "US_EQUITIES",
    "EUR/USD": "FOREX",
    "BTC/USD": "CRYPTO"
}

if "system_live_data" not in st.session_state:
    st.session_state.system_live_data = {
        "last_beat": "Never",
        "market_states": {},
        "allocations": {},
        "vpin_values": {},
        "crash_warnings": {}
    }

# 2. حلقة التشغيل الخلفية المستمرة (24/7 Background Engine)
def core_execution_loop():
    while True:
        try:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            market_states = {}
            signals = {}
            vpin_values = {}
            crash_warnings = {}

            for symbol, asset_type in TARGET_ASSETS.items():
                is_open, status_desc, sec_left = timer_eng.get_market_status(asset_type)
                market_states[symbol] = {
                    "is_open": is_open,
                    "status": status_desc,
                    "sec_left": sec_left
                }

                if is_open:
                    # محاكاة التك المالي اللحظي
                    dummy_tick = MarketTick(
                        timestamp=time.time(),
                        price=150.0 + np.random.randn(),
                        volume=5000.0,
                        bid=149.9, ask=150.1,
                        bid_vol=12000.0, ask_vol=8000.0
                    )
                    
                    vpin = micro_eng.update_vpin(dummy_tick)
                    _, is_crash = micro_eng.compute_hawkes_intensity(time.time())
                    
                    vpin_values[symbol] = vpin
                    crash_warnings[symbol] = is_crash
                    
                    # صياغة الإشارة النهائية
                    if is_crash or vpin > ai_core_eng.params["vpin_threshold"]:
                        signals[symbol] = -1.0 # حظر الشراء والتصفية
                    else:
                        signals[symbol] = 0.5 # إشارة صعود معتدلة
                else:
                    signals[symbol] = 0.0
                    vpin_values[symbol] = 0.0
                    crash_warnings[symbol] = False

            # استمثال المحفظة عبر ERC و Ledoit-Wolf
            dummy_returns = pd.DataFrame(np.random.randn(60, len(TARGET_ASSETS)) * 0.01, columns=list(TARGET_ASSETS.keys()))
            allocations = portfolio_eng.solve_erc_weights(dummy_returns, signals)

            # التعديل الذاتي للمعاملات
            ai_core_eng.self_tune_hyperparameters(list(np.random.randn(20) * 0.02 + 0.005))

            # تحديث الحالة العامة
            st.session_state.system_live_data["last_beat"] = now_str
            st.session_state.system_live_data["market_states"] = market_states
            st.session_state.system_live_data["allocations"] = allocations
            st.session_state.system_live_data["vpin_values"] = vpin_values
            st.session_state.system_live_data["crash_warnings"] = crash_warnings

        except Exception as e:
            print(f"Error in continuous background engine: {e}")

        time.sleep(5)

@st.cache_resource
def launch_background_thread():
    t = threading.Thread(target=core_execution_loop, daemon=True)
    t.start()
    return t

launch_background_thread()

# --- 3. واجهة التحكم والتفاعل (Streamlit UI) ---
st.title("⚡ Institutional Autonomous Trading Brain")
st.caption("نظام التداول الكمي المؤسسي الشامل: الميكروثانية، استمثال المحفظة، ومحيّد الجلسات")

# عرض حالة الأسواق
st.subheader("🌐 حالة الأسواق ومؤقتات الجلسات")
m_cols = st.columns(len(TARGET_ASSETS))

for idx, (symbol, asset_type) in enumerate(TARGET_ASSETS.items()):
    state = st.session_state.system_live_data["market_states"].get(symbol, {"is_open": False, "status": "CHECKING", "sec_left": 0})
    with m_cols[idx]:
        if state["is_open"]:
            st.success(f"**{symbol}**\n🟢 مفتوح ({state['status']})")
        else:
            mins = state["sec_left"] // 60
            st.error(f"**{symbol}**\n🛑 مغلق ({state['status']})\nافتتاح بعد: {mins} دقيقة")

st.divider()

# عرض أوزان المحفظة ومؤشرات VPIN
c_left, c_right = st.columns([2, 1])

with c_left:
    st.subheader("📊 أوزان المحفظة المباشرة (Ledoit-Wolf & ERC)")
    allocs = st.session_state.system_live_data["allocations"]
    if allocs:
        df_alloc = pd.DataFrame(list(allocs.items()), columns=["Asset", "Optimal Weight"])
        st.dataframe(df_alloc, use_container_width=True)
        
        fig = go.Figure(go.Pie(labels=df_alloc["Asset"], values=df_alloc["Optimal Weight"], hole=0.4))
        fig.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig, use_container_width=True)

with c_right:
    st.subheader("🛡️ مؤشرات Mico-Risk & VPIN")
    for sym in TARGET_ASSETS.keys():
        vpin_val = st.session_state.system_live_data["vpin_values"].get(sym, 0.0)
        is_warn = st.session_state.system_live_data["crash_warnings"].get(sym, False)
        
        st.metric(f"VPIN - {sym}", f"{vpin_val:.3f}", delta="⚠️ تحذير انهيار!" if is_warn else "آمن", delta_color="inverse" if is_warn else "normal")

st.info(f"💡 آخر تحديث أوتوماتيكي محلي: {st.session_state.system_live_data['last_beat']}")
