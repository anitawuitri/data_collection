#!/usr/bin/env python3
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

print("檢查 matplotlib 可用的字體...")

# 獲取所有可用字體
available_fonts = [f.name for f in fm.fontManager.ttflist]

# 檢查 Noto CJK 字體
noto_cjk_fonts = [font for font in available_fonts if 'Noto Sans CJK' in font]

print(f"找到 {len(noto_cjk_fonts)} 個 Noto Sans CJK 字體：")
for font in sorted(set(noto_cjk_fonts)):
    print(f"  - {font}")

# 測試字體設定
if noto_cjk_fonts:
    test_font = noto_cjk_fonts[0]
    print(f"\n測試字體: {test_font}")
    plt.rcParams['font.sans-serif'] = [test_font]
    
    # 創建簡單測試圖
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.text(0.5, 0.5, '測試中文字體顯示', fontsize=16, ha='center', va='center')
    ax.set_title('字體測試圖表')
    plt.savefig('/home/amditri/data_collection/plots/font_debug_test.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("測試圖表已保存至 plots/font_debug_test.png")
else:
    print("未找到 Noto Sans CJK 字體")

print(f"\n所有可用字體數量: {len(set(available_fonts))}")
