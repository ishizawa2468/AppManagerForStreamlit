"""
アプリやポートの状態を処理するメソッド
"""
import streamlit as st
import subprocess
import time
import pandas as pd

from log_util import logger
from config import OS, APPS, ALL_PORT_RANGE
from os_utils import run_command, get_port_search_command, shape_to_dataframe
from process_utils import summarize_unique_values, add_extracted_app_name


def search_ports() -> pd.DataFrame | None:
    """現在稼働中のポートのプロセス情報を取得し、DataFrame で整理"""
    ports_data = []
    logger.info("Start to search the ports info")

    for port in ALL_PORT_RANGE:
        logger.debug(f'Investigate {port} port')
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
            logger.error(f"エラー発生: {e}")

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
        logger.error(f"エラー: アプリ {app_name} は存在しません。")
        return False, [f"エラー: アプリ {app_name} は存在しません。"]

    app_file = app_info["path"]
    app_dir = app_info["dir"]  # ここを起点に起動コマンドをうつことで、rootをこれにする
    
    # Streamlitの起動コマンド
    cmd = f"streamlit run {app_file} --server.port={port}"
    logger.info(f'Command: {cmd}')
    
    # 起動を試みる
    try:
        logger.debug('Subprocess start')
        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=app_dir,
            stdout=None,
            stderr=None
        )
        
        logger.debug('Subprocess running, capturing output...')

        # ここまで来たらOK
        logger.info(f"{app_name} がポート {port} で正常に起動しました。")
        return True, "OK"
    except Exception as e:
        logger.error(f"エラー: {e}")
        return False, [f"エラー: {e}"]


def stop_app(port):
    """指定ポートのアプリを停止"""
    # FIXME: OSに依存する部分は os_utils に移管すべき
    try:
        if OS == "Darwin" or OS == "Linux":  # macOS / Linux
            result = run_command(f"lsof -t -i :{port}")
            if result:
                for pid in result.split("\n"):
                    run_command(f"kill -2 {pid}")
                return True, f"ポート {port} のアプリを停止しました。"
        elif OS == "Windows":
            ports_data = search_ports()
            if ports_data is None or port not in ports_data.index:
                return False, f"ポート {port} で動作中のプロセスが見つかりませんでした。"
            
            pids = ports_data.loc[str(port), "PID"]
            if pd.isna(pids) or not isinstance(pids, str):
                return False, f"ポート {port} で動作中のプロセスが見つかりませんでした。"

            pids_list = [pid.strip() for pid in pids.split(",") if pid.strip().isdigit()]

            if not pids_list:
                return False, f"ポート {port} で動作中のプロセスが見つかりませんでした。"

            # すべての PID を `taskkill` で停止
            for pid in pids_list:
                run_command(f"taskkill /F /PID {pid}")

            return True, f"ポート {port} のアプリを停止しました。（PID: {', '.join(pids_list)}）"

        else:
            return False, "対応していないOSです。"

    except Exception as e:
        return False, f"エラー発生: {e}"
