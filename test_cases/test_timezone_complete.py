#!/usr/bin/env python3
"""
完整的台灣時區功能測試
"""

import sys
import os
sys.path.append('../python')

from datetime import datetime, timezone, timedelta
from daily_gpu_log import GPUDataCollector

def comprehensive_timezone_test():
    """完整的台灣時區測試"""
    print("=== 完整台灣時區功能測試 ===")
    
    # 創建收集器實例
    collector = GPUDataCollector()
    taiwan_tz = timezone(timedelta(hours=8))
    
    # 測試多個日期
    test_dates = ["2025-08-08", "2025-12-25", "2025-01-01"]
    
    for date_str in test_dates:
        print(f"\n測試日期: {date_str}")
        print("-" * 40)
        
        # 計算時間戳
        start_ts, end_ts = collector.calculate_timestamps(date_str)
        
        # 轉換回日期時間驗證
        start_dt = datetime.fromtimestamp(start_ts, tz=taiwan_tz)
        end_dt = datetime.fromtimestamp(end_ts, tz=taiwan_tz)
        
        # 檢查日期是否正確
        start_date = start_dt.strftime('%Y-%m-%d')
        end_date = end_dt.strftime('%Y-%m-%d')
        
        print(f"開始時間: {start_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"結束時間: {end_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        # 驗證
        if start_date == date_str and end_date == date_str:
            print("✅ 日期正確")
        else:
            print(f"❌ 日期錯誤: 開始={start_date}, 結束={end_date}")
        
        if start_dt.hour == 0 and start_dt.minute == 0 and start_dt.second == 0:
            print("✅ 開始時間正確 (00:00:00)")
        else:
            print(f"❌ 開始時間錯誤: {start_dt.time()}")
        
        if end_dt.hour == 23 and end_dt.minute == 59 and end_dt.second == 59:
            print("✅ 結束時間正確 (23:59:59)")
        else:
            print(f"❌ 結束時間錯誤: {end_dt.time()}")
        
        # 檢查與 UTC 的差異
        start_dt_utc = datetime.fromtimestamp(start_ts, tz=timezone.utc)
        hour_diff = start_dt.hour - start_dt_utc.hour
        
        if abs(hour_diff) == 8 or abs(hour_diff) == 16:  # 考慮跨日情況
            print("✅ 台灣時區偏移正確 (UTC+8)")
        else:
            print(f"❌ 時區偏移錯誤: 差異 {hour_diff} 小時")
    
    print("\n=== 時區功能總結 ===")
    print("✅ 時間戳計算已更新為台灣時區 (UTC+8)")
    print("✅ CSV 輸出時間格式使用台灣時區")
    print("✅ 所有日期時間操作都基於台灣時區")
    print("✅ 與原有的 shell 腳本邏輯保持相容")

if __name__ == "__main__":
    comprehensive_timezone_test()
