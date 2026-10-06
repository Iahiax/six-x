import streamlit as st
import threading
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

from broker_client import CapitalComClient
from microstructure_engine import MicrostructureQuantEngine, MarketTick
from portfolio_optimizer import InstitutionalPortfolioOptimizer
from market_session_engine import AdvancedMarketSessionTimer
from macro_surprise_engine import EconomicSurpriseMacroEngine
from self_improving_core import SelfImprovingAdaptiveCore
from telegram_bot import TelegramNotifier

st.set_page_config(page_title="Institutional Autonomous Engine", layout="wide")

@st.cache_resource
def init_all_modules():
    broker = CapitalComClient()
    micro = MicrostructureQuantEngine()
    portfolio = InstitutionalPortfolioOptimizer()
    timer = AdvancedMarketSessionTimer()
    macro = EconomicSurpriseMacroEngine()
    ai_core = SelfImprovingAdaptiveCore()
    telegram = TelegramNotifier()
    return broker, micro, portfolio, timer, macro, ai_core, telegram

broker, micro, portfolio, timer, macro, ai_core, telegram = init_all_modules()

TARGET_ASSETS = {
    "NVDA": "US_EQUITIES",
    "EURUSD": "FOREX",
    "BTCUSD": "CRYPTO"
}

if "system_state" not in st.session_state:
    st.session_state.system_state = {
        "last_sync": "Never",
        "market_states": {},
        "allocations": {},
        "vpin_metrics": {},
        "warnings": {}
    }

def background_loop():
    while True:
        try:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            market_states = {}
            signals = {}
            vpin_metrics = {}
            warnings = {}

            for symbol, asset_type in TARGET_ASSETS.items():
                is_open, status_desc, sec_left = timer.get_market_status(asset_type)
                market_states[symbol] = {
                    "is_open": is_open,
                    "status": status_desc,
                    "sec_left": sec_left
                }

                if is_open:
                    dummy_tick = MarketTick(
                        timestamp=time.time(),
                        price=150.0 + np.random.randn(),
                        volume=5000.0,
                        bid=149.9, ask=150.1,
                        bid_vol=12000.0, ask_vol=8000.0
                    )
                    vpin = micro.update_vpin(dummy_tick)
                    _, is_crash = micro.compute_hawkes_intensity(time.time())
                    
                    vpin_metrics[symbol] = vpin
                    warnings[symbol] = is_crash
                    
                    if is_crash or vpin > ai_core.params["vpin_threshold"]:
                        signals[symbol] = -1.0
                    else:
                        signals[symbol] = 0.5
                else:
                    signals[symbol] = 0.0
                    vpin_metrics[symbol] = 0.0
                    warnings[symbol] = False

            dummy_returns = pd.DataFrame(np.random.randn(60, len(TARGET_ASSETS)) * 0.01, columns=list(TARGET_ASSETS.keys()))
            allocations = portfolio.solve_erc_weights(dummy_returns, signals)

            st.session_state.system_state["last_sync"] = now_str
            st.session_state.system_state["market_states"] = market_states
            st.session_state.system_state["allocations"] = allocations
            st.session_state.system_state["vpin_metrics"] = vpin_metrics
            st.session_state.system_state["warnings"] = warnings

        except Exception as e:
            print(f"Error in execution thread: {e}")

        time.sleep(5)

@st.cache_resource
def start_thread():
    t = threading.Thread(target=background_loop, daemon=True)
    t.start()
    return t

start_thread()

st.title("⚡ Autonomous Institutional Engine")
st.caption("النظام التداولي الآلي الشامل لـ Capital.com والمحفظة متعددة الأصول")

# مؤقت الجلسات
st.subheader("🌐 حالة الأسواق وتتبع الجلسات")
m_cols = st.columns(len(TARGET_ASSETS))
for idx, (symbol, asset_type) in enumerate(TARGET_ASSETS.items()):
    state = st.session_state.system_state["market_states"].get(symbol, {"is_open": False, "status": "CHECKING", "sec_left": 0})
    with m_cols[idx]:
        if state["is_open"]:
            st.success(f"**{symbol}**\n🟢 مفتوح ({state['status']})")
        else:
            mins = state["sec_left"] // 60
            st.error(f"**{symbol}**\n🛑 مغلق ({state['status']})\nافتتاح بعد: {mins} دقيقة")

st.divider()

col_left, col_right = st.columns([2, 1])
with col_left:
    st.subheader("📊 أوزان المحفظة المباشرة (Ledoit-Wolf & ERC)")
    allocs = st.session_state.system_state["allocations"]
    if allocs:
        df_alloc = pd.DataFrame(list(allocs.items()), columns=["Asset", "Optimal Weight"])
        st.dataframe(df_alloc, use_container_width=True)
        fig = go.Figure(go.Pie(labels=df_alloc["Asset"], values=df_alloc["Optimal Weight"], hole=0.4))
        fig.update_layout(template="plotly_dark", height=280)
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🛡️ مؤشرات Mico-Risk & VPIN")
    for sym in TARGET_ASSETS.keys():
        vpin_val = st.session_state.system_state["vpin_metrics"].get(sym, 0.0)
        is_warn = st.session_state.system_state["warnings"].get(sym, False)
        st.metric(f"VPIN - {sym}", f"{vpin_val:.3f}", delta="⚠️ تحذير انهيار!" if is_warn else "آمن", delta_color="inverse" if is_warn else "normal")

st.info(f"💡 آخر تحديث تزامني: {st.session_state.system_state['last_sync']}")
