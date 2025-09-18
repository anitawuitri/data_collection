"""數據收集服務

提供統一的數據收集介面，整合 Netdata 和管理 API。
"""

import asyncio
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..collectors.netdata_collector import NetdataCollector
from ..collectors.management_collector import ManagementCollector
from ..models.node import Node
from ..models.gpu import GPU
from ..models.user import User
from ...infrastructure.config.settings import AppConfig


logger = logging.getLogger(__name__)


class DataCollectionService:
    """數據收集服務
    
    統一管理從多個數據源收集 GPU 相關數據的過程。
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.netdata_collector = NetdataCollector(config)
        self.management_collector = ManagementCollector(config)
    
    async def collect_daily_data(self, 
                                target_date: date,
                                nodes: Optional[List[str]] = None) -> Dict[str, Any]:
        """收集指定日期的所有數據
        
        Args:
            target_date: 目標日期
            nodes: 指定節點列表，None 表示所有節點
            
        Returns:
            包含收集結果的字典
        """
        logger.info(f"開始收集 {target_date} 的數據")
        
        # 確定目標節點
        target_nodes = nodes or [node.name for node in self.config.nodes]
        
        # 收集使用者任務資訊 (可選，需要 Bearer Token) - 先收集以便整合到節點數據中
        user_tasks = {}
        if self.config.api.bearer_token:
            try:
                logger.info("開始收集使用者任務資訊...")
                user_task_data = await self.management_collector.collect_user_tasks(target_date)
                user_tasks = user_task_data
                logger.info(f"使用者任務資訊收集成功: {len(user_task_data.get('users', []))} 個使用者")
            except Exception as e:
                logger.warning(f"收集使用者任務資訊失敗: {e}")
                collection_results['errors'].append({
                    'source': 'management_api',
                    'error': str(e)
                })
                user_tasks = {'users': [], 'gpu_user_mapping': {}}
        else:
            logger.info("跳過使用者任務資訊收集 (未設定 MANAGEMENT_API_TOKEN)")
            user_tasks = {'users': [], 'gpu_user_mapping': {}}

        # 並行收集各節點數據 (傳遞使用者任務資訊)
        tasks = []
        for node_name in target_nodes:
            node_config = self.config.get_node_by_name(node_name)
            if not node_config:
                logger.warning(f"節點配置未找到: {node_name}")
                continue
            
            task = self._collect_node_data(node_config, target_date, user_tasks)
            tasks.append(task)
        
        # 等待所有任務完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 處理結果
        collection_results = {
            'date': target_date.isoformat(),
            'nodes': {},
            'errors': [],
            'summary': {
                'total_nodes': len(target_nodes),
                'successful_nodes': 0,
                'failed_nodes': 0,
                'total_gpus': 0
            }
        }
        
        for i, result in enumerate(results):
            node_name = target_nodes[i]
            if isinstance(result, Exception):
                logger.error(f"節點 {node_name} 收集失敗: {result}")
                collection_results['errors'].append({
                    'node': node_name,
                    'error': str(result)
                })
                collection_results['summary']['failed_nodes'] += 1
            else:
                collection_results['nodes'][node_name] = result
                collection_results['summary']['successful_nodes'] += 1
                if 'gpu_count' in result:
                    collection_results['summary']['total_gpus'] += result['gpu_count']
        
        # 儲存使用者任務資訊到結果中
        collection_results['user_tasks'] = user_tasks
        
        logger.info(f"數據收集完成: {collection_results['summary']}")
        return collection_results
    
    async def _collect_node_data(self, 
                                 node_config, 
                                 target_date: date,
                                 user_tasks: Dict[str, Any] = None) -> Dict[str, Any]:
        """收集單個節點的數據
        
        Args:
            node_config: 節點配置
            target_date: 目標日期
            user_tasks: 使用者任務資訊 (可選)
        """
        logger.info(f"收集節點 {node_config.name} 的數據")
        
        node_result = {
            'node_name': node_config.name,
            'collection_time': datetime.now().isoformat(),
            'gpu_data': {},
            'gpu_count': 0,
            'errors': []
        }
        
        # 為每個 GPU 收集數據
        for gpu_index, card_id in enumerate(self.config.gpu.mapping.keys()):
            try:
                logger.debug(f"開始收集節點 {node_config.name} GPU{gpu_index} (Card {card_id}) 數據")
                
                # 收集 GPU 使用率數據
                gpu_data = None
                try:
                    gpu_data = await self.netdata_collector.collect_gpu_utilization(
                        node_config, card_id, target_date
                    )
                except Exception as gpu_error:
                    logger.warning(f"GPU 使用率收集失敗 {node_config.name} GPU{gpu_index}: {gpu_error}")
                    gpu_data = {'data': []}  # 使用空數據
                
                # 收集 VRAM 數據
                vram_data = None
                try:
                    vram_data = await self.netdata_collector.collect_vram_usage(
                        node_config, card_id, target_date
                    )
                except Exception as vram_error:
                    logger.warning(f"VRAM 使用率收集失敗 {node_config.name} GPU{gpu_index}: {vram_error}")
                    vram_data = {'data': []}  # 使用空數據
                
                # 合併數據
                gpu_result = {
                    'card_id': card_id,
                    'gpu_index': self.config.gpu.mapping[card_id],
                    'utilization': gpu_data,
                    'vram': vram_data,
                    'data_points': len(gpu_data.get('data', [])) if gpu_data else 0
                }
                
                # 嘗試從使用者任務資訊中找到使用者 (如果有的話)
                user_info = self._get_gpu_user_info(node_config.name, gpu_index, user_tasks)
                if user_info:
                    gpu_result['user'] = user_info['username']
                    gpu_result['user_info'] = user_info
                else:
                    gpu_result['user'] = 'unknown'
                
                node_result['gpu_data'][f'gpu{gpu_index}'] = gpu_result
                node_result['gpu_count'] += 1
                
                logger.debug(f"成功收集節點 {node_config.name} GPU{gpu_index}，數據點: {gpu_result['data_points']}")
                
            except Exception as e:
                logger.error(f"收集節點 {node_config.name} GPU{gpu_index} 數據失敗: {e}")
                node_result['errors'].append({
                    'gpu': f'gpu{gpu_index}',
                    'card_id': card_id,
                    'error': str(e)
                })
        
        logger.info(f"節點 {node_config.name} 收集完成，成功 GPU: {node_result['gpu_count']}, 錯誤: {len(node_result['errors'])}")
        return node_result
    
    def _get_gpu_user_info(self, node_name: str, gpu_index: int, user_tasks: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """獲取指定節點和 GPU 的使用者資訊
        
        Args:
            node_name: 節點名稱 (如 'colab-gpu1')
            gpu_index: GPU 索引 (0-7)
            user_tasks: 使用者任務資訊
            
        Returns:
            使用者資訊字典，如果沒有找到則回傳 None
        """
        if not user_tasks or 'users' not in user_tasks:
            return None
        
        # 從節點名稱提取主機名 (如 colab-gpu1 -> gpu1)
        hostname_suffix = node_name.replace('colab-', '')
        
        # 查找在此節點上運行的使用者任務
        for user in user_tasks['users']:
            # 檢查主機名是否匹配 (可能的格式: gpu1, colab-gpu1 等)
            user_hostname = user.get('hostname', '').lower()
            if (hostname_suffix.lower() in user_hostname or 
                node_name.lower() in user_hostname or
                user_hostname in node_name.lower()):
                
                # 如果使用者有 GPU，根據 GPU 數量和索引判斷
                gpu_count = user.get('gpu_count', 0)
                if gpu_count > 0:
                    # 簡單分配邏輯：假設使用者的 GPU 是連續分配的
                    # 可以根據實際需求調整這個邏輯
                    if gpu_index < gpu_count:
                        return {
                            'username': user.get('username', 'unknown'),
                            'task_type': user.get('task_type', 'unknown'),
                            'gpu_type': user.get('gpu_type', ''),
                            'gpu_count': gpu_count,
                            'task_uuid': user.get('task_uuid', ''),
                            'project_uuid': user.get('project_uuid', '')
                        }
        
        return None
    
    def save_collection_results(self, 
                               results: Dict[str, Any],
                               output_format: str = 'csv') -> List[Path]:
        """保存收集結果到文件
        
        Args:
            results: 收集結果
            output_format: 輸出格式 ('csv', 'json')
            
        Returns:
            生成的文件路徑列表
        """
        saved_files = []
        target_date = results['date']
        
        # 為每個節點保存數據
        for node_name, node_data in results['nodes'].items():
            if output_format == 'csv':
                files = self._save_node_data_as_csv(node_name, node_data, target_date)
                saved_files.extend(files)
            elif output_format == 'json':
                file_path = self._save_node_data_as_json(node_name, node_data, target_date)
                saved_files.append(file_path)
        
        return saved_files
    
    def _save_node_data_as_csv(self, 
                              node_name: str,
                              node_data: Dict[str, Any],
                              target_date: str) -> List[Path]:
        """以 CSV 格式保存節點數據"""
        import csv
        from collections import defaultdict
        
        saved_files = []
        node_dir = self.config.data_dir / node_name / target_date
        node_dir.mkdir(parents=True, exist_ok=True)
        
        # 為每個 GPU 生成 CSV 文件
        for gpu_key, gpu_data in node_data['gpu_data'].items():
            gpu_index = gpu_data['gpu_index']
            
            # GPU 使用率文件
            gpu_file = node_dir / f"gpu{gpu_index}_{target_date}.csv"
            with open(gpu_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['時間', 'GPU使用率(%)'])
                
                if gpu_data['utilization'] and gpu_data['utilization']['data']:
                    for timestamp, value in gpu_data['utilization']['data']:
                        dt = datetime.fromtimestamp(timestamp)
                        # 處理 None 值
                        value = value if value is not None else 0.0
                        writer.writerow([dt.strftime('%Y-%m-%d %H:%M:%S'), f"{float(value):.1f}"])
            
            saved_files.append(gpu_file)
            
            # VRAM 使用率文件
            vram_file = node_dir / f"gpu{gpu_index}_vram_{target_date}.csv"
            with open(vram_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['時間', 'VRAM使用率(%)'])
                
                if gpu_data['vram'] and gpu_data['vram']['data']:
                    for timestamp, value in gpu_data['vram']['data']:
                        dt = datetime.fromtimestamp(timestamp)
                        # 處理 None 值
                        value = value if value is not None else 0.0
                        writer.writerow([dt.strftime('%Y-%m-%d %H:%M:%S'), f"{float(value):.1f}"])
            
            saved_files.append(vram_file)
        
        # 生成平均值文件
        avg_file = node_dir / f"average_{target_date}.csv"
        self._generate_average_file(node_data, avg_file)
        saved_files.append(avg_file)
        
        return saved_files
    
    def _save_node_data_as_json(self,
                               node_name: str, 
                               node_data: Dict[str, Any],
                               target_date: str) -> Path:
        """以 JSON 格式保存節點數據"""
        import json
        
        node_dir = self.config.data_dir / node_name / target_date  
        node_dir.mkdir(parents=True, exist_ok=True)
        
        json_file = node_dir / f"{node_name}_{target_date}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(node_data, f, indent=2, ensure_ascii=False)
        
        return json_file
    
    def _generate_average_file(self, node_data: Dict[str, Any], avg_file: Path):
        """生成平均值 CSV 文件"""
        import csv
        from statistics import mean
        
        with open(avg_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['gpu', 'usage', 'vram', 'user'])
            
            total_usage = 0
            total_vram = 0
            gpu_count = 0
            
            # 為每個 GPU 計算平均值
            for gpu_key, gpu_data in node_data['gpu_data'].items():
                gpu_index = gpu_data['gpu_index']
                
                # 計算平均使用率
                usage_avg = 0
                if gpu_data['utilization'] and gpu_data['utilization']['data']:
                    usage_values = [float(val) if val is not None else 0.0 for _, val in gpu_data['utilization']['data']]
                    usage_avg = mean(usage_values) if usage_values else 0
                
                # 計算平均 VRAM 使用率
                vram_avg = 0
                if gpu_data['vram'] and gpu_data['vram']['data']:
                    vram_values = [float(val) if val is not None else 0.0 for _, val in gpu_data['vram']['data']]
                    vram_avg = mean(vram_values) if vram_values else 0
                
                # 使用者資訊 (如果有的話)
                user = gpu_data.get('user', 'unknown')
                
                writer.writerow([f'gpu{gpu_index}', f'{usage_avg:.1f}', f'{vram_avg:.1f}', user])
                
                total_usage += usage_avg
                total_vram += vram_avg
                gpu_count += 1
            
            # 寫入總平均
            if gpu_count > 0:
                writer.writerow([
                    '全部平均',
                    f'{total_usage/gpu_count:.1f}',
                    f'{total_vram/gpu_count:.1f}',
                    'all'
                ])