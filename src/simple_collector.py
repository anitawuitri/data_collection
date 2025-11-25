#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的 GPU 數據收集工具

基於 Linus 的簡潔原則重寫，去掉不必要的抽象。
直接幹活，不搞企業級垃圾！
"""

import os
import sys
import asyncio
import aiohttp
import csv
import json
import logging
from datetime import datetime, date, timedelta
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional, Any


class SimpleGPUCollector:
    """簡化的 GPU 收集器
    
    不搞複雜的抽象，直接完成任務。
    """
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        
        # 硬編碼配置（簡單直接）
        self.nodes = {
            "colab-gpu1": "192.168.10.103",
            "colab-gpu2": "192.168.10.104", 
            "colab-gpu3": "192.168.10.105",
            "colab-gpu4": "192.168.10.106"
        }
        
        # GPU 配置
        self.gpu_cards = [1, 9, 17, 25, 33, 41, 49, 57]  # Card IDs
        self.gpu_mapping = {1: 0, 9: 1, 17: 2, 25: 3, 33: 4, 41: 5, 49: 6, 57: 7}  # Card -> Index
        
        # 管理 API
        self.management_api_url = "http://192.168.10.100/api/v2/consumption/task"
        self.bearer_token = os.getenv('MANAGEMENT_API_TOKEN', '')
        
        # 數據點設定
        self.points = 144  # 每天144個點（每10分鐘一個）
    
    async def collect_node_data(self, node_name: str, node_ip: str, target_date: date) -> Dict[str, Any]:
        """收集單個節點的數據"""
        logging.info(f"收集 {node_name} ({node_ip}) 數據")
        
        # 計算時間戳
        start_time = datetime.combine(target_date, datetime.min.time())
        end_time = start_time + timedelta(days=1, seconds=-1)
        timestamp_start = int(start_time.timestamp())
        timestamp_end = int(end_time.timestamp())
        
        netdata_url = f"http://{node_ip}:19999"
        gpu_data = {}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            for card_id in self.gpu_cards:
                gpu_index = self.gpu_mapping[card_id]
                
                try:
                    # GPU 使用率
                    gpu_chart = f"amdgpu.gpu_utilization_unknown_AMD_GPU_card{card_id}"
                    gpu_util_data = await self._fetch_netdata(
                        session, netdata_url, gpu_chart, timestamp_start, timestamp_end
                    )
                    
                    # VRAM 使用率
                    vram_chart = f"amdgpu.gpu_mem_vram_usage_perc_unknown_AMD_GPU_card{card_id}"
                    vram_data = await self._fetch_netdata(
                        session, netdata_url, vram_chart, timestamp_start, timestamp_end
                    )
                    
                    gpu_data[f'gpu{gpu_index}'] = {
                        'card_id': card_id,
                        'gpu_index': gpu_index,
                        'utilization': gpu_util_data,
                        'vram': vram_data
                    }
                    
                except Exception as e:
                    logging.warning(f"收集 GPU{gpu_index} 失敗: {e}")
                    gpu_data[f'gpu{gpu_index}'] = {
                        'card_id': card_id,
                        'gpu_index': gpu_index,
                        'utilization': {'data': []},
                        'vram': {'data': []},
                        'error': str(e)
                    }
        
        return gpu_data
    
    async def _fetch_netdata(self, session: aiohttp.ClientSession, 
                           base_url: str, chart: str, after: int, before: int) -> Dict[str, Any]:
        """從 Netdata API 獲取數據"""
        url = f"{base_url}/api/v1/data"
        params = {
            'chart': chart,
            'after': after,
            'before': before,
            'points': self.points,
            'group': 'average',
            'format': 'json'
        }
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"HTTP {response.status}")
    
    async def get_user_info(self, target_date: date) -> Dict[str, str]:
        """獲取使用者資訊（可選）"""
        if not self.bearer_token:
            logging.info("未設定 Bearer Token，跳過使用者資訊收集")
            return {}
        
        start_time = f"{target_date} 00:00:00"
        end_time = f"{target_date} 23:59:59"
        
        params = {'start_t': start_time, 'end_t': end_time}
        headers = {
            'accept': 'application/json',
            'Authorization': f"Bearer {self.bearer_token}"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.management_api_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_user_data(data)
                    else:
                        logging.warning(f"管理 API 失敗: HTTP {response.status}")
                        return {}
        except Exception as e:
            logging.warning(f"獲取使用者資訊失敗: {e}")
            return {}
    
    def _process_user_data(self, api_data: Dict) -> Dict[int, str]:
        """處理使用者數據，返回 Card ID -> Username 映射"""
        card_user_map = {}
        
        for task_id, task_info in api_data.items():
            username = task_info.get('username', 'unknown')
            hostname = task_info.get('hostname', '').lower()
            
            # 簡單的主機名映射
            if 'gpu1' in hostname:
                # 為該節點分配前幾個 GPU
                gpu_count = task_info.get('flavor', {}).get('gpu', 1)
                for i in range(min(gpu_count, len(self.gpu_cards))):
                    card_user_map[self.gpu_cards[i]] = username
            # 可以添加更多主機映射邏輯...
        
        return card_user_map
    
    def save_node_data(self, node_name: str, target_date: date, 
                      gpu_data: Dict[str, Any], user_mapping: Dict[int, str]):
        """保存節點數據到 CSV"""
        date_str = target_date.isoformat()
        node_dir = self.data_dir / node_name / date_str
        node_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存個別 GPU 文件
        for gpu_key, data in gpu_data.items():
            if 'error' in data:
                continue
            
            gpu_index = data['gpu_index']
            gpu_file = node_dir / f"gpu{gpu_index}_{date_str}.csv"
            
            self._write_gpu_csv(gpu_file, data['utilization'], data['vram'])
        
        # 保存平均值文件
        avg_file = node_dir / f"average_{date_str}.csv"
        self._write_average_csv(avg_file, gpu_data, user_mapping)
        
        # 保存摘要文件
        summary_file = node_dir / f"summary_{date_str}.txt"
        self._write_summary(summary_file, node_name, date_str, gpu_data, user_mapping)
        
        logging.info(f"{node_name} 數據已保存到 {node_dir}")
    
    def _write_gpu_csv(self, file_path: Path, util_data: Dict, vram_data: Dict):
        """寫入單個 GPU CSV 文件"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['時間戳', '日期時間', 'GPU使用率(%)', 'VRAM使用率(%)'])
            
            # 建立 VRAM 數據映射
            vram_map = {row[0]: row[1] if row[1] is not None else 0.0 
                       for row in vram_data.get('data', [])}
            
            # 寫入數據
            for row in util_data.get('data', []):
                if len(row) >= 2:
                    timestamp = row[0]
                    gpu_util = row[1] if row[1] is not None else 0.0
                    vram_util = vram_map.get(timestamp, 0.0)
                    
                    dt = datetime.fromtimestamp(timestamp)
                    writer.writerow([
                        timestamp,
                        dt.strftime('%Y-%m-%d %H:%M:%S'),
                        f"{gpu_util:.1f}",
                        f"{vram_util:.1f}"
                    ])
    
    def _write_average_csv(self, file_path: Path, gpu_data: Dict[str, Any], user_mapping: Dict[int, str]):
        """寫入平均值 CSV"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['GPU編號', '平均GPU使用率(%)', '平均VRAM使用率(%)', '使用者'])
            
            total_gpu = 0
            total_vram = 0
            count = 0
            
            for gpu_key in sorted(gpu_data.keys()):
                data = gpu_data[gpu_key]
                if 'error' in data:
                    continue
                
                gpu_index = data['gpu_index']
                card_id = data['card_id']
                
                # 計算平均值
                util_data = data['utilization'].get('data', [])
                vram_data = data['vram'].get('data', [])
                
                gpu_avg = mean([row[1] for row in util_data if row[1] is not None]) if util_data else 0.0
                vram_avg = mean([row[1] for row in vram_data if row[1] is not None]) if vram_data else 0.0
                
                username = user_mapping.get(card_id, '未使用')
                
                writer.writerow([f'GPU[{gpu_index}]', f'{gpu_avg:.2f}', f'{vram_avg:.2f}', username])
                
                total_gpu += gpu_avg
                total_vram += vram_avg
                count += 1
            
            if count > 0:
                writer.writerow(['全部平均', f'{total_gpu/count:.2f}', f'{total_vram/count:.2f}', '所有使用者'])
    
    def _write_summary(self, file_path: Path, node_name: str, date_str: str,
                      gpu_data: Dict[str, Any], user_mapping: Dict[int, str]):
        """寫入摘要文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"AMD GPU 使用率統計報告\n")
            f.write(f"日期: {date_str}\n")
            f.write(f"節點: {node_name}\n")
            f.write("=" * 40 + "\n\n")
            
            # GPU 硬體對應表
            f.write("GPU 硬體對應表:\n")
            for card_id, gpu_index in self.gpu_mapping.items():
                f.write(f"GPU[{gpu_index}] -> Card {card_id}\n")
            f.write("\n")
            
            # 各 GPU 使用情況
            f.write("GPU 使用情況:\n")
            for gpu_key in sorted(gpu_data.keys()):
                data = gpu_data[gpu_key]
                if 'error' in data:
                    f.write(f"GPU[{data['gpu_index']}]: 數據收集失敗\n")
                    continue
                
                gpu_index = data['gpu_index']
                card_id = data['card_id']
                
                util_data = data['utilization'].get('data', [])
                vram_data = data['vram'].get('data', [])
                
                gpu_avg = mean([row[1] for row in util_data if row[1] is not None]) if util_data else 0.0
                vram_avg = mean([row[1] for row in vram_data if row[1] is not None]) if vram_data else 0.0
                
                username = user_mapping.get(card_id, '未使用')
                f.write(f"GPU[{gpu_index}]: GPU={gpu_avg:.1f}%, VRAM={vram_avg:.1f}%, 使用者={username}\n")
    
    async def collect_daily_data(self, target_date: date, nodes: Optional[List[str]] = None) -> bool:
        """主要收集函數"""
        target_nodes = nodes or list(self.nodes.keys())
        logging.info(f"開始收集 {target_date} 的數據，節點: {target_nodes}")
        
        # 獲取使用者資訊
        user_mapping = await self.get_user_info(target_date)
        if user_mapping:
            logging.info(f"獲取到 {len(user_mapping)} 個 GPU 使用者資訊")
        
        success_count = 0
        
        for node_name in target_nodes:
            if node_name not in self.nodes:
                logging.error(f"未知節點: {node_name}")
                continue
            
            try:
                node_ip = self.nodes[node_name]
                gpu_data = await self.collect_node_data(node_name, node_ip, target_date)
                self.save_node_data(node_name, target_date, gpu_data, user_mapping)
                success_count += 1
                
            except Exception as e:
                logging.error(f"收集 {node_name} 失敗: {e}")
        
        logging.info(f"數據收集完成: {success_count}/{len(target_nodes)} 節點成功")
        return success_count > 0


def main():
    """主程式"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='簡化的 GPU 數據收集工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例用法:
  %(prog)s                    # 收集今天的數據
  %(prog)s 2025-09-19         # 收集指定日期
  %(prog)s --nodes gpu1,gpu2  # 指定節點
        """
    )
    
    parser.add_argument('date', nargs='?', help='指定日期 (YYYY-MM-DD)')
    parser.add_argument('--nodes', help='指定節點，逗號分隔')
    parser.add_argument('--data-dir', default='./data', help='數據目錄')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細輸出')
    
    args = parser.parse_args()
    
    # 設置日誌
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s - %(message)s'
    )
    
    # 解析日期
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print(f"❌ 日期格式無效: {args.date}")
            sys.exit(1)
    else:
        target_date = datetime.now().date()
    
    # 解析節點
    nodes = None
    if args.nodes:
        nodes = [n.strip() for n in args.nodes.split(',')]
    
    # 執行收集
    try:
        collector = SimpleGPUCollector(args.data_dir)
        success = asyncio.run(collector.collect_daily_data(target_date, nodes))
        
        if success:
            print("✅ 數據收集完成")
        else:
            print("❌ 數據收集失敗")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  用戶中斷")
        sys.exit(130)
    except Exception as e:
        print(f"💥 錯誤: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()