#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VRAM 數據抓取驗證腳本
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加路徑
sys.path.append('visualization')
from quick_gpu_trend_plots import load_gpu_data_with_users

def check_vram_data():
    """檢查 VRAM 數據抓取情況"""
    print("🔍 檢查 VRAM 數據抓取情況...")
    
    # 測試日期範圍
    start_date = '2025-07-16'
    end_date = '2025-08-04'
    
    # 生成日期列表
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)
    
    nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
    
    # 統計數據
    total_files = 0
    valid_files = 0
    vram_data_summary = {}
    
    for node in nodes:
        node_vram_data = []
        print(f"\n📊 檢查節點: {node}")
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            avg_file = os.path.join('data', node, date_str, f"average_{date_str}.csv")
            
            total_files += 1
            
            if os.path.exists(avg_file):
                try:
                    df = load_gpu_data_with_users(avg_file)
                    if df is not None:
                        # 檢查列名
                        print(f"  日期 {date_str}: 列名 = {list(df.columns)}")
                        
                        # 檢查 VRAM 數據
                        if '平均VRAM使用率(%)' in df.columns:
                            df = df.rename(columns={'平均VRAM使用率(%)': 'vram'})
                        
                        if 'vram' in df.columns:
                            # 過濾非平均行
                            gpu_data = df[~df['gpu'].str.contains('全部平均', na=False)]
                            
                            if not gpu_data.empty:
                                vram_values = pd.to_numeric(gpu_data['vram'], errors='coerce')
                                vram_values = vram_values.dropna()
                                
                                if len(vram_values) > 0:
                                    daily_avg = vram_values.mean()
                                    node_vram_data.append(daily_avg)
                                    print(f"    VRAM 平均: {daily_avg:.3f}%")
                                    print(f"    VRAM 範圍: {vram_values.min():.3f}% - {vram_values.max():.3f}%")
                                    
                                    # 顯示各 GPU 的 VRAM 使用率
                                    for _, row in gpu_data.iterrows():
                                        gpu = row.get('gpu', 'N/A')
                                        vram = row.get('vram', 'N/A')
                                        user = row.get('user', 'N/A')
                                        print(f"      {gpu}: {vram}% (使用者: {user})")
                                    
                                    valid_files += 1
                                else:
                                    print(f"    無有效 VRAM 數據")
                        else:
                            print(f"    缺少 VRAM 列")
                        
                        # 只顯示前3天的詳細數據
                        if len(node_vram_data) >= 3:
                            break
                            
                except Exception as e:
                    print(f"  錯誤讀取 {avg_file}: {e}")
            else:
                print(f"  檔案不存在: {avg_file}")
        
        if node_vram_data:
            vram_data_summary[node] = {
                'avg': np.mean(node_vram_data),
                'min': np.min(node_vram_data),
                'max': np.max(node_vram_data),
                'count': len(node_vram_data)
            }
    
    print(f"\n📈 數據抓取統計:")
    print(f"總檔案數: {total_files}")
    print(f"有效檔案數: {valid_files}")
    print(f"成功率: {valid_files/total_files*100:.1f}%")
    
    print(f"\n📊 各節點 VRAM 使用率總結:")
    for node, stats in vram_data_summary.items():
        print(f"{node}: 平均 {stats['avg']:.3f}%, 範圍 {stats['min']:.3f}%-{stats['max']:.3f}% ({stats['count']} 天)")
    
    return vram_data_summary

def test_vram_stacked_generation():
    """測試 VRAM 堆疊圖生成"""
    print("\n🎨 測試 VRAM 堆疊圖生成...")
    
    try:
        from quick_gpu_trend_plots import quick_nodes_vram_stacked_utilization
        
        result = quick_nodes_vram_stacked_utilization(
            start_date='2025-07-16', 
            end_date='2025-08-04',
            data_dir='data',
            plots_dir='plots',
            show_users=True
        )
        
        if result and os.path.exists(result):
            file_size = os.path.getsize(result) / 1024  # KB
            print(f"✅ 圖表生成成功: {result}")
            print(f"✅ 檔案大小: {file_size:.1f} KB")
            return True
        else:
            print("❌ 圖表生成失敗")
            return False
    except Exception as e:
        print(f"❌ 生成錯誤: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 VRAM 數據抓取驗證")
    print("=" * 60)
    
    # 檢查數據抓取
    vram_summary = check_vram_data()
    
    # 測試圖表生成
    generation_result = test_vram_stacked_generation()
    
    print("\n" + "=" * 60)
    print("📋 驗證結果")
    print("=" * 60)
    
    if vram_summary:
        print("✅ VRAM 數據抓取正常")
        total_avg = np.mean([stats['avg'] for stats in vram_summary.values()])
        print(f"✅ 整體平均 VRAM 使用率: {total_avg:.3f}%")
    else:
        print("❌ VRAM 數據抓取異常")
    
    if generation_result:
        print("✅ 圖表生成正常")
    else:
        print("❌ 圖表生成異常")

if __name__ == "__main__":
    main()