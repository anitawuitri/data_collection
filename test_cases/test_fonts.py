#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字體測試和驗證腳本

測試中文字體顯示是否正常工作
"""

import matplotlib.pyplot as plt
import numpy as np
from font_config import setup_chinese_font, test_chinese_display

def run_font_tests():
    """執行字體測試"""
    print("=== 字體測試開始 ===")
    
    # 設定字體
    font_name = setup_chinese_font()
    print(f"已設定字體: {font_name}")
    
    # 執行測試
    test_path = test_chinese_display()
    print(f"測試圖表位置: {test_path}")
    
    # 額外測試：創建簡單的中文標籤圖表
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 測試數據
    categories = ['GPU 使用率', '記憶體使用率', '溫度', '功耗']
    values = [75.5, 62.3, 58.9, 85.1]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    bars = ax.bar(categories, values, color=colors)
    
    # 添加數值標籤
    for i, (bar, value) in enumerate(zip(bars, values)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value}%', ha='center', va='bottom', fontsize=12)
    
    ax.set_title('AMD GPU 監控數據範例', fontsize=16, fontweight='bold')
    ax.set_ylabel('百分比 (%)', fontsize=12)
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3, axis='y')
    
    # 保存測試圖表
    test_path2 = "../plots/font_test_advanced.png"
    plt.tight_layout()
    plt.savefig(test_path2, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"進階測試圖表位置: {test_path2}")
    print("=== 字體測試完成 ===")
    
    return test_path, test_path2

if __name__ == "__main__":
    run_font_tests()
