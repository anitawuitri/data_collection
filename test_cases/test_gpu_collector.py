#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Python 版本的 GPU 數據收集器

提供基本的功能測試和環境檢查
"""

import sys
import subprocess
from pathlib import Path

def test_python_environment():
    """測試 Python 環境"""
    print("=== Python 環境檢查 ===")
    
    # 檢查 Python 版本
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 7):
        print("❌ Python 版本過舊，需要 3.7+")
        return False
    else:
        print("✅ Python 版本符合要求")
    
    # 檢查必要套件
    required_packages = ['requests', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安裝")
        except ImportError:
            print(f"❌ {package} 未安裝")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n請安裝缺失的套件: pip3 install {' '.join(missing_packages)}")
        return False
    
    return True

def test_script_syntax():
    """測試腳本語法"""
    print("\n=== 腳本語法檢查 ===")
    
    script_path = Path(__file__).parent / "daily_gpu_log.py"
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'py_compile', str(script_path)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 腳本語法正確")
            return True
        else:
            print(f"❌ 腳本語法錯誤: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 語法檢查失敗: {e}")
        return False

def test_class_import():
    """測試類別匯入"""
    print("\n=== 類別匯入測試 ===")
    
    try:
        # 添加當前目錄到路徑
        sys.path.insert(0, str(Path(__file__).parent))
        
        from daily_gpu_log import GPUDataCollector
        
        # 測試初始化
        collector = GPUDataCollector()
        print("✅ GPUDataCollector 類別匯入成功")
        
        # 測試基本屬性
        print(f"✅ GPU IDs: {collector.gpu_ids}")
        print(f"✅ 節點對照: {list(collector.ip_name_map.values())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 類別匯入失敗: {e}")
        return False

def test_date_validation():
    """測試日期驗證功能"""
    print("\n=== 日期驗證測試 ===")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from daily_gpu_log import GPUDataCollector
        
        collector = GPUDataCollector()
        
        # 測試有效日期
        valid_dates = ['2025-08-01', '2025-12-31', '2024-02-29']
        for date in valid_dates:
            if collector.validate_date(date):
                print(f"✅ 有效日期: {date}")
            else:
                print(f"❌ 日期驗證失敗: {date}")
        
        # 測試無效日期
        invalid_dates = ['2025-13-01', '2025-02-30', '25-08-01', 'invalid']
        for date in invalid_dates:
            if not collector.validate_date(date):
                print(f"✅ 正確拒絕無效日期: {date}")
            else:
                print(f"❌ 錯誤接受無效日期: {date}")
        
        return True
        
    except Exception as e:
        print(f"❌ 日期驗證測試失敗: {e}")
        return False

def test_timestamp_calculation():
    """測試時間戳計算"""
    print("\n=== 時間戳計算測試 ===")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from daily_gpu_log import GPUDataCollector
        
        collector = GPUDataCollector()
        
        # 測試特定日期
        test_date = '2025-08-01'
        start, end = collector.calculate_timestamps(test_date)
        
        print(f"✅ {test_date} 開始時間戳: {start}")
        print(f"✅ {test_date} 結束時間戳: {end}")
        
        # 驗證時間戳合理性 (一天 = 86400 秒)
        if (end - start) == 86399:  # 23:59:59 - 00:00:00 = 86399 秒
            print("✅ 時間戳計算正確")
            return True
        else:
            print(f"❌ 時間戳計算錯誤，差值: {end - start}")
            return False
        
    except Exception as e:
        print(f"❌ 時間戳計算測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("AMD GPU 數據收集器 - Python 版本測試")
    print("=" * 50)
    
    tests = [
        test_python_environment,
        test_script_syntax,
        test_class_import,
        test_date_validation,
        test_timestamp_calculation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 測試異常: {e}")
    
    print("\n" + "=" * 50)
    print(f"測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！Python 版本準備就緒。")
        return 0
    else:
        print("⚠️  部分測試失敗，請檢查上述錯誤訊息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
