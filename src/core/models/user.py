"""使用者領域模型

定義使用者相關的數據結構和業務邏輯。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class User:
    """使用者實體模型"""
    username: str
    hostname: str
    task_type: Optional[str] = None
    project_uuid: Optional[str] = None
    start_time: Optional[str] = None
    gpu_uuids: List[str] = field(default_factory=list)
    
    @property
    def display_name(self) -> str:
        """顯示名稱"""
        return self.username
    
    @property 
    def gpu_count(self) -> int:
        """使用的 GPU 數量"""
        return len(self.gpu_uuids)
    
    def has_gpus(self) -> bool:
        """是否有使用 GPU"""
        return self.gpu_count > 0
    
    @classmethod
    def from_api_data(cls, api_data: Dict) -> 'User':
        """從 API 數據創建使用者實例"""
        return cls(
            username=api_data.get('username', '未知'),
            hostname=api_data.get('hostname', '未知'),
            task_type=api_data.get('task_type'),
            project_uuid=api_data.get('project_uuid'),
            start_time=api_data.get('start_time'),
            gpu_uuids=api_data.get('gpu_uuids', [])
        )


@dataclass
class UserGPUUsage:
    """使用者 GPU 使用情況"""
    user: User
    node_name: str
    gpu_assignments: List[Dict] = field(default_factory=list)
    
    def add_gpu_assignment(self, gpu_index: int, card_id: int, 
                          avg_gpu_util: float, avg_vram_util: float) -> None:
        """添加 GPU 分配資訊"""
        self.gpu_assignments.append({
            'gpu_index': gpu_index,
            'card_id': card_id,
            'avg_gpu_utilization': avg_gpu_util,
            'avg_vram_utilization': avg_vram_util
        })
    
    @property
    def assigned_gpu_count(self) -> int:
        """分配的 GPU 數量"""
        return len(self.gpu_assignments)
    
    @property
    def total_avg_gpu_utilization(self) -> float:
        """總平均 GPU 使用率"""
        if not self.gpu_assignments:
            return 0.0
        
        total = sum(assignment['avg_gpu_utilization'] for assignment in self.gpu_assignments)
        return total / len(self.gpu_assignments)
    
    @property
    def total_avg_vram_utilization(self) -> float:
        """總平均 VRAM 使用率"""
        if not self.gpu_assignments:
            return 0.0
        
        total = sum(assignment['avg_vram_utilization'] for assignment in self.gpu_assignments)
        return total / len(self.gpu_assignments)
    
    def get_summary(self) -> Dict:
        """獲取使用摘要"""
        return {
            'username': self.user.username,
            'hostname': self.user.hostname,
            'node_name': self.node_name,
            'task_type': self.user.task_type,
            'project_uuid': self.user.project_uuid,
            'assigned_gpu_count': self.assigned_gpu_count,
            'total_avg_gpu_utilization': self.total_avg_gpu_utilization,
            'total_avg_vram_utilization': self.total_avg_vram_utilization,
            'gpu_assignments': self.gpu_assignments
        }
    
    def format_for_display(self) -> str:
        """格式化為顯示字符串"""
        gpu_details = []
        for assignment in self.gpu_assignments:
            gpu_details.append(
                f"📍 {self.node_name}:GPU[{assignment['gpu_index']}] - "
                f"GPU: {assignment['avg_gpu_utilization']:.1f}%, "
                f"VRAM: {assignment['avg_vram_utilization']:.1f}%"
            )
        
        summary = [
            f"👤 {self.user.username}:",
            *gpu_details,
            f"📊 平均: GPU {self.total_avg_gpu_utilization:.1f}%, "
            f"VRAM {self.total_avg_vram_utilization:.1f}% ({self.assigned_gpu_count} GPU)"
        ]
        
        return '\n   '.join(summary)


@dataclass
class UserQueryResult:
    """使用者查詢結果"""
    username: str
    date_range: str
    records: List[Dict] = field(default_factory=list)
    
    def add_record(self, date: str, node: str, gpu_index: int, 
                   gpu_util: float, vram_util: float) -> None:
        """添加使用記錄"""
        self.records.append({
            'date': date,
            'node': node,
            'gpu_index': gpu_index,
            'gpu_utilization': gpu_util,
            'vram_utilization': vram_util,
            'is_active': gpu_util > 1.0
        })
    
    @property
    def total_records(self) -> int:
        """總記錄數"""
        return len(self.records)
    
    @property
    def active_records(self) -> List[Dict]:
        """活躍記錄"""
        return [record for record in self.records if record['is_active']]
    
    @property
    def active_record_count(self) -> int:
        """活躍記錄數"""
        return len(self.active_records)
    
    @property
    def activity_percentage(self) -> float:
        """活動比例"""
        if not self.records:
            return 0.0
        return (self.active_record_count / self.total_records) * 100
    
    @property
    def average_gpu_utilization(self) -> float:
        """平均 GPU 使用率"""
        if not self.records:
            return 0.0
        return sum(record['gpu_utilization'] for record in self.records) / len(self.records)
    
    @property
    def average_vram_utilization(self) -> float:
        """平均 VRAM 使用率"""
        if not self.records:
            return 0.0
        return sum(record['vram_utilization'] for record in self.records) / len(self.records)
    
    @property
    def peak_gpu_utilization(self) -> float:
        """峰值 GPU 使用率"""
        if not self.records:
            return 0.0
        return max(record['gpu_utilization'] for record in self.records)
    
    @property
    def peak_vram_utilization(self) -> float:
        """峰值 VRAM 使用率"""
        if not self.records:
            return 0.0
        return max(record['vram_utilization'] for record in self.records)
    
    @property
    def used_nodes(self) -> List[str]:
        """使用的節點列表"""
        return list(set(record['node'] for record in self.records))
    
    @property
    def used_gpu_count(self) -> int:
        """使用的 GPU 數量"""
        gpu_identifiers = set(f"{record['node']}-GPU[{record['gpu_index']}]" for record in self.records)
        return len(gpu_identifiers)
    
    def get_statistics_summary(self) -> Dict:
        """獲取統計摘要"""
        return {
            'username': self.username,
            'date_range': self.date_range,
            'total_records': self.total_records,
            'active_records': self.active_record_count,
            'activity_percentage': self.activity_percentage,
            'average_gpu_utilization': self.average_gpu_utilization,
            'average_vram_utilization': self.average_vram_utilization,
            'peak_gpu_utilization': self.peak_gpu_utilization,
            'peak_vram_utilization': self.peak_vram_utilization,
            'used_nodes': ', '.join(self.used_nodes),
            'used_gpu_count': self.used_gpu_count
        }