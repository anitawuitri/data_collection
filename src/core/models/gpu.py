"""GPU 領域模型

定義 GPU 相關的數據結構和業務邏輯。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class GPUMetric:
    """GPU 指標數據點"""
    timestamp: int
    datetime: str
    gpu_utilization: float
    vram_utilization: float
    temperature: Optional[float] = None
    
    @property
    def is_active(self) -> bool:
        """判斷 GPU 是否處於活躍狀態"""
        return self.gpu_utilization > 1.0  # 使用率超過 1% 視為活躍
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GPUMetric':
        """從字典創建 GPUMetric"""
        return cls(
            timestamp=data['timestamp'],
            datetime=data['datetime'], 
            gpu_utilization=float(data['gpu_utilization']),
            vram_utilization=float(data['vram_utilization']),
            temperature=data.get('temperature')
        )


@dataclass 
class GPU:
    """GPU 實體模型"""
    card_id: int
    index: int
    node_name: str
    user: Optional[str] = None
    metrics: List[GPUMetric] = field(default_factory=list)
    
    def add_metric(self, metric: GPUMetric) -> None:
        """添加指標數據點"""
        self.metrics.append(metric)
    
    def add_metrics(self, metrics: List[GPUMetric]) -> None:
        """批量添加指標數據點"""
        self.metrics.extend(metrics)
    
    @property
    def gpu_identifier(self) -> str:
        """GPU 識別符"""
        return f"{self.node_name}-GPU[{self.index}]"
    
    @property
    def has_data(self) -> bool:
        """是否有指標數據"""
        return len(self.metrics) > 0
    
    @property
    def total_records(self) -> int:
        """總記錄數"""
        return len(self.metrics)
    
    @property
    def active_records(self) -> List[GPUMetric]:
        """活躍記錄 (GPU 使用率 > 1%)"""
        return [metric for metric in self.metrics if metric.is_active]
    
    @property
    def active_record_count(self) -> int:
        """活躍記錄數"""
        return len(self.active_records)
    
    @property
    def activity_percentage(self) -> float:
        """活動比例"""
        if not self.metrics:
            return 0.0
        return (self.active_record_count / self.total_records) * 100
    
    def average_gpu_utilization(self) -> float:
        """平均 GPU 使用率"""
        if not self.metrics:
            return 0.0
        return sum(metric.gpu_utilization for metric in self.metrics) / len(self.metrics)
    
    def average_vram_utilization(self) -> float:
        """平均 VRAM 使用率"""
        if not self.metrics:
            return 0.0
        return sum(metric.vram_utilization for metric in self.metrics) / len(self.metrics)
    
    def peak_gpu_utilization(self) -> float:
        """峰值 GPU 使用率"""
        if not self.metrics:
            return 0.0
        return max(metric.gpu_utilization for metric in self.metrics)
    
    def peak_vram_utilization(self) -> float:
        """峰值 VRAM 使用率"""
        if not self.metrics:
            return 0.0
        return max(metric.vram_utilization for metric in self.metrics)
    
    def get_utilization_summary(self) -> Dict:
        """獲取使用率統計摘要"""
        return {
            'gpu_identifier': self.gpu_identifier,
            'user': self.user or '未使用',
            'total_records': self.total_records,
            'active_records': self.active_record_count,
            'activity_percentage': self.activity_percentage,
            'average_gpu_utilization': self.average_gpu_utilization(),
            'average_vram_utilization': self.average_vram_utilization(),
            'peak_gpu_utilization': self.peak_gpu_utilization(),
            'peak_vram_utilization': self.peak_vram_utilization()
        }
    
    def to_csv_average_format(self) -> Dict:
        """轉換為 CSV 平均格式"""
        return {
            'GPU編號': f"GPU[{self.index}]",
            '平均GPU使用率(%)': f"{self.average_gpu_utilization():.2f}",
            '平均VRAM使用率(%)': f"{self.average_vram_utilization():.2f}",
            '使用者': self.user or '未使用'
        }
    
    def get_metrics_in_time_range(self, start_time: datetime, end_time: datetime) -> List[GPUMetric]:
        """獲取指定時間範圍內的指標"""
        start_ts = int(start_time.timestamp())
        end_ts = int(end_time.timestamp())
        
        return [
            metric for metric in self.metrics 
            if start_ts <= metric.timestamp <= end_ts
        ]
    
    @classmethod
    def from_collection_data(cls, collection_data: Dict) -> 'GPU':
        """從收集器數據創建 GPU 實例"""
        gpu = cls(
            card_id=collection_data['gpu_card_id'],
            index=collection_data['gpu_index'],
            node_name=collection_data['node_name'],
            user=collection_data.get('user')
        )
        
        # 添加指標數據
        for metric_data in collection_data.get('metrics', []):
            metric = GPUMetric.from_dict(metric_data)
            gpu.add_metric(metric)
        
        return gpu