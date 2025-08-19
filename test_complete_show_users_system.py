#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
綜合測試所有命令的 show_users 參數功能
驗證完整的使用者顯示控制系統
"""

import subprocess
import sys
import os

def run_command(cmd):
    """執行命令並返回結果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd='/home/amditri/data_collection')
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_all_show_users_commands():
    """測試所有支援 show_users 參數的命令"""
    
    start_date = "2025-08-11"
    end_date = "2025-08-17"
    base_cmd = "./run_gpu_visualization.sh"
    
    commands_to_test = [
        ("vram-stacked", f"{base_cmd} vram-stacked {start_date} {end_date}"),
        ("vram-stacked false", f"{base_cmd} vram-stacked {start_date} {end_date} false"),
        ("nodes", f"{base_cmd} nodes {start_date} {end_date}"),
        ("nodes false", f"{base_cmd} nodes {start_date} {end_date} false"),
        ("quick", f"{base_cmd} quick {start_date} {end_date}"),
        ("quick false", f"{base_cmd} quick {start_date} {end_date} false"),
        ("vram-all", f"{base_cmd} vram-all {start_date} {end_date}"),
        ("vram-all false", f"{base_cmd} vram-all {start_date} {end_date} false"),
    ]
    
    print("🧪 使用者顯示控制系統綜合測試")
    print("=" * 60)
    print(f"測試期間: {start_date} 到 {end_date}")
    print("=" * 60)
    
    results = {}
    
    for test_name, cmd in commands_to_test:
        print(f"\n📊 測試 {test_name}...")
        print(f"命令: {cmd}")
        
        success, stdout, stderr = run_command(cmd)
        
        if success:
            print("✅ 命令執行成功")
            # 計算生成的檔案數量
            if "共 " in stdout:
                import re
                matches = re.findall(r'共 (\d+) 張圖', stdout)
                if matches:
                    chart_count = matches[-1]  # 取最後一個匹配
                    print(f"📈 生成圖表數量: {chart_count} 張")
                    results[test_name] = {"success": True, "charts": int(chart_count)}
                else:
                    results[test_name] = {"success": True, "charts": "未知"}
            else:
                results[test_name] = {"success": True, "charts": "未知"}
        else:
            print("❌ 命令執行失敗")
            if stderr:
                print(f"錯誤: {stderr[:200]}...")
            results[test_name] = {"success": False, "charts": 0}
    
    print("\n" + "=" * 60)
    print("📋 測試結果摘要")
    print("=" * 60)
    
    success_count = 0
    total_count = len(commands_to_test)
    
    for test_name, result in results.items():
        status = "✅ 通過" if result["success"] else "❌ 失敗"
        charts = f"({result['charts']} 張圖)" if result["success"] else ""
        print(f"{test_name:20} {status} {charts}")
        if result["success"]:
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 總體結果: {success_count}/{total_count} 個測試通過")
    
    if success_count == total_count:
        print("🎉 所有測試通過！使用者顯示控制系統實現完成！")
    else:
        print(f"⚠️  有 {total_count - success_count} 個測試失敗，需要進一步檢查")
    
    print("\n🔍 圖表生成數量分析:")
    if "quick" in results and "quick false" in results:
        quick_true = results["quick"]["charts"]
        quick_false = results["quick false"]["charts"]
        if isinstance(quick_true, int) and isinstance(quick_false, int):
            print(f"• quick 命令: {quick_true} → {quick_false} 張圖 (預期: 8→6)")
    
    if "vram-all" in results and "vram-all false" in results:
        vram_true = results["vram-all"]["charts"]
        vram_false = results["vram-all false"]["charts"]
        if isinstance(vram_true, int) and isinstance(vram_false, int):
            print(f"• vram-all 命令: {vram_true} → {vram_false} 張圖 (預期: 5→4)")

def check_generated_files():
    """檢查生成的檔案"""
    print("\n📁 檢查生成的檔案:")
    plots_dir = "/home/amditri/data_collection/plots"
    
    if os.path.exists(plots_dir):
        all_files = os.listdir(plots_dir)
        
        # 統計不同類型的檔案
        with_users_files = [f for f in all_files if "_with_users" in f and "2025-08-11" in f and "2025-08-17" in f]
        without_users_files = [f for f in all_files if "_without_users" in f and "2025-08-11" in f and "2025-08-17" in f]
        
        print(f"• 包含使用者資訊的檔案: {len(with_users_files)} 個")
        print(f"• 不包含使用者資訊的檔案: {len(without_users_files)} 個")
        
        if with_users_files:
            print("\n包含使用者資訊的檔案範例:")
            for f in sorted(with_users_files)[:5]:  # 顯示前 5 個
                print(f"  ✅ {f}")
        
        if without_users_files:
            print("\n不包含使用者資訊的檔案範例:")
            for f in sorted(without_users_files)[:5]:  # 顯示前 5 個
                print(f"  ❌ {f}")

if __name__ == "__main__":
    test_all_show_users_commands()
    check_generated_files()
    
    print("\n💡 提示:")
    print("1. 請手動檢查生成的圖表是否正確顯示/隱藏使用者資訊")
    print("2. 所有主要視覺化命令現在都支援使用者資訊控制")
    print("3. 使用 ./run_gpu_visualization.sh help 查看完整使用說明")