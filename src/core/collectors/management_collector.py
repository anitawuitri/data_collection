"""管理 API 數據收集器

從管理系統 API 收集 GPU 使用者任務資訊。
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlencode

from .base_collector import BaseCollector, CollectionError
from ..models.user import UserGPUUsage


class ManagementCollector(BaseCollector):
    """管理 API 數據收集器"""
    
    def __init__(self, config):
        super().__init__(config)
        self.timeout = aiohttp.ClientTimeout(total=config.api.timeout)
        self.api_url = config.api.management_url
        self.bearer_token = config.api.bearer_token
    
    async def collect(self, start_time: datetime, end_time: datetime, **kwargs) -> Dict[str, Any]:
        """收集管理 API 數據
        
        Args:
            start_time: 開始時間
            end_time: 結束時間
            **kwargs: 額外參數
                
        Returns:
            包含使用者任務資訊的數據字典
        """
        target = f"管理API ({start_time.strftime('%Y-%m-%d')})"
        self.log_collection_start(target)
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                task_data = await self._fetch_task_info(session, start_time, end_time)
                
                # 處理和轉換數據
                processed_data = self._process_task_data(task_data)
                
                self.log_collection_success(target, len(processed_data.get('users', [])))
                
                return {
                    'users': processed_data.get('users', []),
                    'gpu_user_mapping': processed_data.get('gpu_user_mapping', {}),
                    'start_time': start_time,
                    'end_time': end_time
                }
                
        except Exception as e:
            self.log_collection_failure(target, str(e))
            raise CollectionError(
                f"管理 API 數據收集失敗: {str(e)}",
                self.__class__.__name__,
                target
            )
    
    async def _fetch_task_info(self, session: aiohttp.ClientSession, 
                              start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """從管理 API 獲取任務資訊"""
        
        params = {
            'start_t': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_t': end_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        headers = {
            'accept': 'application/json',
            'Authorization': f"Bearer {self.bearer_token}"
        }
        
        url = f"{self.api_url}?" + urlencode(params)
        
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise CollectionError(
                    f"管理 API 請求失敗: HTTP {response.status}",
                    self.__class__.__name__,
                    "管理API"
                )
            
            data = await response.json()
            
            if not self.validate_management_response(data):
                raise CollectionError(
                    "管理 API 回應格式無效",
                    self.__class__.__name__,
                    "管理API"
                )
            
            return data
    
    def _process_task_data(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理任務數據，建立 GPU 使用者映射"""
        
        users = []
        gpu_user_mapping = {}
        
        # API 回應格式是以任務 ID 為鍵的字典
        # 遍歷所有任務
        for task_id, task in task_data.items():
            try:
                user_info = self._extract_user_info(task)
                if user_info:
                    users.append(user_info)
                    
                    # 建立 GPU 映射
                    for gpu_uuid in user_info.get('gpu_uuids', []):
                        gpu_user_mapping[gpu_uuid] = {
                            'username': user_info['username'],
                            'hostname': user_info['hostname'],
                            'task_type': user_info.get('task_type'),
                            'project_uuid': user_info.get('project_uuid'),
                            'start_time': user_info.get('start_time')
                        }
                        
            except Exception as e:
                self.logger.warning(f"處理任務數據時發生錯誤: {e}")
                continue
        
        return {
            'users': users,
            'gpu_user_mapping': gpu_user_mapping
        }
    
    def _extract_user_info(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """從任務數據中提取使用者資訊"""
        
        try:
            # 基本使用者資訊 (根據實際 API 格式)
            user_info = {
                'username': task.get('username', '未知'),
                'hostname': task.get('hostname', '未知'),
                'task_type': task.get('task', {}).get('_type', '未知') if isinstance(task.get('task'), dict) else '未知',
                'project_uuid': task.get('uuid', ''),
                'start_time': task.get('start_time', ''),
                'gpu_uuids': [],
                'task_uuid': task.get('task', {}).get('uuid', '') if isinstance(task.get('task'), dict) else ''
            }
            
            # 從 flavor 信息提取 GPU 數量和類型
            flavor = task.get('flavor', {})
            if isinstance(flavor, dict):
                gpu_count = flavor.get('gpu', 0)
                gpu_type = flavor.get('gpu_type', '')
                user_info['gpu_count'] = gpu_count
                user_info['gpu_type'] = gpu_type
            
            # 如果有 GPU 資源，創建假的 GPU UUID 列表 (因為 API 似乎沒有提供實際的 GPU UUID)
            if user_info.get('gpu_count', 0) > 0:
                # 使用任務 UUID + GPU 索引作為標識
                task_uuid = user_info.get('task_uuid', user_info.get('project_uuid', 'unknown'))
                user_info['gpu_uuids'] = [f"{task_uuid}_gpu_{i}" for i in range(user_info['gpu_count'])]
            
            return user_info if user_info.get('gpu_count', 0) > 0 else None
            
        except Exception as e:
            self.logger.warning(f"提取使用者資訊失敗: {e}")
            return None
    
    def map_absolute_gpu_to_card_id(self, absolute_gpu_id: int, hostname: str) -> Optional[int]:
        """將絕對 GPU ID 轉換為 Card ID
        
        Args:
            absolute_gpu_id: API 回傳的絕對 GPU ID (0-31)
            hostname: 主機名稱
            
        Returns:
            對應的 Card ID，如果無法映射則回傳 None
        """
        
        # 節點映射 (每個節點 8 個 GPU)
        node_mapping = {
            'colab-gpu1': 0,   # GPU 0-7
            'colab-gpu2': 8,   # GPU 8-15  
            'colab-gpu3': 16,  # GPU 16-23
            'colab-gpu4': 24   # GPU 24-31
        }
        
        if hostname not in node_mapping:
            return None
        
        node_offset = node_mapping[hostname]
        local_gpu_id = absolute_gpu_id - node_offset
        
        # 檢查範圍是否有效 (0-7)
        if local_gpu_id < 0 or local_gpu_id >= 8:
            return None
        
        # 映射到 Card ID
        card_ids = self.config.gpu.card_ids
        if local_gpu_id < len(card_ids):
            return card_ids[local_gpu_id]
        
        return None
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """驗證收集到的數據"""
        required_keys = ['users', 'gpu_user_mapping']
        
        for key in required_keys:
            if key not in data:
                return False
        
        users = data['users']
        if not isinstance(users, list):
            return False
        
        gpu_mapping = data['gpu_user_mapping'] 
        if not isinstance(gpu_mapping, dict):
            return False
        
        return True
    
    def validate_management_response(self, data: Dict[str, Any]) -> bool:
        """驗證管理 API 回應格式"""
        if not isinstance(data, dict):
            return False
        
        # API 回應格式是以任務 ID 為鍵的字典
        # 例如: {"671": {...}, "672": {...}}
        # 檢查是否有至少一個數字鍵
        if len(data) == 0:
            return True  # 空回應也是有效的
        
        # 檢查第一個鍵是否可能是任務 ID (數字字串)
        first_key = next(iter(data))
        if not isinstance(first_key, str) or not first_key.isdigit():
            return False
        
        # 檢查值是否是字典格式
        first_value = data[first_key]
        if not isinstance(first_value, dict):
            return False
        
        return True

    async def collect_user_tasks(self, target_date) -> Dict[str, Any]:
        """收集指定日期的使用者任務資訊
        
        Args:
            target_date: 目標日期 (date 對象)
            
        Returns:
            使用者任務資訊字典
        """
        from datetime import datetime, timedelta
        
        # 構建時間範圍 (當天 00:00:00 到 23:59:59)
        start_time = datetime.combine(target_date, datetime.min.time())
        end_time = start_time + timedelta(days=1, seconds=-1)
        
        try:
            result = await self.collect(start_time, end_time)
            return result
            
        except Exception as e:
            raise CollectionError(
                f"使用者任務收集失敗: {str(e)}",
                self.__class__.__name__,
                f"date-{target_date}"
            )