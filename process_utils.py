import streamlit as st
import pandas as pd

from log_util import logger
from config import OS, APPS
from os_utils import get_process_details

# ユニークな要素をカンマ区切りでまとめる関数
def summarize_unique_values(df) -> pd.DataFrame:
    merged_data = {}
    for col in df.columns:
        unique_values = set(df[col])  # ユニークな値を取得
        unique_values.discard(None)  # None（欠損値）は除外
        merged_data[col] = ", ".join(unique_values)  # カンマ区切りで結合
    return pd.DataFrame([merged_data])  # 1行のDataFrameとして返す

def extract_app_name(process_output: str) -> str:
    """
    プロセスの詳細情報からアプリ名を抽出
    """
    logger.debug('Process_output: ' + process_output)
    
    # Google Chrome
    if "Chrome" in process_output:
        return "Chrome"
    # Safari
    if "Safari" in process_output:
        return "Safari"
    # MS Edge
    if "Edge" in process_output:
        return "Edge"
    # Streamlit アプリ
    if any(substring in process_output for substring in ["streamlit run", 'streamlit.exe" run']):
        for app, info in APPS.items():
            if info["path"] in process_output:
                return app
        return "Streamlit App"  # どのアプリにも一致しない場合
    if "python" in process_output:
        return "python"

    return "Unknown"

def add_extracted_app_name(df):
    """DataFrame にアプリ名情報を追加"""
    if ("PID" not in df.columns) or (df["PID"].empty):
        return df  # PID カラムがない場合はそのまま返す

    pids = df["PID"].iloc[0].split(", ")  # PID をリスト化
    app_names = [extract_app_name(get_process_details(pid.strip())) for pid in pids if pid.strip().isdigit()]

    df["APP_NAME"] = ", ".join(set(app_names)) if app_names else None
    return df
