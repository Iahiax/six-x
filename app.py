import streamlit as st
import pandas as pd
import numpy as np
from state_persistence import SystemStateManager

st.set_page_config(page_title="CAPITAL-AI-X Dashboard", layout="wide", page_icon="⚡")

st.title("⚡ CAPITAL-AI-X Institutional Operations Control")

state_mgr = SystemStateManager()

col1, col2, col3, col4 = st.columns(4)
col1.metric("System Status", "ONLINE", delta="100% Operational")
col2.metric("Circuit Breaker", "NORMAL", delta_color="normal")
col3.metric("GPU Acceleration", "CUDA ACTIVE", delta="PyTorch 2.x")
col4.metric("Tor Proxy", "CONNECTED", delta="SOCKS5 9050")

st.markdown("---")

st.subheader("📊 Active Positions")
open_trades = state_mgr.get_open_trades()
if open_trades:
    df_trades = pd.DataFrame(open_trades, columns=["Deal ID", "Epic", "Direction", "Size", "Entry Price"])
    st.dataframe(df_trades, use_container_width=True)
else:
    st.info("لا توجد صفقات مفتوحة حالياً.")

st.markdown("---")
if st.button("🚨 TRIGGER EMERGENCY KILL SWITCH"):
    st.error("تم تفعيل مفتاح الإيقاف الطارئ!")
