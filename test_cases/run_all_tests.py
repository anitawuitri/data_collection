#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPU 監控系統測試套件主執行器
"""

import os
import sys
import subprocess
import importlib.util

# 設定路徑
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)
VISUALIZATION_DIR = os.path.join(PROJECT_ROOT, 'visualization')
PYTHON_DIR = os.path.join(PROJECT_ROOT, 'python')

# 添加路徑到 sys.path
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, VISUALIZATION_DIR)
sys.path.insert(0, PYTHON_DIR)

def print_header(title):
    """列印標題"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_section(title):
    """列印段落標題"""
    print(f"\n{title}")
    print("-" * 50)

def run_test_module(module_name, description):
    """執行測試模組"""
    print(f"\n🧪 執行測試: {description}")
    print(f"   模組: {module_name}")
    
    try:
        # 載入並執行模組
        spec = importlib.util.spec_from_file_location("test_module", 
                                                     os.path.join(TEST_DIR, module_name))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"   ✅ {description} - 通過")
        return True
    except Exception as e:
        print(f"   ❌ {description} - 失敗: {str(e)}")
        return False

def run_shell_command(command, description):
    """執行 shell 命令"""
    print(f"\n🔧 執行命令: {description}")
    print(f"   命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, cwd=PROJECT_ROOT, 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"   ✅ {description} - 成功")
            return True
        else:
            print(f"   ❌ {description} - 失敗")
            if result.stderr:
                print(f"   錯誤: {result.stderr[:200]}...")
            return False
    except subprocess.TimeoutExpired:
        print(f"   ⏰ {description} - 超時")
        return False
    except Exception as e:
        print(f"   ❌ {description} - 異常: {str(e)}")
        return False

def main():
    """主要測試流程"""
    print_header("GPU 監控系統完整測試套件")
    
    # 測試結果統計
    total_tests = 0
    passed_tests = 0
    
    # 1. 基礎功能測試
    print_section("1. 基礎功能測試")
    
    basic_tests = [
        ("test_chinese_font.py", "中文字體支援測試"),
        ("test_fonts.py", "字體配置測試"),
        ("test_gpu_mapping.py", "GPU ID 映射測試"),
        ("test_gpu_task_info.py", "GPU 任務資訊測試"),
        ("test_user_column.py", "使用者欄位測試"),
        ("test_gpu_collector.py", "GPU 資料收集器測試")
    ]
    
    for module, description in basic_tests:
        total_tests += 1
        if run_test_module(module, description):
            passed_tests += 1
    
    # 2. 視覺化功能測試
    print_section("2. 視覺化功能測試")
    
    visualization_tests = [
        ("test_user_info.py", "使用者資訊視覺化測試"),
        ("test_heatmap_users.py", "Heatmap 使用者資訊測試")
    ]
    
    for module, description in visualization_tests:
        total_tests += 1
        if run_test_module(module, description):
            passed_tests += 1
    
    # 3. 系統驗證測試
    print_section("3. 系統驗證測試")
    
    verification_tests = [
        ("chart_verification.py", "圖表檔案驗證"),
        ("final_verification.py", "最終系統驗證")
    ]
    
    for module, description in verification_tests:
        total_tests += 1
        if run_test_module(module, description):
            passed_tests += 1
    
    # 4. 整合測試
    print_section("4. 整合測試")
    
    integration_tests = [
        ("python3 python/daily_gpu_log.py 2025-08-04", "資料收集整合測試"),
        ("./run_user_monitor.sh verify", "系統驗證整合測試")
    ]
    
    for command, description in integration_tests:
        total_tests += 1
        if run_shell_command(command, description):
            passed_tests += 1
    
    # 5. 圖表生成測試
    print_section("5. 圖表生成測試")
    
    chart_tests = [
        ("./run_user_monitor.sh quick 2025-08-04 2025-08-05", "快速圖表生成測試"),
        ("./run_user_monitor.sh heatmap 2025-08-04 2025-08-05", "熱力圖生成測試"),
        ("./run_user_monitor.sh users 2025-08-04 2025-08-05", "使用者活動摘要測試")
    ]
    
    for command, description in chart_tests:
        total_tests += 1
        if run_shell_command(command, description):
            passed_tests += 1
    
    # 測試總結
    print_header("測試結果總結")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 測試統計:")
    print(f"   總測試數: {total_tests}")
    print(f"   通過測試: {passed_tests}")
    print(f"   失敗測試: {total_tests - passed_tests}")
    print(f"   成功率: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print(f"\n🎉 測試結果: 優秀！系統功能正常")
        print("✅ GPU 監控系統已準備就緒")
    elif success_rate >= 70:
        print(f"\n⚠️  測試結果: 良好，部分功能需要檢查")
        print("🔧 建議檢查失敗的測試項目")
    else:
        print(f"\n❌ 測試結果: 需要改進")
        print("🚨 請修復失敗的測試項目後重新測試")
    
    # 系統資訊
    print(f"\n📋 系統資訊:")
    print(f"   測試執行目錄: {TEST_DIR}")
    print(f"   專案根目錄: {PROJECT_ROOT}")
    print(f"   Python 版本: {sys.version.split()[0]}")
    
    print("\n" + "=" * 70)
    
    return success_rate >= 90

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
