# AMD GPU 使用率監控與視覺化工具

[![License: WTFPL](https://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-2.png)](http://www.wtfpl.net/)

完整的 AMD GPU 使用率監控與視覺化解決方案，支援多節點環境的 GPU 監控、數據收集、分析和視覺化。

## ✨ 主要功能

### 🔍 數據收集與監控

- **多節點 GPU 監控** - 同時監控多個節點的 AMD GPU 使用率
- **自動化數據收集** - 支援定時任務，每日自動收集 GPU 使用率數據  
- **詳細統計分析** - 計算平均使用率、生成摘要報告
- **多種數據格式** - 支援 CSV、SVG 圖表和文字摘要

### 📊 視覺化與分析

- **多種圖表類型** - 節點對比、GPU趨勢、熱力圖、時間序列分析
- **中文字體支援** - 自動配置中文字體，完美顯示中文標籤
- **跨平台相容** - 支援 Linux、Windows、macOS
- **一鍵式操作** - 提供便捷的執行腳本

### 🛠️ 工具與腳本

- **時間轉換工具** - Unix 時間戳與日期時間互轉
- **日期區間分析** - 靈活的時間範圍分析功能
- **報告生成** - 自動生成各種格式的分析報告

## 🚀 快速開始

### 視覺化工具

```bash
# 自動偵測數據並生成所有圖表
./run_gpu_visualization.sh auto

# 快速生成指定日期範圍的圖表  
./run_gpu_visualization.sh quick 2025-05-23 2025-05-26

# 生成節點對比圖
./run_gpu_visualization.sh nodes 2025-05-23 2025-05-26

# 執行所有範例
./run_gpu_visualization.sh examples
```

### 數據收集

```bash
# 收集今天的 GPU 數據
./scripts/daily_gpu_log.sh

# 分析日期區間的使用率
./scripts/calculate_gpu_range.sh 2025-05-01 2025-05-15

# 分析節點使用率
./scripts/calculate_node_gpu_usage.sh 2025-05-01 2025-05-15
```

## 📁 專案結構

```text
data_collection/
├── README.md                           # 專案說明文件
├── VISUALIZATION_QUICK_START.md        # 視覺化快速指南
├── run_gpu_visualization.sh            # 主要視覺化執行腳本
├── requirements.txt                    # Python 依賴套件
├── .gitignore                          # Git 忽略規則
├── plots/                              # 生成的圖表輸出目錄
│   ├── *.png                          # 各種視覺化圖表
│   └── font_test*.png                 # 字體測試圖表
├── data/                               # GPU 監控數據目錄 (git 忽略)
│   ├── colab-gpu1/                    # 各節點數據
│   │   ├── 2025-05-23/               # 依日期存放
│   │   │   ├── average_*.csv         # 平均使用率
│   │   │   ├── gpu*_*.csv           # 各 GPU 數據
│   │   │   ├── gpu*_*.svg           # GPU 圖表
│   │   │   └── summary_*.txt        # 摘要報告
│   │   └── ...
│   ├── colab-gpu2/                    # 其他節點數據
│   ├── colab-gpu3/
│   ├── colab-gpu4/
│   └── reports/                       # 綜合分析報告
├── scripts/                           # 數據收集腳本
│   ├── daily_gpu_log.sh              # 主要數據收集腳本
│   ├── calculate_gpu_range.sh        # GPU 日期區間分析
│   ├── calculate_node_gpu_usage.sh   # 節點使用率分析
│   └── test/                         # 輔助工具
│       ├── time_convert.sh           # 時間轉換工具
│       ├── test.sh                   # 測試腳本
│       └── test.csv                  # 測試數據
└── visualization/                     # Python 視覺化工具集
    ├── README.md                     # 視覺化工具說明
    ├── GPU_TREND_VISUALIZATION_GUIDE.md # 詳細使用指南
    ├── requirements.txt              # 視覺化依賴套件
    ├── run_viz.sh                    # 視覺化執行腳本
    ├── font_config.py                # 中文字體配置模組
    ├── test_fonts.py                 # 字體測試工具
    ├── advanced_gpu_trend_analyzer.py # 進階趨勢分析器
    ├── quick_gpu_trend_plots.py      # 快速趨勢繪圖
    ├── gpu_trend_visualizer.py       # GPU 趨勢視覺化器
    └── gpu_trend_examples.py         # 使用範例與教學
```

## 🖥️ 節點配置

目前配置監控以下節點：

- **colab-gpu1**: 192.168.10.103
- **colab-gpu2**: 192.168.10.104  
- **colab-gpu3**: 192.168.10.105
- **colab-gpu4**: 192.168.10.106

每個節點監控 8 個 GPU ID: `1, 9, 17, 25, 33, 41, 49, 57`

## 📊 視覺化功能詳述

### 可用的圖表類型

1. **節點對比趨勢圖** - 比較各節點的平均 GPU 使用率
2. **單一節點所有 GPU 趨勢圖** - 查看特定節點內所有 GPU 的使用率趨勢
3. **特定 GPU 跨節點對比圖** - 比較相同 GPU ID 在不同節點上的使用率
4. **熱力圖** - 以熱力圖形式顯示所有 GPU 的使用率分佈
5. **詳細時間序列圖** - 顯示特定 GPU 在特定日期的詳細使用率變化
6. **綜合儀表板** - 包含多種視圖的綜合分析頁面

### 主要執行腳本命令

```bash
# 自動模式 - 偵測數據並生成所有圖表
./run_gpu_visualization.sh auto

# 快速模式 - 生成常用圖表
./run_gpu_visualization.sh quick [開始日期] [結束日期]

# 節點對比圖
./run_gpu_visualization.sh nodes [開始日期] [結束日期]

# 單一節點所有 GPU 圖
./run_gpu_visualization.sh node [節點名稱] [開始日期] [結束日期]

# 特定 GPU 跨節點對比圖
./run_gpu_visualization.sh gpu [GPU_ID] [開始日期] [結束日期]

# 熱力圖
./run_gpu_visualization.sh heatmap [開始日期] [結束日期]

# 詳細時間序列圖
./run_gpu_visualization.sh timeline [節點] [GPU_ID] [日期]

# 執行所有範例
./run_gpu_visualization.sh examples
```

### 中文字體支援

系統會自動偵測並配置最佳的中文字體：

- **Ubuntu/Debian**: Noto Sans CJK TC/SC/JP
- **Windows**: Microsoft YaHei
- **macOS**: PingFang SC
- **備用字體**: DejaVu Sans, Arial Unicode MS

如果遇到字體顯示問題，可執行字體測試：

```bash
cd visualization
python3 test_fonts.py
```

## 📋 腳本詳細說明

### 1. 數據收集與平均值計算 (`scripts/daily_gpu_log.sh`)

此腳本會從多個節點收集所有 AMD GPU 的使用率數據，並計算每日平均值。

**用法:**

```bash
./scripts/daily_gpu_log.sh [日期]
```

**參數:**

- `日期`: 可選，指定要收集的日期 (格式: YYYY-MM-DD)，如不指定則使用當天日期

**輸出:**

- 各節點的 SVG 格式 GPU 使用率圖表
- 各節點的 CSV 格式 GPU 使用率數據
- 各節點的每日 GPU 平均使用率摘要

### 2. 日期區間 GPU 使用率統計 (`scripts/calculate_gpu_range.sh`)

此腳本計算指定日期區間內，各 GPU 的平均使用率。

**用法:**

```bash
./scripts/calculate_gpu_range.sh 開始日期 結束日期 [特定 GPU ID]
```

**參數:**

- `開始日期`: 分析的起始日期 (格式: YYYY-MM-DD)
- `結束日期`: 分析的結束日期 (格式: YYYY-MM-DD)
- `特定 GPU ID`: 可選，指定要分析的 GPU ID（例如: 1, 9, 17...等）

**輸出:**

- 包含每個 GPU 平均使用率的摘要報表
- 詳細的 CSV 格式統計數據

### 3. 節點 GPU 使用率統計 (`scripts/calculate_node_gpu_usage.sh`)

此腳本針對多節點環境，計算指定日期區間內每個節點的 GPU 平均使用率。

**用法:**

```bash
./scripts/calculate_node_gpu_usage.sh 開始日期 結束日期 [節點名稱]
```

**參數:**

- `開始日期`: 分析的起始日期 (格式: YYYY-MM-DD)
- `結束日期`: 分析的結束日期 (格式: YYYY-MM-DD)
- `節點名稱`: 可選，指定要分析的節點 (例如: colab-gpu1)

**輸出:**

- 各節點的平均 GPU 使用率統計
- 各節點中每個 GPU 的平均使用率統計
- 每日使用率統計
- CSV 格式的詳細數據

### 4. 時間轉換工具 (`scripts/test/time_convert.sh`)

輔助工具，用於在日期時間與 Unix 時間戳之間進行轉換，支援多種時區。

**用法:**

```bash
# 日期轉時間戳記
./scripts/test/time_convert.sh date2ts "2025-05-27 00:00:00" [時區]

# 時間戳記轉日期
./scripts/test/time_convert.sh ts2date 1748217600 [時區]
```

## ⚙️ 系統需求與安裝

### 依賴項

**Shell 腳本:**

- `bash`
- `curl`
- `jq`
- `awk`
- `bc` (基本計算器)

**Python 視覺化:**

- Python 3.7+
- 套件列表請參考 `requirements.txt` 或 `visualization/requirements.txt`

### 安裝步驟

```bash
# 1. 克隆專案
git clone <repository-url>
cd data_collection

# 2. 安裝 Python 依賴
pip install -r visualization/requirements.txt

# 3. 設定執行權限
chmod +x run_gpu_visualization.sh
chmod +x scripts/*.sh
chmod +x scripts/test/*.sh
chmod +x visualization/run_viz.sh

# 4. 測試字體配置
cd visualization && python3 test_fonts.py
```

## ⏰ 定時任務配置

系統可設定在每天晚上 23:45 自動執行數據收集：

```bash
# 編輯 crontab
crontab -e

# 添加以下行
45 23 * * * /bin/bash /path/to/data_collection/scripts/daily_gpu_log.sh
```

## 📝 使用範例

### 收集今天的 GPU 使用率數據

```bash
./scripts/daily_gpu_log.sh
```

### 統計特定日期範圍的節點使用率

```bash
./scripts/calculate_node_gpu_usage.sh 2025-05-01 2025-05-15
```

### 分析特定節點的 GPU 使用率

```bash
./scripts/calculate_node_gpu_usage.sh 2025-05-01 2025-05-15 colab-gpu1
```

### 查看特定 GPU 的使用率統計

```bash
./scripts/calculate_gpu_range.sh 2025-05-01 2025-05-15 1
```

### 生成視覺化圖表

```bash
# 快速生成所有常用圖表
./run_gpu_visualization.sh quick 2025-05-23 2025-05-26

# 生成特定類型圖表
./run_gpu_visualization.sh heatmap 2025-05-23 2025-05-26
./run_gpu_visualization.sh nodes 2025-05-23 2025-05-26
```

### 將日期時間轉換為時間戳記

```bash
./scripts/test/time_convert.sh date2ts "2025-05-27 00:00:00" Asia/Taipei
```

## 🎯 進階功能

### 直接使用 Python 視覺化工具

```bash
cd visualization

# 使用快速繪圖工具
python3 quick_gpu_trend_plots.py

# 使用進階分析器
python3 advanced_gpu_trend_analyzer.py --start-date 2025-05-23 --end-date 2025-05-26 --mode all

# 執行所有範例
python3 gpu_trend_examples.py
```

### 自訂視覺化腳本

可以基於 `visualization/` 目錄中的模組創建自訂的視覺化腳本。詳細說明請參考：

- `visualization/README.md` - 視覺化工具說明
- `visualization/GPU_TREND_VISUALIZATION_GUIDE.md` - 詳細使用指南
- `VISUALIZATION_QUICK_START.md` - 快速指南

## ⚠️ 注意事項

- 這些腳本依賴於 Netdata 監控系統來收集 GPU 使用率數據
- 確保各節點的 Netdata 服務正常運行並可透過網路存取
- 若要調整 GPU 的採樣頻率，可修改 `daily_gpu_log.sh` 中的 `POINTS` 變數
- 數據目錄 `data/` 已加入 `.gitignore`，不會被提交到版本控制
- 圖表輸出目錄為 `plots/`，建議定期清理舊圖表

## 🔧 故障排除

### 字體顯示問題

如果圖表中的中文文字顯示為方塊或亂碼：

```bash
cd visualization
python3 test_fonts.py
```

### 數據收集問題

1. 檢查 Netdata 服務狀態
2. 驗證節點網路連接
3. 檢查腳本執行權限

### Python 依賴問題

```bash
# 重新安裝依賴
pip install -r visualization/requirements.txt

# 檢查 Python 版本
python3 --version
```

## 📄 License

<a href="http://www.wtfpl.net/"><img
       src="https://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-1.png"
       width="88" height="31" alt="WTFPL" /></a>

This project uses the WTFPL license (Do What The Fuck You Want To Public License)
