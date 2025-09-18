"""應用程式配置管理

提供統一的配置管理，支援環境變數和預設值。
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

# 載入 .env 檔案
from dotenv import load_dotenv

# 載入當前目錄的 .env 檔案
env_path = Path(__file__).parent.parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


@dataclass
class NodeConfig:
    """節點配置"""
    name: str
    ip: str
    port: int = 19999
    
    @property
    def netdata_url(self) -> str:
        return f"http://{self.ip}:{self.port}"


@dataclass
class GPUConfig:
    """GPU 硬體配置"""
    card_ids: List[int]
    indices: List[int]
    mapping: Dict[int, int]
    
    @classmethod
    def default(cls) -> 'GPUConfig':
        """預設 GPU 配置"""
        card_ids = [1, 9, 17, 25, 33, 41, 49, 57]
        indices = list(range(8))  # 0-7
        mapping = {
            1: 0, 9: 1, 17: 2, 25: 3,
            33: 4, 41: 5, 49: 6, 57: 7
        }
        return cls(card_ids=card_ids, indices=indices, mapping=mapping)


@dataclass
class APIConfig:
    """API 配置"""
    management_url: str
    bearer_token: str
    timeout: int = 30
    
    @classmethod
    def from_env(cls) -> 'APIConfig':
        """從環境變數載入 API 配置"""
        return cls(
            management_url=os.getenv(
                'MANAGEMENT_API_URL', 
                'http://192.168.10.100/api/v2/consumption/task'
            ),
            bearer_token=os.getenv('MANAGEMENT_API_TOKEN', ''),
            timeout=int(os.getenv('API_TIMEOUT', '30'))
        )


@dataclass
class AppConfig:
    """應用程式主配置"""
    data_dir: Path
    plots_dir: Path
    nodes: List[NodeConfig]
    gpu: GPUConfig
    api: APIConfig
    points: int = 144  # 數據點數：每10分鐘一個點，一天共144個點
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """從環境變數載入配置"""
        return cls(
            data_dir=Path(os.getenv('DATA_DIR', './data')),
            plots_dir=Path(os.getenv('PLOTS_DIR', './plots')),
            nodes=[
                NodeConfig('colab-gpu1', '192.168.10.103'),
                NodeConfig('colab-gpu2', '192.168.10.104'),
                NodeConfig('colab-gpu3', '192.168.10.105'),
                NodeConfig('colab-gpu4', '192.168.10.106'),
            ],
            gpu=GPUConfig.default(),
            api=APIConfig.from_env(),
            points=int(os.getenv('DATA_POINTS', '144'))
        )
    
    def get_node_by_name(self, name: str) -> Optional[NodeConfig]:
        """根據名稱獲取節點配置"""
        for node in self.nodes:
            if node.name == name:
                return node
        return None
    
    def get_node_by_ip(self, ip: str) -> Optional[NodeConfig]:
        """根據 IP 獲取節點配置"""
        for node in self.nodes:
            if node.ip == ip:
                return node
        return None