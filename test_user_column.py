#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 GPU 日報表中的使用者欄位功能

此腳本展示新增的使用者欄位在 CSV 檔案和摘要報告中的顯示
"""

import pandas as pd
from pathlib import Path

def test_user_column_in_reports():
    """測試 GPU 日報表中的使用者欄位"""
    print("=== 測試 GPU 日報表使用者欄位功能 ===\n")
    
    # 測試日期和節點
    test_date = "2025-07-22"
    test_nodes = ["colab-gpu1", "colab-gpu2", "colab-gpu3", "colab-gpu4"]
    
    print(f"測試日期: {test_date}")
    print(f"測試節點: {test_nodes}\n")
    
    for node in test_nodes:
        data_dir = Path(f"./data/{node}/{test_date}")
        avg_csv = data_dir / f"average_{test_date}.csv"
        summary_txt = data_dir / f"summary_{test_date}.txt"
        
        print(f"=== {node} ===")
        
        if avg_csv.exists():
            print(f"✅ 平均值 CSV 檔案存在: {avg_csv}")
            
            # 讀取 CSV 檔案
            try:
                df = pd.read_csv(avg_csv)
                print(f"📊 CSV 欄位: {list(df.columns)}")
                
                # 檢查是否包含使用者欄位
                if '使用者' in df.columns:
                    print("✅ 包含使用者欄位")
                    
                    # 顯示有使用者的 GPU
                    used_gpus = df[df['使用者'] != '未使用']
                    if not used_gpus.empty:
                        print("🎯 使用中的 GPU:")
                        for _, row in used_gpus.iterrows():
                            if row['GPU編號'] != '全部平均':
                                print(f"   {row['GPU編號']}: {row['使用者']} (GPU使用率: {row['平均GPU使用率(%)']}%, VRAM使用率: {row['平均VRAM使用率(%)']}%)")
                    else:
                        print("⚪ 此節點無使用中的 GPU")
                else:
                    print("❌ 缺少使用者欄位")
                    
            except Exception as e:
                print(f"❌ 讀取 CSV 時發生錯誤: {e}")
        else:
            print(f"❌ 平均值 CSV 檔案不存在: {avg_csv}")
        
        if summary_txt.exists():
            print(f"✅ 摘要報告存在: {summary_txt}")
            
            # 檢查摘要報告是否包含使用者資訊
            with open(summary_txt, 'r', encoding='utf-8') as f:
                content = f.read()
                if "使用者:" in content:
                    print("✅ 摘要報告包含使用者資訊")
                else:
                    print("⚠️  摘要報告可能缺少使用者資訊")
        else:
            print(f"❌ 摘要報告不存在: {summary_txt}")
        
        print()

def show_csv_format_comparison():
    """顯示 CSV 格式的對比"""
    print("=== CSV 格式對比 ===\n")
    
    print("舊格式 (無使用者欄位):")
    print("GPU卡號,平均GPU使用率(%),平均VRAM使用率(%)")
    print("gpu1,0.00,0.14")
    print("gpu17,19.93,83.38")
    print("全部平均,4.82,20.81")
    print()
    
    print("新格式 (包含使用者欄位):")
    print("GPU編號,平均GPU使用率(%),平均VRAM使用率(%),使用者")
    print("GPU[0],0.00,0.14,未使用")
    print("GPU[2],20.28,83.38,未使用")
    print("GPU[3],18.17,82.27,nycubme")
    print("全部平均,4.81,20.81,所有使用者")
    print()

def demonstrate_user_mapping():
    """展示使用者對應功能"""
    print("=== 使用者對應功能展示 ===\n")
    
    # 讀取 colab-gpu4 的資料作為範例
    test_file = "./data/colab-gpu4/2025-07-22/average_2025-07-22.csv"
    
    if Path(test_file).exists():
        df = pd.read_csv(test_file)
        
        print("colab-gpu4 節點的 GPU 使用者對應:")
        print("-" * 50)
        
        for _, row in df.iterrows():
            if row['GPU編號'] != '全部平均':
                gpu_id = row['GPU編號']
                username = row['使用者']
                gpu_usage = row['平均GPU使用率(%)']
                vram_usage = row['平均VRAM使用率(%)']
                
                status_emoji = "🟢" if username != "未使用" else "⚪"
                print(f"{status_emoji} {gpu_id}: {username}")
                print(f"   GPU使用率: {gpu_usage}%, VRAM使用率: {vram_usage}%")
                
        print()
        
        # 統計資訊
        used_count = len(df[(df['使用者'] != '未使用') & (df['GPU編號'] != '全部平均')])
        total_count = len(df[df['GPU編號'] != '全部平均'])
        
        print(f"📊 使用統計: {used_count}/{total_count} GPU 正在使用")
        
        if used_count > 0:
            users = df[(df['使用者'] != '未使用') & (df['GPU編號'] != '全部平均')]['使用者'].unique()
            print(f"👥 使用者: {', '.join(users)}")
    else:
        print(f"❌ 測試檔案不存在: {test_file}")

def main():
    """主程式"""
    print("GPU 日報表使用者欄位功能測試\n")
    print("=" * 60)
    
    # 測試使用者欄位功能
    test_user_column_in_reports()
    
    # 顯示格式對比
    show_csv_format_comparison()
    
    # 展示使用者對應功能
    demonstrate_user_mapping()
    
    print("\n" + "=" * 60)
    print("測試完成！")
    
    print("\n🎉 新功能摘要:")
    print("✅ CSV 檔案現在包含使用者欄位")
    print("✅ 摘要報告顯示詳細的使用者任務資訊")
    print("✅ GPU 編號採用新的 index 格式 (GPU[0] - GPU[7])")
    print("✅ 自動對應 GPU 硬體 ID 到使用者名稱")
    print("✅ 區分使用中和未使用的 GPU")

if __name__ == "__main__":
    main()
