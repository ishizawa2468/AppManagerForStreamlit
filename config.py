"""
設定情報の記載
"""
import platform

# OSの取得
OS = platform.system()

# 起動できるアプリ情報
"""
NOTE: jsonの構造 = {
  "アプリ名": {
      "path": "そのアプリの最初のページファイルまでのpath",
      "dir": "そのアプリでrootとなるフォルダで、そのアプリでのimportの起点"
  },
  "アプリ名2": { ... },
  ...
}
"""
APPS = {
    "HDFViewer": {
        "path": "../HDFViewer/home.py",
        "dir": "../HDFViewer",
    },
    "PlanckThermoEmulator": {
        "path": "../PlanckThermoEmulator/home.py",
        "dir": "../PlanckThermoEmulator"
    },
    "RadiationSpectraRotator": {
        "path": "../RadiationSpectraRotator/home.py",
        "dir": "../RadiationSpectraRotator"
    },
    "XRDSpotAnalyzer": {
        "path": "../XRDSpotAnalyzer/home.py",
        "dir": "../XRDSpotAnalyzer"
    },
    "AppManager": {
        "path": "main.py",
        "dir": "."
    },
}

# 使用する(管理する)PORT番号を設定
BASE_PORT = 8500  # App Manager用
# 外部アプリ用
EXT_PORT_FROM = 8501
EXT_PORT_TO = 8510 # NOTE: 可変だが、外部接続を考える場合はポートの開放が必要になる

ALL_PORT_RANGE = list(
    range(BASE_PORT, EXT_PORT_TO + 1)
)
# managerである8500を除いた、他アプリで使用可能なポート範囲 (8501 - 8510)
SELECTABLE_PORT_RANGE = list(
    range(EXT_PORT_FROM, EXT_PORT_TO + 1)
)
