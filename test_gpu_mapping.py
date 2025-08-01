#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 GPU 硬體對應功能

此腳本用於測試 daily_gpu_log.py 中的 GPU 硬體對應表是否正確載入
"""

import sys
from pathlib import Path

# 將 python 目錄加入路徑
python_dir = Path(__file__).parent / "python"
sys.path.insert(0, str(python_dir))

from daily_gpu_log import GPUDataCollector

def test_gpu_mapping():
    """測試 GPU 對應表功能"""
    print("=== GPU 硬體對應表測試 ===\n")
    
    # 初始化收集器
    collector = GPUDataCollector()
    
    print("1. Card ID 到 GPU Index 的對應:")
    for card_id, gpu_index in collector.gpu_card_to_index.items():
        print(f"   Card {card_id} -> GPU[{gpu_index}]")
    
    print("\n2. GPU Index 到 Card ID 的對應:")
    for gpu_index, card_id in collector.gpu_index_to_card.items():
        print(f"   GPU[{gpu_index}] -> Card {card_id}")
    
    print(f"\n3. 用於 API 查詢的 Card IDs: {collector.gpu_card_ids}")
    print(f"4. 用於檔案命名的 GPU Indices: {collector.gpu_indices}")
    
    print("\n5. 驗證對應關係的完整性:")
    
    # 檢查所有 card ID 都有對應的 index
    all_card_ids_mapped = all(card_id in collector.gpu_card_to_index for card_id in collector.gpu_card_ids)
    print(f"   所有 Card IDs 都有對應的 Index: {all_card_ids_mapped}")
    
    # 檢查所有 index 都有對應的 card ID
    all_indices_mapped = all(gpu_index in collector.gpu_index_to_card for gpu_index in collector.gpu_indices)
    print(f"   所有 Indices 都有對應的 Card ID: {all_indices_mapped}")
    
    # 檢查雙向對應是否一致
    bidirectional_consistency = all(
        collector.gpu_index_to_card[collector.gpu_card_to_index[card_id]] == card_id
        for card_id in collector.gpu_card_ids
    )
    print(f"   雙向對應一致性: {bidirectional_consistency}")
    
    if all_card_ids_mapped and all_indices_mapped and bidirectional_consistency:
        print("\n✅ GPU 硬體對應表測試通過！")
        return True
    else:
        print("\n❌ GPU 硬體對應表測試失敗！")
        return False

def test_shell_script_mapping():
    """測試 Shell 腳本的對應表"""
    print("\n=== Shell 腳本對應表驗證 ===")
    
    # 讀取 gpu_hardware_mapping.txt
    mapping_file = Path(__file__).parent / "gpu_hardware_mapping.txt"
    if not mapping_file.exists():
        print("❌ 找不到 gpu_hardware_mapping.txt 檔案")
        return False
    
    print("gpu_hardware_mapping.txt 內容:")
    with open(mapping_file, 'r') as f:
        content = f.read()
        print(content)
    
    # 解析對應關係
    expected_mapping = {}
    for line in content.strip().split('\n'):
        if '->' in line:
            parts = line.split('->')
            if len(parts) == 2:
                card_part = parts[0].strip()
                gpu_part = parts[1].strip()
                
                # 提取 card 數字
                card_num = int(card_part.replace('card', ''))
                
                # 提取 GPU index
                gpu_index = int(gpu_part.replace('GPU[', '').replace(']', ''))
                
                expected_mapping[card_num] = gpu_index
    
    print(f"\n從檔案解析的對應關係: {expected_mapping}")
    
    # 比較與 Python 版本的對應關係
    collector = GPUDataCollector()
    python_mapping = collector.gpu_card_to_index
    
    print(f"Python 版本的對應關係: {python_mapping}")
    
    mapping_matches = expected_mapping == python_mapping
    print(f"\n對應關係一致性: {mapping_matches}")
    
    if mapping_matches:
        print("✅ Shell 與 Python 版本的對應表一致！")
        return True
    else:
        print("❌ Shell 與 Python 版本的對應表不一致！")
        return False

if __name__ == "__main__":
    print("開始測試 GPU 硬體對應功能...\n")
    
    python_test = test_gpu_mapping()
    shell_test = test_shell_script_mapping()
    
    print("\n" + "="*50)
    print("測試結果總結:")
    print(f"Python 版本對應表: {'✅ 通過' if python_test else '❌ 失敗'}")
    print(f"Shell 版本對應表: {'✅ 通過' if shell_test else '❌ 失敗'}")
    
    if python_test and shell_test:
        print("\n🎉 所有測試通過！GPU 硬體對應功能已成功整合。")
        sys.exit(0)
    else:
        print("\n⚠️  某些測試失敗，請檢查對應表設定。")
        sys.exit(1)
