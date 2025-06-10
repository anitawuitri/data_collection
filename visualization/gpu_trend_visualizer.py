#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AMD GPU 使用率趨勢視覺化工具

此腳本提供多種 GPU 使用率數據的視覺化功能：
1. 單個 GPU 的時間序列趨勢圖
2. 多個 GPU 的對比圖  
3. 多節點的對比圖
4. 日期範圍內的趨勢分析
5. 熱力圖顯示
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

class GPUTrendVisualizer:
    def __init__(self, data_dir="../data"):
        """
        初始化 GPU 趨勢視覺化器
        
        Args:
            data_dir (str): 數據目錄路徑
        """
        self.data_dir = data_dir
        self.nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
        self.gpu_ids = [1, 9, 17, 25, 33, 41, 49, 57]
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
        
    def get_available_dates(self, node=None):
        """
        獲取可用的日期列表
        
        Args:
            node (str): 指定節點名稱，若為 None 則搜尋所有節點
            
        Returns:
            list: 可用日期列表
        """
        dates = set()
        search_nodes = [node] if node else self.nodes
        
        for node_name in search_nodes:
            node_dir = os.path.join(self.data_dir, node_name)
            if os.path.exists(node_dir):
                for date_dir in os.listdir(node_dir):
                    if os.path.isdir(os.path.join(node_dir, date_dir)):
                        # 驗證日期格式
                        try:
                            datetime.strptime(date_dir, '%Y-%m-%d')
                            dates.add(date_dir)
                        except ValueError:
                            continue
        
        return sorted(list(dates))
    
    def load_gpu_data(self, node, gpu_id, date):
        """
        載入特定 GPU 的詳細數據
        
        Args:
            node (str): 節點名稱
            gpu_id (int): GPU ID
            date (str): 日期 (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: GPU 數據
        """
        file_path = os.path.join(self.data_dir, node, date, f"gpu{gpu_id}_{date}.csv")
        
        if not os.path.exists(file_path):
            return None
            
        try:
            # 讀取 CSV 數據
            df = pd.read_csv(file_path, header=None, 
                           names=['timestamp', 'datetime', 'usage'])
            df['datetime'] = pd.to_datetime(df['datetime'])
            df['usage'] = pd.to_numeric(df['usage'], errors='coerce')
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
            # 處理中文列名
            if 'GPU卡號' in df.columns and '平均使用率(%)' in df.columns:
                df = df.rename(columns={'GPU卡號': 'gpu', '平均使用率(%)': 'usage'})
            elif len(df.columns) == 2:
                df.columns = ['gpu', 'usage']
                
            # 過濾掉 "全部平均" 行
            df = df[~df['gpu'].str.contains('全部平均', na=False)]
            df['usage'] = pd.to_numeric(df['usage'], errors='coerce')
            df['date'] = date
            df['node'] = node
            return df
        except Exception as e:
            print(f"讀取檔案 {file_path} 時發生錯誤: {e}")
            return None
    
    def plot_single_gpu_trend(self, node, gpu_id, start_date, end_date, save_path=None):
        """
        繪製單個 GPU 的時間序列趨勢圖
        
        Args:
            node (str): 節點名稱
            gpu_id (int): GPU ID
            start_date (str): 開始日期
            end_date (str): 結束日期
            save_path (str): 保存路徑
        """
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # 生成日期範圍
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        all_data = []
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            data = self.load_gpu_data(node, gpu_id, date_str)
            if data is not None:
                all_data.append(data)
        
        if not all_data:
            print(f"未找到 {node} GPU{gpu_id} 在 {start_date} 至 {end_date} 期間的數據")
            return
        
        # 合併所有數據
        combined_data = pd.concat(all_data, ignore_index=True)
        combined_data = combined_data.sort_values('datetime')
        
        # 繪製趨勢線
        ax.plot(combined_data['datetime'], combined_data['usage'], 
                linewidth=1.5, alpha=0.8, color=self.colors[0])
        
        # 設定圖表標題和標籤
        ax.set_title(f'{node} GPU {gpu_id} 使用率趨勢\n({start_date} 至 {end_date})', 
                    fontsize=16, fontweight='bold')
        ax.set_xlabel('日期時間', fontsize=12)
        ax.set_ylabel('GPU 使用率 (%)', fontsize=12)
        
        # 格式化 x 軸
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # 添加網格
        ax.grid(True, alpha=0.3)
        
        # 調整佈局
        plt.tight_layout()
        
        # 保存或顯示圖表
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"圖表已保存至: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_multi_gpu_comparison(self, node, date, save_path=None):
        """
        繪製單個節點多個 GPU 的對比圖
        
        Args:
            node (str): 節點名稱
            date (str): 日期
            save_path (str): 保存路徑
        """
        fig, ax = plt.subplots(figsize=(15, 10))
        
        # 載入每個 GPU 的數據
        for i, gpu_id in enumerate(self.gpu_ids):
            data = self.load_gpu_data(node, gpu_id, date)
            if data is not None:
                ax.plot(data['datetime'], data['usage'], 
                       label=f'GPU {gpu_id}', 
                       linewidth=1.5, 
                       color=self.colors[i % len(self.colors)],
                       alpha=0.8)
        
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
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"圖表已保存至: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_node_comparison(self, start_date, end_date, save_path=None):
        """
        繪製多節點平均使用率對比圖
        
        Args:
            start_date (str): 開始日期
            end_date (str): 結束日期
            save_path (str): 保存路徑
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
                    # 計算當天所有 GPU 的平均使用率
                    avg_usage = daily_avg['usage'].mean()
                    if not np.isnan(avg_usage):
                        node_data.append(avg_usage)
                        node_dates.append(date)
            
            if node_data:
                ax.plot(node_dates, node_data, 
                       label=node, 
                       marker='o', 
                       linewidth=2, 
                       markersize=6,
                       color=self.colors[i % len(self.colors)])
        
        # 設定圖表
        ax.set_title(f'各節點 GPU 平均使用率趨勢對比\n({start_date} 至 {end_date})', 
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
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"圖表已保存至: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_heatmap(self, start_date, end_date, save_path=None):
        """
        繪製 GPU 使用率熱力圖
        
        Args:
            start_date (str): 開始日期
            end_date (str): 結束日期
            save_path (str): 保存路徑
        """
        # 收集所有數據
        all_data = []
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        for node in self.nodes:
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                daily_avg = self.load_daily_average_data(node, date_str)
                
                if daily_avg is not None:
                    for _, row in daily_avg.iterrows():
                        gpu_num = row['gpu'].replace('gpu', '') if 'gpu' in row['gpu'] else row['gpu']
                        all_data.append({
                            'node': node,
                            'gpu': f'GPU {gpu_num}',
                            'date': date_str,
                            'usage': row['usage']
                        })
        
        if not all_data:
            print("未找到數據進行熱力圖繪製")
            return
        
        df = pd.DataFrame(all_data)
        
        # 創建樞紐表
        pivot_table = df.pivot_table(
            values='usage', 
            index=['node', 'gpu'], 
            columns='date', 
            aggfunc='mean'
        )
        
        # 繪製熱力圖
        fig, ax = plt.subplots(figsize=(max(12, len(dates) * 0.8), max(8, len(pivot_table) * 0.3)))
        
        sns.heatmap(pivot_table, 
                   annot=True, 
                   fmt='.2f', 
                   cmap='YlOrRd', 
                   ax=ax,
                   cbar_kws={'label': 'GPU 使用率 (%)'})
        
        ax.set_title(f'GPU 使用率熱力圖\n({start_date} 至 {end_date})', 
                    fontsize=16, fontweight='bold')
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('節點 - GPU', fontsize=12)
        
        plt.setp(ax.get_xticklabels(), rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"熱力圖已保存至: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def create_summary_dashboard(self, start_date, end_date, save_path=None):
        """
        創建綜合儀表板
        
        Args:
            start_date (str): 開始日期
            end_date (str): 結束日期
            save_path (str): 保存路徑
        """
        fig = plt.figure(figsize=(20, 15))
        
        # 子圖1: 節點對比
        ax1 = plt.subplot(2, 2, 1)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        for i, node in enumerate(self.nodes):
            node_data = []
            node_dates = []
            
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                daily_avg = self.load_daily_average_data(node, date_str)
                
                if daily_avg is not None:
                    avg_usage = daily_avg['usage'].mean()
                    if not np.isnan(avg_usage):
                        node_data.append(avg_usage)
                        node_dates.append(date)
            
            if node_data:
                ax1.plot(node_dates, node_data, 
                        label=node, 
                        marker='o', 
                        linewidth=2,
                        color=self.colors[i % len(self.colors)])
        
        ax1.set_title('各節點平均使用率趨勢', fontsize=14, fontweight='bold')
        ax1.set_ylabel('GPU 使用率 (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        
        # 子圖2: 整體統計柱狀圖
        ax2 = plt.subplot(2, 2, 2)
        node_averages = []
        node_names = []
        
        for node in self.nodes:
            all_usage = []
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                daily_avg = self.load_daily_average_data(node, date_str)
                if daily_avg is not None:
                    all_usage.extend(daily_avg['usage'].dropna().tolist())
            
            if all_usage:
                node_averages.append(np.mean(all_usage))
                node_names.append(node)
        
        bars = ax2.bar(node_names, node_averages, color=self.colors[:len(node_names)])
        ax2.set_title('各節點平均使用率統計', fontsize=14, fontweight='bold')
        ax2.set_ylabel('平均 GPU 使用率 (%)')
        
        # 在柱狀圖上添加數值標籤
        for bar, value in zip(bars, node_averages):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.2f}%', ha='center', va='bottom')
        
        # 子圖3: GPU 使用率分佈
        ax3 = plt.subplot(2, 2, 3)
        all_gpu_data = []
        
        for node in self.nodes:
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                daily_avg = self.load_daily_average_data(node, date_str)
                if daily_avg is not None:
                    all_gpu_data.extend(daily_avg['usage'].dropna().tolist())
        
        if all_gpu_data:
            ax3.hist(all_gpu_data, bins=20, alpha=0.7, color=self.colors[0], edgecolor='black')
            ax3.set_title('GPU 使用率分佈直方圖', fontsize=14, fontweight='bold')
            ax3.set_xlabel('GPU 使用率 (%)')
            ax3.set_ylabel('頻次')
            ax3.grid(True, alpha=0.3)
        
        # 子圖4: 時間序列箱線圖
        ax4 = plt.subplot(2, 2, 4)
        daily_data = []
        daily_labels = []
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            day_usage = []
            
            for node in self.nodes:
                daily_avg = self.load_daily_average_data(node, date_str)
                if daily_avg is not None:
                    day_usage.extend(daily_avg['usage'].dropna().tolist())
            
            if day_usage:
                daily_data.append(day_usage)
                daily_labels.append(date.strftime('%m-%d'))
        
        if daily_data:
            box_plot = ax4.boxplot(daily_data)
            ax4.set_xticklabels(daily_labels)
            ax4.set_title('每日 GPU 使用率箱線圖', fontsize=14, fontweight='bold')
            ax4.set_xlabel('日期')
            ax4.set_ylabel('GPU 使用率 (%)')
            ax4.grid(True, alpha=0.3)
            plt.setp(ax4.get_xticklabels(), rotation=45)
        
        plt.suptitle(f'GPU 使用率分析儀表板\n({start_date} 至 {end_date})', 
                    fontsize=18, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"儀表板已保存至: {save_path}")
        else:
            plt.show()
        
        plt.close()


def main():
    parser = argparse.ArgumentParser(description='AMD GPU 使用率趨勢視覺化工具')
    parser.add_argument('--data-dir', default='./data', help='數據目錄路徑')
    parser.add_argument('--output-dir', default='./plots', help='輸出目錄路徑')
    parser.add_argument('--start-date', required=True, help='開始日期 (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='結束日期 (YYYY-MM-DD)')
    parser.add_argument('--node', help='指定節點名稱')
    parser.add_argument('--gpu-id', type=int, help='指定 GPU ID')
    parser.add_argument('--plot-type', 
                       choices=['single', 'multi', 'nodes', 'heatmap', 'dashboard', 'all'],
                       default='all', help='圖表類型')
    
    args = parser.parse_args()
    
    # 創建視覺化器
    visualizer = GPUTrendVisualizer(args.data_dir)
    
    # 創建輸出目錄
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 驗證日期
    try:
        datetime.strptime(args.start_date, '%Y-%m-%d')
        datetime.strptime(args.end_date, '%Y-%m-%d')
    except ValueError:
        print("錯誤: 日期格式不正確，應為 YYYY-MM-DD")
        return
    
    print(f"開始生成 GPU 使用率趨勢圖...")
    print(f"數據目錄: {args.data_dir}")
    print(f"輸出目錄: {args.output_dir}")
    print(f"日期範圍: {args.start_date} 至 {args.end_date}")
    
    if args.plot_type in ['single', 'all'] and args.node and args.gpu_id:
        save_path = os.path.join(args.output_dir, 
                                f'{args.node}_gpu{args.gpu_id}_{args.start_date}_to_{args.end_date}.png')
        visualizer.plot_single_gpu_trend(args.node, args.gpu_id, 
                                        args.start_date, args.end_date, save_path)
    
    if args.plot_type in ['multi', 'all'] and args.node:
        # 為每一天生成多 GPU 對比圖
        dates = pd.date_range(start=args.start_date, end=args.end_date, freq='D')
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            save_path = os.path.join(args.output_dir, 
                                   f'{args.node}_multi_gpu_{date_str}.png')
            visualizer.plot_multi_gpu_comparison(args.node, date_str, save_path)
    
    if args.plot_type in ['nodes', 'all']:
        save_path = os.path.join(args.output_dir, 
                                f'nodes_comparison_{args.start_date}_to_{args.end_date}.png')
        visualizer.plot_node_comparison(args.start_date, args.end_date, save_path)
    
    if args.plot_type in ['heatmap', 'all']:
        save_path = os.path.join(args.output_dir, 
                                f'heatmap_{args.start_date}_to_{args.end_date}.png')
        visualizer.plot_heatmap(args.start_date, args.end_date, save_path)
    
    if args.plot_type in ['dashboard', 'all']:
        save_path = os.path.join(args.output_dir, 
                                f'dashboard_{args.start_date}_to_{args.end_date}.png')
        visualizer.create_summary_dashboard(args.start_date, args.end_date, save_path)
    
    print("圖表生成完成！")


if __name__ == "__main__":
    main()
