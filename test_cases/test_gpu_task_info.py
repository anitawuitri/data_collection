#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 GPU 使用者任務資訊功能

此腳本用於測試 daily_gpu_log.py 中新增的 GPU 使用者任務資訊功能
"""

import sys
from pathlib import Path

# 將 python 目錄加入路徑
python_dir = Path(__file__).parent / "python"
sys.path.insert(0, str(python_dir))

from daily_gpu_log import GPUDataCollector

def test_task_info_api():
    """測試 GPU 使用者任務資訊 API"""
    print("=== 測試 GPU 使用者任務資訊 API ===\n")
    
    # 初始化收集器
    collector = GPUDataCollector()
    
    # 測試日期
    test_date = "2025-07-22"
    
    print(f"測試日期: {test_date}")
    print(f"管理 API 域名: {collector.management_api['domain']}")
    print(f"Access Token: {collector.management_api['access_token'][:50]}...")
    
    # 獲取任務資訊
    task_info = collector.fetch_gpu_task_info(test_date)
    
    if task_info:
        print(f"\n✅ 成功獲取 {len(task_info)} 個 GPU 任務資訊")
        
        print("\n詳細任務資訊:")
        print("-" * 60)
        
        for gpu_uuid, info in task_info.items():
            print(f"GPU UUID: {gpu_uuid}")
            print(f"  使用者: {info['username']}")
            print(f"  主機名稱: {info['hostname']}")
            print(f"  GPU ID: {info['gpu_id']}")
            print(f"  GPU 名稱: {info['gpu_name']}")
            print(f"  GPU 記憶體: {info['gpu_memory']} MB")
            print(f"  任務類型: {info['task_type']}")
            print(f"  專案 UUID: {info['project_uuid']}")
            print(f"  映像檔: {info['image']}")
            print(f"  建立時間: {info['create_time']}")
            print(f"  開始時間: {info['start']}")
            print(f"  結束時間: {info['end'] if info['end'] else '執行中'}")
            print(f"  使用時長: {info['total_seconds']:.1f} 秒")
            print()
        
        # 測試生成使用者報告
        print("=== 生成使用者報告 ===")
        collector.generate_gpu_usage_report(test_date)
        
        return True
    else:
        print("❌ 未獲取到任務資訊")
        return False

def test_integration():
    """測試完整整合功能"""
    print("\n=== 測試完整整合功能 ===\n")
    
    collector = GPUDataCollector()
    
    # 測試只獲取使用者報告
    test_date = "2025-07-22"
    
    try:
        print("測試場景：只獲取使用者任務報告")
        collector.fetch_gpu_task_info(test_date)
        collector.generate_gpu_usage_report(test_date)
        
        print("\n✅ 整合功能測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 整合功能測試失敗: {e}")
        return False

def main():
    """主測試程式"""
    print("開始測試 GPU 使用者任務資訊功能...\n")
    
    # 測試 API 功能
    api_test = test_task_info_api()
    
    # 測試整合功能
    integration_test = test_integration()
    
    print("\n" + "="*60)
    print("測試結果總結:")
    print(f"API 功能測試: {'✅ 通過' if api_test else '❌ 失敗'}")
    print(f"整合功能測試: {'✅ 通過' if integration_test else '❌ 失敗'}")
    
    if api_test and integration_test:
        print("\n🎉 所有測試通過！GPU 使用者任務資訊功能已成功整合。")
        
        print("\n使用方式:")
        print("1. 正常數據收集 (包含使用者資訊):")
        print("   python3 python/daily_gpu_log.py 2025-07-22")
        print("\n2. 只顯示使用者任務報告:")
        print("   python3 python/daily_gpu_log.py --user-report 2025-07-22")
        print("\n3. 跳過使用者任務資訊:")
        print("   python3 python/daily_gpu_log.py --skip-task-info 2025-07-22")
        
        sys.exit(0)
    else:
        print("\n⚠️  某些測試失敗，請檢查設定。")
        sys.exit(1)

if __name__ == "__main__":
    main()
