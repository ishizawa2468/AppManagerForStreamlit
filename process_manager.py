"""
起動・取得・終了
"""

import subprocess
import pandas as pd
from config import APPS, BASE_PORT, PORT_RANGE
from os_utils import get_os, run_command

def get_running_apps():
    """現在稼働中のポートのプロセス情報を取得し、DataFrame で整理"""
    data = []
    os_type = get_os()

    for port in PORT_RANGE:
        try:
            if os_type == "Darwin" or os_type == "Linux":  # macOS / Linux
                search_command = f"lsof -i :{port}"
                result = run_command(search_command)

                if result:
                    lines = result.split("\n")
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

                            # `ps` でプロセスの詳細コマンドを取得
                            cmdline = run_command(f"ps -p {pid} -o command=").strip()

                            # App Managerの識別
                            if port == BASE_PORT:
                                app_name = "App Manager"
                            elif "streamlit run" in cmdline:
                                for app, info in APPS.items():
                                    if info["path"] in cmdline:
                                        app_name = app
                                        break
                            elif "Google Chrome" in cmdline:
                                app_name = "Google Chrome"
                            elif "Safari" in cmdline:
                                app_name = "Safari"

                            data.append({
                                "Port": port,
                                "APP_NAME": app_name,
                                "COMMAND": command,
                                "PID": pid,
                                "TYPE": cols[idx_map["TYPE"]],
                                "NODE": cols[idx_map["NODE"]],
                                "NAME": cols[idx_map["NAME"]],
                            })

            elif os_type == "Windows":  # Windows
                # `netstat` でポートのプロセス情報を取得
                search_command = f'netstat -ano | findstr :{port}'
                result = run_command(search_command)

                if result:
                    lines = result.split("\n")
                    for line in lines:
                        parts = line.split()
                        if len(parts) < 5:
                            continue

                        pid = parts[-1]
                        command_info = run_command(f'tasklist /FI "PID eq {pid}" /FO CSV')

                        app_name = "other"
                        if 'streamlit' in command_info.lower():
                            for app, info in APPS.items():
                                if info["path"].lower() in command_info.lower():
                                    app_name = app
                                    break

                        data.append({
                            "Port": port,
                            "APP_NAME": app_name,
                            "COMMAND": command_info,
                            "PID": pid,
                            "TYPE": parts[1],
                            "NODE": parts[2],
                            "NAME": parts[0],
                        })

        except Exception as e:
            print(f"エラー発生: {e}")

    if data:
        df = pd.DataFrame(data)

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

def start_app(app_name, port):
    """アプリを指定ポートで起動"""
    if app_name not in APPS:
        return f"アプリ {app_name} は存在しません。"

    app_info = APPS[app_name]
    app_file = app_info["path"]
    app_dir = app_info["dir"]

    cmd = f"streamlit run {app_file} --server.port {port}"
    subprocess.Popen(cmd, shell=True, cwd=app_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return f"{app_name} をポート {port} で起動しました。"

def stop_app(port):
    """指定ポートのアプリを停止"""
    os_type = get_os()
    try:
        if os_type == "Darwin" or os_type == "Linux":  # macOS / Linux
            result = run_command(f"lsof -t -i :{port}")
            if result:
                for pid in result.split("\n"):
                    run_command(f"kill -9 {pid}")
                return f"ポート {port} のアプリを停止しました。"
        elif os_type == "Windows":
            result = run_command(f"netstat -ano | findstr :{port}")
            if result:
                pid = result.strip().split()[-1]
                run_command(f"taskkill /F /PID {pid}")
                return f"ポート {port} のアプリを停止しました。"
        else:
            return "対応していないOSです。"

    except Exception as e:
        return f"エラー発生: {e}"
