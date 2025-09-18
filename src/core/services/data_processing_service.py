"""數據處理服務

提供數據分析、聚合和轉換功能。
"""

import logging
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from statistics import mean, median, stdev
from collections import defaultdict

from ..models.gpu import GPU
from ..models.node import Node
from ..models.user import User
from ...infrastructure.config.settings import AppConfig


logger = logging.getLogger(__name__)


class DataProcessingService:
    """數據處理服務
    
    提供數據清理、分析、聚合和統計功能。
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
    
    def load_node_data(self, 
                       node_name: str, 
                       target_date: date) -> Optional[Dict[str, Any]]:
        """載入節點數據
        
        Args:
            node_name: 節點名稱
            target_date: 目標日期
            
        Returns:
            節點數據字典或 None
        """
        date_str = target_date.isoformat()
        node_dir = self.config.data_dir / node_name / date_str
        
        if not node_dir.exists():
            logger.warning(f"節點數據目錄不存在: {node_dir}")
            return None
        
        node_data = {
            'node_name': node_name,
            'date': date_str,
            'gpu_data': {},
            'averages': None
        }
        
        # 載入 GPU 數據
        for gpu_index in self.config.gpu.indices:
            gpu_file = node_dir / f"gpu{gpu_index}_{date_str}.csv"
            vram_file = node_dir / f"gpu{gpu_index}_vram_{date_str}.csv"
            
            gpu_data = {}
            
            # 載入 GPU 使用率
            if gpu_file.exists():
                gpu_data['utilization'] = self._load_csv_data(gpu_file)
            
            # 載入 VRAM 使用率
            if vram_file.exists():
                gpu_data['vram'] = self._load_csv_data(vram_file)
            
            if gpu_data:
                node_data['gpu_data'][f'gpu{gpu_index}'] = gpu_data
        
        # 載入平均值
        avg_file = node_dir / f"average_{date_str}.csv"
        if avg_file.exists():
            node_data['averages'] = self._load_average_data(avg_file)
        
        return node_data
    
    def load_multi_node_data(self, 
                            nodes: List[str], 
                            start_date: date,
                            end_date: date) -> Dict[str, Dict[str, Any]]:
        """載入多節點多日期數據
        
        Args:
            nodes: 節點名稱列表
            start_date: 開始日期
            end_date: 結束日期
            
        Returns:
            按節點和日期組織的數據
        """
        all_data = defaultdict(dict)
        
        current_date = start_date
        while current_date <= end_date:
            for node_name in nodes:
                node_data = self.load_node_data(node_name, current_date)
                if node_data:
                    all_data[node_name][current_date.isoformat()] = node_data
            
            current_date += timedelta(days=1)
        
        return dict(all_data)
    
    def calculate_node_statistics(self, 
                                 node_data: Dict[str, Any]) -> Dict[str, Any]:
        """計算節點統計資訊
        
        Args:
            node_data: 節點數據
            
        Returns:
            統計資訊字典
        """
        stats = {
            'node_name': node_data['node_name'],
            'date': node_data['date'],
            'gpu_count': len(node_data['gpu_data']),
            'gpu_stats': {},
            'node_total': {
                'avg_utilization': 0,
                'avg_vram': 0,
                'max_utilization': 0,
                'max_vram': 0,
                'min_utilization': 100,
                'min_vram': 100
            }
        }
        
        utilization_values = []
        vram_values = []
        
        # 為每個 GPU 計算統計
        for gpu_key, gpu_data in node_data['gpu_data'].items():
            gpu_stats = self._calculate_gpu_statistics(gpu_data)
            stats['gpu_stats'][gpu_key] = gpu_stats
            
            if gpu_stats['utilization']:
                utilization_values.extend(gpu_stats['utilization']['values'])
                vram_values.extend(gpu_stats['vram']['values'])
        
        # 計算節點總體統計
        if utilization_values:
            stats['node_total']['avg_utilization'] = mean(utilization_values)
            stats['node_total']['max_utilization'] = max(utilization_values)
            stats['node_total']['min_utilization'] = min(utilization_values)
        
        if vram_values:
            stats['node_total']['avg_vram'] = mean(vram_values)
            stats['node_total']['max_vram'] = max(vram_values)
            stats['node_total']['min_vram'] = min(vram_values)
        
        return stats
    
    def calculate_multi_node_summary(self,
                                   multi_node_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """計算多節點摘要統計
        
        Args:
            multi_node_data: 多節點數據
            
        Returns:
            摘要統計字典
        """
        summary = {
            'total_nodes': len(multi_node_data),
            'date_range': {},
            'node_summaries': {},
            'overall_stats': {
                'avg_utilization': 0,
                'avg_vram': 0,
                'total_data_points': 0,
                'active_gpus': 0
            }
        }
        
        all_utilization = []
        all_vram = []
        all_dates = set()
        total_gpus = 0
        
        # 處理每個節點的數據
        for node_name, node_dates in multi_node_data.items():
            node_summary = {
                'dates': list(node_dates.keys()),
                'total_days': len(node_dates),
                'avg_utilization': 0,
                'avg_vram': 0
            }
            
            node_utilization = []
            node_vram = []
            
            for date_str, node_data in node_dates.items():
                all_dates.add(date_str)
                stats = self.calculate_node_statistics(node_data)
                
                node_utilization.append(stats['node_total']['avg_utilization'])
                node_vram.append(stats['node_total']['avg_vram'])
                total_gpus += stats['gpu_count']
            
            if node_utilization:
                node_summary['avg_utilization'] = mean(node_utilization)
                node_summary['avg_vram'] = mean(node_vram)
                all_utilization.extend(node_utilization)
                all_vram.extend(node_vram)
            
            summary['node_summaries'][node_name] = node_summary
        
        # 計算整體統計
        if all_utilization:
            summary['overall_stats']['avg_utilization'] = mean(all_utilization)
        if all_vram:
            summary['overall_stats']['avg_vram'] = mean(all_vram)
        
        summary['overall_stats']['active_gpus'] = total_gpus
        summary['overall_stats']['total_data_points'] = len(all_utilization)
        
        # 設定日期範圍
        if all_dates:
            sorted_dates = sorted(all_dates)
            summary['date_range'] = {
                'start': sorted_dates[0],
                'end': sorted_dates[-1],
                'total_days': len(sorted_dates)
            }
        
        return summary
    
    def find_peak_usage_periods(self,
                               node_data: Dict[str, Any],
                               threshold: float = 80.0) -> List[Dict[str, Any]]:
        """尋找高使用率時段
        
        Args:
            node_data: 節點數據
            threshold: 使用率閾值
            
        Returns:
            高使用率時段列表
        """
        peak_periods = []
        
        for gpu_key, gpu_data in node_data['gpu_data'].items():
            if 'utilization' not in gpu_data:
                continue
            
            utilization_data = gpu_data['utilization']
            current_period = None
            
            for timestamp, value in utilization_data:
                if value >= threshold:
                    if current_period is None:
                        current_period = {
                            'gpu': gpu_key,
                            'start_time': timestamp,
                            'end_time': timestamp,
                            'max_usage': value,
                            'avg_usage': value,
                            'values': [value]
                        }
                    else:
                        current_period['end_time'] = timestamp
                        current_period['values'].append(value)
                        current_period['max_usage'] = max(current_period['max_usage'], value)
                        current_period['avg_usage'] = mean(current_period['values'])
                else:
                    if current_period is not None:
                        # 計算持續時間
                        duration = current_period['end_time'] - current_period['start_time']
                        current_period['duration_minutes'] = duration / 60
                        
                        peak_periods.append(current_period)
                        current_period = None
            
            # 處理最後一個時段
            if current_period is not None:
                duration = current_period['end_time'] - current_period['start_time']
                current_period['duration_minutes'] = duration / 60
                peak_periods.append(current_period)
        
        # 按持續時間排序
        peak_periods.sort(key=lambda x: x['duration_minutes'], reverse=True)
        
        return peak_periods
    
    def generate_usage_report(self,
                            multi_node_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """生成使用率報告
        
        Args:
            multi_node_data: 多節點數據
            
        Returns:
            使用率報告
        """
        report = {
            'generation_time': datetime.now().isoformat(),
            'summary': self.calculate_multi_node_summary(multi_node_data),
            'node_details': {},
            'recommendations': []
        }
        
        # 為每個節點生成詳細報告
        for node_name, node_dates in multi_node_data.items():
            node_details = {
                'daily_stats': {},
                'peak_periods': [],
                'trends': {}
            }
            
            daily_utilization = []
            daily_vram = []
            
            for date_str, node_data in node_dates.items():
                stats = self.calculate_node_statistics(node_data)
                node_details['daily_stats'][date_str] = stats
                
                daily_utilization.append(stats['node_total']['avg_utilization'])
                daily_vram.append(stats['node_total']['avg_vram'])
                
                # 尋找高使用率時段
                peaks = self.find_peak_usage_periods(node_data)
                node_details['peak_periods'].extend(peaks)
            
            # 計算趨勢
            if len(daily_utilization) > 1:
                node_details['trends'] = {
                    'utilization_trend': self._calculate_trend(daily_utilization),
                    'vram_trend': self._calculate_trend(daily_vram)
                }
            
            report['node_details'][node_name] = node_details
        
        # 生成建議
        report['recommendations'] = self._generate_recommendations(report)
        
        return report
    
    def _load_csv_data(self, csv_file: Path) -> List[Tuple[datetime, float]]:
        """載入 CSV 數據"""
        data = []
        try:
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                timestamp = datetime.strptime(row['時間'], '%Y-%m-%d %H:%M:%S')
                value = float(row.iloc[1])  # 第二列是數值
                data.append((timestamp.timestamp(), value))
        except Exception as e:
            logger.error(f"載入 CSV 文件失敗 {csv_file}: {e}")
        
        return data
    
    def _load_average_data(self, avg_file: Path) -> Dict[str, Any]:
        """載入平均值數據"""
        averages = {}
        try:
            df = pd.read_csv(avg_file)
            for _, row in df.iterrows():
                gpu_name = row['gpu']
                averages[gpu_name] = {
                    'usage': float(row['usage']),
                    'vram': float(row['vram']),
                    'user': row['user']
                }
        except Exception as e:
            logger.error(f"載入平均值文件失敗 {avg_file}: {e}")
        
        return averages
    
    def _calculate_gpu_statistics(self, gpu_data: Dict[str, Any]) -> Dict[str, Any]:
        """計算單個 GPU 的統計資訊"""
        stats = {
            'utilization': None,
            'vram': None
        }
        
        # 處理使用率數據
        if 'utilization' in gpu_data and gpu_data['utilization']:
            values = [val for _, val in gpu_data['utilization']]
            if values:
                stats['utilization'] = {
                    'count': len(values),
                    'mean': mean(values),
                    'median': median(values),
                    'std': stdev(values) if len(values) > 1 else 0,
                    'min': min(values),
                    'max': max(values),
                    'values': values
                }
        
        # 處理 VRAM 數據
        if 'vram' in gpu_data and gpu_data['vram']:
            values = [val for _, val in gpu_data['vram']]
            if values:
                stats['vram'] = {
                    'count': len(values),
                    'mean': mean(values),
                    'median': median(values),
                    'std': stdev(values) if len(values) > 1 else 0,
                    'min': min(values),
                    'max': max(values),
                    'values': values
                }
        
        return stats
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """計算趨勢（簡單線性回歸）"""
        if len(values) < 2:
            return {'trend': 'insufficient_data'}
        
        n = len(values)
        x = list(range(n))
        
        # 計算線性回歸
        x_mean = mean(x)
        y_mean = mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # 判斷趨勢
        if slope > 0.5:
            trend = 'increasing'
        elif slope < -0.5:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'slope': slope,
            'start_value': values[0],
            'end_value': values[-1],
            'change_percent': ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
        }
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """生成使用建議"""
        recommendations = []
        
        overall_stats = report['summary']['overall_stats']
        
        # 基於整體使用率的建議
        if overall_stats['avg_utilization'] > 90:
            recommendations.append("🔴 整體 GPU 使用率過高，建議考慮增加計算資源")
        elif overall_stats['avg_utilization'] < 30:
            recommendations.append("🟢 GPU 使用率較低，資源利用效率有提升空間")
        
        # 基於 VRAM 使用率的建議
        if overall_stats['avg_vram'] > 85:
            recommendations.append("🟡 VRAM 使用率較高，建議監控記憶體洩漏")
        
        # 基於節點使用的建議
        node_utilizations = []
        for node_name, node_summary in report['summary']['node_summaries'].items():
            node_utilizations.append((node_name, node_summary['avg_utilization']))
        
        # 找出使用率差異較大的節點
        if len(node_utilizations) > 1:
            utilizations = [util for _, util in node_utilizations]
            max_util = max(utilizations)
            min_util = min(utilizations)
            
            if max_util - min_util > 40:
                recommendations.append("⚖️ 節點間負載不均衡，建議重新分配工作負載")
        
        return recommendations