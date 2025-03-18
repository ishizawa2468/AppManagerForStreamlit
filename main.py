import streamlit as st
import numpy as np

from log_util import logger
from config import SELECTABLE_PORT_RANGE, APPS
from process_manager import search_ports, try_starting_app, stop_app

st.set_page_config(
    page_title="App Manager",
    # layout="wide", # 広く表示したい場合にはコメントアウト
)

st.title("Streamlit アプリ管理")
print("\n  -- Main page is loaded -- ") # log用


# --- 📡 現在の稼働状況を表示するセクション ---
st.subheader("現在の稼働状況")
ports_search_result = search_ports() # 起動状態をpd.DataFrameで取得
logger.info('Finished ports search')

# ポートを調べた結果を表示
if ports_search_result is not None:
    logger.info('Display ports search result')
    st.dataframe(
        ports_search_result,
        use_container_width=True, # 広めに表示する設定
    )
else:
    logger.error("Ports info not found")
    st.write("Port情報の取得に失敗しました。")


# --- 🎛 アプリを起動するセクション ---
st.divider()
st.subheader("起動するアプリ・ポートを選択")

# アプリ名, Port番号の入力欄を作る
app_col, port_col = st.columns(2)
with app_col:
    app_choice = st.selectbox("起動するアプリを選択", list(APPS.keys()))
with port_col:
    selected_port = st.selectbox("使用するポートを選択 (`8501` - `8510`)", SELECTABLE_PORT_RANGE)

# 起動ボタン
if st.button("サーバー起動"):
    logger.info("Launch button is pressed. Ports will be searched again.")
    # ボタンが押されたらポートを調べ直す
    ports_search_result = search_ports()
    logger.info('Finished ports search')
    # 選択されたポートで起動しているアプリがないか調べる
    # 起動していればstringが入り、無ければ (Windows, Mac) = (None, np.nan) がそれぞれ入る
    app_of_selected_port = ports_search_result.loc[str(selected_port)][("APP_NAME")]
    logger.debug(f'selected_app: {app_of_selected_port}')

    # 起動を試みる。すでに起動済みのポートでは起動しない
    if (app_of_selected_port is None) or (app_of_selected_port is np.nan):
        # 起動できたか: is_launched、その出力(streamlitによるURLの表示): output_linesを取得
        is_launched, output_lines = try_starting_app(app_choice, selected_port)
        if is_launched: # 起動できた場合
            logger.debug('App is launched')
            st.success(f"{app_choice} をポート {selected_port} で起動しました。")
            st.write('### -> Please access the `Network URL` below!')
            st.write(output_lines)
        else:
            logger.error('Launch is failed')
            st.error(f"起動に失敗しました -- App:{app_choice}, Port: {selected_port}"
                     f"\n指定されたアプリのプログラムが正しい場所に存在しない可能性があります。")
    # すでにポートが使用されていた場合、失敗
    else:
        logger.info(f'Ports {selected_port} is already used')
        st.warning(f"ポート {selected_port} ではすでにサーバーが起動しています。")


# --- 🛑 アプリを停止するセクション ---
st.divider()
st.subheader("アプリの停止")

if ports_search_result is not None: # ポート検索結果が存在すれば
    stop_port = st.selectbox("停止するポートを選択", ports_search_result.index.unique())
    if st.button("サーバー停止"):
        logger.info("Stop button is pressed")
        # 止められたか: is_stopped、状態に応じたメッセージ: resultを受け取る
        is_stopped, result = stop_app(stop_port)
        if is_stopped:
            st.success(result)
        else:
            st.warning(result)
else: # ポート検索結果が存在しなければ
    st.error('Failed to get ports info')
    st.write("Port情報の取得に失敗しました。")
