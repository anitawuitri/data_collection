#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AMD GPU VRAM 使用量監控與視覺化工具

提供 GPU VRAM (顯示記憶體) 使用量的收集、分析和視覺化功能
支援多節點環境和多種圖表類型
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import os
import glob
import requests
import json
from pathlib import Path

# 導入字體配置模組
from font_config import setup_chinese_font

# 設定中文字體
setup_chinese_font()

class VRAMMonitor:
    def __init__(self, data_dir="../data", plots_dir="../plots"):
        """
        初始化 VRAM 監控器
        
        Args:
            data_dir (str): 數據目錄路徑
            plots_dir (str): 圖表輸出目錄路徑
        """
        # 轉換為絕對路徑
        self.data_dir = os.path.abspath(data_dir)
        self.plots_dir = os.path.abspath(plots_dir)
        self.nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
        self.node_ips = {
            'colab-gpu1': '192.168.10.103',
            'colab-gpu2': '192.168.10.104', 
            'colab-gpu3': '192.168.10.105',
            'colab-gpu4': '192.168.10.106'
        }
        self.gpu_ids = [1, 9, 17, 25, 33, 41, 49, 57]
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
        
        # 創建輸出目錄
        os.makedirs(self.plots_dir, exist_ok=True)
        
    def collect_vram_data(self, node, gpu_id, date_str=None):
        """
        從 Netdata 收集指定節點和 GPU 的 VRAM 使用量數據
        
        Args:
            node (str): 節點名稱
            gpu_id (int): GPU ID
            date_str (str): 日期 (YYYY-MM-DD)，預設為今天
            
        Returns:
            pd.DataFrame: VRAM 使用量數據
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
            
        if node not in self.node_ips:
            print(f"未知節點: {node}")
            return pd.DataFrame()
            
        ip = self.node_ips[node]
        
        try:
            # 計算時間範圍（當天的開始和結束）
            start_time = int(datetime.strptime(f"{date_str} 00:00:00", "%Y-%m-%d %H:%M:%S").timestamp())
            end_time = int(datetime.strptime(f"{date_str} 23:59:59", "%Y-%m-%d %H:%M:%S").timestamp())
            
            # Netdata API URL for VRAM usage
            # 假設 VRAM 數據在 amdgpu_mem chart 中
            url = f"http://{ip}:19999/api/v1/data"
            params = {
                'chart': f'amdgpu_mem.gpu{gpu_id}',
                'after': start_time,
                'before': end_time,
                'format': 'json',
                'points': 1440  # 每分鐘一個點，一天1440個點
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data:
                print(f"節點 {node} GPU {gpu_id} 沒有 VRAM 數據")
                return pd.DataFrame()
                
            # 解析數據
            timestamps = []
            vram_used = []
            vram_total = []
            
            for row in data['data']:
                timestamp = row[0]
                # 假設第一個值是已使用 VRAM，第二個值是總 VRAM
                if len(row) >= 3:
                    used = row[1] if row[1] is not None else 0
                    total = row[2] if row[2] is not None else 0
                    
                    timestamps.append(datetime.fromtimestamp(timestamp))
                    vram_used.append(used / (1024**3))  # 轉換為 GB
                    vram_total.append(total / (1024**3))  # 轉換為 GB
            
            if not timestamps:
                return pd.DataFrame()
                
            df = pd.DataFrame({
                'timestamp': timestamps,
                'vram_used_gb': vram_used,
                'vram_total_gb': vram_total,
                'vram_usage_percent': [used/total*100 if total > 0 else 0 for used, total in zip(vram_used, vram_total)]
            })
            
            return df
            
        except requests.RequestException as e:
            print(f"收集 {node} GPU {gpu_id} VRAM 數據時發生錯誤: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"處理 {node} GPU {gpu_id} VRAM 數據時發生錯誤: {e}")
            return pd.DataFrame()

    def save_vram_data(self, node, gpu_id, date_str=None):
        """
        收集並保存 VRAM 數據到 CSV 檔案
        
        Args:
            node (str): 節點名稱
            gpu_id (int): GPU ID
            date_str (str): 日期
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
            
        df = self.collect_vram_data(node, gpu_id, date_str)
        
        if df.empty:
            print(f"沒有收集到 {node} GPU {gpu_id} 的 VRAM 數據")
            return
            
        # 創建保存目錄
        save_dir = os.path.join(self.data_dir, node, date_str)
        os.makedirs(save_dir, exist_ok=True)
        
        # 保存 CSV 檔案
        csv_file = os.path.join(save_dir, f"gpu{gpu_id}_vram_{date_str}.csv")
        df.to_csv(csv_file, index=False)
        
        print(f"VRAM 數據已保存至: {csv_file}")
        
    def plot_vram_usage_timeline(self, node, gpu_id, date_str, save_plot=True):
        """
        繪製單一 GPU 的 VRAM 使用量時間序列圖
        
        Args:
            node (str): 節點名稱
            gpu_id (int): GPU ID
            date_str (str): 日期
            save_plot (bool): 是否保存圖表
            
        Returns:
            str: 圖表檔案路徑（如果保存）
        """
        # 嘗試從現有數據讀取
        csv_file = os.path.join(self.data_dir, node, date_str, f"gpu{gpu_id}_vram_{date_str}.csv")
        
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        else:
            df = self.collect_vram_data(node, gpu_id, date_str)
            
        if df.empty:
            print(f"沒有 {node} GPU {gpu_id} 在 {date_str} 的 VRAM 數據")
            return None
            
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # 上圖：VRAM 使用量 (GB)
        ax1.plot(df['timestamp'], df['vram_used_gb'], label='已使用 VRAM', color='#d62728', linewidth=2)
        ax1.plot(df['timestamp'], df['vram_total_gb'], label='總 VRAM', color='#2ca02c', linewidth=2, linestyle='--')
        ax1.fill_between(df['timestamp'], df['vram_used_gb'], alpha=0.3, color='#d62728')
        
        ax1.set_title(f'{node} GPU {gpu_id} VRAM 使用量 - {date_str}', fontsize=16, fontweight='bold')
        ax1.set_ylabel('VRAM (GB)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 下圖：VRAM 使用率 (%)
        ax2.plot(df['timestamp'], df['vram_usage_percent'], label='VRAM 使用率', color='#1f77b4', linewidth=2)
        ax2.fill_between(df['timestamp'], df['vram_usage_percent'], alpha=0.3, color='#1f77b4')
        
        ax2.set_title(f'{node} GPU {gpu_id} VRAM 使用率 - {date_str}', fontsize=16, fontweight='bold')
        ax2.set_xlabel('時間', fontsize=12)
        ax2.set_ylabel('VRAM 使用率 (%)', fontsize=12)
        ax2.set_ylim(0, 100)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 格式化 x 軸
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        if save_plot:
            save_path = os.path.join(self.plots_dir, f'{node}_gpu{gpu_id}_vram_{date_str}.png')
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"VRAM 使用量圖表已保存至: {save_path}")
            return save_path
        else:
            plt.show()
            return None

    def plot_nodes_vram_comparison(self, start_date, end_date, gpu_id=None):
        """
        繪製多節點 VRAM 使用量對比圖
        
        Args:
            start_date (str): 開始日期
            end_date (str): 結束日期  
            gpu_id (int): 指定 GPU ID，若為 None 則使用所有 GPU 的平均值
        """
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
        
        for i, node in enumerate(self.nodes):
            node_vram_used = []
            node_vram_percent = []
            valid_dates = []
            
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                
                if gpu_id is not None:
                    # 指定 GPU
                    gpus_to_check = [gpu_id]
                else:
                    # 所有 GPU
                    gpus_to_check = self.gpu_ids
                
                daily_vram_used = []
                daily_vram_percent = []
                
                for gid in gpus_to_check:
                    csv_file = os.path.join(self.data_dir, node, date_str, f"gpu{gid}_vram_{date_str}.csv")
                    
                    if os.path.exists(csv_file):
                        try:
                            df = pd.read_csv(csv_file)
                            if not df.empty:
                                avg_used = df['vram_used_gb'].mean()
                                avg_percent = df['vram_usage_percent'].mean()
                                daily_vram_used.append(avg_used)
                                daily_vram_percent.append(avg_percent)
                        except Exception as e:
                            print(f"讀取 {csv_file} 時發生錯誤: {e}")
                
                if daily_vram_used and daily_vram_percent:
                    node_vram_used.append(np.mean(daily_vram_used))
                    node_vram_percent.append(np.mean(daily_vram_percent))
                    valid_dates.append(date)
            
            if node_vram_used and node_vram_percent:
                color = self.colors[i % len(self.colors)]
                
                # VRAM 使用量 (GB)
                ax1.plot(valid_dates, node_vram_used, label=node, color=color, 
                        marker='o', linewidth=2.5, markersize=6)
                
                # VRAM 使用率 (%)
                ax2.plot(valid_dates, node_vram_percent, label=node, color=color,
                        marker='o', linewidth=2.5, markersize=6)
        
        # 設定圖表標題和標籤
        gpu_title = f"GPU {gpu_id}" if gpu_id is not None else "所有 GPU 平均"
        period_title = f"{start_date} 至 {end_date}"
        
        ax1.set_title(f'各節點 {gpu_title} VRAM 使用量對比\n期間: {period_title}', 
                     fontsize=16, fontweight='bold', pad=20)
        ax1.set_ylabel('VRAM 使用量 (GB)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        if ax1.get_lines():
            ax1.legend()
        
        ax2.set_title(f'各節點 {gpu_title} VRAM 使用率對比\n期間: {period_title}', 
                     fontsize=16, fontweight='bold', pad=20)
        ax2.set_xlabel('日期', fontsize=12)
        ax2.set_ylabel('VRAM 使用率 (%)', fontsize=12)
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)
        if ax2.get_lines():
            ax2.legend()
        
        # 格式化 x 軸
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        gpu_suffix = f"_gpu{gpu_id}" if gpu_id is not None else "_all_gpus"
        save_path = os.path.join(self.plots_dir, f'nodes_vram_comparison{gpu_suffix}_{start_date}_to_{end_date}.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"節點 VRAM 對比圖已保存至: {save_path}")
        return save_path

    def plot_vram_heatmap(self, start_date, end_date):
        """
        繪製 VRAM 使用率熱力圖
        
        Args:
            start_date (str): 開始日期
            end_date (str): 結束日期
        """
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 創建數據矩陣
        vram_data = []
        row_labels = []
        
        for node in self.nodes:
            for gpu_id in self.gpu_ids:
                daily_usage = []
                
                for date in dates:
                    date_str = date.strftime('%Y-%m-%d')
                    csv_file = os.path.join(self.data_dir, node, date_str, f"gpu{gpu_id}_vram_{date_str}.csv")
                    
                    if os.path.exists(csv_file):
                        try:
                            df = pd.read_csv(csv_file)
                            avg_usage = df['vram_usage_percent'].mean() if not df.empty else 0
                            daily_usage.append(avg_usage)
                        except:
                            daily_usage.append(0)
                    else:
                        daily_usage.append(0)
                
                vram_data.append(daily_usage)
                row_labels.append(f"{node}\nGPU {gpu_id}")
        
        if not vram_data:
            print("沒有可用的 VRAM 數據來生成熱力圖")
            return None
            
        # 創建熱力圖
        fig, ax = plt.subplots(figsize=(max(len(dates), 12), max(len(row_labels), 10)))
        
        vram_array = np.array(vram_data)
        
        # 創建熱力圖
        im = ax.imshow(vram_array, cmap='YlOrRd', aspect='auto', vmin=0, vmax=100)
        
        # 設定軸標籤
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels([date.strftime('%m-%d') for date in dates], rotation=45)
        ax.set_yticks(range(len(row_labels)))
        ax.set_yticklabels(row_labels)
        
        # 添加數值標籤
        for i in range(len(row_labels)):
            for j in range(len(dates)):
                if vram_array[i, j] > 0:
                    text = ax.text(j, i, f'{vram_array[i, j]:.1f}%',
                                 ha="center", va="center", color="black" if vram_array[i, j] < 50 else "white",
                                 fontsize=8)
        
        # 添加色彩條
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel('VRAM 使用率 (%)', rotation=-90, va="bottom", fontsize=12)
        
        ax.set_title(f'GPU VRAM 使用率熱力圖\n期間: {start_date} 至 {end_date}', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('節點 & GPU', fontsize=12)
        
        plt.tight_layout()
        
        save_path = os.path.join(self.plots_dir, f'vram_heatmap_{start_date}_to_{end_date}.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"VRAM 熱力圖已保存至: {save_path}")
        return save_path

def collect_all_vram_data(date_str=None):
    """
    收集所有節點所有 GPU 的 VRAM 數據
    
    Args:
        date_str (str): 日期，預設為今天
    """
    monitor = VRAMMonitor()
    
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    print(f"開始收集 {date_str} 的 VRAM 數據...")
    
    for node in monitor.nodes:
        for gpu_id in monitor.gpu_ids:
            print(f"收集 {node} GPU {gpu_id} VRAM 數據...")
            monitor.save_vram_data(node, gpu_id, date_str)
    
    print("VRAM 數據收集完成！")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='GPU VRAM 監控工具')
    parser.add_argument('--collect', action='store_true', help='收集今天的 VRAM 數據')
    parser.add_argument('--date', type=str, help='指定日期 (YYYY-MM-DD)')
    parser.add_argument('--node', type=str, help='節點名稱')
    parser.add_argument('--gpu', type=int, help='GPU ID')
    parser.add_argument('--start-date', type=str, help='開始日期')
    parser.add_argument('--end-date', type=str, help='結束日期')
    parser.add_argument('--plot-type', type=str, choices=['timeline', 'comparison', 'heatmap'], 
                       default='timeline', help='圖表類型')
    
    args = parser.parse_args()
    
    monitor = VRAMMonitor()
    
    if args.collect:
        collect_all_vram_data(args.date)
    elif args.plot_type == 'timeline' and args.node and args.gpu and args.date:
        monitor.plot_vram_usage_timeline(args.node, args.gpu, args.date)
    elif args.plot_type == 'comparison' and args.start_date and args.end_date:
        monitor.plot_nodes_vram_comparison(args.start_date, args.end_date, args.gpu)
    elif args.plot_type == 'heatmap' and args.start_date and args.end_date:
        monitor.plot_vram_heatmap(args.start_date, args.end_date)
    else:
        print("請提供正確的參數組合")
        parser.print_help()
