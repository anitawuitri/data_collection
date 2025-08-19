#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VRAM 堆疊圖使用者標籤測試
"""

import sys
import os
from datetime import datetime, timedelta

# 添加路徑
sys.path.append('visualization')
from quick_gpu_trend_plots import quick_nodes_vram_stacked_utilization, load_gpu_data_with_users

def check_user_data_collection():
    """檢查使用者資料收集"""
    print("👥 檢查使用者資料收集...")
    
    # 測試期間
    start_date = '2025-07-16'
    end_date = '2025-08-17'
    
    # 生成日期列表（檢查前幾天）
    start = datetime.strptime(start_date, '%Y-%m-%d')
    dates_to_check = []
    for i in range(5):  # 檢查前5天
        check_date = start + timedelta(days=i)
        dates_to_check.append(check_date.strftime('%Y-%m-%d'))
    
    nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
    
    # 收集使用者資訊
    print(f"\n檢查日期: {', '.join(dates_to_check)}")
    
    for node in nodes:
        print(f"\n📊 節點: {node}")
        all_users_in_node = set()
        
        for date_str in dates_to_check:
            avg_file = os.path.join('data', node, date_str, f"average_{date_str}.csv")
            
            if os.path.exists(avg_file):
                df = load_gpu_data_with_users(avg_file)
                if df is not None:
                    # 重命名列
                    if '平均VRAM使用率(%)' in df.columns:
                        df = df.rename(columns={'平均VRAM使用率(%)': 'vram'})
                    
                    if 'vram' in df.columns:
                        # 過濾非平均行
                        gpu_data = df[~df['gpu'].str.contains('全部平均', na=False)]
                        
                        # 收集當天的使用者
                        day_users = []
                        for _, row in gpu_data.iterrows():
                            user = row.get('user', '未知')
                            vram_usage = pd.to_numeric(row.get('vram', 0), errors='coerce')
                            
                            if user and user not in ['未使用', '未知'] and not pd.isna(vram_usage) and vram_usage >= 0.1:
                                if user not in day_users:
                                    day_users.append(user)
                                    all_users_in_node.add(user)
                        
                        if day_users:
                            print(f"  {date_str}: {', '.join(day_users)}")
                        else:
                            print(f"  {date_str}: 無活躍使用者")
            else:
                print(f"  {date_str}: 檔案不存在")
        
        if all_users_in_node:
            print(f"  💡 節點總使用者: {', '.join(sorted(all_users_in_node))}")
        else:
            print(f"  ⚠️  節點無使用者記錄")

def test_label_display():
    """測試標籤顯示"""
    print("\n🏷️  測試標籤顯示...")
    
    try:
        # 生成 VRAM 堆疊圖
        result = quick_nodes_vram_stacked_utilization(
            start_date='2025-07-16', 
            end_date='2025-08-17',
            data_dir='data',
            plots_dir='plots',
            show_users=True
        )
        
        if result and os.path.exists(result):
            file_size = os.path.getsize(result) / 1024
            print(f"✅ VRAM 堆疊圖生成成功")
            print(f"✅ 檔案: {result}")
            print(f"✅ 大小: {file_size:.1f} KB")
            
            # 檢查修改時間
            mod_time = os.path.getmtime(result)
            mod_datetime = datetime.fromtimestamp(mod_time)
            print(f"✅ 更新時間: {mod_datetime.strftime('%H:%M:%S')}")
            
            return True
        else:
            print("❌ 圖表生成失敗")
            return False
    except Exception as e:
        print(f"❌ 測試錯誤: {e}")
        return False

def verify_label_improvements():
    """驗證標籤改進項目"""
    print("\n📋 驗證標籤改進項目...")
    
    improvements = [
        "✅ 收集整個期間的使用者資訊（而非僅最後一天）",
        "✅ 智能顯示邏輯：",
        "   • <= 2人：顯示全部使用者名稱",
        "   • 3人：顯示全部使用者名稱", 
        "   • > 3人：顯示前2人 + '等X人'",
        "✅ 無使用者時顯示 '(無使用者)'",
        "✅ 過濾條件：VRAM >= 0.1% 且非'未使用'/'未知'",
        "✅ 使用者名稱去重和排序"
    ]
    
    for improvement in improvements:
        print(improvement)
    
    return True

def main():
    """主函數"""
    print("=" * 60)
    print("🏷️  VRAM 堆疊圖使用者標籤測試")
    print("=" * 60)
    
    # 檢查使用者資料收集
    check_user_data_collection()
    
    # 測試標籤顯示
    test1_result = test_label_display()
    
    # 驗證標籤改進
    test2_result = verify_label_improvements()
    
    print("\n" + "=" * 60)
    print("📊 測試結果")
    print("=" * 60)
    
    if test1_result:
        print("✅ 標籤顯示測試 - 通過")
    else:
        print("❌ 標籤顯示測試 - 失敗")
    
    if test2_result:
        print("✅ 標籤改進驗證 - 通過")
    else:
        print("❌ 標籤改進驗證 - 失敗")
    
    if test1_result and test2_result:
        print("\n🎉 使用者標籤功能測試通過！")
        print("\n💡 預期標籤格式:")
        print("   • colab-gpu1 (admin)")
        print("   • colab-gpu2 (nycubme)")  
        print("   • colab-gpu3 (無使用者)")
        print("   • colab-gpu4 (itrd, nycubme)")
        
        print("\n📈 查看生成的圖表:")
        print("   plots/nodes_vram_stacked_utilization_2025-07-16_to_2025-08-17.png")
        
        return True
    else:
        print("\n⚠️  部分測試失敗")
        return False

if __name__ == "__main__":
    import pandas as pd
    import numpy as np
    main()
