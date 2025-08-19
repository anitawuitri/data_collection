#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試 VRAM 堆疊圖的 show_users 參數功能
驗證是否能正確控制使用者資訊顯示
"""

import sys
import os

# 添加路徑
sys.path.append('./visualization')

from quick_gpu_trend_plots import quick_nodes_vram_stacked_utilization

def test_show_users_parameter():
    """測試 show_users 參數"""
    
    start_date = "2025-07-16"
    end_date = "2025-08-04"
    
    print("🧪 測試 VRAM 堆疊圖的 show_users 參數功能")
    print("=" * 50)
    
    # 測試 1: show_users=True (預設)
    print("\n📊 測試 1: 生成包含使用者資訊的 VRAM 堆疊圖...")
    try:
        result1 = quick_nodes_vram_stacked_utilization(
            start_date, end_date, 
            data_dir="./data", 
            plots_dir="./plots", 
            show_users=True
        )
        if result1:
            print(f"✅ 成功生成包含使用者資訊的圖表: {result1}")
            # 檢查檔名是否包含 _with_users
            if "_with_users" in result1:
                print("✅ 檔名正確包含 '_with_users' 後綴")
            else:
                print("❌ 檔名未包含預期的 '_with_users' 後綴")
        else:
            print("❌ 生成失敗")
    except Exception as e:
        print(f"❌ 測試 1 失敗: {e}")
    
    # 測試 2: show_users=False
    print("\n📊 測試 2: 生成不包含使用者資訊的 VRAM 堆疊圖...")
    try:
        result2 = quick_nodes_vram_stacked_utilization(
            start_date, end_date, 
            data_dir="./data", 
            plots_dir="./plots", 
            show_users=False
        )
        if result2:
            print(f"✅ 成功生成不包含使用者資訊的圖表: {result2}")
            # 檢查檔名是否包含 _without_users
            if "_without_users" in result2:
                print("✅ 檔名正確包含 '_without_users' 後綴")
            else:
                print("❌ 檔名未包含預期的 '_without_users' 後綴")
        else:
            print("❌ 生成失敗")
    except Exception as e:
        print(f"❌ 測試 2 失敗: {e}")
    
    print("\n🔍 比較兩個生成的圖表檔案:")
    plots_dir = "./plots"
    if os.path.exists(plots_dir):
        vram_files = [f for f in os.listdir(plots_dir) if "vram_stacked_utilization" in f and start_date in f and end_date in f]
        for file in sorted(vram_files):
            file_path = os.path.join(plots_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"  📄 {file} ({file_size} bytes)")
    
    print("\n✅ show_users 參數測試完成！")
    print("💡 提示: 請手動檢查生成的圖表是否正確顯示/隱藏使用者資訊")

if __name__ == "__main__":
    test_show_users_parameter()