import pandas as pd
from config import APPS
from os_utils import get_process_details

def shape_to_dataframe(search_output: str) -> pd.DataFrame:
    # ヘッダー: 1次元のリスト
    header = search_output.split("\n")[0].split()
    # 要素: 2次元のリスト
    lines = list(map(
        lambda line: line.split(maxsplit=len(header)-1),
        search_output.split("\n")[1:]
    ))
    # dfにして返す
    return pd.DataFrame(
        lines,
        columns=header
    )

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
    # Google Chrome
    if "Google Chrome" in process_output:
        return "Google Chrome"
    # Safari
    if "Safari" in process_output:
        return "Safari"
    # Streamlit アプリ
    if "streamlit run" in process_output:
        for app, info in APPS.items():
            if info["path"] in process_output:
                return app
        return "Streamlit App"  # どのアプリにも一致しない場合

    return "Unknown"

def add_extracted_app_name(df):
    """DataFrame にアプリ名情報を追加"""
    if "PID" not in df.columns:
        return df  # PID カラムがない場合はそのまま返す

    pids = df["PID"].iloc[0].split(", ")  # PID をリスト化
    app_names = [extract_app_name(get_process_details(pid.strip())) for pid in pids if pid.strip().isdigit()]

    df["APP_NAME"] = ", ".join(set(app_names)) if app_names else "Unknown"
    return df
