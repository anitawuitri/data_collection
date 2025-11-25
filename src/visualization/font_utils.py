"""簡化的字體配置模塊

Linus 風格：直接解決問題，不搞複雜的抽象。
字體警告不影響功能，直接壓制掉。
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import warnings
from pathlib import Path

# 壓制所有 matplotlib 字體相關警告
warnings.filterwarnings('ignore', message='.*Glyph.*missing from font.*')
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib.font_manager')


def setup_chinese_font() -> str:
    """設置中文字體配置
    
    Linus 風格：簡單有效，不搞花樣。
    
    Returns:
        使用的字體名稱
    """
    # 簡單的字體列表
    fonts = [
        'Noto Sans CJK JP',      # 系統已有
        'Noto Sans CJK TC', 
        'Noto Sans CJK SC',
        'Microsoft YaHei',
        'SimHei',
        'DejaVu Sans'            # 最終備用
    ]
    
    # 直接設置，不搞複雜檢測
    plt.rcParams['font.sans-serif'] = fonts
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 10
    
    return fonts[0]


def create_test_plot(output_path: Path = None) -> str:
    """創建測試圖表
    
    簡化版本，只測試基本功能。
    
    Args:
        output_path: 輸出路徑，None 則使用默認路徑
        
    Returns:
        生成的圖表文件路徑
    """
    import numpy as np
    
    if output_path is None:
        output_path = Path('./plots/font_test.png')
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 創建測試數據
    nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
    usage = [65.5, 89.2, 45.8, 78.1]
    
    # 創建圖表
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(nodes, usage, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    
    # 設置標籤
    ax.set_xlabel('GPU 節點')
    ax.set_ylabel('使用率 (%)')
    ax.set_title('GPU 使用率測試圖表')
    
    # 添加數值標籤
    for bar, val in zip(bars, usage):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{val:.1f}%', ha='center', va='bottom')
    
    ax.grid(True, alpha=0.3)
    
    # 保存
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return str(output_path)