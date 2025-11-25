#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPU 使用率趨勢視覺化工具

基於 data 資料夾中的 GPU 使用率數據，生成各種趨勢圖表：
1. 節點間趨勢對比
2. 單一節點所有 GPU 趨勢
3. 特定 GPU 跨節點對比  
4. 熱力圖顯示
5. 詳細時間序列分析
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import os
import glob
import argparse
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 導入字體配置模組
from font_config import setup_chinese_font

# 設定中文字體
setup_chinese_font()

class GPUUsageTrendAnalyzer:
    def __init__(self, data_dir="../data", plots_dir="../plots"):
        """
        初始化 GPU 使用率趨勢分析器
        
        Args:
            data_dir (str): 資料目錄路徑
            plots_dir (str): 圖表輸出目錄
        """
        self.data_dir = data_dir
        self.plots_dir = plots_dir
        self.nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
        self.gpu_ids = [1, 9, 17, 25, 33, 41, 49, 57]
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
        
        # 確保輸出目錄存在
        os.makedirs(plots_dir, exist_ok=True)
        
    def get_available_dates(self, node=None):
        """
        獲取可用的日期列表
        
        Args:
            node (str): 指定節點名稱，若為 None 則搜尋所有節點
            
        Returns:
            list: 可用日期列表 (sorted)
        """
        dates = set()
        search_nodes = [node] if node else self.nodes
        
        for node_name in search_nodes:
            node_dir = os.path.join(self.data_dir, node_name)
            if os.path.exists(node_dir):
                for date_dir in os.listdir(node_dir):
                    date_path = os.path.join(node_dir, date_dir)
                    if os.path.isdir(date_path):
                        # 驗證日期格式
                        try:
                            datetime.strptime(date_dir, '%Y-%m-%d')
                            dates.add(date_dir)
                        except ValueError:
                            continue
        
        return sorted(list(dates))
    
    def load_gpu_detailed_data(self, node, gpu_id, date):
        """
        載入特定 GPU 的詳細時間序列數據
        
        Args:
            node (str): 節點名稱
            gpu_id (int): GPU ID
            date (str): 日期 (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: GPU 詳細數據，包含 timestamp, datetime, usage 欄位
        """
        file_path = os.path.join(self.data_dir, node, date, f"gpu{gpu_id}_{date}.csv")
        
        if not os.path.exists(file_path):
            return None
            
        try:
            # 讀取 CSV 數據，根據實際格式調整
            df = pd.read_csv(file_path, header=None, 
                           names=['timestamp', 'datetime', 'usage'])
            
            # 處理日期時間
            df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
            df['usage'] = pd.to_numeric(df['usage'], errors='coerce')
            df['date'] = date
            df['node'] = node
            df['gpu_id'] = gpu_id
            
            return df
        except Exception as e:
            print(f"讀取檔案 {file_path} 時發生錯誤: {e}")
            return None
    
    def load_daily_average_data(self, node, date):
        """
        載入每日平均數據
        
        Args:
            node (str): 節點名稱
            date (str): 日期 (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: 每日平均數據
        """
        file_path = os.path.join(self.data_dir, node, date, f"average_{date}.csv")
        
        if not os.path.exists(file_path):
            return None
            
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            
            # 處理新的 CSV 格式（包含使用者資訊）
            if 'GPU編號' in df.columns and '平均GPU使用率(%)' in df.columns:
                df = df.rename(columns={
                    'GPU編號': 'gpu', 
                    '平均GPU使用率(%)': 'usage',
                    '平均VRAM使用率(%)': 'vram',
                    '使用者': 'user'
                })
            # 處理舊的中文列名
            elif 'GPU卡號' in df.columns and '平均使用率(%)' in df.columns:
                df = df.rename(columns={'GPU卡號': 'gpu', '平均使用率(%)': 'usage'})
            elif len(df.columns) >= 2:
                df.columns = ['gpu', 'usage'] + list(df.columns[2:])
                
            # 過濾掉 "全部平均" 行
            df = df[~df['gpu'].str.contains('全部平均', na=False)]
            
            # 提取 GPU 編號
            df['gpu_id'] = df['gpu'].str.extract(r'(\d+)').astype(int)
            df['usage'] = pd.to_numeric(df['usage'], errors='coerce')
            
            # 確保有使用者資訊欄位
            if 'user' not in df.columns:
                df['user'] = '未知'
            df['date'] = date
            df['node'] = node
            
            return df
        except Exception as e:
            print(f"讀取檔案 {file_path} 時發生錯誤: {e}")
            return None
    
    def plot_nodes_comparison_trend(self, start_date, end_date, save_plot=True):
        """
        繪製各節點平均 GPU 使用率趨勢對比圖
        
        Args:
            start_date (str): 開始日期 (YYYY-MM-DD)
            end_date (str): 結束日期 (YYYY-MM-DD)
            save_plot (bool): 是否保存圖表
        """
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # 生成日期範圍
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        for i, node in enumerate(self.nodes):
            node_data = []
            node_dates = []
            
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                daily_avg = self.load_daily_average_data(node, date_str)
                
                if daily_avg is not None and not daily_avg.empty:
                    # 計算當天所有 GPU 的平均使用率（排除 NaN）
                    valid_usage = daily_avg['usage'].dropna()
                    if len(valid_usage) > 0:
                        avg_usage = valid_usage.mean()
                        node_data.append(avg_usage)
                        node_dates.append(date)
            
            if node_data:
                ax.plot(node_dates, node_data, 
                       label=node, 
                       marker='o', 
                       linewidth=2.5, 
                       markersize=6,
                       color=self.colors[i])
        
        # 設定圖表
        ax.set_title(f'各節點 GPU 平均使用率趨勢對比\n期間: {start_date} 至 {end_date}', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('平均 GPU 使用率 (%)', fontsize=12)
        
        # 格式化 x 軸
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # 設定 y 軸範圍為 0-100%
        ax.set_ylim(0, 100)
        
        # 添加圖例和網格
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_plot:
            save_path = os.path.join(self.plots_dir, f'nodes_comparison_{start_date}_to_{end_date}.png')
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"節點對比趨勢圖已保存至: {save_path}")
        
        plt.show()
        plt.close()
    
    def plot_single_node_all_gpus(self, node, start_date, end_date, save_plot=True):
        """
        繪製單一節點所有 GPU 的趨勢對比
        
        Args:
            node (str): 節點名稱
            start_date (str): 開始日期
            end_date (str): 結束日期
            save_plot (bool): 是否保存圖表
        """
        fig, ax = plt.subplots(figsize=(15, 10))
        
        # 生成日期範圍
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        for i, gpu_id in enumerate(self.gpu_ids):
            gpu_data = []
            gpu_dates = []
            
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                daily_avg = self.load_daily_average_data(node, date_str)
                
                if daily_avg is not None:
                    gpu_row = daily_avg[daily_avg['gpu_id'] == gpu_id]
                    if not gpu_row.empty and not pd.isna(gpu_row['usage'].iloc[0]):
                        gpu_data.append(gpu_row['usage'].iloc[0])
                        gpu_dates.append(date)
            
            if gpu_data:
                ax.plot(gpu_dates, gpu_data, 
                       label=f'GPU {gpu_id}', 
                       marker='o', 
                       linewidth=2, 
                       markersize=4,
                       color=self.colors[i])
        
        # 設定圖表
        ax.set_title(f'{node} 所有 GPU 使用率趨勢對比\n期間: {start_date} 至 {end_date}', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('GPU 使用率 (%)', fontsize=12)
        
        # 格式化 x 軸
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # 添加圖例和網格
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_plot:
            save_path = os.path.join(self.plots_dir, f'{node}_all_gpus_{start_date}_to_{end_date}.png')
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"{node} 所有 GPU 趨勢圖已保存至: {save_path}")
        
        plt.show()
        plt.close()
    
    def plot_specific_gpu_across_nodes(self, gpu_id, start_date, end_date, save_plot=True):
        """
        繪製特定 GPU 跨所有節點的使用率對比
        
        Args:
            gpu_id (int): GPU ID
            start_date (str): 開始日期
            end_date (str): 結束日期
            save_plot (bool): 是否保存圖表
        """
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # 生成日期範圍
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        for i, node in enumerate(self.nodes):
            node_data = []
            node_dates = []
            
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                daily_avg = self.load_daily_average_data(node, date_str)
                
                if daily_avg is not None:
                    gpu_row = daily_avg[daily_avg['gpu_id'] == gpu_id]
                    if not gpu_row.empty and not pd.isna(gpu_row['usage'].iloc[0]):
                        node_data.append(gpu_row['usage'].iloc[0])
                        node_dates.append(date)
            
            if node_data:
                ax.plot(node_dates, node_data, 
                       label=f'{node}', 
                       marker='o', 
                       linewidth=2.5, 
                       markersize=6,
                       color=self.colors[i])
        
        # 設定圖表
        ax.set_title(f'GPU {gpu_id} 跨節點使用率趨勢對比\n期間: {start_date} 至 {end_date}', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('GPU 使用率 (%)', fontsize=12)
        
        # 格式化 x 軸
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # 添加圖例和網格
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_plot:
            save_path = os.path.join(self.plots_dir, f'gpu{gpu_id}_across_nodes_{start_date}_to_{end_date}.png')
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"GPU {gpu_id} 跨節點趨勢圖已保存至: {save_path}")
        
        plt.show()
        plt.close()
    
    def plot_heatmap(self, start_date, end_date, save_plot=True, show_users=True):
        """
        繪製 GPU 使用率熱力圖
        
        Args:
            start_date (str): 開始日期
            end_date (str): 結束日期
            save_plot (bool): 是否保存圖表
            show_users (bool): 是否顯示使用者資訊
        """
        # 收集所有數據
        all_data = []
        user_info = {}  # 儲存使用者資訊
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        for node in self.nodes:
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                daily_avg = self.load_daily_average_data(node, date_str)
                
                if daily_avg is not None:
                    for _, row in daily_avg.iterrows():
                        gpu_key = f"{node}-GPU{row['gpu_id']}"
                        
                        all_data.append({
                            'node': node,
                            'gpu': f'GPU{row["gpu_id"]}',
                            'gpu_key': gpu_key,
                            'date': date_str,
                            'usage': row['usage']
                        })
                        
                        # 收集使用者資訊
                        if show_users and 'user' in row and pd.notna(row['user']):
                            user_info[gpu_key] = row['user']
        
        if not all_data:
            print("未找到數據進行熱力圖繪製")
            return
        
        df = pd.DataFrame(all_data)
        
        # 創建樞紐表：行為節點+GPU，列為日期
        if show_users:
            # 為每個 GPU 添加使用者資訊到標籤
            df['gpu_label'] = df.apply(lambda x: 
                f"{x['node']} {x['gpu']} ({user_info.get(x['gpu_key'], '未知')})" 
                if x['gpu_key'] in user_info else f"{x['node']} {x['gpu']}", axis=1)
            
            pivot_table = df.pivot_table(
                values='usage', 
                index='gpu_label', 
                columns='date', 
                aggfunc='mean'
            )
        else:
            pivot_table = df.pivot_table(
                values='usage', 
                index=['node', 'gpu'], 
                columns='date', 
                aggfunc='mean'
            )
        
        # 繪製熱力圖
        fig, ax = plt.subplots(figsize=(max(12, len(dates) * 0.8), max(10, len(pivot_table) * 0.4)))
        
        sns.heatmap(pivot_table, 
                   annot=True, 
                   fmt='.2f', 
                   cmap='YlOrRd', 
                   cbar_kws={'label': 'GPU 使用率 (%)'},
                   ax=ax)
        
        # 創建標題
        title = f'GPU 使用率熱力圖\n期間: {start_date} 至 {end_date}'
        if show_users and user_info:
            # 統計使用者資訊
            user_counts = {}
            for user in user_info.values():
                if user != '未知' and user != '未使用':
                    user_counts[user] = user_counts.get(user, 0) + 1
            
            if user_counts:
                user_summary = ', '.join([f"{user}({count})" for user, count in user_counts.items()])
                title += f'\n使用者: {user_summary}'
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('節點 & GPU' + (' (使用者)' if show_users else ''), fontsize=12)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_plot:
            suffix = '_with_users' if show_users else ''
            save_path = os.path.join(self.plots_dir, f'heatmap_{start_date}_to_{end_date}{suffix}.png')
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"熱力圖已保存至: {save_path}")
        
        plt.show()
        plt.close()
    
    def plot_detailed_timeline(self, node, gpu_id, date, save_plot=True):
        """
        繪製特定 GPU 的詳細時間序列圖（一整天的數據）
        
        Args:
            node (str): 節點名稱
            gpu_id (int): GPU ID
            date (str): 日期 (YYYY-MM-DD)
            save_plot (bool): 是否保存圖表
        """
        data = self.load_gpu_detailed_data(node, gpu_id, date)
        
        if data is None or data.empty:
            print(f"未找到 {node} GPU{gpu_id} 在 {date} 的詳細數據")
            return
        
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # 繪製時間序列
        ax.plot(data['datetime'], data['usage'], 
                linewidth=1.5, alpha=0.8, color=self.colors[0])
        
        # 添加平均線
        avg_usage = data['usage'].mean()
        ax.axhline(y=avg_usage, color='red', linestyle='--', 
                  label=f'平均使用率: {avg_usage:.2f}%')
        
        # 設定圖表
        ax.set_title(f'{node} GPU {gpu_id} 詳細使用率時間序列\n日期: {date}', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('時間', fontsize=12)
        ax.set_ylabel('GPU 使用率 (%)', fontsize=12)
        
        # 格式化 x 軸
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # 添加圖例和網格
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_plot:
            save_path = os.path.join(self.plots_dir, f'{node}_gpu{gpu_id}_timeline_{date}.png')
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"詳細時間序列圖已保存至: {save_path}")
        
        plt.show()
        plt.close()
    
    def generate_summary_report(self, start_date, end_date):
        """
        生成 GPU 使用率摘要統計報告
        
        Args:
            start_date (str): 開始日期
            end_date (str): 結束日期
        """
        print(f"\n=== GPU 使用率摘要報告 ===")
        print(f"分析期間: {start_date} 至 {end_date}")
        print("=" * 50)
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        all_data = []
        
        # 收集所有數據
        for node in self.nodes:
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                daily_avg = self.load_daily_average_data(node, date_str)
                
                if daily_avg is not None:
                    all_data.append(daily_avg)
        
        if not all_data:
            print("未找到任何數據")
            return
        
        combined_data = pd.concat(all_data, ignore_index=True)
        
        # 各節點統計
        print("\n各節點平均 GPU 使用率:")
        for node in self.nodes:
            node_data = combined_data[combined_data['node'] == node]['usage']
            if len(node_data) > 0:
                print(f"  {node}: {node_data.mean():.2f}% (最高: {node_data.max():.2f}%, 最低: {node_data.min():.2f}%)")
        
        # 各 GPU 統計
        print("\n各 GPU 平均使用率:")
        for gpu_id in self.gpu_ids:
            gpu_data = combined_data[combined_data['gpu_id'] == gpu_id]['usage']
            if len(gpu_data) > 0:
                print(f"  GPU {gpu_id}: {gpu_data.mean():.2f}% (最高: {gpu_data.max():.2f}%, 最低: {gpu_data.min():.2f}%)")
        
        # 整體統計
        overall_avg = combined_data['usage'].mean()
        overall_max = combined_data['usage'].max()
        overall_min = combined_data['usage'].min()
        print(f"\n整體統計:")
        print(f"  平均使用率: {overall_avg:.2f}%")
        print(f"  最高使用率: {overall_max:.2f}%")
        print(f"  最低使用率: {overall_min:.2f}%")
        print("=" * 50)

def main():
    """主函數：命令列介面"""
    parser = argparse.ArgumentParser(description='GPU 使用率趨勢視覺化工具')
    parser.add_argument('--data-dir', default='./data', help='資料目錄路徑')
    parser.add_argument('--plots-dir', default='./plots', help='圖表輸出目錄')
    parser.add_argument('--start-date', required=True, help='開始日期 (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='結束日期 (YYYY-MM-DD)')
    parser.add_argument('--mode', choices=['nodes', 'single-node', 'specific-gpu', 'heatmap', 'timeline', 'all'], 
                       default='all', help='繪圖模式')
    parser.add_argument('--node', help='指定節點名稱 (用於 single-node 或 timeline 模式)')
    parser.add_argument('--gpu-id', type=int, help='指定 GPU ID (用於 specific-gpu 或 timeline 模式)')
    parser.add_argument('--date', help='指定日期 (用於 timeline 模式, YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # 初始化分析器
    analyzer = GPUUsageTrendAnalyzer(args.data_dir, args.plots_dir)
    
    print(f"GPU 使用率趨勢分析 - 期間: {args.start_date} 至 {args.end_date}")
    print(f"資料目錄: {args.data_dir}")
    print(f"輸出目錄: {args.plots_dir}")
    
    # 根據模式執行相應的分析
    if args.mode == 'nodes' or args.mode == 'all':
        print("\n繪製節點對比趨勢圖...")
        analyzer.plot_nodes_comparison_trend(args.start_date, args.end_date)
    
    if args.mode == 'single-node' or args.mode == 'all':
        node = args.node if args.node else 'colab-gpu1'
        print(f"\n繪製 {node} 所有 GPU 趨勢圖...")
        analyzer.plot_single_node_all_gpus(node, args.start_date, args.end_date)
    
    if args.mode == 'specific-gpu' or args.mode == 'all':
        gpu_id = args.gpu_id if args.gpu_id else 1
        print(f"\n繪製 GPU {gpu_id} 跨節點趨勢圖...")
        analyzer.plot_specific_gpu_across_nodes(gpu_id, args.start_date, args.end_date)
    
    if args.mode == 'heatmap' or args.mode == 'all':
        print("\n繪製熱力圖...")
        analyzer.plot_heatmap(args.start_date, args.end_date)
    
    if args.mode == 'timeline':
        node = args.node if args.node else 'colab-gpu1'
        gpu_id = args.gpu_id if args.gpu_id else 1
        date = args.date if args.date else args.start_date
        print(f"\n繪製 {node} GPU {gpu_id} 在 {date} 的詳細時間序列...")
        analyzer.plot_detailed_timeline(node, gpu_id, date)
    
    # 生成摘要報告
    print("\n生成摘要報告...")
    analyzer.generate_summary_report(args.start_date, args.end_date)

if __name__ == '__main__':
    # 如果沒有命令列參數，使用預設範例
    import sys
    if len(sys.argv) == 1:
        print("GPU 使用率趨勢視覺化工具")
        print("=" * 40)
        
        # 初始化分析器
        analyzer = GPUUsageTrendAnalyzer()
        
        # 獲取可用日期
        available_dates = analyzer.get_available_dates()
        if not available_dates:
            print("未找到任何可用的 GPU 數據")
            sys.exit(1)
        
        print(f"發現 {len(available_dates)} 天的數據: {available_dates[0]} 至 {available_dates[-1]}")
        
        # 使用最近的日期範圍
        start_date = available_dates[0]
        end_date = available_dates[-1]
        
        print(f"自動選擇分析期間: {start_date} 至 {end_date}")
        
        # 生成所有類型的圖表
        print("\n1. 繪製節點對比趨勢圖...")
        analyzer.plot_nodes_comparison_trend(start_date, end_date)
        
        print("\n2. 繪製單一節點所有 GPU 趨勢圖...")
        analyzer.plot_single_node_all_gpus('colab-gpu1', start_date, end_date)
        
        print("\n3. 繪製特定 GPU 跨節點趨勢圖...")
        analyzer.plot_specific_gpu_across_nodes(1, start_date, end_date)
        
        print("\n4. 繪製熱力圖...")
        analyzer.plot_heatmap(start_date, end_date)
        
        print("\n5. 生成摘要報告...")
        analyzer.generate_summary_report(start_date, end_date)
        
        print(f"\n所有圖表已保存至 './plots' 目錄")
    else:
        main()
