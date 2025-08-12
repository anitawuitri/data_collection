#!/usr/bin/env python3
"""
測試 CSV 時間格式輸出 (台灣時區)
"""

import sys
import os
sys.path.append('../python')

from datetime import datetime, timezone, timedelta
from daily_gpu_log import GPUDataCollector

def test_csv_time_format():
    """測試 CSV 檔案中的時間格式"""
    print("=== CSV 時間格式測試（台灣時區）===")
    
    # 模擬一些 GPU 數據
    fake_gpu_data = {
        'data': [
            [1754582400, 10.5],  # 2025-08-08 00:00:00 台灣時間
            [1754586000, 20.3],  # 2025-08-08 01:00:00 台灣時間  
            [1754589600, 15.7],  # 2025-08-08 02:00:00 台灣時間
        ]
    }
    
    fake_vram_data = {
        'data': [
            [1754582400, 45.2],  # 2025-08-08 00:00:00 台灣時間
            [1754586000, 55.8],  # 2025-08-08 01:00:00 台灣時間
            [1754589600, 60.1],  # 2025-08-08 02:00:00 台灣時間
        ]
    }
    
    # 創建收集器實例
    collector = GPUDataCollector()
    
    # 測試檔案路徑
    test_dir = "/tmp/test_csv_timezone"
    os.makedirs(test_dir, exist_ok=True)
    
    from pathlib import Path
    tmp_csv = Path(f"{test_dir}/test_gpu.csv.tmp")
    final_csv = Path(f"{test_dir}/test_gpu.csv")
    
    print("生成測試 CSV 檔案...")
    collector.write_gpu_csv(fake_gpu_data, fake_vram_data, tmp_csv, final_csv)
    
    print("CSV 檔案內容:")
    with open(final_csv, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
    
    # 驗證時間格式
    lines = content.strip().split('\n')
    if len(lines) > 1:
        # 檢查第一行數據
        first_data_line = lines[1]  # 跳過標頭
        parts = first_data_line.split(',')
        
        if len(parts) >= 2:
            timestamp = int(parts[0])
            datetime_str = parts[1].strip('"')
            
            # 驗證時間戳對應的台灣時間
            taiwan_tz = timezone(timedelta(hours=8))
            expected_dt = datetime.fromtimestamp(timestamp, tz=taiwan_tz)
            expected_str = expected_dt.strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"\n時間戳驗證:")
            print(f"時間戳: {timestamp}")
            print(f"CSV 中的時間: {datetime_str}")
            print(f"期望的時間: {expected_str}")
            
            if datetime_str == expected_str:
                print("✅ CSV 時間格式正確（台灣時區）")
            else:
                print("❌ CSV 時間格式錯誤")
    
    # 清理測試檔案
    try:
        os.remove(final_csv)
        os.rmdir(test_dir)
    except:
        pass

if __name__ == "__main__":
    test_csv_time_format()
