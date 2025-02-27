import streamlit as st
import subprocess
import pandas as pd

# 各アプリのエントリーポイントとディレクトリ
APPS = {
    "PlanckThermoEmulator": {"path": "../PlanckThermoEmulator/home.py", "dir": "../PlanckThermoEmulator"},
    "RadiationSpectraRotator": {"path": "../RadiationSpectraRotator/home.py", "dir": "../RadiationSpectraRotator"},
    "XRDSpotAnalyzer": {"path": "../XRDSpotAnalyzer/home.py", "dir": "../XRDSpotAnalyzer"},
}

BASE_PORT = 8500  # App Manager用
PORT_RANGE = list(range(BASE_PORT, BASE_PORT + 11))  # 8500〜8510
SELECTABLE_PORT_RANGE = list(range(BASE_PORT + 1, BASE_PORT + 11))  # managerである8500を除く

st.title("Streamlit アプリ管理")

# --- 🔍 `lsof` + `ps` を使ってポートごとのプロセス情報を取得 ---
def get_running_apps():
    """ `lsof` を用いて現在使用中のポートのプロセス情報を取得し、DataFrame で整理 """
    data = []

    for port in PORT_RANGE:
        try:
            result = subprocess.run(
                ["lsof", "-i", f":{port}"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if result.stdout:
                lines = result.stdout.split("\n")
                header = lines[0].split()
                idx_map = {key: i for i, key in enumerate(header)}

                required_cols = ["COMMAND", "PID", "TYPE", "NODE", "NAME"]
                if not all(col in idx_map for col in required_cols):
                    continue

                for line in lines[1:]:
                    cols = line.split()
                    if len(cols) > max(idx_map.values()):
                        pid = cols[idx_map["PID"]]
                        command = cols[idx_map["COMMAND"]]
                        app_name = "other"

                        # `ps` を使ってプロセスの詳細コマンドを取得
                        try:
                            ps_result = subprocess.run(
                                ["ps", "-p", pid, "-o", "command="],
                                stdout=subprocess.PIPE, text=True
                            )
                            cmdline = ps_result.stdout.strip()

                            # App Managerの識別
                            if port == BASE_PORT:
                                app_name = "App Manager"
                            # `streamlit run` の実行スクリプトを解析
                            elif "streamlit run" in cmdline:
                                for app, info in APPS.items():
                                    if info["path"] in cmdline:
                                        app_name = app
                                        break
                            elif "Google Chrome" in cmdline:
                                app_name = "Google Chrome"
                            elif "Safari" in cmdline:
                                app_name = "Safari"
                        except Exception:
                            pass

                        data.append({
                            "Port": port,
                            "APP_NAME": app_name,
                            "COMMAND": command,
                            "PID": pid,
                            "TYPE": cols[idx_map["TYPE"]],
                            "NODE": cols[idx_map["NODE"]],
                            "NAME": cols[idx_map["NAME"]],
                        })
        except Exception as e:
            st.error(f"エラー発生: {e}")

    if data:
        df = pd.DataFrame(data)
        df = df.drop_duplicates()  # 重複削除

        # Portごとにデータを集約
        df = df.groupby("Port").agg({
            "APP_NAME": lambda x: ", ".join(set(x)),
            "COMMAND": lambda x: ", ".join(set(x)),
            "PID": lambda x: ", ".join(set(x)),
            "TYPE": lambda x: ", ".join(set(x)),
            "NODE": lambda x: ", ".join(set(x)),
            "NAME": lambda x: ", ".join(set(x)),
        }).reset_index()

        df.set_index("Port", inplace=True)  # Port をインデックスに設定
        return df
    else:
        return pd.DataFrame(columns=["APP_NAME", "COMMAND", "PID", "TYPE", "NODE", "NAME"]).set_index("Port")

# --- 📡 現在の稼働状況を DataFrame で表示 ---
st.subheader("現在の稼働状況")
running_apps = get_running_apps()

if not running_apps.empty:
    st.dataframe(running_apps)
else:
    st.write("現在、起動中のアプリはありません。")

# --- 🎛 ポート選択 & アプリ選択 ---
st.divider()
st.subheader("起動するアプリ・ポートを選択")
app_col, port_col = st.columns(2)
with app_col:
    app_choice = st.selectbox("起動するアプリを選択", list(APPS.keys()))
with port_col:
    port = st.selectbox("使用するポートを選択 (`8501` - `8510`)", SELECTABLE_PORT_RANGE)

# --- 🚀 アプリ起動ボタン ---
if st.button("サーバー起動"):
    running_ports = get_running_apps().index.tolist()

    if port in running_ports:
        st.warning(f"ポート {port} ではすでにサーバーが起動しています。")
    else:
        app_info = APPS[app_choice]
        app_file = app_info["path"]
        app_dir = app_info["dir"]

        cmd = f"streamlit run {app_file} --server.port {port}"
        process = subprocess.Popen(cmd, shell=True, cwd=app_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        st.success(f"{app_choice} サーバーをポート {port} で起動しました。")

# --- 🛑 アプリ停止ボタン ---
st.divider()
st.subheader("アプリの停止")
if not running_apps.empty:
    stop_port = st.selectbox("停止するポートを選択", running_apps.index.unique())
    if st.button("サーバー停止"):
        try:
            result = subprocess.run(
                ["lsof", "-t", "-i", f":{stop_port}"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            pids = result.stdout.strip().split("\n")

            if pids:
                for pid in pids:
                    subprocess.run(["kill", "-9", pid])
                st.success(f"ポート {stop_port} のアプリを停止しました。リロードしてください。")
            else:
                st.warning(f"ポート {stop_port} に関連するプロセスが見つかりませんでした。")

        except Exception as e:
            st.error(f"アプリ停止時にエラー発生: {e}")
