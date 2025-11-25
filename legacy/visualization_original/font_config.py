#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字體配置模組

此模組提供中文字體的配置功能，確保圖表中的中文文字能正確顯示。
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import sys
from pathlib import Path

def setup_chinese_font():
    """
    設定中文字體配置，確保圖表中的中文文字能正確顯示
    """
    # 嘗試不同的中文字體列表（按優先順序）
    chinese_fonts = [
        'Noto Sans CJK TC',      # Ubuntu/Debian 繁體中文（優先）
        'Noto Sans CJK SC',      # Ubuntu/Debian 簡體中文
        'Noto Sans CJK JP',      # Ubuntu/Debian 日文
        'Noto Sans CJK KR',      # Ubuntu/Debian 韓文
        'Noto Sans',             # 基本 Noto Sans
        'Source Han Sans TC',    # 思源黑體繁體
        'Source Han Sans SC',    # 思源黑體簡體
        'Microsoft YaHei',       # Windows
        'PingFang SC',           # macOS
        'SimHei',                # Windows 預設
        'WenQuanYi Micro Hei',   # Linux 常見中文字體
        'WenQuanYi Zen Hei',     # Linux 常見中文字體
        'DejaVu Sans',           # 最後備用
        'Arial Unicode MS',      # 最後備用
    ]
    
    # 檢查可用的字體
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 尋找第一個可用的中文字體
    selected_font = None
    for font in chinese_fonts:
        if font in available_fonts:
            selected_font = font
            print(f"[字體配置] 使用字體: {font}")
            break
    
    if not selected_font:
        # 如果沒有找到理想的字體，使用系統預設
        print("[字體配置] 警告: 未找到理想的中文字體，使用系統預設")
        selected_font = 'DejaVu Sans'
    
    # 設定 matplotlib 字體配置
    plt.rcParams['font.sans-serif'] = [selected_font] + chinese_fonts
    plt.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
    plt.rcParams['font.size'] = 10
    
    # 確保字體配置生效
    try:
        # 重新設定字體配置
        plt.rcParams['font.sans-serif'] = [selected_font] + chinese_fonts
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['font.size'] = 10
    except Exception as e:
        print(f"[字體配置] 警告: 字體配置過程中出現問題: {e}")
        pass
    
    return selected_font

def get_font_family():
    """
    獲取當前配置的字體系列
    
    Returns:
        str: 字體系列名稱
    """
    return plt.rcParams['font.sans-serif'][0]

def test_chinese_display():
    """
    測試中文字體顯示
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    # 設定字體
    font = setup_chinese_font()
    
    # 創建測試圖表
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    
    # 測試數據
    x = np.arange(4)
    y = [65.5, 89.2, 45.8, 78.1]
    labels = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
    
    # 創建長條圖
    bars = ax.bar(x, y, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    
    # 設定標籤和標題
    ax.set_xlabel('GPU 節點')
    ax.set_ylabel('使用率 (%)')
    ax.set_title('GPU 使用率測試圖表 (字體測試)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    
    # 添加數值標籤
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{y[i]:.1f}%', ha='center', va='bottom')
    
    # 顯示網格
    ax.grid(True, alpha=0.3)
    
    # 保存測試圖表
    output_path = Path(__file__).parent.parent / 'plots' / 'font_test.png'
    output_path.parent.mkdir(exist_ok=True)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"[字體測試] 測試圖表已保存至: {output_path}")
    print(f"[字體測試] 使用字體: {font}")
    
    return str(output_path)

if __name__ == "__main__":
    print("=== 中文字體配置測試 ===")
    setup_chinese_font()
    test_chinese_display()
    print("測試完成！")
