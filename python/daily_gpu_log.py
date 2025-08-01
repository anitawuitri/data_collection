#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AMD GPU 每日數據收集工具 (Python 版本)

改寫自 scripts/daily_gpu_log.sh，提供相同功能但使用 Python 實現：
- 從多個節點收集 GPU 使用率和 VRAM 使用率數據
- 支援指定日期或使用當前日期
- 自動計算平均值並生成摘要報告
- 輸出格式與原 shell 腳本完全相容
"""

import os
import sys
import json
import requests
import pandas as pd
import argparse
from datetime import datetime, timezone
from pathlib import Path
import time


class GPUDataCollector:
    """AMD GPU 數據收集器"""
    
    def __init__(self, data_dir="./data"):
        self.data_dir = Path(data_dir)
        
        # 節點配置
        self.ip_name_map = {
            "192.168.10.103": "colab-gpu1",
            "192.168.10.104": "colab-gpu2", 
            "192.168.10.105": "colab-gpu3",
            "192.168.10.106": "colab-gpu4"
        }
        
        # GPU 硬體對應表 (基於 gpu_hardware_mapping.txt)
        self.gpu_card_to_index = {
            1: 0, 9: 1, 17: 2, 25: 3,
            33: 4, 41: 5, 49: 6, 57: 7
        }
        self.gpu_index_to_card = {v: k for k, v in self.gpu_card_to_index.items()}
        
        # 使用 card IDs 進行 API 查詢，但輸出使用 GPU indices
        self.gpu_card_ids = [1, 9, 17, 25, 33, 41, 49, 57]
        self.gpu_indices = list(range(8))  # 0-7
        
        # 數據點設定：每10分鐘一個點，一天共144個點
        self.points = 144
        
        print(f"GPU 硬體對應: Card {self.gpu_card_ids} -> Index {self.gpu_indices}")
        print(f"使用 Card IDs 進行 API 查詢，檔案以 GPU Index 命名")
    
    def validate_date(self, date_str):
        """驗證日期格式"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def calculate_timestamps(self, date_str):
        """計算指定日期的開始和結束時間戳"""
        # 計算當天開始時間戳記 (00:00:00 UTC)
        start_dt = datetime.strptime(f"{date_str} 00:00:00", '%Y-%m-%d %H:%M:%S')
        start_dt = start_dt.replace(tzinfo=timezone.utc)
        timestamp_start = int(start_dt.timestamp())
        
        # 計算當天結束時間戳記 (23:59:59 UTC)
        end_dt = datetime.strptime(f"{date_str} 23:59:59", '%Y-%m-%d %H:%M:%S')
        end_dt = end_dt.replace(tzinfo=timezone.utc)
        timestamp_end = int(end_dt.timestamp())
        
        print(f"{date_str} 的時間戳記計算...")
        print(f"計算時間戳記: {timestamp_start} (UTC)")
        
        return timestamp_start, timestamp_end
    
    def fetch_netdata_data(self, host, chart, timestamp_start, timestamp_end):
        """從 Netdata API 獲取數據"""
        url = f"{host}/api/v1/data"
        params = {
            'chart': chart,
            'after': timestamp_start,
            'before': timestamp_end,
            'points': self.points,
            'group': 'average',
            'format': 'json'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"錯誤：無法從 {host} 獲取數據 {chart}: {e}")
            return None
    
    def process_gpu_data(self, ip, name, date_str, timestamp_start, timestamp_end):
        """處理單一節點的 GPU 數據"""
        ip_outdir = self.data_dir / name / date_str
        ip_outdir.mkdir(parents=True, exist_ok=True)
        
        netdata_host = f"http://{ip}:19999"
        
        print(f"正在處理 {name} ({ip})...")
        print(f"輸出目錄: {ip_outdir}")
        
        for card_id in self.gpu_card_ids:
            gpu_index = self.gpu_card_to_index[card_id]
            print(f"  處理 GPU[{gpu_index}] (Card {card_id})...")
            
            # 檔案路徑 (使用 GPU index 命名)
            tmp_csv = ip_outdir / f"gpu{gpu_index}_{date_str}.csv.tmp"
            final_csv = ip_outdir / f"gpu{gpu_index}_{date_str}.csv"
            
            # 獲取 GPU 使用率數據
            gpu_util_chart = f"amdgpu.gpu_utilization_unknown_AMD_GPU_card{card_id}"
            gpu_util_json = self.fetch_netdata_data(
                netdata_host, gpu_util_chart, timestamp_start, timestamp_end
            )
            
            # 獲取 VRAM 使用率數據
            vram_usage_chart = f"amdgpu.gpu_mem_vram_usage_perc_unknown_AMD_GPU_card{card_id}"
            vram_usage_json = self.fetch_netdata_data(
                netdata_host, vram_usage_chart, timestamp_start, timestamp_end
            )
            
            if not gpu_util_json or not vram_usage_json:
                print(f"    警告：GPU[{gpu_index}] (Card {card_id}) 數據獲取失敗，跳過")
                continue
            
            # 處理數據並寫入 CSV
            self.write_gpu_csv(gpu_util_json, vram_usage_json, tmp_csv, final_csv)
    
    def write_gpu_csv(self, gpu_util_json, vram_usage_json, tmp_csv, final_csv):
        """寫入 GPU 數據到 CSV 檔案"""
        # 創建臨時 CSV 並寫入標頭
        with open(tmp_csv, 'w', encoding='utf-8') as f:
            f.write("時間戳,日期時間,GPU使用率(%),VRAM使用率(%)\n")
            
            # 處理 GPU 使用率數據
            gpu_data = gpu_util_json.get('data', [])
            vram_data = vram_usage_json.get('data', [])
            
            # 建立 VRAM 數據的時間戳對照表
            vram_dict = {}
            for row in vram_data:
                if len(row) >= 2:
                    timestamp = row[0]
                    vram_value = row[1] if row[1] is not None else 0
                    vram_dict[timestamp] = vram_value
            
            # 處理每個時間點的數據
            csv_rows = []
            for row in gpu_data:
                if len(row) >= 2:
                    timestamp = row[0]
                    gpu_util = row[1] if row[1] is not None else 0
                    
                    # 轉換時間戳為日期時間字串
                    dt = datetime.fromtimestamp(timestamp)
                    datetime_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 獲取對應的 VRAM 使用率
                    vram_usage = vram_dict.get(timestamp, 0)
                    
                    # 儲存行資料
                    csv_rows.append((timestamp, datetime_str, gpu_util, vram_usage))
            
            # 按時間戳排序並寫入檔案
            csv_rows.sort(key=lambda x: x[0])
            for timestamp, datetime_str, gpu_util, vram_usage in csv_rows:
                f.write(f'{timestamp},"{datetime_str}",{gpu_util},{vram_usage}\n')
        
        # 移動臨時檔案到最終位置
        tmp_csv.rename(final_csv)
    
    def calculate_averages(self, date_str):
        """計算各節點的平均使用率"""
        for name in self.ip_name_map.values():
            colab_outdir = self.data_dir / name / date_str
            
            if not colab_outdir.exists():
                print(f"警告：找不到 {name} 的數據目錄")
                continue
            
            print(f"計算 {date_str} {name} 的 GPU 平均使用率...")
            
            # 創建平均值 CSV
            avg_csv = colab_outdir / f"average_{date_str}.csv"
            with open(avg_csv, 'w', encoding='utf-8') as f:
                f.write("GPU編號,平均GPU使用率(%),平均VRAM使用率(%)\n")
                
                gpu_averages = []
                vram_averages = []
                
                for gpu_index in self.gpu_indices:
                    csv_file = colab_outdir / f"gpu{gpu_index}_{date_str}.csv"
                    
                    if csv_file.exists():
                        try:
                            # 讀取 CSV 數據
                            df = pd.read_csv(csv_file)
                            
                            if not df.empty:
                                # 計算平均值
                                avg_gpu = df['GPU使用率(%)'].mean()
                                avg_vram = df['VRAM使用率(%)'].mean()
                                
                                gpu_averages.append(avg_gpu)
                                vram_averages.append(avg_vram)
                                
                                card_id = self.gpu_index_to_card[gpu_index]
                                print(f"GPU[{gpu_index}] (Card {card_id}): 平均使用率 = {avg_gpu:.2f}%, 平均VRAM使用率 = {avg_vram:.2f}%")
                                f.write(f"GPU[{gpu_index}],{avg_gpu:.2f},{avg_vram:.2f}\n")
                            else:
                                print(f"警告：GPU[{gpu_index}] 的數據檔案為空")
                                f.write(f"GPU[{gpu_index}],N/A,N/A\n")
                        except Exception as e:
                            print(f"錯誤：讀取 {csv_file} 時發生錯誤: {e}")
                            f.write(f"GPU[{gpu_index}],N/A,N/A\n")
                    else:
                        print(f"警告：找不到 {csv_file} 檔案")
                        f.write(f"GPU[{gpu_index}],N/A,N/A\n")
                
                # 計算整體平均值
                if gpu_averages:
                    overall_avg_gpu = sum(gpu_averages) / len(gpu_averages)
                    overall_avg_vram = sum(vram_averages) / len(vram_averages)
                else:
                    overall_avg_gpu = 0
                    overall_avg_vram = 0
                
                print("=" * 43)
                print(f"{name} 所有 GPU 的整體平均使用率: {overall_avg_gpu:.2f}%")
                print(f"{name} 所有 GPU 的整體平均 VRAM 使用率: {overall_avg_vram:.2f}%")
                print("=" * 43)
                
                f.write(f"全部平均,{overall_avg_gpu:.2f},{overall_avg_vram:.2f}\n")
                print(f"結果已保存至 {avg_csv}")
                
                # 生成摘要報告
                self.generate_summary_report(colab_outdir, date_str, name, overall_avg_gpu, overall_avg_vram)
    
    def generate_summary_report(self, outdir, date_str, name, overall_avg_gpu, overall_avg_vram):
        """生成摘要報告"""
        summary_file = outdir / f"summary_{date_str}.txt"
        avg_csv = outdir / f"average_{date_str}.csv"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("================================\n")
            f.write("AMD GPU 與 VRAM 每日使用率統計\n")
            f.write(f"日期: {date_str}\n")
            f.write(f"節點: {name}\n")
            f.write("================================\n\n")
            
            # 顯示 GPU 硬體對應表
            f.write("GPU 硬體對應表:\n")
            for gpu_index in self.gpu_indices:
                card_id = self.gpu_index_to_card[gpu_index]
                f.write(f"GPU[{gpu_index}] -> Card {card_id}\n")
            
            f.write("\n各 GPU 使用率與 VRAM 使用率:\n")
            
            # 讀取平均值數據並寫入報告
            if avg_csv.exists():
                try:
                    df = pd.read_csv(avg_csv)
                    for _, row in df.iterrows():
                        if row['GPU編號'] != '全部平均':
                            gpu_id = row['GPU編號']
                            gpu_usage = row['平均GPU使用率(%)']
                            vram_usage = row['平均VRAM使用率(%)']
                            f.write(f"{gpu_id}: GPU使用率 = {gpu_usage}%, VRAM使用率 = {vram_usage}%\n")
                except Exception as e:
                    f.write(f"錯誤：無法讀取平均值數據: {e}\n")
            
            f.write(f"\n整體平均 GPU 使用率: {overall_avg_gpu:.2f}%\n")
            f.write(f"整體平均 VRAM 使用率: {overall_avg_vram:.2f}%\n")
            f.write("================================\n")
        
        print(f"摘要報告已保存至 {summary_file}")
    
    def collect_data(self, date_str=None):
        """主要數據收集函數"""
        # 設定日期
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        elif not self.validate_date(date_str):
            raise ValueError("錯誤：日期格式無效，請使用 YYYY-MM-DD 格式")
        
        print(f"使用日期: {date_str}")
        
        # 計算時間戳
        timestamp_start, timestamp_end = self.calculate_timestamps(date_str)
        
        # 從各節點收集數據
        for ip, name in self.ip_name_map.items():
            try:
                self.process_gpu_data(ip, name, date_str, timestamp_start, timestamp_end)
            except Exception as e:
                print(f"錯誤：處理 {name} ({ip}) 時發生錯誤: {e}")
                continue
        
        # 計算平均值
        try:
            self.calculate_averages(date_str)
        except Exception as e:
            print(f"錯誤：計算平均值時發生錯誤: {e}")


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='AMD GPU 每日數據收集工具 (Python 版本)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例用法:
  %(prog)s                    # 收集今天的數據
  %(prog)s 2025-08-01         # 收集指定日期的數據
  %(prog)s --help             # 顯示此說明
        """
    )
    
    parser.add_argument(
        'date',
        nargs='?',
        help='指定日期 (格式: YYYY-MM-DD)，若不指定則使用今天日期'
    )
    
    parser.add_argument(
        '--data-dir',
        default='./data',
        help='數據輸出目錄 (預設: ./data)'
    )
    
    args = parser.parse_args()
    
    try:
        # 創建數據收集器
        collector = GPUDataCollector(data_dir=args.data_dir)
        
        # 收集數據
        collector.collect_data(args.date)
        
        print("\n數據收集完成！")
        
    except KeyboardInterrupt:
        print("\n\n使用者中斷操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n錯誤：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
