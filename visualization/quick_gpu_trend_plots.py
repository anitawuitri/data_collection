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
from datetime import datetime, timedelta
import os
import glob

# 導入字體配置模組
from font_config import setup_chinese_font

# 設定中文字體
setup_chinese_font()

def load_gpu_data_with_users(avg_file):
    """
    讀取包含使用者資訊的 GPU 數據
    
    Args:
        avg_file (str): CSV 檔案路徑
        
    Returns:
        pandas.DataFrame: 包含使用者資訊的數據，如果失敗則返回 None
    """
    try:
        df = pd.read_csv(avg_file, encoding='utf-8')
        
        # 檢查是否有新格式的使用者欄位
        if '使用者' in df.columns:
            # 新格式：GPU編號,平均GPU使用率(%),平均VRAM使用率(%),使用者
            expected_cols = ['GPU編號', '平均GPU使用率(%)', '平均VRAM使用率(%)', '使用者']
            if all(col in df.columns for col in expected_cols):
                df = df.rename(columns={
                    'GPU編號': 'gpu',
                    '平均GPU使用率(%)': 'usage',
                    '平均VRAM使用率(%)': 'vram',
                    '使用者': 'user'
                })
                return df
        
        # 處理舊格式或其他格式
        if 'GPU卡號' in df.columns and '平均使用率(%)' in df.columns:
            df = df.rename(columns={'GPU卡號': 'gpu', '平均使用率(%)': 'usage'})
        elif len(df.columns) >= 2:
            # 最基本的格式處理
            df.columns = ['gpu', 'usage'] + list(df.columns[2:])
        
        # 如果沒有使用者欄位，添加預設值
        if 'user' not in df.columns:
            df['user'] = '未知'
            
        return df
        
    except Exception as e:
        print(f"讀取 {avg_file} 時發生錯誤: {e}")
        return None

def get_user_info_for_node(node, date_str, data_dir="../data"):
    """
    獲取特定節點和日期的使用者資訊
    
    Args:
        node (str): 節點名稱
        date_str (str): 日期字符串 (YYYY-MM-DD)
        data_dir (str): 資料目錄
        
    Returns:
        dict: GPU ID 到使用者的對應字典
    """
    avg_file = os.path.join(data_dir, node, date_str, f"average_{date_str}.csv")
    df = load_gpu_data_with_users(avg_file)
    
    if df is None:
        return {}
    
    user_info = {}
    # 處理非"全部平均"的行
    gpu_data = df[~df['gpu'].str.contains('全部平均', na=False)]
    
    for _, row in gpu_data.iterrows():
        gpu_id = row['gpu']
        user = row.get('user', '未知')
        if user and user != '未使用':
            user_info[gpu_id] = user
    
    return user_info

def quick_nodes_trend(start_date, end_date, data_dir="../data", plots_dir="../plots", show_users=True):
    """
    快速繪製各節點 GPU 平均使用率趨勢對比
    
    Args:
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        show_users (bool): 是否在圖表中顯示使用者資訊
        
    Returns:
        str: 保存的圖片路徑
    """
    nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    # 創建輸出目錄
    os.makedirs(plots_dir, exist_ok=True)
    
    # 調整圖表大小以容納使用者資訊
    fig_height = 10 if show_users else 8
    fig, ax = plt.subplots(figsize=(15, fig_height))
    
    # 生成日期範圍
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 存儲使用者資訊用於顯示
    user_info_text = []
    
    for i, node in enumerate(nodes):
        node_data = []
        node_dates = []
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            avg_file = os.path.join(data_dir, node, date_str, f"average_{date_str}.csv")
            
            if os.path.exists(avg_file):
                df = load_gpu_data_with_users(avg_file)
                if df is not None:
                    # 過濾掉 "全部平均" 行並計算平均值
                    gpu_data = df[~df['gpu'].str.contains('全部平均', na=False)]
                    avg_usage = pd.to_numeric(gpu_data['usage'], errors='coerce').mean()
                    
                    if not np.isnan(avg_usage):
                        node_data.append(avg_usage)
                        node_dates.append(date)
                        
                        # 收集使用者資訊（僅最後一天）
                        if show_users and date == dates[-1]:
                            users = []
                            for _, row in gpu_data.iterrows():
                                user = row.get('user', '未知')
                                if user and user not in ['未使用', '未知']:
                                    users.append(user)
                            if users:
                                unique_users = list(set(users))
                                user_info_text.append(f"{node}: {', '.join(unique_users)}")
        
        if node_data:
            ax.plot(node_dates, node_data, 
                   label=node, 
                   marker='o', 
                   linewidth=2.5, 
                   markersize=6,
                   color=colors[i])
    
    # 設定圖表
    title = f'各節點 GPU 平均使用率趨勢\n期間: {start_date} 至 {end_date}'
    if show_users and user_info_text:
        title += f'\n\n使用者資訊 ({end_date}):\n' + '\n'.join(user_info_text)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
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

def quick_single_node_gpus(node, start_date, end_date, data_dir="../data", plots_dir="../plots", show_users=True):
    """
    快速繪製單一節點所有 GPU 的使用率趨勢
    
    Args:
        node (str): 節點名稱 (如: colab-gpu1)
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        show_users (bool): 是否在圖表中顯示使用者資訊
        
    Returns:
        str: 保存的圖片路徑
    """
    # 更新為使用 GPU index 而不是 card ID
    gpu_indices = list(range(8))  # GPU[0] 到 GPU[7]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    
    os.makedirs(plots_dir, exist_ok=True)
    
    # 調整圖表大小以容納使用者資訊
    fig_height = 12 if show_users else 10
    fig, ax = plt.subplots(figsize=(15, fig_height))
    
    # 生成日期範圍
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 存儲使用者資訊
    gpu_user_info = {}
    
    for i, gpu_index in enumerate(gpu_indices):
        gpu_data = []
        gpu_dates = []
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            avg_file = os.path.join(data_dir, node, date_str, f"average_{date_str}.csv")
            
            if os.path.exists(avg_file):
                df = load_gpu_data_with_users(avg_file)
                if df is not None:
                    # 尋找特定 GPU 的數據
                    gpu_row = df[df['gpu'] == f'GPU[{gpu_index}]']
                    if not gpu_row.empty:
                        usage = pd.to_numeric(gpu_row['usage'].iloc[0], errors='coerce')
                        if not np.isnan(usage):
                            gpu_data.append(usage)
                            gpu_dates.append(date)
                            
                            # 收集使用者資訊（最後一天）
                            if show_users and date == dates[-1]:
                                user = gpu_row['user'].iloc[0] if 'user' in gpu_row.columns else '未知'
                                if user and user not in ['未使用', '未知']:
                                    gpu_user_info[f'GPU[{gpu_index}]'] = user
        
        if gpu_data:
            # 構建標籤，包含使用者資訊（如果有的話）
            label = f'GPU[{gpu_index}]'
            if show_users and f'GPU[{gpu_index}]' in gpu_user_info:
                label += f' ({gpu_user_info[f"GPU[{gpu_index}]"]})'
                
            ax.plot(gpu_dates, gpu_data, 
                   label=label, 
                   marker='o', 
                   linewidth=2, 
                   markersize=4,
                   color=colors[i])
    
    # 設定圖表
    title = f'{node} 所有 GPU 使用率趨勢\n期間: {start_date} 至 {end_date}'
    if show_users and gpu_user_info:
        title += f'\n\n使用者資訊 ({end_date}):'
        user_list = [f"{gpu}: {user}" for gpu, user in gpu_user_info.items()]
        title += '\n' + ', '.join(user_list)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
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

def quick_gpu_across_nodes(gpu_index, start_date, end_date, data_dir="../data", plots_dir="../plots", show_users=True):
    """
    快速繪製特定 GPU 跨所有節點的使用率對比
    
    Args:
        gpu_index (int): GPU 索引 (如: 0, 1, 2, 3, 4, 5, 6, 7)
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        show_users (bool): 是否在圖表中顯示使用者資訊
        
    Returns:
        str: 保存的圖片路徑
    """
    nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    os.makedirs(plots_dir, exist_ok=True)
    
    # 調整圖表大小以容納使用者資訊
    fig_height = 10 if show_users else 8
    fig, ax = plt.subplots(figsize=(15, fig_height))
    
    # 生成日期範圍
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 存儲使用者資訊
    node_user_info = {}
    
    for i, node in enumerate(nodes):
        node_data = []
        node_dates = []
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            avg_file = os.path.join(data_dir, node, date_str, f"average_{date_str}.csv")
            
            if os.path.exists(avg_file):
                df = load_gpu_data_with_users(avg_file)
                if df is not None:
                    # 尋找特定 GPU 的數據
                    gpu_row = df[df['gpu'] == f'GPU[{gpu_index}]']
                    if not gpu_row.empty:
                        usage = pd.to_numeric(gpu_row['usage'].iloc[0], errors='coerce')
                        if not np.isnan(usage):
                            node_data.append(usage)
                            node_dates.append(date)
                            
                            # 收集使用者資訊（最後一天）
                            if show_users and date == dates[-1]:
                                user = gpu_row['user'].iloc[0] if 'user' in gpu_row.columns else '未知'
                                if user and user not in ['未使用', '未知']:
                                    node_user_info[node] = user
        
        if node_data:
            # 構建標籤，包含使用者資訊（如果有的話）
            label = node
            if show_users and node in node_user_info:
                label += f' ({node_user_info[node]})'
                
            ax.plot(node_dates, node_data, 
                   label=label, 
                   marker='o', 
                   linewidth=2.5, 
                   markersize=6,
                   color=colors[i])
    
    # 設定圖表
    title = f'GPU[{gpu_index}] 跨節點使用率趨勢\n期間: {start_date} 至 {end_date}'
    if show_users and node_user_info:
        title += f'\n\n使用者資訊 ({end_date}):'
        user_list = [f"{node}: {user}" for node, user in node_user_info.items()]
        title += '\n' + ', '.join(user_list)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
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
    
    save_path = os.path.join(plots_dir, f'gpu{gpu_index}_across_nodes_{start_date}_to_{end_date}.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"GPU[{gpu_index}] 跨節點趨勢圖已保存至: {save_path}")
    plt.close()
    
    return save_path

def quick_nodes_stacked_utilization(start_date, end_date, data_dir="../data", plots_dir="../plots", show_users=True):
    """
    繪製各節點 GPU 使用率累積的堆疊區域圖
    按節點分層顯示使用率累積情況，更清楚地展示各節點的貢獻
    
    Args:
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        show_users (bool): 是否在圖表中顯示使用者資訊
        
    Returns:
        str: 保存的圖片路徑
    """
    nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
    node_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # 節點專用顏色
    
    os.makedirs(plots_dir, exist_ok=True)
    
    # 調整圖表大小以容納使用者資訊
    fig_height = 12 if show_users else 10
    fig, ax = plt.subplots(figsize=(18, fig_height))
    
    # 生成日期範圍
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    date_list = [date.strftime('%Y-%m-%d') for date in dates]
    
    # 存儲各節點的使用率數據
    node_data = {}  # {node: [daily_avg_usage]}
    node_user_info = {}  # {node: {date: [users]}}
    
    # 收集各節點的平均使用率數據
    for node in nodes:
        node_usage_data = []
        node_user_info[node] = {}
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            avg_file = os.path.join(data_dir, node, date_str, f"average_{date_str}.csv")
            
            daily_avg = 0
            active_users = []
            
            if os.path.exists(avg_file):
                df = load_gpu_data_with_users(avg_file)
                if df is not None:
                    # 過濾掉 "全部平均" 行並計算節點平均使用率
                    gpu_data = df[~df['gpu'].str.contains('全部平均', na=False)]
                    
                    if not gpu_data.empty:
                        # 計算該節點當日的平均GPU使用率
                        usage_values = pd.to_numeric(gpu_data['usage'], errors='coerce')
                        daily_avg = usage_values.mean()
                        
                        if np.isnan(daily_avg):
                            daily_avg = 0
                        
                        # 收集使用者資訊
                        if show_users:
                            for _, row in gpu_data.iterrows():
                                user = row.get('user', '未知')
                                usage = pd.to_numeric(row.get('usage', 0), errors='coerce')
                                if user and user not in ['未使用', '未知'] and usage > 1:
                                    if user not in active_users:
                                        active_users.append(user)
            
            node_usage_data.append(daily_avg)
            node_user_info[node][date_str] = active_users
        
        node_data[node] = node_usage_data
    
    # 繪製堆疊區域圖
    bottom = np.zeros(len(date_list))
    
    for i, node in enumerate(nodes):
        values = node_data[node]
        
        # 構建標籤
        label = node
        if show_users:
            # 獲取最後一天的使用者資訊
            last_date = date_list[-1]
            users = node_user_info[node].get(last_date, [])
            if users:
                user_str = ', '.join(users[:3])  # 最多顯示3個使用者
                if len(users) > 3:
                    user_str += f'等{len(users)}人'
                label += f' ({user_str})'
        
        # 繪製堆疊區域
        ax.fill_between(range(len(date_list)), bottom, bottom + values, 
                       label=label, alpha=0.8, color=node_colors[i])
        bottom += values
    
    # 設定圖表標題
    title = f'各節點 GPU 使用率累積視圖（堆疊區域圖）\n期間: {start_date} 至 {end_date}'
    
    if show_users:
        # 統計活躍使用者總數
        all_users = set()
        for node in nodes:
            for date_users in node_user_info[node].values():
                all_users.update(date_users)
        if all_users:
            title += f'\n\n總活躍使用者數: {len(all_users)} 人'
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('累積 GPU 使用率 (%)', fontsize=12)
    
    # 設定 x 軸
    ax.set_xticks(range(0, len(date_list), max(1, len(date_list)//10)))
    ax.set_xticklabels([date_list[i] for i in range(0, len(date_list), max(1, len(date_list)//10))], 
                       rotation=45)
    
    # 添加網格和圖例
    ax.grid(True, alpha=0.3)
    
    # 優化圖例位置，避免與統計框重疊
    legend = ax.legend(loc='upper right', bbox_to_anchor=(0.98, 0.98), 
                      frameon=True, framealpha=0.9, fancybox=True, shadow=True)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_edgecolor('gray')
    
    # 添加統計資訊文字框
    max_utilization = np.max(bottom)
    avg_utilization = np.mean(bottom)
    
    stats_text = f'統計資訊:\n'
    stats_text += f'最大累積使用率: {max_utilization:.1f}%\n'
    stats_text += f'平均累積使用率: {avg_utilization:.1f}%\n'
    
    # 計算各節點平均貢獻
    for i, node in enumerate(nodes):
        node_avg = np.mean(node_data[node])
        stats_text += f'{node}: {node_avg:.1f}%\n'
    
    # 在圖表左上角添加統計框，與圖例分離
    ax.text(0.02, 0.75, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9))
    
    plt.tight_layout()
    
    save_path = os.path.join(plots_dir, f'nodes_stacked_utilization_{start_date}_to_{end_date}.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"各節點累積使用率堆疊區域圖已保存至: {save_path}")
    plt.close()
    
    return save_path

def quick_user_activity_summary(start_date, end_date, data_dir="../data", plots_dir="../plots"):
    """
    生成使用者活動摘要圖表
    
    Args:
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        
    Returns:
        str: 保存的圖片路徑
    """
    nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    os.makedirs(plots_dir, exist_ok=True)
    
    # 收集所有使用者活動數據
    user_activity = {}  # {user: {date: gpu_count}}
    daily_totals = {}   # {date: total_active_gpus}
    
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        daily_totals[date_str] = 0
        
        for node in nodes:
            avg_file = os.path.join(data_dir, node, date_str, f"average_{date_str}.csv")
            df = load_gpu_data_with_users(avg_file)
            
            if df is not None:
                # 處理非"全部平均"的行
                gpu_data = df[~df['gpu'].str.contains('全部平均', na=False)]
                
                for _, row in gpu_data.iterrows():
                    user = row.get('user', '未知')
                    usage = pd.to_numeric(row.get('usage', 0), errors='coerce')
                    
                    # 只計算有實際使用率的 GPU (>1%)
                    if user and user not in ['未使用', '未知'] and usage > 1:
                        if user not in user_activity:
                            user_activity[user] = {}
                        if date_str not in user_activity[user]:
                            user_activity[user][date_str] = 0
                        user_activity[user][date_str] += 1
                        daily_totals[date_str] += 1
    
    if not user_activity:
        print("未找到使用者活動數據")
        return None
    
    # 創建堆疊長條圖
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    
    # 圖表1: 使用者每日活動 GPU 數量
    date_list = [date.strftime('%Y-%m-%d') for date in dates]
    users = list(user_activity.keys())
    colors = plt.cm.Set3(np.linspace(0, 1, len(users)))
    
    bottom = np.zeros(len(date_list))
    
    for i, user in enumerate(users):
        values = [user_activity[user].get(date_str, 0) for date_str in date_list]
        ax1.bar(date_list, values, bottom=bottom, label=user, color=colors[i])
        bottom += values
    
    ax1.set_title(f'使用者每日活動 GPU 數量\n期間: {start_date} 至 {end_date}', 
                 fontsize=14, fontweight='bold')
    ax1.set_ylabel('活動 GPU 數量')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 設定 x 軸標籤
    ax1.set_xticks(range(0, len(date_list), max(1, len(date_list)//10)))
    ax1.set_xticklabels([date_list[i] for i in range(0, len(date_list), max(1, len(date_list)//10))], 
                       rotation=45)
    
    # 圖表2: 每日總活動 GPU 數量趨勢
    total_values = [daily_totals[date_str] for date_str in date_list]
    ax2.plot(date_list, total_values, marker='o', linewidth=2, color='#2ca02c')
    ax2.fill_between(date_list, total_values, alpha=0.3, color='#2ca02c')
    
    ax2.set_title('每日總活動 GPU 數量趨勢', fontsize=14, fontweight='bold')
    ax2.set_xlabel('日期')
    ax2.set_ylabel('總活動 GPU 數量')
    ax2.grid(True, alpha=0.3)
    
    # 設定 x 軸標籤
    ax2.set_xticks(range(0, len(date_list), max(1, len(date_list)//10)))
    ax2.set_xticklabels([date_list[i] for i in range(0, len(date_list), max(1, len(date_list)//10))], 
                       rotation=45)
    
    plt.tight_layout()
    
    save_path = os.path.join(plots_dir, f'user_activity_summary_{start_date}_to_{end_date}.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"使用者活動摘要圖已保存至: {save_path}")
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

def generate_all_quick_plots(start_date=None, end_date=None, data_dir="../data", plots_dir="../plots", show_users=True):
    """
    生成所有常用的 GPU 使用率趨勢圖
    
    Args:
        start_date (str): 開始日期，若為 None 則自動選擇
        end_date (str): 結束日期，若為 None 則自動選擇
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        show_users (bool): 是否在圖表中顯示使用者資訊
        
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
    plot_path = quick_nodes_trend(start_date, end_date, data_dir, plots_dir, show_users)
    generated_plots.append(plot_path)
    
    # 2. 第一個節點的所有 GPU 趨勢
    print("\n2. 生成 colab-gpu1 所有 GPU 趨勢圖...")
    plot_path = quick_single_node_gpus('colab-gpu1', start_date, end_date, data_dir, plots_dir, show_users)
    generated_plots.append(plot_path)
    
    # 3. GPU[0] 跨節點對比
    print("\n3. 生成 GPU[0] 跨節點趨勢圖...")
    plot_path = quick_gpu_across_nodes(0, start_date, end_date, data_dir, plots_dir, show_users)
    generated_plots.append(plot_path)
    
    # 4. 使用者活動摘要（如果啟用使用者資訊）
    if show_users:
        print("\n4. 生成使用者活動摘要圖...")
        plot_path = quick_user_activity_summary(start_date, end_date, data_dir, plots_dir)
        if plot_path:
            generated_plots.append(plot_path)
    
    # 5. 🔥 各節點 GPU 使用率累積堆疊視圖（新功能）
    print("\n5. 生成各節點 GPU 使用率累積堆疊視圖...")
    plot_path = quick_nodes_stacked_utilization(start_date, end_date, data_dir, plots_dir, show_users)
    generated_plots.append(plot_path)
    
    # 6. GPU 使用率熱力圖
    print("\n6. 生成 GPU 使用率熱力圖...")
    plot_path = quick_gpu_heatmap(start_date, end_date, data_dir, plots_dir, show_users)
    if plot_path:
        generated_plots.append(plot_path)
    
    # 7. VRAM 使用者活動摘要（如果啟用使用者資訊且 VRAM 可用）
    if show_users and VRAM_AVAILABLE:
        print("\n7. 生成 VRAM 使用者活動摘要...")
        plot_path = quick_vram_user_activity_summary(start_date, end_date, data_dir, plots_dir)
        if plot_path:
            generated_plots.append(plot_path)
    
    # 8. VRAM 節點對比圖（包含使用者資訊）
    if VRAM_AVAILABLE:
        print(f"\n8. 生成 VRAM 節點對比圖（{'包含' if show_users else '不包含'}使用者資訊）...")
        plot_path = quick_vram_nodes_comparison_with_users(start_date, end_date, data_dir, plots_dir, show_users=show_users)
        if plot_path:
            generated_plots.append(plot_path)
    
    print("\n" + "=" * 50)
    print(f"所有圖表已生成完成！共 {len(generated_plots)} 張圖片")
    print(f"保存位置: {plots_dir}")
    if show_users:
        print("✓ 包含使用者資訊")
    if VRAM_AVAILABLE:
        print("✓ 包含 VRAM 監控圖表")
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

def quick_vram_heatmap(start_date, end_date, data_dir="../data", plots_dir="../plots", show_users=True):
    """
    快速繪製 VRAM 使用率熱力圖（包含使用者資訊）
    
    Args:
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        show_users (bool): 是否顯示使用者資訊
        
    Returns:
        str: 保存的圖片路徑
    """
    if not VRAM_AVAILABLE:
        print("VRAM 監控功能不可用")
        return None
        
    monitor = VRAMMonitor(data_dir, plots_dir)
    return monitor.plot_vram_heatmap(start_date, end_date, show_users)

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

def quick_vram_user_activity_summary(start_date, end_date, data_dir="../data", plots_dir="../plots"):
    """
    快速繪製 VRAM 使用者活動摘要圖表
    
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
    return monitor.plot_vram_user_activity_summary(start_date, end_date)

def quick_vram_nodes_comparison_with_users(start_date, end_date, data_dir="../data", plots_dir="../plots", gpu_id=None, show_users=True):
    """
    快速繪製 VRAM 節點對比圖（包含使用者資訊）
    
    Args:
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        gpu_id (int): 指定 GPU ID，若為 None 則使用所有 GPU 平均
        show_users (bool): 是否顯示使用者資訊
        
    Returns:
        str: 保存的圖片路徑
    """
    if not VRAM_AVAILABLE:
        print("VRAM 監控功能不可用")
        return None
        
    monitor = VRAMMonitor(data_dir, plots_dir)
    return monitor.plot_vram_nodes_comparison_with_users(start_date, end_date, gpu_id, show_users)

def quick_gpu_heatmap(start_date, end_date, data_dir="../data", plots_dir="../plots", show_users=True):
    """
    生成 GPU 使用率熱力圖（包含使用者資訊）
    
    Args:
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        data_dir (str): 資料目錄
        plots_dir (str): 輸出目錄
        show_users (bool): 是否顯示使用者資訊
        
    Returns:
        str: 保存的圖片路徑
    """
    try:
        from advanced_gpu_trend_analyzer import GPUUsageTrendAnalyzer
        analyzer = GPUUsageTrendAnalyzer(data_dir, plots_dir)
        analyzer.plot_heatmap(start_date, end_date, show_users=show_users)
        
        suffix = '_with_users' if show_users else ''
        save_path = os.path.join(plots_dir, f'heatmap_{start_date}_to_{end_date}{suffix}.png')
        return save_path
    except ImportError as e:
        print(f"無法導入 advanced_gpu_trend_analyzer: {e}")
        return None

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
        
        # 2. VRAM 熱力圖（包含使用者資訊）
        print("\n2. 生成 VRAM 使用率熱力圖（包含使用者資訊）...")
        path = quick_vram_heatmap(start_date, end_date, data_dir, plots_dir, show_users=True)
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

def quick_nodes_vram_stacked_utilization(start_date, end_date, data_dir="../data", plots_dir="../plots", show_users=True):
    """
    生成各節點 VRAM 使用率累積堆疊區域圖
    
    Args:
        start_date (str): 開始日期 (YYYY-MM-DD)
        end_date (str): 結束日期 (YYYY-MM-DD)
        data_dir (str): 資料目錄路徑
        plots_dir (str): 圖表輸出目錄路徑
        show_users (bool): 是否顯示使用者資訊
        
    Returns:
        str: 生成的圖片檔案路徑
    """
    try:
        # 設定中文字體
        setup_chinese_font()
        
        # 生成日期列表
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        dates = []
        current = start
        while current <= end:
            dates.append(current)
            current += timedelta(days=1)
        
        date_list = [date.strftime('%Y-%m-%d') for date in dates]
        nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
        
        # 收集各節點的 VRAM 數據
        node_data = {}
        node_user_info = {}
        
        # 節點顏色配置
        node_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        # 收集各節點的平均 VRAM 使用率數據
        for node in nodes:
            node_vram_data = []
            node_user_info[node] = {}
            
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                avg_file = os.path.join(data_dir, node, date_str, f"average_{date_str}.csv")
                
                daily_avg = 0
                active_users = []
                
                if os.path.exists(avg_file):
                    df = load_gpu_data_with_users(avg_file)
                    if df is not None:
                        # 檢查是否有 VRAM 列
                        has_vram_data = 'vram' in df.columns or '平均VRAM使用率(%)' in df.columns
                        
                        if has_vram_data:
                            # 確保使用正確的列名
                            if '平均VRAM使用率(%)' in df.columns:
                                df = df.rename(columns={'平均VRAM使用率(%)': 'vram'})
                            
                            # 過濾掉 "全部平均" 行並計算節點平均 VRAM 使用率
                            gpu_data = df[~df['gpu'].str.contains('全部平均', na=False)]
                            
                            if not gpu_data.empty:
                                # 計算該節點當日的平均 VRAM 使用率
                                vram_values = pd.to_numeric(gpu_data['vram'], errors='coerce')
                                # 過濾掉 NaN 值
                                vram_values = vram_values.dropna()
                                
                                if len(vram_values) > 0:
                                    daily_avg = vram_values.mean()
                                else:
                                    daily_avg = 0
                                
                                # 收集使用者資訊（所有有 VRAM 使用的用戶）
                                if show_users:
                                    for _, row in gpu_data.iterrows():
                                        user = row.get('user', '未知')
                                        vram_usage = pd.to_numeric(row.get('vram', 0), errors='coerce')
                                        # 只收集有實際 VRAM 使用的使用者（>= 0.1%）
                                        if user and user not in ['未使用', '未知'] and not pd.isna(vram_usage) and vram_usage >= 0.1:
                                            if user not in active_users:
                                                active_users.append(user)
                
                node_vram_data.append(daily_avg)
                # 將當天的使用者資訊存儲
                node_user_info[node][date_str] = active_users.copy()
            
            # 將所有日期的使用者合併到節點資訊中
            all_node_users = set()
            for date_users in node_user_info[node].values():
                all_node_users.update(date_users)
            node_user_info[node]['all_users'] = list(all_node_users)
            
            node_data[node] = node_vram_data
        
        # 創建堆疊區域圖
        fig, ax = plt.subplots(figsize=(15, 10))
        
        # 繪製堆疊區域圖
        bottom = np.zeros(len(date_list))
        
        for i, node in enumerate(nodes):
            values = np.array(node_data[node])
            
            # 構建標籤，包含使用者資訊
            label = node
            if show_users:
                # 獲取該節點在整個期間的所有使用者
                all_users = node_user_info[node].get('all_users', [])
                if all_users:
                    # 根據使用者數量決定顯示方式
                    if len(all_users) <= 2:
                        user_str = ', '.join(all_users)
                    elif len(all_users) == 3:
                        user_str = ', '.join(all_users)
                    else:
                        # 超過3個使用者，顯示前2個加上總數
                        user_str = ', '.join(all_users[:2]) + f' 等{len(all_users)}人'
                    
                    label += f' ({user_str})'
                else:
                    # 如果沒有找到活躍使用者，檢查是否有任何使用者記錄
                    has_any_user = False
                    for date_str in date_list:
                        if date_str in node_user_info[node] and node_user_info[node][date_str]:
                            has_any_user = True
                            break
                    
                    if not has_any_user:
                        label += ' (無使用者)'
            
            # 繪製堆疊區域
            ax.fill_between(range(len(date_list)), bottom, bottom + values, 
                           label=label, alpha=0.8, color=node_colors[i])
            bottom += values
        
        # 設定圖表標題
        title = f'各節點 VRAM 使用率累積視圖（堆疊區域圖）\n期間: {start_date} 至 {end_date}'
        
        if show_users:
            # 統計活躍使用者總數
            all_users = set()
            for node in nodes:
                for date_users in node_user_info[node].values():
                    all_users.update(date_users)
            if all_users:
                title += f'\n\n總活躍使用者數: {len(all_users)} 人'
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('累積 VRAM 使用率 (%)', fontsize=12)
        
        # 設定 Y 軸範圍，確保從 0 開始
        max_vram = np.max(bottom) if len(bottom) > 0 and np.max(bottom) > 0 else 1.0
        ax.set_ylim(0, max_vram * 1.1)  # 上限增加 10% 留白
        
        # 設定 x 軸
        ax.set_xticks(range(0, len(date_list), max(1, len(date_list)//10)))
        ax.set_xticklabels([date_list[i] for i in range(0, len(date_list), max(1, len(date_list)//10))], 
                           rotation=45)
        
        # 添加網格和圖例
        ax.grid(True, alpha=0.3)
        
        # 優化圖例位置，避免與統計框重疊
        legend = ax.legend(loc='upper right', bbox_to_anchor=(0.98, 0.98), 
                          frameon=True, framealpha=0.9, fancybox=True, shadow=True)
        legend.get_frame().set_facecolor('white')
        legend.get_frame().set_edgecolor('gray')
        
        # 添加統計資訊文字框
        max_vram_utilization = np.max(bottom)
        avg_vram_utilization = np.mean(bottom)
        
        stats_text = f'VRAM 統計資訊:\n'
        stats_text += f'最大累積使用率: {max_vram_utilization:.1f}%\n'
        stats_text += f'平均累積使用率: {avg_vram_utilization:.1f}%\n'
        
        # 計算各節點平均貢獻
        for i, node in enumerate(nodes):
            node_avg = np.mean(node_data[node])
            stats_text += f'{node}: {node_avg:.1f}%\n'
        
        # 在圖表左上角添加統計框，與圖例分離
        ax.text(0.02, 0.75, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.9))
        
        plt.tight_layout()
        
        save_path = os.path.join(plots_dir, f'nodes_vram_stacked_utilization_{start_date}_to_{end_date}.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"各節點 VRAM 累積使用率堆疊區域圖已保存至: {save_path}")
        plt.close()
        
        return save_path
        
    except Exception as e:
        print(f"生成 VRAM 堆疊區域圖時發生錯誤: {e}")
        return None
