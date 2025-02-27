"""
OSごとに異なる処理
"""

import platform
import subprocess

def get_os():
    """現在のOSを取得"""
    return platform.system()

def run_command(command, cwd=None):
    """OSごとのシェルコマンドを実行"""
    try:
        if get_os() == "Windows":
            result = subprocess.run(command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            result = subprocess.run(command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, executable="/bin/bash")
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"
