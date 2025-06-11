#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡易 GPU 使用率視覺化工具

快速生成 GPU 使用率趨勢圖的簡化版本
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
import os
import glob

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def quick_plot_node_trends(start_date, end_date, data_dir="./data", output_dir="./plots"):
    """
    快速生成各節點趨勢對比圖
    
    Args:
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        data_dir (str): 數據目錄
        output_dir (str): 輸出目錄
    """
    nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    # 創建輸出目錄
    os.makedirs(output_dir, exist_ok=True)
    
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
                    if 'GPU卡號' in df.columns:
                        df = df.rename(columns={'GPU卡號': 'gpu', '平均使用率(%)': 'usage'})
                    elif len(df.columns) == 2:
                        df.columns = ['gpu', 'usage']
                    
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
                   linewidth=2, 
                   markersize=6,
                   color=colors[i])
    
    # 設定圖表
    ax.set_title(f'各節點 GPU 平均使用率趨勢\n({start_date} 至 {end_date})', 
                fontsize=16, fontweight='bold')
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('平均 GPU 使用率 (%)', fontsize=12)
    
    # 格式化 x 軸
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # 添加圖例和網格
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    save_path = os.path.join(output_dir, f'nodes_trend_{start_date}_to_{end_date}.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"節點趨勢圖已保存至: {save_path}")
    plt.show()

def quick_plot_gpu_comparison(node, date, data_dir="./data", output_dir="./plots"):
    """
    快速生成單節點多 GPU 對比圖
    
    Args:
        node (str): 節點名稱
        date (str): 日期 (YYYY-MM-DD)
        data_dir (str): 數據目錄
        output_dir (str): 輸出目錄
    """
    gpu_ids = [1, 9, 17, 25, 33, 41, 49, 57]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    
    os.makedirs(output_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(15, 10))
    
    for i, gpu_id in enumerate(gpu_ids):
        csv_file = os.path.join(data_dir, node, date, f"gpu{gpu_id}_{date}.csv")
        
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file, header=None, 
                               names=['timestamp', 'datetime', 'usage'])
                df['datetime'] = pd.to_datetime(df['datetime'])
                df['usage'] = pd.to_numeric(df['usage'], errors='coerce')
                
                ax.plot(df['datetime'], df['usage'], 
                       label=f'GPU {gpu_id}', 
                       linewidth=1.5, 
                       color=colors[i],
                       alpha=0.8)
            except Exception as e:
                print(f"讀取 {csv_file} 時發生錯誤: {e}")
    
    # 設定圖表
    ax.set_title(f'{node} 所有 GPU 使用率對比\n日期: {date}', 
                fontsize=16, fontweight='bold')
    ax.set_xlabel('時間', fontsize=12)
    ax.set_ylabel('GPU 使用率 (%)', fontsize=12)
    
    # 格式化 x 軸
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # 添加圖例和網格
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    save_path = os.path.join(output_dir, f'{node}_gpu_comparison_{date}.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"GPU 對比圖已保存至: {save_path}")
    plt.show()

def quick_plot_daily_summary(start_date, end_date, data_dir="./data", output_dir="./plots"):
    """
    快速生成每日摘要統計圖
    
    Args:
        start_date (str): 開始日期
        end_date (str): 結束日期
        data_dir (str): 數據目錄
        output_dir (str): 輸出目錄
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 收集數據
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
    
    # 準備數據結構
    daily_data = {node: [] for node in nodes}
    date_labels = []
    
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        date_labels.append(date.strftime('%m-%d'))
        
        for node in nodes:
            avg_file = os.path.join(data_dir, node, date_str, f"average_{date_str}.csv")
            
            if os.path.exists(avg_file):
                try:
                    df = pd.read_csv(avg_file, encoding='utf-8')
                    if 'GPU卡號' in df.columns:
                        df = df.rename(columns={'GPU卡號': 'gpu', '平均使用率(%)': 'usage'})
                    elif len(df.columns) == 2:
                        df.columns = ['gpu', 'usage']
                    
                    # 計算該節點該日的平均使用率
                    gpu_data = df[~df['gpu'].str.contains('全部平均', na=False)]
                    avg_usage = pd.to_numeric(gpu_data['usage'], errors='coerce').mean()
                    daily_data[node].append(avg_usage if not np.isnan(avg_usage) else 0)
                except:
                    daily_data[node].append(0)
            else:
                daily_data[node].append(0)
    
    # 創建子圖
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    
    # 堆疊柱狀圖
    bottom = np.zeros(len(date_labels))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for i, node in enumerate(nodes):
        ax1.bar(date_labels, daily_data[node], bottom=bottom, 
               label=node, color=colors[i], alpha=0.8)
        bottom += daily_data[node]
    
    ax1.set_title('每日各節點 GPU 使用率堆疊圖', fontsize=14, fontweight='bold')
    ax1.set_ylabel('GPU 使用率 (%)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    plt.setp(ax1.get_xticklabels(), rotation=45)
    
    # 總和趨勢線
    total_usage = [sum(daily_data[node][i] for node in nodes) for i in range(len(date_labels))]
    ax2.plot(date_labels, total_usage, marker='o', linewidth=2, markersize=8, color='red')
    ax2.fill_between(date_labels, total_usage, alpha=0.3, color='red')
    
    ax2.set_title('所有節點 GPU 使用率總和趨勢', fontsize=14, fontweight='bold')
    ax2.set_xlabel('日期')
    ax2.set_ylabel('總 GPU 使用率 (%)')
    ax2.grid(True, alpha=0.3)
    plt.setp(ax2.get_xticklabels(), rotation=45)
    
    plt.suptitle(f'GPU 使用率每日摘要\n({start_date} 至 {end_date})', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    save_path = os.path.join(output_dir, f'daily_summary_{start_date}_to_{end_date}.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"每日摘要圖已保存至: {save_path}")
    plt.show()

# 使用範例
if __name__ == "__main__":
    # 設定參數
    START_DATE = "2025-05-23"
    END_DATE = "2025-05-26"
    DATA_DIR = "./data"
    OUTPUT_DIR = "./plots"
    
    print("正在生成 GPU 使用率趨勢圖...")
    
    # 生成各種圖表
    print("\n1. 生成節點趨勢對比圖...")
    quick_plot_node_trends(START_DATE, END_DATE, DATA_DIR, OUTPUT_DIR)
    
    print("\n2. 生成每日摘要統計圖...")
    quick_plot_daily_summary(START_DATE, END_DATE, DATA_DIR, OUTPUT_DIR)
    
    print("\n3. 生成單節點 GPU 對比圖...")
    # 為每個節點生成最新日期的 GPU 對比圖
    for node in ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']:
        print(f"   處理 {node}...")
        quick_plot_gpu_comparison(node, END_DATE, DATA_DIR, OUTPUT_DIR)
    
    print("\n所有圖表生成完成！")
