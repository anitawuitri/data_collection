#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查詢特定使用者的 GPU 使用率工具

此腳本可以查詢指定使用者在特定日期或日期範圍內的 GPU 使用情況，
包括使用率、VRAM 使用量、使用的節點和 GPU 編號等資訊。

使用範例:
    python3 get_user_gpu_usage.py paslab_openai 2025-09-15
    python3 get_user_gpu_usage.py paslab_openai 2025-09-10 2025-09-15
    python3 get_user_gpu_usage.py --list-users 2025-09-15
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import csv

# 嘗試導入可選的套件
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("⚠️  未安裝 pandas，將使用基本功能")

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
    
    # 添加 visualization 目錄到 path
    sys.path.append(os.path.join(os.path.dirname(__file__), 'visualization'))
    try:
        from font_config import setup_chinese_font
        HAS_FONT_CONFIG = True
    except ImportError:
        HAS_FONT_CONFIG = False
        
except ImportError:
    HAS_PLOTTING = False
    HAS_FONT_CONFIG = False

class UserGPUUsageQuery:
    """查詢使用者 GPU 使用率的工具類"""
    
    def __init__(self, data_dir="./data", plots_dir="./plots"):
        self.data_dir = Path(data_dir)
        self.plots_dir = Path(plots_dir)
        self.plots_dir.mkdir(exist_ok=True)
        
        # 節點配置
        self.nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
        
        # 設定中文字體
        if HAS_FONT_CONFIG:
            setup_chinese_font()
        
    def load_gpu_data_with_users_basic(self, csv_file):
        """使用基本 csv 模組載入 GPU 數據（不依賴 pandas）"""
        if not os.path.exists(csv_file):
            return None
            
        try:
            data = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 標準化欄位名稱
                    if 'GPU編號' in row:
                        standardized_row = {
                            'gpu': row['GPU編號'],
                            'usage': float(row['平均GPU使用率(%)']),
                            'vram_usage': float(row['平均VRAM使用率(%)']),
                            'user': row['使用者']
                        }
                    else:
                        standardized_row = row
                    data.append(standardized_row)
            return data
        except Exception as e:
            print(f"載入檔案時發生錯誤 {csv_file}: {e}")
            return None
    
    def load_gpu_data_with_users(self, csv_file):
        """載入包含使用者資訊的 GPU 數據"""
        if HAS_PANDAS:
            return self.load_gpu_data_with_users_pandas(csv_file)
        else:
            return self.load_gpu_data_with_users_basic(csv_file)
    
    def load_gpu_data_with_users_pandas(self, csv_file):
        """使用 pandas 載入 GPU 數據"""
        if not os.path.exists(csv_file):
            return None
            
        try:
            df = pd.read_csv(csv_file)
            
            # 檢查欄位名稱並標準化
            if 'GPU編號' in df.columns:
                df = df.rename(columns={
                    'GPU編號': 'gpu',
                    '平均GPU使用率(%)': 'usage',
                    '平均VRAM使用率(%)': 'vram_usage',
                    '使用者': 'user'
                })
            
            return df
        except Exception as e:
            print(f"載入檔案時發生錯誤 {csv_file}: {e}")
            return None
    
    def get_date_range(self, start_date, end_date=None):
        """取得日期範圍"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end = start
            
        dates = []
        current = start
        while current <= end:
            dates.append(current)
            current += timedelta(days=1)
            
        return dates
    
    def query_user_gpu_usage(self, username, start_date, end_date=None):
        """
        查詢特定使用者的 GPU 使用情況
        
        Args:
            username (str): 使用者名稱
            start_date (str): 開始日期 (YYYY-MM-DD)
            end_date (str): 結束日期 (YYYY-MM-DD)，可選
            
        Returns:
            list: 包含使用者 GPU 使用紀錄的列表
        """
        dates = self.get_date_range(start_date, end_date)
        user_records = []
        
        print(f"🔍 查詢使用者 '{username}' 的 GPU 使用情況...")
        print(f"📅 日期範圍: {start_date} 至 {end_date if end_date else start_date}")
        print("=" * 60)
        
        for node in self.nodes:
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                daily_found = False
                
                avg_file = self.data_dir / node / date_str / f"average_{date_str}.csv"
                data = self.load_gpu_data_with_users(avg_file)
                
                if data is not None:
                    # 過濾該使用者的記錄 (處理 pandas DataFrame 或基本列表)
                    if HAS_PANDAS and isinstance(data, pd.DataFrame):
                        user_data = data[data['user'] == username]
                        user_rows = user_data.to_dict('records')
                    else:
                        user_rows = [row for row in data if row['user'] == username]
                    
                    if user_rows:
                        daily_found = True
                        
                        for row in user_rows:
                            record = {
                                'date': date_str,
                                'node': node,
                                'gpu': row['gpu'],
                                'gpu_usage': float(row['usage']),
                                'vram_usage': float(row['vram_usage']),
                                'user': row['user']
                            }
                            user_records.append(record)
            
            if not daily_found:
                print(f"📊 {date_str}: 未找到使用者 '{username}' 的 GPU 使用記錄")
        
        return user_records
    
    def display_user_usage_summary(self, records):
        """顯示使用者 GPU 使用摘要"""
        if not records:
            print("❌ 未找到任何使用記錄")
            return
        
        print(f"\n📈 找到 {len(records)} 筆使用記錄:")
        print("-" * 60)
        
        for record in records:
            status_emoji = "🟢" if record['gpu_usage'] > 1 else "🟡"
            print(f"{status_emoji} {record['date']} | {record['node']} | {record['gpu']}")
            print(f"   GPU使用率: {record['gpu_usage']:.2f}%")
            print(f"   VRAM使用率: {record['vram_usage']:.2f}%")
            print()
        
        # 計算統計資訊
        if records:
            total_records = len(records)
            active_records = [r for r in records if r['gpu_usage'] > 1]
            
            avg_gpu_usage = sum(r['gpu_usage'] for r in records) / total_records
            avg_vram_usage = sum(r['vram_usage'] for r in records) / total_records
            
            max_gpu_usage = max(r['gpu_usage'] for r in records)
            max_vram_usage = max(r['vram_usage'] for r in records)
            
            print("📊 統計摘要:")
            print(f"   總記錄數: {total_records}")
            print(f"   有活動記錄數: {len(active_records)} ({len(active_records)/total_records*100:.1f}%)")
            print(f"   平均 GPU 使用率: {avg_gpu_usage:.2f}%")
            print(f"   平均 VRAM 使用率: {avg_vram_usage:.2f}%")
            print(f"   最大 GPU 使用率: {max_gpu_usage:.2f}%")
            print(f"   最大 VRAM 使用率: {max_vram_usage:.2f}%")
            
            # 使用的節點和 GPU 統計
            nodes_used = list(set(r['node'] for r in records))
            gpus_used = list(set(f"{r['node']}:{r['gpu']}" for r in records))
            
            print(f"   使用的節點: {', '.join(nodes_used)}")
            print(f"   使用的 GPU: {len(gpus_used)} 個")
    
    def plot_user_gpu_trends(self, records, username):
        """繪製使用者 GPU 使用趨勢圖"""
        if not HAS_PLOTTING:
            print("⚠️  未安裝 matplotlib/seaborn，無法生成圖表")
            return None
            
        if not records:
            print("❌ 沒有資料可繪製")
            return None
            
        # 準備資料
        if HAS_PANDAS:
            df = pd.DataFrame(records)
            df['datetime'] = pd.to_datetime(df['date'])
            df['node_gpu'] = df['node'] + ':' + df['gpu']
        else:
            # 不使用 pandas 的基本處理
            print("⚠️  建議安裝 pandas 以獲得更好的圖表功能")
        
        # 創建圖表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # 準備數據結構
        date_usage_map = defaultdict(lambda: defaultdict(list))
        for record in records:
            node_gpu = f"{record['node']}:{record['gpu']}"
            date_usage_map[record['date']][node_gpu].append({
                'gpu_usage': record['gpu_usage'],
                'vram_usage': record['vram_usage']
            })
        
        # 繪製 GPU 使用率趨勢
        node_gpu_data = defaultdict(lambda: {'dates': [], 'gpu_usage': [], 'vram_usage': []})
        
        for date_str in sorted(date_usage_map.keys()):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            for node_gpu, usage_list in date_usage_map[date_str].items():
                avg_gpu = sum(u['gpu_usage'] for u in usage_list) / len(usage_list)
                avg_vram = sum(u['vram_usage'] for u in usage_list) / len(usage_list)
                
                node_gpu_data[node_gpu]['dates'].append(date_obj)
                node_gpu_data[node_gpu]['gpu_usage'].append(avg_gpu)
                node_gpu_data[node_gpu]['vram_usage'].append(avg_vram)
        
        # 繪製 GPU 使用率
        for node_gpu, data in node_gpu_data.items():
            ax1.plot(data['dates'], data['gpu_usage'], 
                    marker='o', label=node_gpu, linewidth=2)
        
        ax1.set_title(f"{username} GPU 使用率趨勢", fontsize=16, fontweight='bold')
        ax1.set_ylabel("GPU 使用率 (%)", fontsize=12)
        ax1.set_ylim(0, 100)
        ax1.grid(True, alpha=0.3)
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 繪製 VRAM 使用率
        for node_gpu, data in node_gpu_data.items():
            ax2.plot(data['dates'], data['vram_usage'], 
                    marker='s', label=node_gpu, linewidth=2)
        
        ax2.set_title(f"{username} VRAM 使用率趨勢", fontsize=16, fontweight='bold')
        ax2.set_xlabel("日期", fontsize=12)
        ax2.set_ylabel("VRAM 使用率 (%)", fontsize=12)
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        
        # 保存圖表
        filename = f"user_gpu_trends_{username}_{records[0]['date']}"
        if len(records) > 1:
            filename += f"_to_{records[-1]['date']}"
        filename += ".png"
        
        output_path = self.plots_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"📊 趨勢圖已保存至: {output_path}")
        
        plt.close()
        return str(output_path)
    
    def list_all_users(self, date):
        """列出指定日期所有使用 GPU 的使用者"""
        date_str = date
        all_users = set()
        user_details = defaultdict(list)
        
        print(f"📋 {date_str} 的所有 GPU 使用者:")
        print("=" * 50)
        
        for node in self.nodes:
            avg_file = self.data_dir / node / date_str / f"average_{date_str}.csv"
            data = self.load_gpu_data_with_users(avg_file)
            
            if data is not None:
                # 過濾活動使用者 (處理 pandas DataFrame 或基本列表)
                if HAS_PANDAS and isinstance(data, pd.DataFrame):
                    active_users = data[
                        (data['user'] != '未使用') & 
                        (~data['gpu'].str.contains('全部平均', na=False)) &
                        (pd.to_numeric(data['usage'], errors='coerce') > 1)
                    ]
                    active_rows = active_users.to_dict('records')
                else:
                    active_rows = [
                        row for row in data 
                        if (row['user'] != '未使用' and 
                            '全部平均' not in row['gpu'] and 
                            float(row['usage']) > 1)
                    ]
                
                for row in active_rows:
                    username = row['user']
                    all_users.add(username)
                    user_details[username].append({
                        'node': node,
                        'gpu': row['gpu'],
                        'gpu_usage': float(row['usage']),
                        'vram_usage': float(row['vram_usage'])
                    })
        
        if not all_users:
            print("❌ 未找到任何活動使用者")
            return []
        
        # 顯示使用者詳情
        for username in sorted(all_users):
            print(f"\n👤 {username}:")
            total_gpu_usage = 0
            total_vram_usage = 0
            
            for detail in user_details[username]:
                print(f"   📍 {detail['node']}:{detail['gpu']} - "
                      f"GPU: {detail['gpu_usage']:.1f}%, "
                      f"VRAM: {detail['vram_usage']:.1f}%")
                total_gpu_usage += detail['gpu_usage']
                total_vram_usage += detail['vram_usage']
            
            avg_gpu = total_gpu_usage / len(user_details[username])
            avg_vram = total_vram_usage / len(user_details[username])
            print(f"   📊 平均: GPU {avg_gpu:.1f}%, VRAM {avg_vram:.1f}% "
                  f"({len(user_details[username])} GPU)")
        
        return sorted(all_users)


def main():
    parser = argparse.ArgumentParser(
        description="查詢特定使用者的 GPU 使用率",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # 查詢特定使用者單日使用情況
  python3 get_user_gpu_usage.py paslab_openai 2025-09-15
  
  # 查詢特定使用者多日使用情況
  python3 get_user_gpu_usage.py paslab_openai 2025-09-10 2025-09-15
  
  # 列出指定日期的所有使用者
  python3 get_user_gpu_usage.py --list-users 2025-09-15
  
  # 生成使用者趨勢圖
  python3 get_user_gpu_usage.py paslab_openai 2025-09-10 2025-09-15 --plot
        """
    )
    
    parser.add_argument('username', nargs='?', help='使用者名稱')
    parser.add_argument('start_date', help='開始日期 (YYYY-MM-DD)')
    parser.add_argument('end_date', nargs='?', help='結束日期 (YYYY-MM-DD)，可選')
    parser.add_argument('--list-users', action='store_true', 
                       help='列出指定日期的所有使用者')
    parser.add_argument('--plot', action='store_true', 
                       help='生成使用者 GPU 使用趨勢圖')
    parser.add_argument('--data-dir', default='./data', 
                       help='資料目錄路徑，預設為 ./data')
    parser.add_argument('--plots-dir', default='./plots', 
                       help='圖表輸出目錄，預設為 ./plots')
    
    args = parser.parse_args()
    
    # 驗證日期格式
    try:
        datetime.strptime(args.start_date, '%Y-%m-%d')
        if args.end_date:
            datetime.strptime(args.end_date, '%Y-%m-%d')
    except ValueError:
        print("❌ 日期格式錯誤，請使用 YYYY-MM-DD 格式")
        return
    
    # 建立查詢工具
    query_tool = UserGPUUsageQuery(args.data_dir, args.plots_dir)
    
    if args.list_users:
        # 列出所有使用者
        users = query_tool.list_all_users(args.start_date)
        print(f"\n📈 總共找到 {len(users)} 位使用者")
        
    elif args.username:
        # 查詢特定使用者
        records = query_tool.query_user_gpu_usage(
            args.username, args.start_date, args.end_date
        )
        
        # 顯示摘要
        query_tool.display_user_usage_summary(records)
        
        # 生成趨勢圖
        if args.plot and records:
            query_tool.plot_user_gpu_trends(records, args.username)
            
    else:
        print("❌ 請指定使用者名稱或使用 --list-users")
        parser.print_help()


if __name__ == "__main__":
    main()