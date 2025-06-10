# GPU 使用率視覺化工具 - 快速使用指南

## 📁 檔案結構

已將所有 Python 視覺化相關檔案整理到 `visualization/` 資料夾：

```
data_collection/
├── visualization/              # 🆕 視覺化工具資料夾
│   ├── README.md              # 視覺化工具說明
│   ├── requirements.txt       # Python 套件依賴
│   ├── run_viz.sh            # 快速執行腳本
│   ├── advanced_gpu_trend_analyzer.py    # 進階分析工具
│   ├── quick_gpu_trend_plots.py          # 快速繪圖工具
│   ├── gpu_trend_visualizer.py           # 原有視覺化工具
│   ├── gpu_trend_examples.py             # 使用範例
│   └── GPU_TREND_VISUALIZATION_GUIDE.md  # 詳細指南
├── data/                      # GPU 數據目錄
├── plots/                     # 輸出圖表目錄
├── scripts/                   # 數據收集腳本
└── run_gpu_visualization.sh   # 主執行腳本
```

## 🚀 三種使用方式

### 方式 1: 主執行腳本（推薦）

```bash
# 自動模式 - 偵測可用數據並生成所有圖表
./run_gpu_visualization.sh auto

# 快速模式 - 指定日期範圍
./run_gpu_visualization.sh quick 2025-05-23 2025-05-26

# 節點對比圖
./run_gpu_visualization.sh nodes 2025-05-23 2025-05-26

# 單一節點所有 GPU
./run_gpu_visualization.sh node colab-gpu1 2025-05-23 2025-05-26

# 特定 GPU 跨節點對比
./run_gpu_visualization.sh gpu 1 2025-05-23 2025-05-26
```

### 方式 2: 在 visualization 資料夾內執行

```bash
cd visualization

# 自動模式
./run_viz.sh auto

# 快速模式
./run_viz.sh quick 2025-05-23 2025-05-26

# 執行範例
./run_viz.sh examples

# 進階分析
./run_viz.sh advanced 2025-05-23 2025-05-26
```

### 方式 3: 直接執行 Python 腳本

```bash
cd visualization

# 安裝套件
pip3 install -r requirements.txt

# 快速生成所有圖表
python3 quick_gpu_trend_plots.py

# 或指定日期範圍
python3 quick_gpu_trend_plots.py 2025-05-23 2025-05-26

# 進階分析
python3 advanced_gpu_trend_analyzer.py --start-date 2025-05-23 --end-date 2025-05-26 --mode all
```

## 📊 可生成的圖表類型

1. **節點對比趨勢圖** - 比較各節點平均 GPU 使用率
2. **單一節點所有 GPU** - 特定節點內所有 GPU 的使用率趨勢
3. **特定 GPU 跨節點** - 相同 GPU ID 在不同節點上的使用率對比
4. **熱力圖** - 所有 GPU 使用率的熱力圖顯示
5. **詳細時間序列** - 特定 GPU 在特定日期的詳細變化

## 🛠️ 故障排除

### Python 套件問題
```bash
cd visualization
pip3 install -r requirements.txt
```

### 權限問題
```bash
chmod +x run_gpu_visualization.sh
chmod +x visualization/run_viz.sh
```

### 路徑問題
確保在專案根目錄執行主腳本，或在 visualization 目錄執行 run_viz.sh

## 📈 輸出

所有圖表都會保存在 `plots/` 目錄中，命名格式：
- `nodes_comparison_2025-05-23_to_2025-05-26.png`
- `colab-gpu1_all_gpus_2025-05-23_to_2025-05-26.png`
- `gpu1_across_nodes_2025-05-23_to_2025-05-26.png`
- `heatmap_2025-05-23_to_2025-05-26.png`

## 📚 詳細文檔

- `visualization/README.md` - 視覺化工具詳細說明
- `visualization/GPU_TREND_VISUALIZATION_GUIDE.md` - 完整使用指南
- `visualization/gpu_trend_examples.py` - 程式範例

立即開始：`./run_gpu_visualization.sh auto` 🎉
