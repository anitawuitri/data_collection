#!/usr/bin/env python3
"""重構測試腳本

測試重構後的模組結構是否正確，無需外部依賴。
"""

import sys
import os
from pathlib import Path

# 添加 src 目錄到路徑
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

def test_imports():
    """測試模組導入"""
    print("🔍 測試模組導入...")
    
    try:
        # 測試配置模組
        from infrastructure.config.settings import AppConfig
        print("✅ 配置模組導入成功")
        
        # 測試領域模型
        from core.models.gpu import GPU
        from core.models.user import User  
        from core.models.node import Node
        print("✅ 領域模型導入成功")
        
        # 測試基礎收集器
        from core.collectors.base_collector import BaseCollector
        print("✅ 基礎收集器導入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模組導入失敗: {e}")
        return False

def test_config():
    """測試配置系統"""
    print("\n📊 測試配置系統...")
    
    try:
        from infrastructure.config.settings import AppConfig
        
        # 測試配置載入
        config = AppConfig.from_env()
        
        print(f"✅ 配置載入成功")
        print(f"   • 數據目錄: {config.data_dir}")
        print(f"   • 圖表目錄: {config.plots_dir}")
        print(f"   • 節點數量: {len(config.nodes)}")
        print(f"   • GPU 數量: {len(config.gpu.card_ids)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置測試失敗: {e}")
        return False

def test_models():
    """測試領域模型"""
    print("\n🏗️ 測試領域模型...")
    
    try:
        from core.models.gpu import GPU, GPUMetric
        from core.models.user import User
        from core.models.node import Node
        
        # 測試 GPU 模型
        gpu_metric = GPUMetric(
            timestamp=1694950000,
            datetime="2025-09-17 10:00:00",
            gpu_utilization=75.5,
            vram_utilization=60.2,
            temperature=65.0
        )
        
        gpu = GPU(
            card_id=1,
            index=0,
            node_name="colab-gpu1",
            metrics=[gpu_metric]
        )
        
        print(f"✅ GPU 模型測試成功 - Card ID: {gpu.card_id}, 指標數: {len(gpu.metrics)}")
        
        # 測試使用者模型
        user = User(
            username="test_user",
            hostname="test_host"
        )
        
        print(f"✅ 使用者模型測試成功 - 使用者: {user.username}")
        
        # 測試節點模型
        node = Node(
            name="colab-gpu1",
            ip="192.168.10.103",
            port=19999
        )
        
        print(f"✅ 節點模型測試成功 - 節點: {node.name} ({node.ip}:{node.port})")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型測試失敗: {e}")
        return False

def test_cli_structure():
    """測試 CLI 結構"""
    print("\n🖥️ 測試 CLI 結構...")
    
    try:
        # 檢查 CLI 文件是否存在
        cli_files = [
            'cli/main.py',
            'cli/commands/collect.py',
            'cli/commands/query.py',
            'cli/commands/visualize.py'
        ]
        
        missing_files = []
        for file_path in cli_files:
            full_path = src_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ 缺少 CLI 文件: {missing_files}")
            return False
        
        print("✅ CLI 文件結構完整")
        
        # 檢查入口點
        main_script = Path(__file__).parent / 'gpu-monitor.py'
        if main_script.exists():
            print("✅ 主入口點腳本存在")
        else:
            print("⚠️ 主入口點腳本不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI 結構測試失敗: {e}")
        return False

def test_project_structure():
    """測試專案結構"""
    print("\n📁 測試專案結構...")
    
    required_dirs = [
        'src/core/collectors',
        'src/core/models', 
        'src/core/services',
        'src/cli/commands',
        'src/infrastructure/config'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        full_path = Path(__file__).parent / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ 缺少目錄: {missing_dirs}")
        return False
    
    print("✅ 專案目錄結構完整")
    
    # 檢查配置文件
    config_files = [
        'pyproject.toml',
        'requirements.txt',
        'setup.sh',
        'Dockerfile',
        'docker-compose.yml'
    ]
    
    existing_configs = []
    for config_file in config_files:
        full_path = Path(__file__).parent / config_file
        if full_path.exists():
            existing_configs.append(config_file)
    
    print(f"✅ 配置文件: {', '.join(existing_configs)}")
    
    return True

def main():
    """主測試函數"""
    print("🎉 AMD GPU 監控系統重構測試")
    print("=" * 50)
    
    test_results = []
    
    # 執行各項測試
    test_results.append(("專案結構", test_project_structure()))
    test_results.append(("模組導入", test_imports()))
    test_results.append(("配置系統", test_config()))
    test_results.append(("領域模型", test_models()))
    test_results.append(("CLI 結構", test_cli_structure()))
    
    # 統計結果
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"\n📊 測試結果總結:")
    print("=" * 50)
    
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name:<12}: {status}")
    
    print(f"\n🎯 總體結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 重構測試完全成功！系統已準備就緒。")
        return True
    else:
        print("⚠️ 部分測試失敗，需要修復問題。")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)