#!/usr/bin/env python3
"""
驗證 VRAM 熱力圖中的使用者資訊讀取
"""

import os
import sys
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), 'visualization'))

def verify_user_info_reading():
    """驗證使用者資訊讀取邏輯"""
    
    print("=== 驗證使用者資訊讀取 ===")
    
    # 檢查包含使用者資訊的檔案
    test_file = "data/colab-gpu4/2025-07-25/average_2025-07-25.csv"
    
    if os.path.exists(test_file):
        print(f"檢查檔案: {test_file}")
        df = pd.read_csv(test_file)
        print("檔案內容:")
        print(df.head())
        print()
        
        # 測試 GPU 映射邏輯
        gpu_ids = [1, 9, 17, 25, 33, 41, 49, 57]
        
        print("GPU ID 到 GPU編號映射:")
        for gpu_id in gpu_ids:
            gpu_index = gpu_id // 8
            gpu_label = f'GPU[{gpu_index}]'
            
            # 查找對應的使用者
            gpu_row = df[df['GPU編號'] == gpu_label]
            if not gpu_row.empty:
                user = gpu_row['使用者'].iloc[0]
                print(f"  GPU ID {gpu_id} -> {gpu_label} -> 使用者: {user}")
            else:
                print(f"  GPU ID {gpu_id} -> {gpu_label} -> 未找到資料")
        
    else:
        print(f"檔案不存在: {test_file}")

if __name__ == "__main__":
    verify_user_info_reading()
