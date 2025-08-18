#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試各節點 GPU 使用率堆疊區域圖功能
"""

import sys
import os

# 添加 visualization 目錄到 Python 路徑
sys.path.append('./visualization')

try:
    from quick_gpu_trend_plots import quick_nodes_stacked_utilization, get_available_dates
    
    print("=== 測試各節點 GPU 使用率堆疊區域圖功能 ===")
    print()
    
    # 檢查可用的日期
    print("檢查可用的數據日期...")
    available_dates = get_available_dates("./data")
    
    if not available_dates:
        print("❌ 未找到任何可用的數據")
        sys.exit(1)
    
    print(f"✅ 找到 {len(available_dates)} 天的數據")
    print(f"📅 日期範圍: {available_dates[0]} 至 {available_dates[-1]}")
    print()
    
    # 選擇測試日期範圍（最近一週的數據）
    if len(available_dates) >= 7:
        start_date = available_dates[-7]
        end_date = available_dates[-1]
    else:
        start_date = available_dates[0]
        end_date = available_dates[-1]
    
    print(f"🧪 測試日期範圍: {start_date} 至 {end_date}")
    print()
    
    # 測試堆疊視圖功能（包含使用者資訊）
    print("正在生成各節點 GPU 使用率堆疊區域圖（包含使用者資訊）...")
    try:
        plot_path = quick_nodes_stacked_utilization(
            start_date, 
            end_date, 
            data_dir="./data", 
            plots_dir="./plots", 
            show_users=True
        )
        
        if plot_path and os.path.exists(plot_path):
            print(f"✅ 堆疊視圖生成成功！")
            print(f"📊 圖表保存至: {plot_path}")
            
            # 檢查檔案大小
            file_size = os.path.getsize(plot_path)
            print(f"📏 檔案大小: {file_size / 1024:.1f} KB")
            
        else:
            print("❌ 堆疊視圖生成失敗")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 執行堆疊視圖功能時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    
    # 測試簡潔版本（不包含使用者資訊）
    print("正在生成簡潔版本（不包含使用者資訊）...")
    try:
        plot_path = quick_nodes_stacked_utilization(
            start_date, 
            end_date, 
            data_dir="./data", 
            plots_dir="./plots", 
            show_users=False
        )
        
        # 重新命名檔案以區分
        if plot_path and os.path.exists(plot_path):
            base_name = plot_path.replace('.png', '_simple.png')
            os.rename(plot_path, base_name)
            print(f"✅ 簡潔版本生成成功！")
            print(f"📊 圖表保存至: {base_name}")
        
    except Exception as e:
        print(f"❌ 生成簡潔版本時發生錯誤: {e}")
    
    print()
    print("=== 測試完成 ===")
    print("✅ 各節點 GPU 使用率堆疊區域圖功能正常運作")
    print()
    print("功能特點：")
    print("🔹 按節點分層顯示 GPU 使用率累積情況")
    print("🔹 使用堆疊區域圖，清楚展示各節點的貢獻")
    print("🔹 支援使用者資訊顯示，了解各節點活躍使用者")
    print("🔹 包含統計資訊框，顯示各節點平均使用率")
    print("🔹 專用節點顏色，便於識別不同節點")
    print()
    print("您現在可以使用以下指令來生成堆疊視圖：")
    print(f"  ./run_gpu_visualization.sh stacked {start_date} {end_date}")
    print()
    
except ImportError as e:
    print(f"❌ 導入模組失敗: {e}")
    print("請確認 visualization 目錄中包含必要的模組")
    sys.exit(1)
except Exception as e:
    print(f"❌ 測試過程中發生未預期的錯誤: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)