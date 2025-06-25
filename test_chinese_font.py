#!/usr/bin/env python3
import sys
sys.path.append('/home/amditri/data_collection')

from visualization.font_config import setup_chinese_font
import matplotlib.pyplot as plt
import numpy as np

print("=== 字體測試 ===")

# 設置字體
font = setup_chinese_font()
print(f"使用字體: {font}")

# 創建測試圖表
fig, ax = plt.subplots(figsize=(10, 6))

# 測試數據
nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
usage = [78.5, 65.2, 89.1, 45.7]

# 創建長條圖
bars = ax.bar(nodes, usage, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])

# 設置中文標籤和標題
ax.set_xlabel('GPU 節點')
ax.set_ylabel('使用率 (%)')
ax.set_title('GPU 使用率測試圖表 - 中文字體顯示測試')

# 添加數值標籤
for i, bar in enumerate(bars):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{usage[i]:.1f}%', ha='center', va='bottom')

# 顯示網格
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 100)

# 保存圖表
plt.tight_layout()
plt.savefig('/home/amditri/data_collection/plots/chinese_font_test.png', dpi=300, bbox_inches='tight')
plt.close()

print("測試圖表已保存至 plots/chinese_font_test.png")
print("字體測試完成！")
