"""測試套件配置

提供 pytest 配置和共用測試工具。
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, patch

from src.infrastructure.config.settings import AppConfig, NodeConfig, GPUConfig, APIConfig


@pytest.fixture
def temp_dir():
    """臨時目錄 fixture"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_config(temp_dir):
    """模擬配置 fixture"""
    return AppConfig(
        data_dir=temp_dir / "data",
        plots_dir=temp_dir / "plots",
        nodes=[
            NodeConfig('test-gpu1', '127.0.0.1', 19999),
            NodeConfig('test-gpu2', '127.0.0.2', 19999),
        ],
        gpu=GPUConfig.default(),
        api=APIConfig(
            management_url="http://test-api.example.com/api/v2/consumption/task",
            bearer_token="test-token-123",
            timeout=10
        ),
        points=144
    )


@pytest.fixture
def sample_netdata_response():
    """範例 Netdata API 回應"""
    return {
        "api": 1,
        "id": "amdgpu.gpu_utilization_unknown_AMD_GPU_card1",
        "name": "amdgpu.gpu_utilization_unknown_AMD_GPU_card1",
        "view_update_every": 1,
        "update_every": 1,
        "first_entry": 1632150000,
        "last_entry": 1632159999,
        "before": 1632159999,
        "after": 1632150000,
        "dimension_names": ["utilization"],
        "dimension_ids": ["utilization"],
        "latest_values": [25.5],
        "view_latest_values": [25.5],
        "dimensions": 1,
        "points": 144,
        "format": "json",
        "result": {
            "data": [
                [1632150000, 12.5],
                [1632150600, 15.3],
                [1632151200, 25.8],
                [1632151800, 30.2]
            ]
        },
        "data": [
            [1632150000, 12.5],
            [1632150600, 15.3], 
            [1632151200, 25.8],
            [1632151800, 30.2]
        ],
        "labels": {
            "chart": "amdgpu.gpu_utilization_unknown_AMD_GPU_card1",
            "family": "amdgpu_card1"
        }
    }


@pytest.fixture
def sample_management_response():
    """範例管理 API 回應"""
    return {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": "task-001",
                "user": {
                    "username": "test_user",
                    "email": "test@example.com"
                },
                "hostname": "test-gpu1",
                "type": "LAB",
                "project_uuid": "project-uuid-123",
                "start_time": "2025-09-15 09:00:00",
                "gpuconfig": {
                    "gpus": ["gpu-uuid-001", "gpu-uuid-002"]
                }
            }
        ]
    }


@pytest.fixture 
def sample_gpu_metrics():
    """範例 GPU 指標數據"""
    from src.core.models.gpu import GPUMetric
    
    return [
        GPUMetric(
            timestamp=1632150000,
            datetime="2025-09-15 09:00:00",
            gpu_utilization=12.5,
            vram_utilization=45.2
        ),
        GPUMetric(
            timestamp=1632150600, 
            datetime="2025-09-15 09:10:00",
            gpu_utilization=15.3,
            vram_utilization=48.7
        ),
        GPUMetric(
            timestamp=1632151200,
            datetime="2025-09-15 09:20:00", 
            gpu_utilization=25.8,
            vram_utilization=52.1
        )
    ]


@pytest.fixture(scope="session")
def event_loop():
    """事件迴圈 fixture for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


class AsyncMock:
    """異步 Mock 工具類別"""
    
    def __init__(self, return_value=None, side_effect=None):
        self.return_value = return_value
        self.side_effect = side_effect
        self.call_count = 0
        self.call_args_list = []
    
    async def __call__(self, *args, **kwargs):
        self.call_count += 1
        self.call_args_list.append((args, kwargs))
        
        if self.side_effect:
            if isinstance(self.side_effect, Exception):
                raise self.side_effect
            return self.side_effect(*args, **kwargs)
        
        return self.return_value


# 測試工具函數
def create_test_data_structure(base_dir: Path):
    """創建測試用數據目錄結構"""
    # 創建節點目錄
    for node in ['colab-gpu1', 'colab-gpu2']:
        node_dir = base_dir / node / '2025-09-15'
        node_dir.mkdir(parents=True, exist_ok=True)
        
        # 創建範例 CSV 文件
        for gpu_index in range(8):
            csv_file = node_dir / f"gpu{gpu_index}_2025-09-15.csv"
            csv_content = """時間戳,日期時間,GPU使用率(%),VRAM使用率(%)
1632150000,"2025-09-15 09:00:00",12.5,45.2
1632150600,"2025-09-15 09:10:00",15.3,48.7
1632151200,"2025-09-15 09:20:00",25.8,52.1
"""
            csv_file.write_text(csv_content)
        
        # 創建平均文件
        avg_file = node_dir / "average_2025-09-15.csv"
        avg_content = """GPU編號,平均GPU使用率(%),平均VRAM使用率(%),使用者
GPU[0],17.9,48.7,test_user
GPU[1],0.0,0.1,未使用
GPU[2],0.0,0.1,未使用
GPU[3],0.0,0.1,未使用
GPU[4],0.0,0.1,未使用
GPU[5],0.0,0.1,未使用
GPU[6],0.0,0.1,未使用
GPU[7],0.0,0.1,未使用
全部平均,2.2,6.2,所有使用者
"""
        avg_file.write_text(avg_content)


# 標記異步測試
asyncio_mark = pytest.mark.asyncio