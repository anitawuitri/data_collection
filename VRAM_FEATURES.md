# 🔥 VRAM 使用量圖表功能

## 功能概述

已成功新增 VRAM (顯示記憶體) 使用量監控與視覺化功能到現有的 AMD GPU 監控系統中。

## 🎯 新增功能

### 1. VRAM 監控模組 (`vram_monitor.py`)
- **節點 VRAM 對比圖** - 比較各節點的 VRAM 使用量趨勢
- **VRAM 使用率熱力圖** - 以熱力圖顯示所有 GPU 的 VRAM 使用分佈
- **VRAM 時間序列圖** - 顯示特定 GPU 的 VRAM 使用量變化曲線
- **自動數據收集** - 支援從 Netdata API 自動收集 VRAM 數據

### 2. 整合到快速繪圖工具 (`quick_gpu_trend_plots.py`)
- `quick_vram_nodes_comparison()` - 快速生成節點 VRAM 對比圖
- `quick_vram_heatmap()` - 快速生成 VRAM 熱力圖
- `quick_vram_timeline()` - 快速生成 VRAM 時間序列圖
- `generate_all_vram_plots()` - 一鍵生成所有 VRAM 圖表

### 3. 主執行腳本整合 (`run_gpu_visualization.sh`)
- `vram-nodes [開始日期] [結束日期] [GPU_ID]` - 生成各節點 VRAM 對比圖
- `vram-heatmap [開始日期] [結束日期]` - 生成 VRAM 使用率熱力圖
- `vram-timeline [節點] [GPU_ID] [日期]` - 生成 VRAM 時間序列圖
- `vram-all [開始日期] [結束日期]` - 生成所有 VRAM 圖表

## 🚀 使用範例

### 命令列使用
```bash
# 生成各節點 VRAM 對比圖
./run_gpu_visualization.sh vram-nodes 2025-05-23 2025-05-26

# 生成 VRAM 熱力圖
./run_gpu_visualization.sh vram-heatmap 2025-05-23 2025-05-26

# 生成特定 GPU 的 VRAM 時間序列圖
./run_gpu_visualization.sh vram-timeline colab-gpu1 1 2025-05-23

# 生成所有 VRAM 圖表
./run_gpu_visualization.sh vram-all 2025-05-23 2025-05-26
```

### Python API 使用
```python
from quick_gpu_trend_plots import (
    quick_vram_nodes_comparison,
    quick_vram_heatmap,
    quick_vram_timeline,
    generate_all_vram_plots
)

# 生成各節點 VRAM 對比圖
quick_vram_nodes_comparison('2025-05-23', '2025-05-26')

# 生成所有 VRAM 圖表
generate_all_vram_plots('2025-05-23', '2025-05-26')
```

## 📂 輸出檔案

VRAM 圖表會保存在 `plots/` 目錄下，檔名格式如下：
- `nodes_vram_comparison_all_gpus_[日期範圍].png` - 所有 GPU 的節點對比圖
- `nodes_vram_comparison_gpu[ID]_[日期範圍].png` - 特定 GPU 的節點對比圖
- `vram_heatmap_[日期範圍].png` - VRAM 使用率熱力圖
- `[節點]_gpu[ID]_vram_[日期].png` - 單一 GPU 的 VRAM 時間序列圖

## ✅ 測試結果

所有 VRAM 功能已經測試並驗證：
- ✅ VRAM 監控模組正常導入
- ✅ 節點對比圖正常生成
- ✅ 熱力圖正常生成  
- ✅ 時間序列圖功能正常
- ✅ 主執行腳本整合完成
- ✅ 文件說明已更新

## 📝 更新的檔案

1. **新增檔案:**
   - `visualization/vram_monitor.py` - VRAM 監控核心模組

2. **更新檔案:**
   - `run_gpu_visualization.sh` - 加入 VRAM 命令選項
   - `visualization/quick_gpu_trend_plots.py` - 加入 VRAM 快速繪圖函數
   - `README.md` - 加入 VRAM 功能說明
   - `visualization/README.md` - 加入 VRAM API 說明
   - `requirements.txt` - 加入 requests 依賴

## 🔮 未來可擴展功能

- **即時 VRAM 監控** - 建立即時數據收集定時任務
- **VRAM 使用率警報** - 當 VRAM 使用量過高時發送通知
- **VRAM 預測分析** - 基於歷史數據預測 VRAM 使用趨勢
- **多維度分析** - 結合 GPU 使用率和 VRAM 使用量的聯合分析

---

**功能完成時間:** 2025-06-10  
**版本:** v1.0  
**狀態:** ✅ 完成並測試通過
