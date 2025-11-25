"""簡化的 GPU 繪圖工具

去掉原來 1200+ 行代碼的複雜性，直接幹活。
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union

from .font_utils import setup_chinese_font


class SimpleGPUPlotter:
    """簡化的 GPU 繪圖器
    
    不搞複雜的類繼承和抽象，直接完成繪圖任務。
    """
    
    def __init__(self, output_dir: str = './plots'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 設置字體
        self.font = setup_chinese_font()
        
        # 顏色配置
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
                      '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    
    def plot_node_comparison(self, data_dir: str, date_str: str, 
                           nodes: List[str] = None) -> str:
        """繪製節點對比圖
        
        Args:
            data_dir: 數據目錄
            date_str: 日期字符串
            nodes: 節點列表，None 表示自動發現
            
        Returns:
            生成的圖表文件路徑
        """
        data_path = Path(data_dir)
        
        if nodes is None:
            # 自動發現節點
            nodes = [d.name for d in data_path.iterdir() 
                    if d.is_dir() and d.name.startswith('colab-gpu')]
        
        node_data = []
        for node in nodes:
            avg_file = data_path / node / date_str / f"average_{date_str}.csv"
            if avg_file.exists():
                try:
                    df = pd.read_csv(avg_file)
                    if '全部平均' in df.iloc[:, 0].values:
                        avg_row = df[df.iloc[:, 0] == '全部平均']
                        gpu_avg = float(avg_row.iloc[0, 1])
                        vram_avg = float(avg_row.iloc[0, 2])
                        node_data.append({
                            'node': node,
                            'gpu_usage': gpu_avg,
                            'vram_usage': vram_avg
                        })
                except Exception as e:
                    print(f"警告: 無法讀取 {node} 數據: {e}")
        
        if not node_data:
            raise ValueError("未找到有效的節點數據")
        
        # 創建圖表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        nodes = [d['node'] for d in node_data]
        gpu_usage = [d['gpu_usage'] for d in node_data]
        vram_usage = [d['vram_usage'] for d in node_data]
        
        # GPU 使用率對比
        bars1 = ax1.bar(nodes, gpu_usage, color=self.colors[:len(nodes)])
        ax1.set_title(f'{date_str} GPU 使用率對比')
        ax1.set_ylabel('使用率 (%)')
        ax1.tick_params(axis='x', rotation=45)
        
        # 添加數值標籤
        for bar, val in zip(bars1, gpu_usage):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{val:.1f}%', ha='center', va='bottom')
        
        # VRAM 使用率對比  
        bars2 = ax2.bar(nodes, vram_usage, color=self.colors[:len(nodes)])
        ax2.set_title(f'{date_str} VRAM 使用率對比')
        ax2.set_ylabel('使用率 (%)')
        ax2.tick_params(axis='x', rotation=45)
        
        for bar, val in zip(bars2, vram_usage):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{val:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        
        output_file = self.output_dir / f'node_comparison_{date_str}.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_file)
    
    def plot_gpu_timeline(self, data_dir: str, node: str, date_str: str, 
                         gpu_index: int = None) -> str:
        """繪製 GPU 時間線圖
        
        Args:
            data_dir: 數據目錄
            node: 節點名稱
            date_str: 日期字符串
            gpu_index: GPU 索引，None 表示所有 GPU
            
        Returns:
            生成的圖表文件路徑
        """
        data_path = Path(data_dir) / node / date_str
        
        if not data_path.exists():
            raise ValueError(f"找不到數據目錄: {data_path}")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        if gpu_index is not None:
            # 單個 GPU
            gpu_files = [data_path / f"gpu{gpu_index}_{date_str}.csv"]
            labels = [f'GPU{gpu_index}']
        else:
            # 所有 GPU
            gpu_files = list(data_path.glob(f"gpu*_{date_str}.csv"))
            gpu_files.sort()
            labels = [f.stem.split('_')[0].upper() for f in gpu_files]
        
        for i, (gpu_file, label) in enumerate(zip(gpu_files, labels)):
            if not gpu_file.exists():
                continue
                
            try:
                df = pd.read_csv(gpu_file)
                df['時間'] = pd.to_datetime(df['日期時間'])
                
                color = self.colors[i % len(self.colors)]
                
                # GPU 使用率
                ax1.plot(df['時間'], df['GPU使用率(%)'], 
                        label=label, color=color, linewidth=1.5)
                
                # VRAM 使用率  
                ax2.plot(df['時間'], df['VRAM使用率(%)'], 
                        label=label, color=color, linewidth=1.5)
                
            except Exception as e:
                print(f"警告: 無法讀取 {gpu_file}: {e}")
        
        # 格式化時間軸
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        ax1.set_title(f'{node} GPU 使用率時間線 - {date_str}')
        ax1.set_ylabel('GPU 使用率 (%)')
        
        ax2.set_title(f'{node} VRAM 使用率時間線 - {date_str}')
        ax2.set_ylabel('VRAM 使用率 (%)')
        ax2.set_xlabel('時間')
        
        plt.tight_layout()
        
        suffix = f"_gpu{gpu_index}" if gpu_index is not None else "_all"
        output_file = self.output_dir / f'{node}_timeline_{date_str}{suffix}.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_file)
    
    def plot_user_usage(self, data_dir: str, date_str: str, 
                       nodes: List[str] = None) -> str:
        """繪製使用者使用情況圖
        
        Args:
            data_dir: 數據目錄
            date_str: 日期字符串  
            nodes: 節點列表
            
        Returns:
            生成的圖表文件路徑
        """
        data_path = Path(data_dir)
        
        if nodes is None:
            nodes = [d.name for d in data_path.iterdir() 
                    if d.is_dir() and d.name.startswith('colab-gpu')]
        
        user_data = {}
        
        for node in nodes:
            avg_file = data_path / node / date_str / f"average_{date_str}.csv"
            if avg_file.exists():
                try:
                    df = pd.read_csv(avg_file)
                    
                    # 檢查是否有使用者列
                    if '使用者' in df.columns or len(df.columns) > 3:
                        user_col = '使用者' if '使用者' in df.columns else df.columns[-1]
                        
                        for _, row in df.iterrows():
                            if row[df.columns[0]] == '全部平均':
                                continue
                                
                            user = row[user_col] if user_col in row else '未知'
                            if user not in ['未使用', '未知', '所有使用者']:
                                gpu_usage = float(row[df.columns[1]])  # GPU使用率
                                vram_usage = float(row[df.columns[2]])  # VRAM使用率
                                
                                if user not in user_data:
                                    user_data[user] = {'gpu': [], 'vram': [], 'gpus': []}
                                
                                user_data[user]['gpu'].append(gpu_usage)
                                user_data[user]['vram'].append(vram_usage)
                                user_data[user]['gpus'].append(f"{node}:{row[df.columns[0]]}")
                
                except Exception as e:
                    print(f"警告: 讀取 {node} 使用者數據失敗: {e}")
        
        if not user_data:
            print("未找到使用者數據")
            return ""
        
        # 創建圖表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        users = list(user_data.keys())
        gpu_avg = [np.mean(user_data[u]['gpu']) for u in users]
        vram_avg = [np.mean(user_data[u]['vram']) for u in users]
        
        # GPU 使用率
        bars1 = ax1.bar(users, gpu_avg, color=self.colors[:len(users)])
        ax1.set_title(f'{date_str} 使用者 GPU 使用率')
        ax1.set_ylabel('平均使用率 (%)')
        ax1.tick_params(axis='x', rotation=45)
        
        for bar, val in zip(bars1, gpu_avg):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{val:.1f}%', ha='center', va='bottom')
        
        # VRAM 使用率
        bars2 = ax2.bar(users, vram_avg, color=self.colors[:len(users)])
        ax2.set_title(f'{date_str} 使用者 VRAM 使用率')
        ax2.set_ylabel('平均使用率 (%)')
        ax2.tick_params(axis='x', rotation=45)
        
        for bar, val in zip(bars2, vram_avg):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{val:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        
        output_file = self.output_dir / f'user_usage_{date_str}.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_file)