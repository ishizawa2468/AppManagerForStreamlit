"""
設定情報の記載
"""

APPS = {
    "AppManager": {"path": "main.py", "dir": "."},
    "PlanckThermoEmulator": {"path": "../PlanckThermoEmulator/home.py", "dir": "../PlanckThermoEmulator"},
    "RadiationSpectraRotator": {"path": "../RadiationSpectraRotator/home.py", "dir": "../RadiationSpectraRotator"},
    "XRDSpotAnalyzer": {"path": "../XRDSpotAnalyzer/home.py", "dir": "../XRDSpotAnalyzer"},
}

BASE_PORT = 8500  # App Manager用
PORT_RANGE = list(range(BASE_PORT, BASE_PORT + 11))  # 8500〜8510
SELECTABLE_PORT_RANGE = list(range(BASE_PORT + 1, BASE_PORT + 11))  # managerである8500を除く
