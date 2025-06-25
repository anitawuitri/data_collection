#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速 GPU 使用率趨勢繪圖工具

提供簡單易用的函數來快速生成 GPU 使用率趨勢圖
專門針對 data 資料夾中的數據格式優化
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
import os
import glob

# 導入字體配置模組
from font_config import setup_chinese_font

# 設定中文字體
setup_chinese_font()

def quick_nodes_trend(start_date, end_date, data_dir="../data", plots_dir="../plots"):
    """
    快速繪製各節點 GPU 平均使用率趨勢對比
    
    Args:
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        
    Returns:
        str: 保存的圖片路徑
    """
    nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    # 創建輸出目錄
    os.makedirs(plots_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # 生成日期範圍
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    for i, node in enumerate(nodes):
        node_data = []
        node_dates = []
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            avg_file = os.path.join(data_dir, node, date_str, f"average_{date_str}.csv")
            
            if os.path.exists(avg_file):
                try:
                    df = pd.read_csv(avg_file, encoding='utf-8')
                    
                    # 處理不同的列名格式
                    if 'GPU卡號' in df.columns and '平均使用率(%)' in df.columns:
                        df = df.rename(columns={'GPU卡號': 'gpu', '平均使用率(%)': 'usage'})
                    elif len(df.columns) >= 2:
                        df.columns = ['gpu', 'usage'] + list(df.columns[2:])
                    
                    # 過濾掉 "全部平均" 行並計算平均值
                    gpu_data = df[~df['gpu'].str.contains('全部平均', na=False)]
                    avg_usage = pd.to_numeric(gpu_data['usage'], errors='coerce').mean()
                    
                    if not np.isnan(avg_usage):
                        node_data.append(avg_usage)
                        node_dates.append(date)
                        
                except Exception as e:
                    print(f"讀取 {avg_file} 時發生錯誤: {e}")
        
        if node_data:
            ax.plot(node_dates, node_data, 
                   label=node, 
                   marker='o', 
                   linewidth=2.5, 
                   markersize=6,
                   color=colors[i])
    
    # 設定圖表
    ax.set_title(f'各節點 GPU 平均使用率趨勢\n期間: {start_date} 至 {end_date}', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('平均 GPU 使用率 (%)', fontsize=12)
    
    # 格式化 x 軸
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # 設定 y 軸範圍為 0-100%
    ax.set_ylim(0, 100)
    
    # 添加圖例和網格（只有當有數據時才顯示圖例）
    if ax.get_lines():  # 檢查是否有繪製的線條
        ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    save_path = os.path.join(plots_dir, f'nodes_trend_{start_date}_to_{end_date}.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"節點趨勢圖已保存至: {save_path}")
    plt.close()
    
    return save_path

def quick_single_node_gpus(node, start_date, end_date, data_dir="../data", plots_dir="../plots"):
    """
    快速繪製單一節點所有 GPU 的使用率趨勢
    
    Args:
        node (str): 節點名稱 (如: colab-gpu1)
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        
    Returns:
        str: 保存的圖片路徑
    """
    gpu_ids = [1, 9, 17, 25, 33, 41, 49, 57]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    
    os.makedirs(plots_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # 生成日期範圍
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    for i, gpu_id in enumerate(gpu_ids):
        gpu_data = []
        gpu_dates = []
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            avg_file = os.path.join(data_dir, node, date_str, f"average_{date_str}.csv")
            
            if os.path.exists(avg_file):
                try:
                    df = pd.read_csv(avg_file, encoding='utf-8')
                    
                    # 處理列名
                    if 'GPU卡號' in df.columns and '平均使用率(%)' in df.columns:
                        df = df.rename(columns={'GPU卡號': 'gpu', '平均使用率(%)': 'usage'})
                    elif len(df.columns) >= 2:
                        df.columns = ['gpu', 'usage'] + list(df.columns[2:])
                    
                    # 尋找特定 GPU 的數據
                    gpu_row = df[df['gpu'] == f'gpu{gpu_id}']
                    if not gpu_row.empty:
                        usage = pd.to_numeric(gpu_row['usage'].iloc[0], errors='coerce')
                        if not np.isnan(usage):
                            gpu_data.append(usage)
                            gpu_dates.append(date)
                            
                except Exception as e:
                    print(f"讀取 {avg_file} 時發生錯誤: {e}")
        
        if gpu_data:
            ax.plot(gpu_dates, gpu_data, 
                   label=f'GPU {gpu_id}', 
                   marker='o', 
                   linewidth=2, 
                   markersize=4,
                   color=colors[i])
    
    # 設定圖表
    ax.set_title(f'{node} 所有 GPU 使用率趨勢\n期間: {start_date} 至 {end_date}', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('GPU 使用率 (%)', fontsize=12)
    
    # 格式化 x 軸
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # 設定 y 軸範圍為 0-100%
    ax.set_ylim(0, 100)
    
    # 添加圖例和網格（只有當有數據時才顯示圖例）
    if ax.get_lines():  # 檢查是否有繪製的線條
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    save_path = os.path.join(plots_dir, f'{node}_all_gpus_{start_date}_to_{end_date}.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"{node} 所有 GPU 趨勢圖已保存至: {save_path}")
    plt.close()
    
    return save_path

def quick_gpu_across_nodes(gpu_id, start_date, end_date, data_dir="../data", plots_dir="../plots"):
    """
    快速繪製特定 GPU 跨所有節點的使用率對比
    
    Args:
        gpu_id (int): GPU ID (如: 1, 9, 17, 25, 33, 41, 49, 57)
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        
    Returns:
        str: 保存的圖片路徑
    """
    nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    os.makedirs(plots_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # 生成日期範圍
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    for i, node in enumerate(nodes):
        node_data = []
        node_dates = []
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            avg_file = os.path.join(data_dir, node, date_str, f"average_{date_str}.csv")
            
            if os.path.exists(avg_file):
                try:
                    df = pd.read_csv(avg_file, encoding='utf-8')
                    
                    # 處理列名
                    if 'GPU卡號' in df.columns and '平均使用率(%)' in df.columns:
                        df = df.rename(columns={'GPU卡號': 'gpu', '平均使用率(%)': 'usage'})
                    elif len(df.columns) >= 2:
                        df.columns = ['gpu', 'usage'] + list(df.columns[2:])
                    
                    # 尋找特定 GPU 的數據
                    gpu_row = df[df['gpu'] == f'gpu{gpu_id}']
                    if not gpu_row.empty:
                        usage = pd.to_numeric(gpu_row['usage'].iloc[0], errors='coerce')
                        if not np.isnan(usage):
                            node_data.append(usage)
                            node_dates.append(date)
                            
                except Exception as e:
                    print(f"讀取 {avg_file} 時發生錯誤: {e}")
        
        if node_data:
            ax.plot(node_dates, node_data, 
                   label=node, 
                   marker='o', 
                   linewidth=2.5, 
                   markersize=6,
                   color=colors[i])
    
    # 設定圖表
    ax.set_title(f'GPU {gpu_id} 跨節點使用率趨勢\n期間: {start_date} 至 {end_date}', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('GPU 使用率 (%)', fontsize=12)
    
    # 格式化 x 軸
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # 設定 y 軸範圍為 0-100%
    ax.set_ylim(0, 100)
    
    # 添加圖例和網格（只有當有數據時才顯示圖例）
    if ax.get_lines():  # 檢查是否有繪製的線條
        ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    save_path = os.path.join(plots_dir, f'gpu{gpu_id}_across_nodes_{start_date}_to_{end_date}.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"GPU {gpu_id} 跨節點趨勢圖已保存至: {save_path}")
    plt.close()
    
    return save_path

def get_available_dates(data_dir="../data"):
    """
    獲取可用的日期列表
    
    Args:
        data_dir (str): 資料目錄
        
    Returns:
        list: 排序後的可用日期列表
    """
    dates = set()
    nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
    
    for node in nodes:
        node_dir = os.path.join(data_dir, node)
        if os.path.exists(node_dir):
            for date_dir in os.listdir(node_dir):
                if os.path.isdir(os.path.join(node_dir, date_dir)):
                    try:
                        datetime.strptime(date_dir, '%Y-%m-%d')
                        dates.add(date_dir)
                    except ValueError:
                        continue
    
    return sorted(list(dates))

def generate_all_quick_plots(start_date=None, end_date=None, data_dir="../data", plots_dir="../plots"):
    """
    生成所有常用的 GPU 使用率趨勢圖
    
    Args:
        start_date (str): 開始日期，若為 None 則自動選擇
        end_date (str): 結束日期，若為 None 則自動選擇
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        
    Returns:
        list: 生成的圖片路徑列表
    """
    # 如果沒有指定日期，自動獲取可用日期範圍
    if start_date is None or end_date is None:
        available_dates = get_available_dates(data_dir)
        if not available_dates:
            print("未找到任何可用的 GPU 數據")
            return []
        
        start_date = available_dates[0]
        end_date = available_dates[-1]
        print(f"自動選擇日期範圍: {start_date} 至 {end_date}")
    
    generated_plots = []
    
    print("=" * 50)
    print("GPU 使用率趨勢圖生成")
    print("=" * 50)
    
    # 1. 各節點趨勢對比
    print("1. 生成各節點趨勢對比圖...")
    plot_path = quick_nodes_trend(start_date, end_date, data_dir, plots_dir)
    generated_plots.append(plot_path)
    
    # 2. 第一個節點的所有 GPU 趨勢
    print("\n2. 生成 colab-gpu1 所有 GPU 趨勢圖...")
    plot_path = quick_single_node_gpus('colab-gpu1', start_date, end_date, data_dir, plots_dir)
    generated_plots.append(plot_path)
    
    # 3. GPU 1 跨節點對比
    print("\n3. 生成 GPU 1 跨節點趨勢圖...")
    plot_path = quick_gpu_across_nodes(1, start_date, end_date, data_dir, plots_dir)
    generated_plots.append(plot_path)
    
    print("\n" + "=" * 50)
    print(f"所有圖表已生成完成！共 {len(generated_plots)} 張圖片")
    print(f"保存位置: {plots_dir}")
    print("=" * 50)
    
    return generated_plots

# 導入 VRAM 監控模組
try:
    from vram_monitor import VRAMMonitor
    VRAM_AVAILABLE = True
except ImportError:
    VRAM_AVAILABLE = False
    print("警告: 無法導入 VRAM 監控模組")

def quick_vram_nodes_comparison(start_date, end_date, data_dir="../data", plots_dir="../plots", gpu_id=None):
    """
    快速繪製各節點 VRAM 使用量對比圖
    
    Args:
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        gpu_id (int): 指定 GPU ID，若為 None 則使用所有 GPU 平均
        
    Returns:
        str: 保存的圖片路徑
    """
    if not VRAM_AVAILABLE:
        print("VRAM 監控功能不可用")
        return None
        
    monitor = VRAMMonitor(data_dir, plots_dir)
    return monitor.plot_nodes_vram_comparison(start_date, end_date, gpu_id)

def quick_vram_heatmap(start_date, end_date, data_dir="../data", plots_dir="../plots"):
    """
    快速繪製 VRAM 使用率熱力圖
    
    Args:
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        
    Returns:
        str: 保存的圖片路徑
    """
    if not VRAM_AVAILABLE:
        print("VRAM 監控功能不可用")
        return None
        
    monitor = VRAMMonitor(data_dir, plots_dir)
    return monitor.plot_vram_heatmap(start_date, end_date)

def quick_vram_timeline(node, gpu_id, date, data_dir="../data", plots_dir="../plots"):
    """
    快速繪製單一 GPU 的 VRAM 使用量時間序列圖
    
    Args:
        node (str): 節點名稱
        gpu_id (int): GPU ID
        date (str): 日期 (YYYY-MM-DD)
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        
    Returns:
        str: 保存的圖片路徑
    """
    if not VRAM_AVAILABLE:
        print("VRAM 監控功能不可用")
        return None
        
    monitor = VRAMMonitor(data_dir, plots_dir)
    return monitor.plot_vram_usage_timeline(node, gpu_id, date)

def generate_all_vram_plots(start_date, end_date, data_dir="../data", plots_dir="../plots"):
    """
    生成所有 VRAM 相關圖表
    
    Args:
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        
    Returns:
        list: 生成的圖表路徑列表
    """
    if not VRAM_AVAILABLE:
        print("VRAM 監控功能不可用")
        return []
        
    print("==================================================")
    print("VRAM 使用量圖表生成")
    print("==================================================")
    
    generated_plots = []
    
    try:
        # 1. 節點 VRAM 對比圖
        print("1. 生成各節點 VRAM 對比圖...")
        path = quick_vram_nodes_comparison(start_date, end_date, data_dir, plots_dir)
        if path:
            generated_plots.append(path)
        
        # 2. VRAM 熱力圖
        print("\n2. 生成 VRAM 使用率熱力圖...")
        path = quick_vram_heatmap(start_date, end_date, data_dir, plots_dir)
        if path:
            generated_plots.append(path)
        
        # 3. 特定 GPU 的 VRAM 對比圖
        print("\n3. 生成 GPU 1 VRAM 跨節點對比圖...")
        path = quick_vram_nodes_comparison(start_date, end_date, data_dir, plots_dir, gpu_id=1)
        if path:
            generated_plots.append(path)
        
        print("\n==================================================")
        print(f"所有 VRAM 圖表已生成完成！共 {len(generated_plots)} 張圖片")
        print(f"保存位置: {plots_dir}")
        print("==================================================")
        
    except Exception as e:
        print(f"生成 VRAM 圖表時發生錯誤: {e}")
    
    return generated_plots

if __name__ == '__main__':
    """
    直接執行此腳本將生成所有常用的 GPU 趨勢圖
    """
    import sys
    
    if len(sys.argv) > 1:
        # 有命令列參數，支援簡單的參數輸入
        if len(sys.argv) >= 3:
            start_date = sys.argv[1]
            end_date = sys.argv[2]
            generate_all_quick_plots(start_date, end_date)
        else:
            print("使用方式:")
            print("  python quick_gpu_trend_plots.py")
            print("  python quick_gpu_trend_plots.py 2025-05-23 2025-05-26")
    else:
        # 無參數，使用自動模式
        print("GPU 使用率快速趨勢分析")
        print("正在自動偵測可用數據...")
        
        available_dates = get_available_dates()
        if available_dates:
            print(f"發現 {len(available_dates)} 天的數據")
            print(f"日期範圍: {available_dates[0]} 至 {available_dates[-1]}")
            
            # 生成所有圖表
            generate_all_quick_plots()
        else:
            print("未找到任何可用的 GPU 數據")
            print("請確認 './data' 目錄中包含正確格式的數據檔案")
