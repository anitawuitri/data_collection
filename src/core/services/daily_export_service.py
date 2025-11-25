"""日常數據導出服務

簡化的數據導出服務，直接輸出 CSV 格式。
不搞複雜的抽象，直接幹活！
"""

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from statistics import mean

logger = logging.getLogger(__name__)


class DailyExportService:
    """日常數據導出服務
    
    簡單直接的 CSV 導出，不搞那些花裡胡哨的抽象。
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
    
    def export_node_data(self, node_name: str, date_str: str, gpu_data: Dict[str, Any], user_mapping: Dict[int, str] = None) -> List[Path]:
        """導出節點數據到 CSV
        
        Args:
            node_name: 節點名稱
            date_str: 日期字符串
            gpu_data: GPU 數據字典
            user_mapping: GPU 使用者映射 (可選)
            
        Returns:
            生成的文件路徑列表
        """
        node_dir = self.data_dir / node_name / date_str
        node_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        
        # 為每個 GPU 生成個別的 CSV 文件
        for gpu_key, data in gpu_data.items():
            if 'error' in data:
                logger.warning(f"跳過有錯誤的 {gpu_key}: {data['error']}")
                continue
                
            gpu_index = data['gpu_index']
            
            # GPU 使用率文件
            gpu_file = node_dir / f"gpu{gpu_index}_{date_str}.csv"
            self._write_gpu_csv(gpu_file, data['utilization'], data['vram'])
            generated_files.append(gpu_file)
        
        # 生成平均值文件 (包含使用者信息)
        avg_file = node_dir / f"average_{date_str}.csv"
        self._write_average_csv(avg_file, gpu_data, user_mapping or {})
        generated_files.append(avg_file)
        
        # 生成摘要文件
        summary_file = node_dir / f"summary_{date_str}.txt"
        self._write_summary_file(summary_file, node_name, date_str, gpu_data, user_mapping or {})
        generated_files.append(summary_file)
        
        logger.info(f"為 {node_name} 生成了 {len(generated_files)} 個文件")
        return generated_files
    
    def _write_gpu_csv(self, file_path: Path, utilization_data: Dict, vram_data: Dict):
        """寫入單個 GPU 的 CSV 文件"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['時間戳', '日期時間', 'GPU使用率(%)', 'VRAM使用率(%)'])
            
            util_data = utilization_data.get('data', [])
            vram_data_dict = {row[0]: row[1] if row[1] is not None else 0.0 
                             for row in vram_data.get('data', []) if len(row) >= 2}
            
            for row in util_data:
                if len(row) >= 2:
                    timestamp = row[0]
                    gpu_util = row[1] if row[1] is not None else 0.0
                    vram_util = vram_data_dict.get(timestamp, 0.0)
                    
                    dt = datetime.fromtimestamp(timestamp)
                    writer.writerow([
                        timestamp,
                        dt.strftime('%Y-%m-%d %H:%M:%S'),
                        f"{gpu_util:.1f}",
                        f"{vram_util:.1f}"
                    ])
    
    def _write_average_csv(self, file_path: Path, gpu_data: Dict[str, Any], user_mapping: Dict[int, str]):
        """寫入平均值 CSV 文件"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['GPU編號', '平均GPU使用率(%)', '平均VRAM使用率(%)', '使用者'])
            
            total_gpu = 0
            total_vram = 0
            valid_gpus = 0
            
            for gpu_key in sorted(gpu_data.keys()):
                data = gpu_data[gpu_key]
                if 'error' in data:
                    continue
                
                gpu_index = data['gpu_index']
                card_id = data['card_id']
                
                # 計算平均值
                util_data = data['utilization'].get('data', [])
                vram_data = data['vram'].get('data', [])
                
                if util_data:
                    gpu_avg = mean([row[1] for row in util_data if row[1] is not None])
                else:
                    gpu_avg = 0.0
                
                if vram_data:
                    vram_avg = mean([row[1] for row in vram_data if row[1] is not None])
                else:
                    vram_avg = 0.0
                
                # 獲取使用者信息
                username = user_mapping.get(card_id, '未使用')
                
                writer.writerow([f'GPU[{gpu_index}]', f'{gpu_avg:.2f}', f'{vram_avg:.2f}', username])
                
                total_gpu += gpu_avg
                total_vram += vram_avg
                valid_gpus += 1
            
            # 寫入總平均
            if valid_gpus > 0:
                writer.writerow([
                    '全部平均',
                    f'{total_gpu/valid_gpus:.2f}',
                    f'{total_vram/valid_gpus:.2f}',
                    '所有使用者'
                ])
    
    def _write_summary_file(self, file_path: Path, node_name: str, date_str: str, 
                           gpu_data: Dict[str, Any], user_mapping: Dict[int, str]):
        """寫入摘要文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("================================\n")
            f.write("AMD GPU 與 VRAM 每日使用率統計\n")
            f.write(f"日期: {date_str}\n")
            f.write(f"節點: {node_name}\n")
            f.write("================================\n\n")
            
            # GPU 硬體對應表
            f.write("GPU 硬體對應表:\n")
            for gpu_key in sorted(gpu_data.keys()):
                data = gpu_data[gpu_key]
                if 'error' not in data:
                    f.write(f"GPU[{data['gpu_index']}] -> Card {data['card_id']}\n")
            f.write("\n")
            
            # GPU 使用狀況
            f.write("各 GPU 使用率與 VRAM 使用率:\n")
            total_gpu = 0
            total_vram = 0
            valid_gpus = 0
            
            for gpu_key in sorted(gpu_data.keys()):
                data = gpu_data[gpu_key]
                if 'error' in data:
                    f.write(f"GPU[{data['gpu_index']}]: 數據收集失敗 - {data['error']}\n")
                    continue
                
                gpu_index = data['gpu_index']
                card_id = data['card_id']
                
                util_data = data['utilization'].get('data', [])
                vram_data = data['vram'].get('data', [])
                
                gpu_avg = mean([row[1] for row in util_data if row[1] is not None]) if util_data else 0.0
                vram_avg = mean([row[1] for row in vram_data if row[1] is not None]) if vram_data else 0.0
                
                username = user_mapping.get(card_id, '未使用')
                f.write(f"GPU[{gpu_index}]: GPU使用率 = {gpu_avg:.2f}%, VRAM使用率 = {vram_avg:.2f}% (使用者: {username})\n")
                
                total_gpu += gpu_avg
                total_vram += vram_avg
                valid_gpus += 1
            
            if valid_gpus > 0:
                f.write(f"\n整體平均 GPU 使用率: {total_gpu/valid_gpus:.2f}%\n")
                f.write(f"整體平均 VRAM 使用率: {total_vram/valid_gpus:.2f}%\n")
            
            f.write("================================\n")