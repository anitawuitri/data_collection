"""節點領域模型

定義節點相關的數據結構和業務邏輯。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime

from .gpu import GPU


@dataclass
class Node:
    """節點實體模型"""
    name: str
    ip: str
    port: int = 19999
    gpus: List[GPU] = field(default_factory=list)
    
    @property
    def netdata_url(self) -> str:
        """Netdata URL"""
        return f"http://{self.ip}:{self.port}"
    
    @property
    def gpu_count(self) -> int:
        """GPU 數量"""
        return len(self.gpus)
    
    @property
    def active_gpu_count(self) -> int:
        """活躍 GPU 數量"""
        return len([gpu for gpu in self.gpus if gpu.active_record_count > 0])
    
    def add_gpu(self, gpu: GPU) -> None:
        """添加 GPU"""
        gpu.node_name = self.name  # 確保 GPU 的節點名稱正確
        self.gpus.append(gpu)
    
    def add_gpus(self, gpus: List[GPU]) -> None:
        """批量添加 GPU"""
        for gpu in gpus:
            self.add_gpu(gpu)
    
    def get_gpu_by_index(self, index: int) -> Optional[GPU]:
        """根據索引獲取 GPU"""
        for gpu in self.gpus:
            if gpu.index == index:
                return gpu
        return None
    
    def get_gpu_by_card_id(self, card_id: int) -> Optional[GPU]:
        """根據 Card ID 獲取 GPU"""
        for gpu in self.gpus:
            if gpu.card_id == card_id:
                return gpu
        return None
    
    def get_gpus_by_user(self, username: str) -> List[GPU]:
        """獲取指定使用者的 GPU"""
        return [gpu for gpu in self.gpus if gpu.user == username]
    
    def get_used_gpus(self) -> List[GPU]:
        """獲取有使用者的 GPU"""
        return [gpu for gpu in self.gpus if gpu.user and gpu.user != '未使用']
    
    def get_unused_gpus(self) -> List[GPU]:
        """獲取未使用的 GPU"""
        return [gpu for gpu in self.gpus if not gpu.user or gpu.user == '未使用']
    
    def calculate_node_averages(self) -> Dict:
        """計算節點平均使用率"""
        if not self.gpus:
            return {
                'node_name': self.name,
                'gpu_count': 0,
                'average_gpu_utilization': 0.0,
                'average_vram_utilization': 0.0,
                'active_gpu_count': 0,
                'users': []
            }
        
        total_gpu_util = sum(gpu.average_gpu_utilization() for gpu in self.gpus)
        total_vram_util = sum(gpu.average_vram_utilization() for gpu in self.gpus)
        
        # 收集使用者資訊
        users = []
        for gpu in self.gpus:
            if gpu.user and gpu.user != '未使用':
                users.append({
                    'username': gpu.user,
                    'gpu_index': gpu.index,
                    'gpu_utilization': gpu.average_gpu_utilization(),
                    'vram_utilization': gpu.average_vram_utilization()
                })
        
        return {
            'node_name': self.name,
            'gpu_count': self.gpu_count,
            'average_gpu_utilization': total_gpu_util / self.gpu_count,
            'average_vram_utilization': total_vram_util / self.gpu_count,
            'active_gpu_count': self.active_gpu_count,
            'users': users
        }
    
    def get_utilization_summary(self) -> Dict:
        """獲取使用率統計摘要"""
        if not self.gpus:
            return {
                'node_name': self.name,
                'total_gpus': 0,
                'used_gpus': 0,
                'usage_percentage': 0.0,
                'average_gpu_utilization': 0.0,
                'average_vram_utilization': 0.0,
                'gpu_details': []
            }
        
        used_gpus = self.get_used_gpus()
        gpu_details = [gpu.get_utilization_summary() for gpu in self.gpus]
        
        # 計算整體平均
        total_gpu_util = sum(gpu.average_gpu_utilization() for gpu in self.gpus)
        total_vram_util = sum(gpu.average_vram_utilization() for gpu in self.gpus)
        
        return {
            'node_name': self.name,
            'total_gpus': self.gpu_count,
            'used_gpus': len(used_gpus),
            'usage_percentage': (len(used_gpus) / self.gpu_count) * 100 if self.gpu_count > 0 else 0.0,
            'average_gpu_utilization': total_gpu_util / self.gpu_count if self.gpu_count > 0 else 0.0,
            'average_vram_utilization': total_vram_util / self.gpu_count if self.gpu_count > 0 else 0.0,
            'gpu_details': gpu_details
        }
    
    def to_csv_format(self) -> List[Dict]:
        """轉換為 CSV 格式"""
        return [gpu.to_csv_average_format() for gpu in self.gpus]
    
    @classmethod
    def from_config(cls, node_config) -> 'Node':
        """從配置創建節點實例"""
        return cls(
            name=node_config.name,
            ip=node_config.ip,
            port=node_config.port
        )