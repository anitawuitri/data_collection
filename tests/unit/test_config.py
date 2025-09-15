"""配置管理測試

測試應用程式配置載入和驗證功能。
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch

from src.infrastructure.config.settings import AppConfig, NodeConfig, GPUConfig, APIConfig


class TestNodeConfig:
    """測試節點配置"""
    
    def test_node_config_creation(self):
        """測試節點配置創建"""
        node = NodeConfig('test-gpu1', '192.168.1.100', 19999)
        
        assert node.name == 'test-gpu1'
        assert node.ip == '192.168.1.100'
        assert node.port == 19999
        assert node.netdata_url == 'http://192.168.1.100:19999'
    
    def test_node_config_default_port(self):
        """測試節點配置預設連接埠"""
        node = NodeConfig('test-gpu1', '192.168.1.100')
        
        assert node.port == 19999
        assert node.netdata_url == 'http://192.168.1.100:19999'


class TestGPUConfig:
    """測試 GPU 配置"""
    
    def test_gpu_config_default(self):
        """測試預設 GPU 配置"""
        config = GPUConfig.default()
        
        assert config.card_ids == [1, 9, 17, 25, 33, 41, 49, 57]
        assert config.indices == list(range(8))
        assert len(config.mapping) == 8
        assert config.mapping[1] == 0
        assert config.mapping[57] == 7
    
    def test_gpu_config_custom(self):
        """測試自定義 GPU 配置"""
        card_ids = [1, 2, 3, 4]
        indices = [0, 1, 2, 3]
        mapping = {1: 0, 2: 1, 3: 2, 4: 3}
        
        config = GPUConfig(card_ids, indices, mapping)
        
        assert config.card_ids == card_ids
        assert config.indices == indices
        assert config.mapping == mapping


class TestAPIConfig:
    """測試 API 配置"""
    
    def test_api_config_creation(self):
        """測試 API 配置創建"""
        config = APIConfig(
            management_url="http://test.com/api",
            bearer_token="test-token",
            timeout=30
        )
        
        assert config.management_url == "http://test.com/api"
        assert config.bearer_token == "test-token"
        assert config.timeout == 30
    
    @patch.dict(os.environ, {
        'MANAGEMENT_API_URL': 'http://env.test.com/api',
        'MANAGEMENT_API_TOKEN': 'env-token',
        'API_TIMEOUT': '60'
    })
    def test_api_config_from_env(self):
        """測試從環境變數載入 API 配置"""
        config = APIConfig.from_env()
        
        assert config.management_url == 'http://env.test.com/api'
        assert config.bearer_token == 'env-token'
        assert config.timeout == 60
    
    def test_api_config_from_env_defaults(self):
        """測試環境變數預設值"""
        with patch.dict(os.environ, {}, clear=True):
            config = APIConfig.from_env()
            
            assert config.management_url == 'http://192.168.10.100/api/v2/consumption/task'
            assert config.bearer_token == ''
            assert config.timeout == 30


class TestAppConfig:
    """測試應用程式主配置"""
    
    def test_app_config_creation(self, temp_dir):
        """測試應用程式配置創建"""
        config = AppConfig(
            data_dir=temp_dir / "data",
            plots_dir=temp_dir / "plots",
            nodes=[
                NodeConfig('test-gpu1', '192.168.1.100'),
                NodeConfig('test-gpu2', '192.168.1.101')
            ],
            gpu=GPUConfig.default(),
            api=APIConfig("http://test.com/api", "token"),
            points=144
        )
        
        assert config.data_dir == temp_dir / "data"
        assert config.plots_dir == temp_dir / "plots"
        assert len(config.nodes) == 2
        assert config.points == 144
    
    @patch.dict(os.environ, {
        'DATA_DIR': '/custom/data',
        'PLOTS_DIR': '/custom/plots',
        'DATA_POINTS': '288'
    })
    def test_app_config_from_env(self):
        """測試從環境變數載入應用程式配置"""
        config = AppConfig.from_env()
        
        assert config.data_dir == Path('/custom/data')
        assert config.plots_dir == Path('/custom/plots')
        assert config.points == 288
        assert len(config.nodes) == 4  # 預設 4 個節點
    
    def test_get_node_by_name(self, mock_config):
        """測試根據名稱獲取節點"""
        node = mock_config.get_node_by_name('test-gpu1')
        
        assert node is not None
        assert node.name == 'test-gpu1'
        assert node.ip == '127.0.0.1'
        
        # 測試不存在的節點
        node = mock_config.get_node_by_name('non-existent')
        assert node is None
    
    def test_get_node_by_ip(self, mock_config):
        """測試根據 IP 獲取節點"""
        node = mock_config.get_node_by_ip('127.0.0.1')
        
        assert node is not None
        assert node.name == 'test-gpu1'
        assert node.ip == '127.0.0.1'
        
        # 測試不存在的 IP
        node = mock_config.get_node_by_ip('192.168.1.999')
        assert node is None
    
    def test_default_nodes_configuration(self):
        """測試預設節點配置"""
        config = AppConfig.from_env()
        
        expected_nodes = [
            ('colab-gpu1', '192.168.10.103'),
            ('colab-gpu2', '192.168.10.104'),
            ('colab-gpu3', '192.168.10.105'),
            ('colab-gpu4', '192.168.10.106')
        ]
        
        assert len(config.nodes) == 4
        
        for i, (name, ip) in enumerate(expected_nodes):
            assert config.nodes[i].name == name
            assert config.nodes[i].ip == ip
            assert config.nodes[i].port == 19999