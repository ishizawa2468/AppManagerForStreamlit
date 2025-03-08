"""
OSごとに異なる処理
"""
import subprocess
from config import OS

# OSを気にせず、シェルスクリプトを走らせる
def run_command(command) -> str:
    """OSごとのシェルコマンドを実行し、取得結果をstringで返す"""
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

# OSを気にせず、PID(process id)における起動コマンドを取得する
def get_process_details(pid: str) -> str:
    """
    指定された PID のプロセス詳細情報を取得する
    Windows: tasklist
    Linux/macOS: ps
    """
    try:
        if OS == "Windows":
            command = f'tasklist /FI "PID eq {pid}" /FO CSV'
            result = run_command(command).split("\n")
            if len(result) > 1:
                return result[1].split('","')[0].replace('"', '')  # プロセス名を取得
        elif OS in ["Darwin", "Linux"]:
            command = f"ps -p {pid} -o command="
            return run_command(command).strip()
        else:
            raise Exception(f"Unsupported OS: {OS}")
    except Exception as e:
        return f"Error: {e}"