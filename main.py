import numpy as np
import streamlit as st
from notebook.app import app_dir

from config import SELECTABLE_PORT_RANGE, APPS
from process_manager import search_ports, try_starting_app, stop_app

st.set_page_config(
    page_title="App Manager",
    # layout="wide",
)

st.title("Streamlit アプリ管理")

# --- 📡 現在の稼働状況を表示するセクション ---
st.subheader("現在の稼働状況")
ports_search_result = search_ports() # 起動状態をpd.DataFrameで取得

if not ports_search_result.empty:
    st.dataframe(
        ports_search_result,
        use_container_width=True,
    )
else:
    st.write("現在、起動中のアプリはありません。")


# --- 🎛 アプリを起動するセクション ---
st.divider()
st.subheader("起動するアプリ・ポートを選択")

app_col, port_col = st.columns(2)
with app_col:
    app_choice = st.selectbox("起動するアプリを選択", list(APPS.keys()))
with port_col:
    port = st.selectbox("使用するポートを選択 (`8501` - `8510`)", SELECTABLE_PORT_RANGE)

# 起動ボタン
if st.button("サーバー起動"):
    # ボタンが押されたらポートを調べ直す
    ports_search_result = search_ports()
    # portに起動アプリケーションを取得。あればstringが入り、無ければnp.nanになる
    app_of_selected_port = ports_search_result.loc[str(port)][("APP_NAME")]

    # 起動を試みる。すでに起動済みのポートでは起動しない
    if app_of_selected_port is np.nan:
        is_launched = try_starting_app(app_choice, port)
        if is_launched:
            st.success(f"{app_choice} をポート {port} で起動しました。")
        else:
            st.error(f"起動に失敗しました -- App:{app_choice}, Port: {port}"
                     f"\n指定されたアプリのプログラムが正しい場所に存在しない可能性があります。")

    else:
        st.warning(f"ポート {port} ではすでにサーバーが起動しています。")


# --- 🛑 アプリを停止するセクション ---
st.divider()
st.subheader("アプリの停止")
if not ports_search_result.empty:
    stop_port = st.selectbox("停止するポートを選択", ports_search_result.index.unique())
    if st.button("サーバー停止"):
        result = stop_app(stop_port)
        st.success(result)
else:
    st.write()
