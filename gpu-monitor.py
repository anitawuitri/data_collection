#!/usr/bin/env python3
"""AMD GPU 監控系統控制台入口點

這是重構版本的主要入口點，提供現代化的 CLI 介面。
"""

import sys
import os
from pathlib import Path

# 設定專案根目錄
project_root = Path(__file__).parent.absolute()
os.chdir(project_root)

# 檢查是否有安裝依賴
try:
    import click
    import pandas
    import aiohttp
except ImportError as e:
    print(f"❌ 缺少依賴套件: {e}")
    print("請先安裝依賴套件:")
    print("  pip install -r requirements.txt")
    print("或使用 Poetry:")
    print("  poetry install")
    sys.exit(1)

try:
    # 使用 python -m src 執行
    if __name__ == '__main__':
        os.system("python3 -m src")
        
except Exception as e:
    print(f"❌ 執行錯誤: {e}")
    sys.exit(1)