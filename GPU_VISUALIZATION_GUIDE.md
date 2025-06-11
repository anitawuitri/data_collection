# GPU 使用率視覺化工具使用指南

## 安裝說明

### 1. 安裝 Python 依賴套件

在專案根目錄執行：

```bash
pip install -r requirements.txt
```

或者手動安裝所需套件：

```bash
pip install pandas matplotlib seaborn numpy
```

### 2. 確認數據結構

確保您的數據目錄結構如下：

```
data/
├── colab-gpu1/
│   ├── 2025-05-23/
│   │   ├── average_2025-05-23.csv
│   │   ├── gpu1_2025-05-23.csv
│   │   ├── gpu9_2025-05-23.csv
│   │   └── ...
│   └── 2025-05-24/
│       └── ...
├── colab-gpu2/
├── colab-gpu3/
└── colab-gpu4/
```

## 使用方法

### 方法一：使用完整功能的視覺化工具

```bash
# 生成所有類型的圖表
python scripts/gpu_trend_visualizer.py --start-date 2025-05-23 --end-date 2025-05-26 --plot-type all

# 只生成節點對比圖
python scripts/gpu_trend_visualizer.py --start-date 2025-05-23 --end-date 2025-05-26 --plot-type nodes

# 生成特定節點的單個 GPU 趨勢圖
python scripts/gpu_trend_visualizer.py --start-date 2025-05-23 --end-date 2025-05-26 --plot-type single --node colab-gpu1 --gpu-id 1

# 生成熱力圖
python scripts/gpu_trend_visualizer.py --start-date 2025-05-23 --end-date 2025-05-26 --plot-type heatmap

# 生成綜合儀表板
python scripts/gpu_trend_visualizer.py --start-date 2025-05-23 --end-date 2025-05-26 --plot-type dashboard
```

### 方法二：使用簡化版快速生成工具

```bash
# 直接執行快速生成腳本
python scripts/quick_gpu_plots.py
```

### 方法三：使用範例腳本

```bash
# 生成範例圖表
python examples/gpu_visualization_examples.py --generate

# 查看使用範例
python examples/gpu_visualization_examples.py --examples
```

## 圖表類型說明

### 1. 節點對比圖 (nodes)
- 顯示所有節點在指定時間範圍內的平均 GPU 使用率趨勢
- 適合比較不同節點的整體性能

### 2. 單個 GPU 趨勢圖 (single)
- 顯示特定節點特定 GPU 的詳細時間序列數據
- 適合深入分析單個 GPU 的使用模式

### 3. 多 GPU 對比圖 (multi)
- 顯示單個節點內所有 GPU 在某一天的使用率對比
- 適合分析節點內 GPU 負載分佈

### 4. 熱力圖 (heatmap)
- 以熱力圖形式顯示所有節點所有 GPU 的使用率
- 適合快速識別高使用率的 GPU 和時間段

### 5. 綜合儀表板 (dashboard)
- 包含多種視圖的綜合分析頁面
- 提供整體概覽和統計資訊

## 參數說明

### 必要參數
- `--start-date`: 開始日期 (格式: YYYY-MM-DD)
- `--end-date`: 結束日期 (格式: YYYY-MM-DD)

### 可選參數
- `--data-dir`: 數據目錄路徑 (預設: ./data)
- `--output-dir`: 輸出目錄路徑 (預設: ./plots)
- `--node`: 指定節點名稱 (例如: colab-gpu1)
- `--gpu-id`: 指定 GPU ID (例如: 1, 9, 17, 25, 33, 41, 49, 57)
- `--plot-type`: 圖表類型 (single, multi, nodes, heatmap, dashboard, all)

## 輸出檔案

所有生成的圖表都會保存為 PNG 格式，檔名格式如下：

- 節點對比圖: `nodes_comparison_YYYY-MM-DD_to_YYYY-MM-DD.png`
- 單個 GPU 趨勢圖: `[節點名]_gpu[ID]_YYYY-MM-DD_to_YYYY-MM-DD.png`
- 多 GPU 對比圖: `[節點名]_multi_gpu_YYYY-MM-DD.png`
- 熱力圖: `heatmap_YYYY-MM-DD_to_YYYY-MM-DD.png`
- 綜合儀表板: `dashboard_YYYY-MM-DD_to_YYYY-MM-DD.png`

## 範例命令

### 分析最近一週的 GPU 使用率
```bash
python scripts/gpu_trend_visualizer.py --start-date 2025-05-20 --end-date 2025-05-27 --plot-type all --output-dir ./weekly_analysis
```

### 分析特定節點的詳細使用情況
```bash
# 生成節點整體趨勢
python scripts/gpu_trend_visualizer.py --start-date 2025-05-23 --end-date 2025-05-26 --plot-type nodes --node colab-gpu1

# 生成該節點各 GPU 對比圖
python scripts/gpu_trend_visualizer.py --start-date 2025-05-26 --end-date 2025-05-26 --plot-type multi --node colab-gpu1

# 生成該節點特定 GPU 的詳細趨勢
python scripts/gpu_trend_visualizer.py --start-date 2025-05-23 --end-date 2025-05-26 --plot-type single --node colab-gpu1 --gpu-id 1
```

### 快速生成所有常用圖表
```bash
python scripts/quick_gpu_plots.py
```

## 故障排除

### 1. 模組導入錯誤
```
ImportError: No module named 'pandas'
```
解決方法：執行 `pip install -r requirements.txt`

### 2. 找不到數據
```
未找到數據，請檢查數據目錄
```
解決方法：
- 確認數據目錄路徑正確
- 確認日期範圍內有對應的數據檔案
- 檢查 CSV 檔案格式是否正確

### 3. 中文字體顯示問題
如果圖表中中文無法正常顯示，可以：
- 在 Linux 系統安裝中文字體
- 修改 `matplotlib` 字體設定

### 4. 記憶體不足
如果處理大量數據時出現記憶體不足：
- 縮小日期範圍
- 分批處理數據

## 自定義擴展

您可以透過修改 `gpu_trend_visualizer.py` 來新增自定義的視覺化功能：

1. 在 `GPUTrendVisualizer` 類別中新增方法
2. 修改顏色配置、圖表樣式等
3. 新增其他數據處理邏輯

## 整合到現有工作流程

可以將視覺化工具整合到現有的 GPU 監控工作流程中：

1. 在 `daily_gpu_log.sh` 腳本末尾新增圖表生成命令
2. 設定定時任務自動生成每日報告
3. 結合 Web 伺服器展示圖表結果
