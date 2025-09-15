"""Netdata API 數據收集器

從 Netdata API 收集 GPU 使用率和 VRAM 使用率數據。
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlencode

from .base_collector import BaseCollector, CollectionError
from ..models.gpu import GPUMetric


class NetdataCollector(BaseCollector):
    """Netdata API 數據收集器"""
    
    def __init__(self, config):
        super().__init__(config)
        self.timeout = aiohttp.ClientTimeout(total=config.api.timeout)
    
    async def collect(self, start_time: datetime, end_time: datetime, **kwargs) -> Dict[str, Any]:
        """收集 Netdata 數據
        
        Args:
            start_time: 開始時間
            end_time: 結束時間
            **kwargs: 
                - node_name: 節點名稱
                - gpu_card_id: GPU Card ID
                
        Returns:
            包含 GPU 使用率和 VRAM 使用率的數據字典
        """
        node_name = kwargs.get('node_name')
        gpu_card_id = kwargs.get('gpu_card_id')
        
        if not node_name or not gpu_card_id:
            raise CollectionError(
                "缺少必要參數 node_name 或 gpu_card_id",
                self.__class__.__name__,
                f"{node_name}-GPU{gpu_card_id}"
            )
        
        node_config = self.config.get_node_by_name(node_name)
        if not node_config:
            raise CollectionError(
                f"找不到節點配置: {node_name}",
                self.__class__.__name__,
                node_name
            )
        
        # 計算時間戳
        timestamp_start = int(start_time.timestamp())
        timestamp_end = int(end_time.timestamp())
        
        target = f"{node_name}-GPU{gpu_card_id}"
        self.log_collection_start(target)
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # 收集 GPU 使用率
                gpu_util_data = await self._fetch_chart_data(
                    session, node_config.netdata_url,
                    f"amdgpu.gpu_utilization_unknown_AMD_GPU_card{gpu_card_id}",
                    timestamp_start, timestamp_end
                )
                
                # 收集 VRAM 使用率
                vram_usage_data = await self._fetch_chart_data(
                    session, node_config.netdata_url,
                    f"amdgpu.gpu_mem_vram_usage_perc_unknown_AMD_GPU_card{gpu_card_id}",
                    timestamp_start, timestamp_end
                )
                
                # 合併數據
                merged_data = self._merge_gpu_vram_data(gpu_util_data, vram_usage_data)
                
                self.log_collection_success(target, len(merged_data.get('metrics', [])))
                
                return {
                    'node_name': node_name,
                    'gpu_card_id': gpu_card_id,
                    'gpu_index': self.config.gpu.mapping.get(gpu_card_id, -1),
                    'metrics': merged_data.get('metrics', []),
                    'start_time': start_time,
                    'end_time': end_time
                }
                
        except Exception as e:
            self.log_collection_failure(target, str(e))
            raise CollectionError(
                f"數據收集失敗: {str(e)}",
                self.__class__.__name__,
                target
            )
    
    async def _fetch_chart_data(self, session: aiohttp.ClientSession, 
                               netdata_url: str, chart: str, 
                               timestamp_start: int, timestamp_end: int) -> Dict[str, Any]:
        """從 Netdata API 獲取圖表數據"""
        
        params = {
            'chart': chart,
            'format': 'json',
            'points': self.config.points,
            'after': timestamp_start,
            'before': timestamp_end
        }
        
        url = f"{netdata_url}/api/v1/data?" + urlencode(params)
        
        async with session.get(url) as response:
            if response.status != 200:
                raise CollectionError(
                    f"API 請求失敗: HTTP {response.status}",
                    self.__class__.__name__,
                    chart
                )
            
            data = await response.json()
            
            if not self.validate_netdata_response(data):
                raise CollectionError(
                    "API 回應格式無效",
                    self.__class__.__name__,
                    chart
                )
            
            return data
    
    def _merge_gpu_vram_data(self, gpu_data: Dict[str, Any], 
                            vram_data: Dict[str, Any]) -> Dict[str, Any]:
        """合併 GPU 使用率和 VRAM 使用率數據"""
        
        metrics = []
        
        # 確保兩個數據集都有有效的數據點
        gpu_values = gpu_data.get('data', [])
        vram_values = vram_data.get('data', [])
        
        if not gpu_values or not vram_values:
            return {'metrics': metrics}
        
        # 取較短的長度，確保配對正確
        min_length = min(len(gpu_values), len(vram_values))
        
        for i in range(min_length):
            gpu_entry = gpu_values[i]
            vram_entry = vram_values[i]
            
            if len(gpu_entry) >= 2 and len(vram_entry) >= 2:
                timestamp = gpu_entry[0]  # 使用 GPU 數據的時間戳
                gpu_util = gpu_entry[1] if gpu_entry[1] is not None else 0.0
                vram_util = vram_entry[1] if vram_entry[1] is not None else 0.0
                
                # 轉換時間戳為 datetime
                dt = datetime.fromtimestamp(timestamp)
                
                metrics.append({
                    'timestamp': timestamp,
                    'datetime': dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'gpu_utilization': float(gpu_util),
                    'vram_utilization': float(vram_util)
                })
        
        return {'metrics': metrics}
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """驗證收集到的數據"""
        required_keys = ['node_name', 'gpu_card_id', 'gpu_index', 'metrics']
        
        for key in required_keys:
            if key not in data:
                return False
        
        metrics = data['metrics']
        if not isinstance(metrics, list):
            return False
        
        # 檢查每個指標的格式
        for metric in metrics:
            if not isinstance(metric, dict):
                return False
            
            required_metric_keys = ['timestamp', 'datetime', 'gpu_utilization', 'vram_utilization']
            for key in required_metric_keys:
                if key not in metric:
                    return False
        
        return True
    
    def validate_netdata_response(self, data: Dict[str, Any]) -> bool:
        """驗證 Netdata API 回應格式"""
        if not isinstance(data, dict):
            return False
        
        # 檢查必要的欄位
        required_fields = ['data', 'labels', 'latest_values']
        for field in required_fields:
            if field not in data:
                return False
        
        # 檢查數據格式
        if not isinstance(data['data'], list):
            return False
        
        return True