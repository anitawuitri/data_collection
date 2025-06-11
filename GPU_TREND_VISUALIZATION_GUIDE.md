# GPU 使用率趨勢視覺化指南

本指南說明如何使用新建立的 GPU 使用率趨勢視覺化工具來分析和繪製 GPU 使用率趨勢圖。

## 檔案結構

```
data_collection/
├── scripts/
│   ├── advanced_gpu_trend_analyzer.py    # 進階分析工具
│   ├── quick_gpu_trend_plots.py          # 快速繪圖工具
│   └── gpu_trend_visualizer.py           # 原有的視覺化工具
├── examples/
│   └── gpu_trend_examples.py             # 使用範例
├── run_gpu_visualization.sh              # 執行腳本
├── data/                                  # GPU 數據目錄
├── plots/                                 # 輸出圖表目錄
└── GPU_TREND_VISUALIZATION_GUIDE.md      # 本指南
```

## 快速開始

### 1. 自動模式（推薦）

最簡單的使用方式，自動偵測可用數據並生成所有常用圖表：

```bash
# 執行自動模式
./run_gpu_visualization.sh auto

# 或直接執行 Python 腳本
python3 scripts/quick_gpu_trend_plots.py
```

### 2. 快速生成指定日期範圍的圖表

```bash
# 生成 2025-05-23 至 2025-05-26 期間的所有常用圖表
./run_gpu_visualization.sh quick 2025-05-23 2025-05-26
```

### 3. 生成特定類型的圖表

```bash
# 節點對比趨勢圖
./run_gpu_visualization.sh nodes 2025-05-23 2025-05-26

# 單一節點所有 GPU 趨勢圖
./run_gpu_visualization.sh node colab-gpu1 2025-05-23 2025-05-26

# 特定 GPU 跨節點對比圖
./run_gpu_visualization.sh gpu 1 2025-05-23 2025-05-26

# 熱力圖
./run_gpu_visualization.sh heatmap 2025-05-23 2025-05-26
```

## 可用的圖表類型

### 1. 節點對比趨勢圖 (Nodes Comparison)
- **用途**: 比較各節點的平均 GPU 使用率趨勢
- **適用情境**: 了解各節點的整體負載情況
- **生成命令**: `./run_gpu_visualization.sh nodes [開始日期] [結束日期]`

### 2. 單一節點所有 GPU 趨勢圖 (Single Node All GPUs)
- **用途**: 查看特定節點內所有 GPU 的使用率趨勢
- **適用情境**: 分析單一節點的 GPU 負載分佈
- **生成命令**: `./run_gpu_visualization.sh node [節點名稱] [開始日期] [結束日期]`

### 3. 特定 GPU 跨節點對比圖 (Specific GPU Across Nodes)
- **用途**: 比較相同 GPU ID 在不同節點上的使用率
- **適用情境**: 分析特定 GPU 的跨節點表現
- **生成命令**: `./run_gpu_visualization.sh gpu [GPU_ID] [開始日期] [結束日期]`

### 4. 熱力圖 (Heatmap)
- **用途**: 以熱力圖形式顯示所有 GPU 的使用率分佈
- **適用情境**: 快速識別高使用率的 GPU 和時間點
- **生成命令**: `./run_gpu_visualization.sh heatmap [開始日期] [結束日期]`

### 5. 詳細時間序列圖 (Detailed Timeline)
- **用途**: 顯示特定 GPU 在特定日期的詳細使用率變化
- **適用情境**: 深入分析特定 GPU 在特定日期的使用模式
- **生成命令**: `./run_gpu_visualization.sh timeline [節點] [GPU_ID] [日期]`

## Python API 使用

### 使用快速繪圖工具

```python
from scripts.quick_gpu_trend_plots import (
    quick_nodes_trend,
    quick_single_node_gpus,
    quick_gpu_across_nodes,
    generate_all_quick_plots
)

# 生成節點對比圖
quick_nodes_trend('2025-05-23', '2025-05-26')

# 生成單一節點所有 GPU 圖
quick_single_node_gpus('colab-gpu1', '2025-05-23', '2025-05-26')

# 生成特定 GPU 跨節點圖
quick_gpu_across_nodes(1, '2025-05-23', '2025-05-26')

# 一次生成所有圖表
generate_all_quick_plots('2025-05-23', '2025-05-26')
```

### 使用進階分析工具

```python
from scripts.advanced_gpu_trend_analyzer import GPUUsageTrendAnalyzer

# 初始化分析器
analyzer = GPUUsageTrendAnalyzer()

# 節點對比趨勢
analyzer.plot_nodes_comparison_trend('2025-05-23', '2025-05-26')

# 單一節點所有 GPU
analyzer.plot_single_node_all_gpus('colab-gpu1', '2025-05-23', '2025-05-26')

# 特定 GPU 跨節點對比
analyzer.plot_specific_gpu_across_nodes(1, '2025-05-23', '2025-05-26')

# 熱力圖
analyzer.plot_heatmap('2025-05-23', '2025-05-26')

# 詳細時間序列
analyzer.plot_detailed_timeline('colab-gpu1', 1, '2025-05-23')

# 生成摘要報告
analyzer.generate_summary_report('2025-05-23', '2025-05-26')
```

## 參數說明

### 日期格式
- **格式**: YYYY-MM-DD
- **範例**: 2025-05-23

### 節點名稱
- colab-gpu1
- colab-gpu2
- colab-gpu3
- colab-gpu4

### GPU ID
- 1, 9, 17, 25, 33, 41, 49, 57

## 輸出檔案

所有生成的圖表會保存在 `./plots/` 目錄中，檔案命名規則如下：

- 節點對比: `nodes_comparison_[開始日期]_to_[結束日期].png`
- 單一節點: `[節點名稱]_all_gpus_[開始日期]_to_[結束日期].png`
- 特定 GPU: `gpu[GPU_ID]_across_nodes_[開始日期]_to_[結束日期].png`
- 熱力圖: `heatmap_[開始日期]_to_[結束日期].png`
- 時間序列: `[節點]_gpu[GPU_ID]_timeline_[日期].png`

## 故障排除

### 1. Python 套件問題
如果出現缺少套件的錯誤，請執行：
```bash
pip3 install pandas matplotlib numpy seaborn
```

### 2. 數據檔案問題
確保 `./data/` 目錄包含正確的數據結構：
```
data/
├── colab-gpu1/
│   ├── 2025-05-23/
│   │   ├── average_2025-05-23.csv
│   │   ├── gpu1_2025-05-23.csv
│   │   └── ...
│   └── ...
└── ...
```

### 3. 權限問題
確保腳本有執行權限：
```bash
chmod +x run_gpu_visualization.sh
```

### 4. 路徑問題
請在專案根目錄執行腳本：
```bash
cd /path/to/data_collection
./run_gpu_visualization.sh auto
```

## 進階使用

### 自訂分析
您可以直接修改 Python 腳本來進行更複雜的分析，例如：
- 調整圖表樣式和顏色
- 添加更多統計指標
- 修改時間範圍和採樣頻率
- 整合其他數據源

### 批次處理
使用 bash 腳本進行批次處理：
```bash
# 為每個月生成報告
for month in 01 02 03; do
    ./run_gpu_visualization.sh quick 2025-${month}-01 2025-${month}-31
done
```

## 範例

查看 `examples/gpu_trend_examples.py` 檔案了解更多使用範例和進階功能。

執行範例：
```bash
./run_gpu_visualization.sh examples
```

這將展示所有可用功能的使用方法。
