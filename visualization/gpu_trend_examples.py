#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPU 使用率趨勢視覺化範例

展示如何使用新建立的 GPU 趨勢分析工具
"""

# 導入我們建立的模組 (需要在正確的路徑下執行)
import sys
import os

try:
    from advanced_gpu_trend_analyzer import GPUUsageTrendAnalyzer
    from quick_gpu_trend_plots import (
        quick_nodes_trend, 
        quick_single_node_gpus, 
        quick_gpu_across_nodes,
        generate_all_quick_plots,
        get_available_dates
    )
except ImportError as e:
    print(f"無法導入模組: {e}")
    print("請確保在 visualization 目錄下執行此腳本")
    sys.exit(1)

def example_quick_plots():
    """
    快速繪圖範例 - 最簡單的使用方式
    """
    print("=== 快速繪圖範例 ===")
    
    # 獲取可用日期
    dates = get_available_dates()
    if not dates:
        print("未找到數據檔案")
        return
        
    start_date = dates[0]
    end_date = dates[-1]
    print(f"使用日期範圍: {start_date} 至 {end_date}")
    
    # 方法 1: 一次生成所有常用圖表
    print("\n方法 1: 一次生成所有常用圖表")
    generate_all_quick_plots(start_date, end_date)
    
    # 方法 2: 分別生成特定圖表
    print("\n方法 2: 生成特定圖表")
    
    # 節點對比圖
    quick_nodes_trend(start_date, end_date)
    
    # 單一節點所有 GPU
    quick_single_node_gpus('colab-gpu1', start_date, end_date)
    
    # 特定 GPU 跨節點對比
    quick_gpu_across_nodes(1, start_date, end_date)

def example_advanced_analysis():
    """
    進階分析範例 - 更多客製化選項
    """
    print("\n=== 進階分析範例 ===")
    
    # 初始化分析器
    analyzer = GPUUsageTrendAnalyzer()
    
    # 獲取可用日期
    dates = analyzer.get_available_dates()
    if not dates:
        print("未找到數據檔案")
        return
        
    start_date = dates[0]
    end_date = dates[-1]
    print(f"使用日期範圍: {start_date} 至 {end_date}")
    
    # 1. 節點對比趨勢
    print("\n1. 繪製節點對比趨勢...")
    analyzer.plot_nodes_comparison_trend(start_date, end_date)
    
    # 2. 單一節點所有 GPU 趨勢
    print("\n2. 繪製 colab-gpu1 所有 GPU 趨勢...")
    analyzer.plot_single_node_all_gpus('colab-gpu1', start_date, end_date)
    
    # 3. 特定 GPU 跨節點對比
    print("\n3. 繪製 GPU 1 跨節點對比...")
    analyzer.plot_specific_gpu_across_nodes(1, start_date, end_date)
    
    # 4. 熱力圖
    print("\n4. 繪製熱力圖...")
    analyzer.plot_heatmap(start_date, end_date)
    
    # 5. 詳細時間序列（如果有單日數據）
    if len(dates) > 0:
        print(f"\n5. 繪製 {dates[0]} 的詳細時間序列...")
        analyzer.plot_detailed_timeline('colab-gpu1', 1, dates[0])
    
    # 6. 生成摘要報告
    print("\n6. 生成摘要報告...")
    analyzer.generate_summary_report(start_date, end_date)

def example_custom_date_range():
    """
    自訂日期範圍分析範例
    """
    print("\n=== 自訂日期範圍分析範例 ===")
    
    # 指定特定的日期範圍
    start_date = "2025-05-24"
    end_date = "2025-05-26"
    
    print(f"分析指定期間: {start_date} 至 {end_date}")
    
    # 使用快速繪圖
    try:
        quick_nodes_trend(start_date, end_date)
        print("節點對比圖完成")
        
        quick_single_node_gpus('colab-gpu2', start_date, end_date)
        print("colab-gpu2 所有 GPU 趨勢圖完成")
        
        quick_gpu_across_nodes(9, start_date, end_date)
        print("GPU 9 跨節點對比圖完成")
        
    except (FileNotFoundError, ValueError) as e:
        print(f"繪圖過程中發生錯誤: {e}")

def example_individual_functions():
    """
    個別功能展示範例
    """
    print("\n=== 個別功能展示 ===")
    
    # 檢查可用數據
    dates = get_available_dates()
    print(f"可用日期: {dates}")
    
    if not dates:
        print("沒有可用的數據檔案")
        return
    
    # 分析器初始化
    analyzer = GPUUsageTrendAnalyzer()
    
    # 載入並顯示數據範例
    sample_date = dates[0]
    print(f"\n載入 {sample_date} 的數據範例:")
    
    # 載入每日平均數據
    daily_data = analyzer.load_daily_average_data('colab-gpu1', sample_date)
    if daily_data is not None:
        print("每日平均數據:")
        print(daily_data.head())
    
    # 載入詳細數據
    detailed_data = analyzer.load_gpu_detailed_data('colab-gpu1', 1, sample_date)
    if detailed_data is not None:
        print("\nGPU 1 詳細數據 (前5筆):")
        print(detailed_data.head())
        print(f"總計 {len(detailed_data)} 筆數據點")

if __name__ == '__main__':
    """
    執行所有範例
    """
    print("GPU 使用率趨勢視覺化工具 - 使用範例")
    print("=" * 60)
    
    # 執行快速繪圖範例
    example_quick_plots()
    
    # 執行進階分析範例
    example_advanced_analysis()
    
    # 執行自訂日期範圍範例
    example_custom_date_range()
    
    # 執行個別功能展示
    example_individual_functions()
    
    print("\n" + "=" * 60)
    print("所有範例執行完成！")
    print("生成的圖表已保存在 './plots' 目錄中")
    print("=" * 60)
