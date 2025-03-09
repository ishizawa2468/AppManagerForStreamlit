"""
アプリやポートの状態を処理するメソッド
"""

import subprocess
import time
import pandas as pd
from config import OS, APPS, BASE_PORT, ALL_PORT_RANGE
from os_utils import run_command, get_port_search_command
from process_utils import shape_to_dataframe, summarize_unique_values, add_extracted_app_name


def search_ports():
    """現在稼働中のポートのプロセス情報を取得し、DataFrame で整理"""
    ports_data = []

    for port in ALL_PORT_RANGE:
        try:
            # port情報を調べるコマンドを取得
            search_command: str = get_port_search_command(port=port)
            # port情報を調べる
            search_output: str = run_command(search_command)
            # 調べた情報をdfに整形する
            port_search_result: pd.DataFrame = shape_to_dataframe(search_output)
            # portあたりの重複した情報を取り除く
            slim_result: pd.DataFrame = summarize_unique_values(port_search_result)
            # portのprocess idを辿って、起動しているアプリケーションを調べる
            port_result: pd.DataFrame = add_extracted_app_name(slim_result)
            # ポート情報を追加
            port_result["Port"] = str(port)
            ports_data.append(port_result)
        except Exception as e:
            print(f"エラー発生: {e}")

    if ports_data:
        # 全てのportの調査結果を1つのdfにまとめる
        integrated_ports_result = pd.concat(ports_data, ignore_index=True)
        # Port をインデックスに設定
        integrated_ports_result.set_index("Port", inplace=True)
        # 重要な部分だけ切り出す
        # 現在は Port, APP_NAME, PID のみを抽出
        return integrated_ports_result[["APP_NAME", "PID"]]
    else:
        return None


def try_starting_app(app_name, port):
    """アプリを指定ポートで起動し、成功したかを判定"""
    app_info = APPS.get(app_name)
    if not app_info:
        print(f"エラー: アプリ {app_name} は存在しません。")
        return False
    app_file = app_info["path"]
    app_dir = app_info["dir"] # ここを起点に起動コマンドをうつことで、rootをこれにする
    # Streamlitの起動コマンドはpythonライブラリのコマンドなのでOSに依存しない
    cmd = f"streamlit run {app_file} --server.port {port}"
    # 起動を試みる
    try:
        process = subprocess.Popen(cmd, shell=True,
                                   cwd=app_dir, # これがroot
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(1) # シェルコマンドの実行は非同期らしいので、起動コマンドの出力が出るのを一応待つ

        # エラーメッセージ・エラーを確認
        stderr_output = process.stderr.read().strip()
        if stderr_output:
            return False
        if process.poll() != 0:  # プロセスが終了していたらエラー
            print(f"エラー: アプリ {app_name} の起動に失敗しました。")
            print(f"エラーメッセージ: {stderr_output}")
            return False
        # ここまで来たらOK
        return True  # 起動成功
    except Exception as e:
        print(f"エラー: {e}")
        return False


def stop_app(port):
    """指定ポートのアプリを停止"""
    try:
        if OS == "Darwin" or OS == "Linux":  # macOS / Linux
            result = run_command(f"lsof -t -i :{port}")
            if result:
                for pid in result.split("\n"):
                    run_command(f"kill -9 {pid}")
                return f"ポート {port} のアプリを停止しました。"
        elif OS == "Windows":
            result = run_command(f"netstat -ano | findstr :{port}")
            if result:
                pid = result.strip().split()[-1]
                run_command(f"taskkill /F /PID {pid}")
                return f"ポート {port} のアプリを停止しました。"
        else:
            return "対応していないOSです。"

    except Exception as e:
        return f"エラー発生: {e}"
