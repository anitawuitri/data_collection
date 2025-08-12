#!/usr/bin/env python3
"""
測試台灣時區時間戳計算功能
"""

import sys
import os
sys.path.append('../python')

from datetime import datetime, timezone, timedelta
from daily_gpu_log import GPUDataCollector

def test_taiwan_timezone():
    """測試台灣時區時間戳計算"""
    print("=== 台灣時區時間戳計算測試 ===")
    
    # 創建收集器實例
    collector = GPUDataCollector()
    
    # 測試日期
    test_date = "2025-08-08"
    
    print(f"測試日期: {test_date}")
    print()
    
    # 計算時間戳
    start_ts, end_ts = collector.calculate_timestamps(test_date)
    
    print()
    print("驗證結果:")
    
    # 驗證開始時間
    taiwan_tz = timezone(timedelta(hours=8))
    start_dt = datetime.fromtimestamp(start_ts, tz=taiwan_tz)
    end_dt = datetime.fromtimestamp(end_ts, tz=taiwan_tz)
    
    print(f"開始時間戳 {start_ts} -> {start_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"結束時間戳 {end_ts} -> {end_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # 驗證 UTC 時間
    start_dt_utc = datetime.fromtimestamp(start_ts, tz=timezone.utc)
    end_dt_utc = datetime.fromtimestamp(end_ts, tz=timezone.utc)
    
    print(f"對應 UTC 開始時間: {start_dt_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"對應 UTC 結束時間: {end_dt_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # 驗證時間差
    time_diff = end_ts - start_ts
    hours_diff = time_diff / 3600
    
    print(f"時間範圍: {hours_diff:.2f} 小時")
    
    # 檢查是否正確
    expected_start = f"{test_date} 00:00:00"
    expected_end = f"{test_date} 23:59:59"
    
    if start_dt.strftime('%Y-%m-%d %H:%M:%S') == expected_start:
        print("✅ 開始時間正確")
    else:
        print(f"❌ 開始時間錯誤，期望: {expected_start}")
    
    if end_dt.strftime('%Y-%m-%d %H:%M:%S') == expected_end:
        print("✅ 結束時間正確")
    else:
        print(f"❌ 結束時間錯誤，期望: {expected_end}")
    
    if abs(hours_diff - 23.999) < 0.01:  # 23小時59分59秒
        print("✅ 時間範圍正確")
    else:
        print(f"❌ 時間範圍錯誤，期望約 23.999 小時")

if __name__ == "__main__":
    test_taiwan_timezone()
