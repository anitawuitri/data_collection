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
    def __init__(self, data_dir=None, plots_dir=None):
        """
        初始化 VRAM 監控器
        
        Args:
            data_dir (str): 數據目錄路徑
            plots_dir (str): 圖表輸出目錄路徑
        """
        # 自動偵測目錄路徑
        if data_dir is None:
            if os.path.exists("./data"):
                data_dir = "./data"
            elif os.path.exists("../data"):
                data_dir = "../data"
            else:
                data_dir = "./data"
                
        if plots_dir is None:
            if os.path.exists("./plots"):
                plots_dir = "./plots"
            elif os.path.exists("../plots"):
                plots_dir = "../plots"
            else:
                plots_dir = "./plots"
        
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
        
    def load_vram_data_with_users(self, csv_file):
        """
        載入包含使用者資訊的 VRAM 資料
        
        Args:
            csv_file (str): CSV 檔案路徑
            
        Returns:
            pd.DataFrame: 包含 VRAM 使用率和使用者資訊的資料
        """
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            # 處理新的 CSV 格式（包含使用者資訊）
            if 'GPU編號' in df.columns and '平均VRAM使用率(%)' in df.columns:
                df = df.rename(columns={
                    'GPU編號': 'gpu',
                    '平均GPU使用率(%)': 'gpu_usage',
                    '平均VRAM使用率(%)': 'vram_usage',
                    '使用者': 'user'
                })
            
            # 過濾掉 "全部平均" 行
            df = df[~df['gpu'].str.contains('全部平均', na=False)]
            
            # 提取 GPU 編號
            df['gpu_id'] = df['gpu'].str.extract(r'(\d+)').astype(int)
            df['vram_usage'] = pd.to_numeric(df['vram_usage'], errors='coerce')
            
            # 確保有使用者資訊欄位
            if 'user' not in df.columns:
                df['user'] = '未知'
                
            return df
            
        except Exception as e:
            print(f"載入檔案 {csv_file} 時發生錯誤: {e}")
            return None
    
    def get_vram_user_info_for_node(self, node, date, data_dir=None):
        """
        獲取特定節點在特定日期的 VRAM 使用者資訊
        
        Args:
            node (str): 節點名稱
            date (str): 日期 (YYYY-MM-DD)
            data_dir (str): 資料目錄
            
        Returns:
            dict: GPU編號對應使用者名稱的字典
        """
        if data_dir is None:
            data_dir = self.data_dir
            
        csv_file = os.path.join(data_dir, node, date, f"average_{date}.csv")
        
        user_info = {}
        df = self.load_vram_data_with_users(csv_file)
        
        if df is not None:
            for _, row in df.iterrows():
                gpu_id = row['gpu_id']
                user = row['user']
                if pd.notna(user) and user != '未使用':
                    user_info[f"GPU[{gpu_id}]"] = user
                    
        return user_info
        
    def collect_vram_data(self, node, gpu_id, date_str=None):
        """
        從現有 CSV 檔案收集指定節點和 GPU 的 VRAM 使用量數據
        
        Args:
            node (str): 節點名稱
            gpu_id (int): GPU ID
            date_str (str): 日期 (YYYY-MM-DD)，預設為今天
            
        Returns:
            pd.DataFrame: VRAM 使用量數據
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
            
        if node not in self.nodes:
            print(f"未知節點: {node}")
            return pd.DataFrame()
            
        try:
            # 構建 CSV 檔案路徑
            csv_file = os.path.join(self.data_dir, node, date_str, f'gpu{gpu_id}_{date_str}.csv')
            
            if not os.path.exists(csv_file):
                print(f"找不到 CSV 檔案: {csv_file}")
                return pd.DataFrame()
                
            # 讀取 CSV 檔案
            df = pd.read_csv(csv_file)
            
            # 檢查必要的欄位
            if 'VRAM使用率(%)' not in df.columns:
                print(f"CSV 檔案中沒有 VRAM使用率(%) 欄位: {csv_file}")
                return pd.DataFrame()
                
            if '日期時間' not in df.columns:
                print(f"CSV 檔案中沒有 日期時間 欄位: {csv_file}")
                return pd.DataFrame()
            
            # 轉換時間格式
            df['datetime'] = pd.to_datetime(df['日期時間'])
            df['vram_usage'] = df['VRAM使用率(%)']
            
            # 只保留需要的欄位
            result_df = df[['datetime', 'vram_usage']].copy()
            result_df = result_df.dropna()
            
            print(f"成功從 {csv_file} 載入 {len(result_df)} 筆 VRAM 資料")
            return result_df
            
        except Exception as e:
            print(f"收集 {node} GPU {gpu_id} VRAM 數據時發生錯誤: {e}")
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
        df = self.collect_vram_data(node, gpu_id, date_str)
            
        if df.empty:
            print(f"沒有 {node} GPU {gpu_id} 在 {date_str} 的 VRAM 數據")
            return None
            
        fig, ax = plt.subplots(1, 1, figsize=(15, 8))
        
        # VRAM 使用率圖表
        ax.plot(df['datetime'], df['vram_usage'], label=f'{node} GPU {gpu_id} VRAM 使用率', 
                color='#1f77b4', linewidth=2)
        ax.fill_between(df['datetime'], df['vram_usage'], alpha=0.3, color='#1f77b4')
        
        ax.set_title(f'{node} GPU {gpu_id} VRAM 使用率時間序列 - {date_str}', fontsize=16, fontweight='bold')
        ax.set_xlabel('時間', fontsize=12)
        ax.set_ylabel('VRAM 使用率 (%)', fontsize=12)
        ax.set_ylim(0, max(100, df['vram_usage'].max() * 1.1) if not df.empty else 100)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 格式化 x 軸
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
                    # 直接使用原始 CSV 檔案，不是 vram 特定檔案
                    csv_file = os.path.join(self.data_dir, node, date_str, f"gpu{gid}_{date_str}.csv")
                    
                    if os.path.exists(csv_file):
                        try:
                            df = pd.read_csv(csv_file)
                            if not df.empty and 'VRAM使用率(%)' in df.columns:
                                avg_percent = df['VRAM使用率(%)'].mean()
                                daily_vram_percent.append(avg_percent)
                                # 假設 VRAM 總量為 80GB (MI250X)，計算使用量
                                avg_used = avg_percent * 80 / 100
                                daily_vram_used.append(avg_used)
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

    def plot_vram_heatmap(self, start_date, end_date, show_users=True):
        """
        繪製 VRAM 使用率熱力圖（包含使用者資訊）
        
        Args:
            start_date (str): 開始日期
            end_date (str): 結束日期
            show_users (bool): 是否顯示使用者資訊
        """
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 創建數據矩陣和使用者資訊
        vram_data = []
        row_labels = []
        user_info = {}  # 儲存每個GPU的使用者資訊
        
        for node in self.nodes:
            for gpu_id in self.gpu_ids:
                daily_usage = []
                gpu_key = f"{node}_GPU{gpu_id}"
                
                for date in dates:
                    date_str = date.strftime('%Y-%m-%d')
                    # 使用原始 CSV 檔案，不是 vram 特定檔案
                    csv_file = os.path.join(self.data_dir, node, date_str, f"gpu{gpu_id}_{date_str}.csv")
                    
                    if os.path.exists(csv_file):
                        try:
                            df = pd.read_csv(csv_file)
                            if not df.empty and 'VRAM使用率(%)' in df.columns:
                                avg_usage = df['VRAM使用率(%)'].mean()
                                daily_usage.append(avg_usage)
                            else:
                                daily_usage.append(0)
                        except:
                            daily_usage.append(0)
                    else:
                        daily_usage.append(0)
                    
                    # 收集使用者資訊（從 average 檔案）
                    if show_users:
                        avg_file = os.path.join(self.data_dir, node, date_str, f"average_{date_str}.csv")
                        if os.path.exists(avg_file):
                            try:
                                avg_df = pd.read_csv(avg_file)
                                if not avg_df.empty and '使用者' in avg_df.columns and 'GPU編號' in avg_df.columns:
                                    # 找到對應的 GPU 編號
                                    gpu_row = avg_df[avg_df['GPU編號'] == f'GPU[{gpu_id // 8}]']
                                    if not gpu_row.empty and not pd.isna(gpu_row['使用者'].iloc[0]):
                                        user = gpu_row['使用者'].iloc[0]
                                        if gpu_key not in user_info:
                                            user_info[gpu_key] = set()
                                        user_info[gpu_key].add(user)
                            except Exception as e:
                                pass  # 忽略讀取錯誤
                
                vram_data.append(daily_usage)
                
                # 創建包含使用者資訊的標籤
                if show_users and gpu_key in user_info and len(user_info[gpu_key]) > 0:
                    users_str = ', '.join(sorted(user_info[gpu_key])[:3])  # 最多顯示3個使用者
                    if len(user_info[gpu_key]) > 3:
                        users_str += f" (+{len(user_info[gpu_key])-3})"
                    row_labels.append(f"{node}\nGPU {gpu_id}\n[{users_str}]")
                else:
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
        
        # 設定標題
        title = f'GPU VRAM 使用率熱力圖\n期間: {start_date} 至 {end_date}'
        if show_users:
            title += '\n(包含使用者資訊)'
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('節點 & GPU', fontsize=12)
        
        plt.tight_layout()
        
        # 檔案名稱包含使用者資訊標記
        filename = f'vram_heatmap_{start_date}_to_{end_date}'
        if show_users:
            filename += '_with_users'
        save_path = os.path.join(self.plots_dir, f'{filename}.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"VRAM 熱力圖已保存至: {save_path}")
        return save_path
        
        return save_path
    
    def plot_vram_user_activity_summary(self, start_date, end_date, save_plot=True):
        """
        繪製 VRAM 使用者活動摘要圖表
        
        Args:
            start_date (str): 開始日期 (YYYY-MM-DD)
            end_date (str): 結束日期 (YYYY-MM-DD)
            save_plot (bool): 是否保存圖表
            
        Returns:
            str: 保存的圖片路徑
        """
        # 收集所有節點的使用者 VRAM 資訊
        all_user_data = []
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        for node in self.nodes:
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                user_info = self.get_vram_user_info_for_node(node, date_str)
                
                csv_file = os.path.join(self.data_dir, node, date_str, f"average_{date_str}.csv")
                df = self.load_vram_data_with_users(csv_file)
                
                if df is not None:
                    for _, row in df.iterrows():
                        if pd.notna(row['user']) and row['user'] != '未使用':
                            all_user_data.append({
                                'node': node,
                                'gpu': f"GPU[{row['gpu_id']}]",
                                'date': date_str,
                                'user': row['user'],
                                'vram_usage': row['vram_usage']
                            })
        
        if not all_user_data:
            print("未找到使用者 VRAM 資料")
            return None
        
        df_users = pd.DataFrame(all_user_data)
        
        # 統計每個使用者的 VRAM 使用情況
        user_stats = df_users.groupby('user').agg({
            'vram_usage': ['mean', 'max', 'count'],
            'node': lambda x: len(set(x)),  # 使用的節點數
            'gpu': lambda x: len(set(x))    # 使用的 GPU 數
        }).round(2)
        
        user_stats.columns = ['平均VRAM使用率', '最大VRAM使用率', '資料點數', '使用節點數', '使用GPU數']
        user_stats = user_stats.sort_values('平均VRAM使用率', ascending=False)
        
        # 創建圖表
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. 使用者平均 VRAM 使用率長條圖
        users = user_stats.index
        colors = plt.cm.Set3(np.linspace(0, 1, len(users)))
        
        bars = ax1.bar(users, user_stats['平均VRAM使用率'], color=colors)
        ax1.set_title('使用者平均 VRAM 使用率', fontsize=14, fontweight='bold')
        ax1.set_ylabel('VRAM 使用率 (%)', fontsize=12)
        ax1.set_xlabel('使用者', fontsize=12)
        plt.setp(ax1.get_xticklabels(), rotation=45)
        
        # 添加數值標籤
        for bar, value in zip(bars, user_stats['平均VRAM使用率']):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.2f}%', ha='center', va='bottom', fontsize=10)
        
        # 2. 使用者最大 VRAM 使用率長條圖
        bars = ax2.bar(users, user_stats['最大VRAM使用率'], color=colors)
        ax2.set_title('使用者最大 VRAM 使用率', fontsize=14, fontweight='bold')
        ax2.set_ylabel('VRAM 使用率 (%)', fontsize=12)
        ax2.set_xlabel('使用者', fontsize=12)
        plt.setp(ax2.get_xticklabels(), rotation=45)
        
        # 添加數值標籤
        for bar, value in zip(bars, user_stats['最大VRAM使用率']):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.2f}%', ha='center', va='bottom', fontsize=10)
        
        # 3. 使用者 GPU 數量圓餅圖
        ax3.pie(user_stats['使用GPU數'], labels=users, autopct='%1.0f個',
               colors=colors, startangle=90)
        ax3.set_title('使用者使用的 GPU 數量分佈', fontsize=14, fontweight='bold')
        
        # 4. 使用者節點分佈圓餅圖
        ax4.pie(user_stats['使用節點數'], labels=users, autopct='%1.0f個',
               colors=colors, startangle=90)
        ax4.set_title('使用者使用的節點數量分佈', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # 總標題
        fig.suptitle(f'VRAM 使用者活動摘要 ({start_date} 至 {end_date})', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        if save_plot:
            save_path = os.path.join(self.plots_dir, f'vram_user_activity_summary_{start_date}_to_{end_date}.png')
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"VRAM 使用者活動摘要圖已保存至: {save_path}")
            
        plt.show()
        plt.close()
        
        return save_path if save_plot else None
    
    def plot_vram_nodes_comparison_with_users(self, start_date, end_date, gpu_id=None, show_users=True):
        """
        繪製各節點 VRAM 使用量對比圖（包含使用者資訊）
        
        Args:
            start_date (str): 開始日期
            end_date (str): 結束日期
            gpu_id (int): 特定 GPU ID，None 表示使用所有 GPU 平均
            show_users (bool): 是否顯示使用者資訊
            
        Returns:
            str: 保存的圖片路徑
        """
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        all_data = []
        user_summary = {}
        
        for node in self.nodes:
            node_data = []
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                
                # 獲取使用者資訊
                if show_users:
                    user_info = self.get_vram_user_info_for_node(node, date_str)
                    for gpu, user in user_info.items():
                        if user not in user_summary:
                            user_summary[user] = 0
                        user_summary[user] += 1
                
                # 載入 VRAM 資料
                csv_file = os.path.join(self.data_dir, node, date_str, f"average_{date_str}.csv")
                df = self.load_vram_data_with_users(csv_file)
                
                if df is not None:
                    if gpu_id is not None:
                        # 特定 GPU
                        gpu_data = df[df['gpu_id'] == gpu_id]
                        if not gpu_data.empty:
                            node_data.append(gpu_data['vram_usage'].iloc[0])
                        else:
                            node_data.append(0)
                    else:
                        # 所有 GPU 平均
                        avg_usage = df['vram_usage'].mean()
                        node_data.append(avg_usage)
                else:
                    node_data.append(0)
            
            all_data.append(node_data)
        
        # 繪製圖表
        fig, ax = plt.subplots(figsize=(14, 8))
        
        date_labels = [date.strftime('%m-%d') for date in dates]
        
        for i, (node, data) in enumerate(zip(self.nodes, all_data)):
            color = self.colors[i % len(self.colors)]
            ax.plot(date_labels, data, 'o-', label=node, color=color, linewidth=2, markersize=6)
        
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('VRAM 使用率 (%)', fontsize=12)
        ax.set_ylim(0, max(100, max([max(data) for data in all_data if data]) * 1.1))
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=11)
        
        # 設定標題
        if gpu_id is not None:
            title = f'GPU {gpu_id} VRAM 使用率跨節點比較\n期間: {start_date} 至 {end_date}'
        else:
            title = f'所有 GPU 平均 VRAM 使用率跨節點比較\n期間: {start_date} 至 {end_date}'
        
        # 添加使用者資訊到標題
        if show_users and user_summary:
            user_summary_str = ', '.join([f"{user}({count})" for user, count in user_summary.items()])
            title += f'\n使用者: {user_summary_str}'
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if gpu_id is not None:
            suffix = '_with_users' if show_users else ''
            save_path = os.path.join(self.plots_dir, f'vram_nodes_comparison_gpu{gpu_id}_{start_date}_to_{end_date}{suffix}.png')
        else:
            suffix = '_with_users' if show_users else ''
            save_path = os.path.join(self.plots_dir, f'vram_nodes_comparison_all_gpus_{start_date}_to_{end_date}{suffix}.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"VRAM 節點對比圖已保存至: {save_path}")
        
        plt.show()
        plt.close()
        
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
