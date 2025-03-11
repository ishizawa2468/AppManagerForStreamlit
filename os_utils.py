"""
OSごとに異なる処理
"""
import subprocess
import pandas as pd

from log_util import logger
from config import OS

# OSを気にせず、シェルスクリプトを走らせる
def run_command(command) -> str:
    """OSごとのシェルコマンドを実行し、取得結果をstringで返す"""
    logger.debug('Command: ' + command)
    
    try:
        if OS == "Windows":
            # Windowsの場合はコマンドプロンプト or PowerShellを想定
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        elif OS in ["Darwin", "Linux"]:
            # Unix系の場合 bash を使わせる
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, executable="/bin/bash")
        else:
            raise Exception(f"Unsupported OS: {OS}")
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

# OSを気にせず、与えられたportの状態を調べる
def get_port_search_command(port: int):
    try:
        if OS == "Windows":
            port_search_command = f"netstat -ano | findstr :{port}"
        elif OS in ["Darwin", "Linux"]:
            port_search_command = f"lsof -i :{port}"
        else:
            raise Exception(f"Unsupported OS: {OS}")
        return port_search_command
    except Exception as e:
        return f"Error: {e}"

def shape_to_dataframe(search_output: str) -> pd.DataFrame:
    if OS in ['Darwin', 'Linux']:
        # ヘッダー: 1行目
        header = search_output.split("\n")[0].split()
        # 要素: 2行目以降
        lines = list(map(
            lambda line: line.split(maxsplit=len(header)-1),
            search_output.split("\n")[1:]
        ))
    elif OS == 'Windows':
        # ヘッダー: 自分で設定
        header = ["protocol", "local_address", "ext_address", "state", "PID"]
        # 中身がない場合、空のdfを早期リターン
        if not search_output.strip():
            return pd.DataFrame(columns=header)
        # 要素がある場合
        lines = list(map(
            lambda line: line.split(maxsplit=len(header)-1),
            search_output.split("\n")[:]
        ))
    else:
        raise Exception('想定外のOSです。')
    # dfにして返す
    return pd.DataFrame(
        lines,
        columns=header
    )

# OSを気にせず、PID(process id)における起動コマンドを取得する
def get_process_details(pid: str) -> str:
    """
    指定された PID のプロセス詳細情報を取得する
    Windows: wmic
    Linux/macOS: ps
    """
    try:
        if OS == "Windows":
            command = f'wmic process where ProcessId={pid} get CommandLine /format:list'
            result = run_command(command).strip()

            # `CommandLine=` から始まる行を探して取得
            for line in result.split("\n"):
                if line.startswith("CommandLine="):
                    return line.replace("CommandLine=", "").strip()
        elif OS in ["Darwin", "Linux"]:
            command = f"ps -p {pid} -o command="
            return run_command(command).strip()
        else:
            raise Exception(f"Unsupported OS: {OS}")
    except Exception as e:
        return f"Error: {e}"