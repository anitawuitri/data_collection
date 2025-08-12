#!/usr/bin/env python3
"""
測試 VRAM 熱力圖使用者資訊功能
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'visualization'))

from vram_monitor import VRAMMonitor

def test_vram_heatmap_users():
    """測試 VRAM 熱力圖使用者資訊功能"""
    
    print("=== VRAM 熱力圖使用者資訊測試 ===")
    
    # 創建 VRAMMonitor 實例
    monitor = VRAMMonitor(data_dir="./data", plots_dir="./plots")
    
    # 測試日期範圍（包含使用者資訊）
    test_dates = [
        ("2025-07-25", "2025-07-26"),
        ("2025-07-23", "2025-07-26"),
    ]
    
    for start_date, end_date in test_dates:
        print(f"\n測試日期範圍: {start_date} 至 {end_date}")
        
        # 測試帶使用者資訊的熱力圖
        print("生成包含使用者資訊的 VRAM 熱力圖...")
        result = monitor.plot_vram_heatmap(start_date, end_date, show_users=True)
        
        if result:
            print(f"✅ 成功生成: {result}")
            
            # 檢查檔案是否包含 _with_users 後綴
            if "_with_users" in result:
                print("✅ 檔案名稱正確包含 _with_users 後綴")
            else:
                print("❌ 檔案名稱缺少 _with_users 後綴")
        else:
            print("❌ 生成失敗")
        
        # 測試不帶使用者資訊的熱力圖
        print("生成不包含使用者資訊的 VRAM 熱力圖...")
        result = monitor.plot_vram_heatmap(start_date, end_date, show_users=False)
        
        if result:
            print(f"✅ 成功生成: {result}")
            
            # 檢查檔案是否不包含 _with_users 後綴
            if "_with_users" not in result:
                print("✅ 檔案名稱正確不包含 _with_users 後綴")
            else:
                print("❌ 檔案名稱錯誤包含 _with_users 後綴")
        else:
            print("❌ 生成失敗")

if __name__ == "__main__":
    test_vram_heatmap_users()
