# GPU 使用率與 VRAM 視覺化工具

這個資料夾包含所有用於 GPU 使用率趨勢分析、VRAM 使用量監控和視覺化的 Python 工具。

## ✨ 新增功能

- **🔥 VRAM 使用量監控** - 全新的 VRAM 使用量收集、分析與視覺化功能
- **自動中文字體配置** - 自動偵測並使用最佳的中文字體顯示圖表
- **跨平台字體支援** - 支援 Linux (Noto Sans CJK)、Windows (Microsoft YaHei)、macOS (PingFang SC)
- **字體測試工具** - 提供字體顯示測試和驗證功能

## 檔案說明

### 主要工具

- `advanced_gpu_trend_analyzer.py` - 進階 GPU 趨勢分析器（完整功能）
- `quick_gpu_trend_plots.py` - 快速 GPU 趨勢繪圖工具（常用功能）
- `vram_monitor.py` - **🔥 VRAM 使用量監控與視覺化工具**
- `gpu_trend_visualizer.py` - 原有的 GPU 趨勢視覺化工具
- `gpu_trend_examples.py` - 使用範例和教學

### 輔助模組

- `font_config.py` - 中文字體配置模組
- `test_fonts.py` - 字體測試和驗證工具
- `requirements.txt` - Python 套件依賴
- `GPU_TREND_VISUALIZATION_GUIDE.md` - 詳細使用指南

## 字體問題解決

如果圖表中的中文文字顯示有問題（顯示為方塊或亂碼），請執行：

```bash
# 測試字體配置
python3 test_fonts.py

# 手動配置字體
python3 font_config.py
```

系統會自動選擇最適合的中文字體：

- **Ubuntu/Debian**: Noto Sans CJK TC/SC/JP
- **Windows**: Microsoft YaHei
- **macOS**: PingFang SC
- **備用字體**: DejaVu Sans, Arial Unicode MS


## 快速開始

### 1. 安裝依賴套件

```bash
cd visualization
pip3 install -r requirements.txt
```

### 2. 執行自動視覺化

```bash
# 自動偵測數據並生成所有圖表
python3 quick_gpu_trend_plots.py

# 或指定日期範圍
python3 quick_gpu_trend_plots.py 2025-05-23 2025-05-26
```

### 3. 執行範例

```bash
python3 gpu_trend_examples.py
```

### 4. 🔥 VRAM 監控功能

```bash
# 生成 VRAM 節點對比圖
python3 -c "from quick_gpu_trend_plots import quick_vram_nodes_comparison; quick_vram_nodes_comparison('2025-05-23', '2025-05-26')"

# 生成 VRAM 熱力圖
python3 -c "from quick_gpu_trend_plots import quick_vram_heatmap; quick_vram_heatmap('2025-05-23', '2025-05-26')"

# 生成特定 GPU 的 VRAM 時間序列圖
python3 -c "from quick_gpu_trend_plots import quick_vram_timeline; quick_vram_timeline('colab-gpu1', 1, '2025-05-23')"

# 生成所有 VRAM 圖表
python3 -c "from quick_gpu_trend_plots import generate_all_vram_plots; generate_all_vram_plots('2025-05-23', '2025-05-26')"
```

## 進階使用

### 使用進階分析器

```bash
python3 advanced_gpu_trend_analyzer.py --start-date 2025-05-23 --end-date 2025-05-26 --mode all
```

### 命令列選項

```bash
# 節點對比圖
python3 advanced_gpu_trend_analyzer.py --start-date 2025-05-23 --end-date 2025-05-26 --mode nodes

# 熱力圖
python3 advanced_gpu_trend_analyzer.py --start-date 2025-05-23 --end-date 2025-05-26 --mode heatmap

# 特定節點的所有 GPU
python3 advanced_gpu_trend_analyzer.py --start-date 2025-05-23 --end-date 2025-05-26 --mode single-node --node colab-gpu1

# 特定 GPU 跨節點對比
python3 advanced_gpu_trend_analyzer.py --start-date 2025-05-23 --end-date 2025-05-26 --mode specific-gpu --gpu-id 1

# 詳細時間序列
python3 advanced_gpu_trend_analyzer.py --mode timeline --node colab-gpu1 --gpu-id 1 --date 2025-05-23
```

## Python API

### 快速繪圖 API

```python
from quick_gpu_trend_plots import (
    quick_nodes_trend,
    quick_single_node_gpus,
    quick_gpu_across_nodes,
    generate_all_quick_plots,
    # 🔥 VRAM 監控 API
    quick_vram_nodes_comparison,
    quick_vram_heatmap,
    quick_vram_timeline,
    generate_all_vram_plots
)

# 生成所有 GPU 使用率圖表
generate_all_quick_plots('2025-05-23', '2025-05-26')

# 🔥 生成所有 VRAM 監控圖表
generate_all_vram_plots('2025-05-23', '2025-05-26')
```

### 🔥 VRAM 監控 API

```python
from vram_monitor import VRAMMonitor

# 初始化 VRAM 監控器
monitor = VRAMMonitor()

# 生成各節點 VRAM 對比圖
monitor.plot_nodes_vram_comparison('2025-05-23', '2025-05-26')

# 生成 VRAM 熱力圖
monitor.plot_vram_heatmap('2025-05-23', '2025-05-26')

# 生成單一 GPU VRAM 時間序列圖
monitor.plot_single_gpu_vram_timeline('colab-gpu1', 1, '2025-05-23')

# 自動收集 VRAM 數據（需要網路連線到各節點）
monitor.collect_vram_data('2025-05-27')
```

### 進階分析 API

```python
from advanced_gpu_trend_analyzer import GPUUsageTrendAnalyzer

analyzer = GPUUsageTrendAnalyzer()
analyzer.plot_nodes_comparison_trend('2025-05-23', '2025-05-26')
analyzer.plot_heatmap('2025-05-23', '2025-05-26')
analyzer.generate_summary_report('2025-05-23', '2025-05-26')
```

## 輸出

所有生成的圖表會保存在 `../plots/` 目錄中。

## 數據結構

這些工具預期的數據結構：

```text
../data/
├── colab-gpu1/
│   ├── 2025-05-23/
│   │   ├── average_2025-05-23.csv
│   │   ├── gpu1_2025-05-23.csv
│   │   └── ...
│   └── ...
└── ...
```

## 故障排除

1. **套件問題**: 執行 `pip3 install -r requirements.txt`
2. **數據路徑**: 確保在正確的目錄執行（數據應在 `../data/`）
3. **權限問題**: 確保有寫入 `../plots/` 的權限

詳細說明請參考 `GPU_TREND_VISUALIZATION_GUIDE.md`。
