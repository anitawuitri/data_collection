#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試 quick 命令的 show_users 參數功能
驗證是否能正確控制使用者資訊顯示
"""

import sys
import os

# 添加路徑
sys.path.append('./visualization')

from quick_gpu_trend_plots import generate_all_quick_plots

def test_quick_show_users_parameter():
    """測試 quick 命令的 show_users 參數"""
    
    start_date = "2025-08-11"
    end_date = "2025-08-17"
    
    print("🧪 測試 quick 命令的 show_users 參數功能")
    print("=" * 50)
    
    # 測試 1: show_users=True (預設)
    print("\n📊 測試 1: 生成包含使用者資訊的所有快速圖表...")
    try:
        result1 = generate_all_quick_plots(
            start_date, end_date, 
            data_dir="./data", 
            plots_dir="./plots", 
            show_users=True
        )
        if result1:
            print(f"✅ 成功生成 {len(result1)} 個包含使用者資訊的圖表")
            # 檢查是否有檔名包含 _with_users
            with_users_count = sum(1 for path in result1 if "_with_users" in str(path))
            print(f"✅ 其中 {with_users_count} 個檔案包含 '_with_users' 後綴")
        else:
            print("❌ 生成失敗")
    except Exception as e:
        print(f"❌ 測試 1 失敗: {e}")
    
    # 測試 2: show_users=False
    print("\n📊 測試 2: 生成不包含使用者資訊的所有快速圖表...")
    try:
        result2 = generate_all_quick_plots(
            start_date, end_date, 
            data_dir="./data", 
            plots_dir="./plots", 
            show_users=False
        )
        if result2:
            print(f"✅ 成功生成 {len(result2)} 個不包含使用者資訊的圖表")
            # 檢查是否有檔名包含 _without_users
            without_users_count = sum(1 for path in result2 if "_without_users" in str(path))
            print(f"✅ 其中 {without_users_count} 個檔案包含 '_without_users' 後綴")
        else:
            print("❌ 生成失敗")
    except Exception as e:
        print(f"❌ 測試 2 失敗: {e}")
    
    print("\n🔍 比較生成的圖表檔案:")
    plots_dir = "./plots"
    if os.path.exists(plots_dir):
        # 查找所有相關檔案
        all_files = [f for f in os.listdir(plots_dir) if start_date in f and end_date in f]
        
        # 分類檔案
        with_users_files = [f for f in all_files if "_with_users" in f]
        without_users_files = [f for f in all_files if "_without_users" in f]
        other_files = [f for f in all_files if "_with_users" not in f and "_without_users" not in f]
        
        print(f"\n📄 包含使用者資訊的檔案 ({len(with_users_files)} 個):")
        for file in sorted(with_users_files):
            file_path = os.path.join(plots_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"  ✅ {file} ({file_size} bytes)")
        
        print(f"\n📄 不包含使用者資訊的檔案 ({len(without_users_files)} 個):")
        for file in sorted(without_users_files):
            file_path = os.path.join(plots_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"  ❌ {file} ({file_size} bytes)")
        
        if other_files:
            print(f"\n📄 其他相關檔案 ({len(other_files)} 個):")
            for file in sorted(other_files):
                file_path = os.path.join(plots_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"  📊 {file} ({file_size} bytes)")
    
    print("\n✅ quick 命令 show_users 參數測試完成！")
    print("💡 提示: 請手動檢查生成的圖表是否正確顯示/隱藏使用者資訊")

if __name__ == "__main__":
    test_quick_show_users_parameter()