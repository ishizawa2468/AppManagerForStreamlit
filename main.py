# main.py
import streamlit as st
import pandas as pd
from config import SELECTABLE_PORT_RANGE, APPS
from process_manager import get_running_apps, start_app, stop_app

st.title("Streamlit アプリ管理")

# --- 📡 現在の稼働状況を表示 ---
st.subheader("現在の稼働状況")
running_apps = get_running_apps()

if not running_apps.empty:
    st.dataframe(running_apps)
else:
    st.write("現在、起動中のアプリはありません。")

# --- 🎛 アプリ起動 ---
st.divider()
st.subheader("起動するアプリ・ポートを選択")
app_col, port_col = st.columns(2)

with app_col:
    app_choice = st.selectbox("起動するアプリを選択", list(APPS.keys()))
with port_col:
    port = st.selectbox("使用するポートを選択 (`8501` - `8510`)", SELECTABLE_PORT_RANGE)

if st.button("サーバー起動"):
    running_ports = get_running_apps().index.tolist()
    if port in running_ports:
        st.warning(f"ポート {port} ではすでにサーバーが起動しています。")
    else:
        result = start_app(app_choice, port)
        st.success(result)

# --- 🛑 アプリ停止 ---
st.divider()
st.subheader("アプリの停止")
if not running_apps.empty:
    stop_port = st.selectbox("停止するポートを選択", running_apps.index.unique())
    if st.button("サーバー停止"):
        result = stop_app(stop_port)
        st.success(result)
