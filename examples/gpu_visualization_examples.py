#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPU 使用率視覺化範例腳本

此腳本展示如何使用 gpu_trend_visualizer.py 來生成各種類型的 GPU 使用率趨勢圖
"""

import os
import sys
from datetime import datetime, timedelta

# 添加腳本目錄到路徑
sys.path.append('./scripts')

try:
    from gpu_trend_visualizer import GPUTrendVisualizer
    print("成功載入 GPU 趨勢視覺化器")
except ImportError as e:
    print(f"載入模組時發生錯誤: {e}")
    print("請確保已安裝所需套件: pip install -r requirements.txt")
    sys.exit(1)

def generate_sample_plots():
    """
    生成範例圖表
    """
    # 設定參數
    data_dir = "./data"
    output_dir = "./plots"
    
    # 創建視覺化器
    visualizer = GPUTrendVisualizer(data_dir)
    
    # 獲取可用日期
    available_dates = visualizer.get_available_dates()
    if not available_dates:
        print("未找到任何數據，請檢查數據目錄")
        return
    
    print(f"找到可用日期: {available_dates}")
    
    # 使用最近的日期範圍
    if len(available_dates) >= 2:
        start_date = available_dates[0]
        end_date = available_dates[-1]
    else:
        start_date = end_date = available_dates[0]
    
    print(f"使用日期範圍: {start_date} 至 {end_date}")
    
    # 創建輸出目錄
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 生成節點對比圖
    print("\n1. 生成節點對比圖...")
    try:
        save_path = os.path.join(output_dir, f'nodes_comparison_{start_date}_to_{end_date}.png')
        visualizer.plot_node_comparison(start_date, end_date, save_path)
    except Exception as e:
        print(f"生成節點對比圖時發生錯誤: {e}")
    
    # 2. 生成熱力圖
    print("\n2. 生成熱力圖...")
    try:
        save_path = os.path.join(output_dir, f'heatmap_{start_date}_to_{end_date}.png')
        visualizer.plot_heatmap(start_date, end_date, save_path)
    except Exception as e:
        print(f"生成熱力圖時發生錯誤: {e}")
    
    # 3. 生成綜合儀表板
    print("\n3. 生成綜合儀表板...")
    try:
        save_path = os.path.join(output_dir, f'dashboard_{start_date}_to_{end_date}.png')
        visualizer.create_summary_dashboard(start_date, end_date, save_path)
    except Exception as e:
        print(f"生成儀表板時發生錯誤: {e}")
    
    # 4. 生成單個 GPU 的趨勢圖（如果有數據）
    print("\n4. 生成單個 GPU 趨勢圖...")
    try:
        # 檢查第一個節點的第一個 GPU
        node = 'colab-gpu1'
        gpu_id = 1
        save_path = os.path.join(output_dir, f'{node}_gpu{gpu_id}_{start_date}_to_{end_date}.png')
        visualizer.plot_single_gpu_trend(node, gpu_id, start_date, end_date, save_path)
    except Exception as e:
        print(f"生成單個 GPU 趨勢圖時發生錯誤: {e}")
    
    # 5. 生成多 GPU 對比圖（使用最後一天的數據）
    print("\n5. 生成多 GPU 對比圖...")
    try:
        node = 'colab-gpu1'
        save_path = os.path.join(output_dir, f'{node}_multi_gpu_{end_date}.png')
        visualizer.plot_multi_gpu_comparison(node, end_date, save_path)
    except Exception as e:
        print(f"生成多 GPU 對比圖時發生錯誤: {e}")
    
    print(f"\n所有圖表已生成並保存到 {output_dir} 目錄")

def show_usage_examples():
    """
    顯示使用範例
    """
    print("=== GPU 使用率視覺化工具使用範例 ===\n")
    
    print("1. 使用命令行工具生成所有類型的圖表:")
    print("   python scripts/gpu_trend_visualizer.py --start-date 2025-05-23 --end-date 2025-05-26 --plot-type all\n")
    
    print("2. 只生成節點對比圖:")
    print("   python scripts/gpu_trend_visualizer.py --start-date 2025-05-23 --end-date 2025-05-26 --plot-type nodes\n")
    
    print("3. 生成特定節點的單個 GPU 趨勢圖:")
    print("   python scripts/gpu_trend_visualizer.py --start-date 2025-05-23 --end-date 2025-05-26 --plot-type single --node colab-gpu1 --gpu-id 1\n")
    
    print("4. 生成特定節點的多 GPU 對比圖:")
    print("   python scripts/gpu_trend_visualizer.py --start-date 2025-05-23 --end-date 2025-05-26 --plot-type multi --node colab-gpu1\n")
    
    print("5. 只生成熱力圖:")
    print("   python scripts/gpu_trend_visualizer.py --start-date 2025-05-23 --end-date 2025-05-26 --plot-type heatmap\n")
    
    print("6. 只生成儀表板:")
    print("   python scripts/gpu_trend_visualizer.py --start-date 2025-05-23 --end-date 2025-05-26 --plot-type dashboard\n")
    
    print("7. 指定輸出目錄:")
    print("   python scripts/gpu_trend_visualizer.py --start-date 2025-05-23 --end-date 2025-05-26 --output-dir ./my_plots\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='GPU 視覺化範例腳本')
    parser.add_argument('--generate', action='store_true', help='生成範例圖表')
    parser.add_argument('--examples', action='store_true', help='顯示使用範例')
    
    args = parser.parse_args()
    
    if args.generate:
        generate_sample_plots()
    elif args.examples:
        show_usage_examples()
    else:
        print("請指定操作:")
        print("  --generate  : 生成範例圖表")
        print("  --examples  : 顯示使用範例")
        print("\n範例:")
        print("  python examples/gpu_visualization_examples.py --generate")
        print("  python examples/gpu_visualization_examples.py --examples")
