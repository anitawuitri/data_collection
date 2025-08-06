#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 GPU 使用者資訊顯示功能
"""

import os
import sys

# 添加父目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'visualization'))

from quick_gpu_trend_plots import (
    load_gpu_data_with_users,
    get_user_info_for_node,
    quick_nodes_trend,
    quick_single_node_gpus,
    quick_gpu_across_nodes,
    quick_user_activity_summary
)

def test_user_info_functions():
    """測試使用者資訊相關功能"""
    
    print("=" * 60)
    print("測試 GPU 使用者資訊功能")
    print("=" * 60)
    
    # 1. 測試資料讀取功能
    print("\n1. 測試資料讀取功能...")
    test_file = "../../data/colab-gpu4/2025-08-04/average_2025-08-04.csv"
    df = load_gpu_data_with_users(test_file)
    if df is not None:
        print(f"✓ 成功讀取檔案: {test_file}")
        print(f"  欄位: {list(df.columns)}")
        print(f"  資料行數: {len(df)}")
        
        # 顯示使用者資訊
        if 'user' in df.columns:
            print("  使用者資訊:")
            for _, row in df.iterrows():
                gpu = row['gpu']
                user = row['user']
                usage = row['usage']
                if not gpu.startswith('全部平均'):
                    print(f"    {gpu}: {user} (使用率: {usage}%)")
    else:
        print(f"✗ 無法讀取檔案: {test_file}")
    
    # 2. 測試節點使用者資訊
    print("\n2. 測試節點使用者資訊...")
    user_info = get_user_info_for_node('colab-gpu4', '2025-08-04', '../../data')
    print(f"colab-gpu4 在 2025-08-04 的使用者資訊:")
    for gpu, user in user_info.items():
        print(f"  {gpu}: {user}")
    
    # 3. 測試單張圖表生成
    print("\n3. 測試包含使用者資訊的圖表生成...")
    
    # 節點對比圖（包含使用者資訊）
    print("  生成節點對比圖（包含使用者資訊）...")
    path = quick_nodes_trend('2025-08-04', '2025-08-05', '../../data', '../../plots', show_users=True)
    print(f"  ✓ 圖表已保存: {path}")
    
    # 單節點GPU圖（包含使用者資訊）
    print("  生成單節點 GPU 圖（包含使用者資訊）...")
    path = quick_single_node_gpus('colab-gpu4', '2025-08-04', '2025-08-05', '../../data', '../../plots', show_users=True)
    print(f"  ✓ 圖表已保存: {path}")
    
    # 跨節點GPU圖（包含使用者資訊）
    print("  生成跨節點 GPU 圖（包含使用者資訊）...")
    path = quick_gpu_across_nodes(0, '2025-08-04', '2025-08-05', '../../data', '../../plots', show_users=True)
    print(f"  ✓ 圖表已保存: {path}")
    
    # 使用者活動摘要
    print("  生成使用者活動摘要...")
    path = quick_user_activity_summary('2025-08-04', '2025-08-05', '../../data', '../../plots')
    if path:
        print(f"  ✓ 圖表已保存: {path}")
    else:
        print("  ✗ 使用者活動摘要生成失敗")
    
    print("\n=" * 60)
    print("測試完成！")
    print("=" * 60)

def test_comparison_with_without_users():
    """比較有無使用者資訊的圖表"""
    
    print("\n比較測試：有無使用者資訊的圖表")
    print("-" * 50)
    
    # 不包含使用者資訊的圖表
    print("生成不包含使用者資訊的圖表...")
    path1 = quick_nodes_trend('2025-08-04', '2025-08-05', '../../data', '../../plots', show_users=False)
    print(f"無使用者資訊: {path1}")
    
    # 包含使用者資訊的圖表
    print("生成包含使用者資訊的圖表...")
    path2 = quick_nodes_trend('2025-08-04', '2025-08-05', '../../data', '../../plots', show_users=True)
    print(f"有使用者資訊: {path2}")
    
    print("比較完成！請檢查圖表檔案的差異。")

if __name__ == '__main__':
    test_user_info_functions()
    test_comparison_with_without_users()
