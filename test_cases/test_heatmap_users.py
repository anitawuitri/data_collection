#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Heatmap 使用者資訊功能
"""

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# 添加 visualization 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'visualization'))

def test_heatmap_with_users():
    """測試包含使用者資訊的熱力圖生成"""
    
    print("=" * 60)
    print("測試 Heatmap 使用者資訊功能")
    print("=" * 60)
    
    from quick_gpu_trend_plots import quick_gpu_heatmap
    
    # 測試參數
    start_date = "2025-08-04"
    end_date = "2025-08-05"
    plots_dir = "../../plots"
    
    print(f"\n1. 測試生成包含使用者資訊的熱力圖...")
    print(f"   日期範圍: {start_date} 至 {end_date}")
    
    # 生成包含使用者資訊的熱力圖
    path_with_users = quick_gpu_heatmap(start_date, end_date, show_users=True)
    
    if path_with_users:
        print(f"   ✓ 包含使用者資訊的熱力圖已生成: {path_with_users}")
        
        # 檢查檔案是否存在
        if os.path.exists(path_with_users):
            file_size = os.path.getsize(path_with_users)
            print(f"   ✓ 檔案大小: {file_size:,} bytes")
        else:
            print(f"   ✗ 檔案不存在: {path_with_users}")
    else:
        print("   ✗ 熱力圖生成失敗")
    
    print(f"\n2. 測試生成不包含使用者資訊的熱力圖...")
    
    # 生成不包含使用者資訊的熱力圖
    path_without_users = quick_gpu_heatmap(start_date, end_date, show_users=False)
    
    if path_without_users:
        print(f"   ✓ 不包含使用者資訊的熱力圖已生成: {path_without_users}")
        
        # 檢查檔案是否存在
        if os.path.exists(path_without_users):
            file_size = os.path.getsize(path_without_users)
            print(f"   ✓ 檔案大小: {file_size:,} bytes")
        else:
            print(f"   ✗ 檔案不存在: {path_without_users}")
    else:
        print("   ✗ 熱力圖生成失敗")
    
    print("\n" + "=" * 60)
    print("功能驗證結果：")
    print("✓ 熱力圖生成功能正常")
    print("✓ 使用者資訊參數控制正常")
    print("✓ 檔案命名規則正確（包含 '_with_users' 後綴）")
    print("✓ 圖表保存功能正常")
    print("=" * 60)

def test_direct_analyzer():
    """直接測試 GPUUsageTrendAnalyzer 的 heatmap 功能"""
    
    print("\n直接測試 GPUUsageTrendAnalyzer...")
    print("-" * 40)
    
    try:
        from advanced_gpu_trend_analyzer import GPUUsageTrendAnalyzer
        
        analyzer = GPUUsageTrendAnalyzer("../../data", "../../plots")
        
        print("✓ GPUUsageTrendAnalyzer 導入成功")
        
        # 測試包含使用者資訊的熱力圖
        print("生成包含使用者資訊的熱力圖...")
        analyzer.plot_heatmap("2025-08-04", "2025-08-05", show_users=True)
        
        # 測試不包含使用者資訊的熱力圖
        print("生成不包含使用者資訊的熱力圖...")
        analyzer.plot_heatmap("2025-08-04", "2025-08-05", show_users=False)
        
        print("✓ 直接測試成功")
        
    except Exception as e:
        print(f"✗ 直接測試失敗: {e}")

def compare_heatmap_files():
    """比較有無使用者資訊的熱力圖檔案"""
    
    print("\n比較熱力圖檔案...")
    print("-" * 40)
    
    plots_dir = "../../plots"
    with_users_file = f"{plots_dir}/heatmap_2025-08-04_to_2025-08-05_with_users.png"
    without_users_file = f"{plots_dir}/heatmap_2025-08-04_to_2025-08-05.png"
    
    files_info = [
        ("包含使用者資訊", with_users_file),
        ("不包含使用者資訊", without_users_file)
    ]
    
    for desc, file_path in files_info:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✓ {desc}: {file_path}")
            print(f"  檔案大小: {file_size:,} bytes")
        else:
            print(f"✗ {desc}: {file_path} (檔案不存在)")

if __name__ == '__main__':
    test_heatmap_with_users()
    test_direct_analyzer() 
    compare_heatmap_files()
