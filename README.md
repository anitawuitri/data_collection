# AMD GPU 使用率監控與視覺化工具

[![License: WTFPL](https://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-2.png)](http://www.wtfpl.net/)

> 🎉 **重大更新 (2025-08-01)**: GPU 使用者追蹤系統正式上線！
> 
> ✨ **新功能亮點**:
> - 🔥 **GPU 使用者追蹤** - 即時顯示哪些使用者正在使用哪些 GPU
> - 🗃️ **硬體對應表** - 自動建立 GPU Card ID 到 GPU Index 對應關係
> - 📊 **使用者欄位報表** - CSV 檔案和摘要報告包含詳細使用者資訊
> - 🔗 **管理 API 整合** - 透過 JWT 認證獲取使用者任務資訊
> - 🏗️ **物件導向設計** - 模組化架構，易於維護和擴展

完整的 AMD GPU 使用率監控與視覺化解決方案，支援多節點環境的 GPU 監控、數據收集、分析和視覺化。

## ✨ 主要功能

### 🖥️ 數據收集與監控
- **多節點 GPU 監控** - 同時監控多個節點的 AMD GPU 使用率與 VRAM 使用量
- **🔥 GPU 使用者追蹤** - 即時顯示哪些使用者正在使用哪些 GPU
- **硬體對應系統** - 自動建立 GPU 硬體 ID 與 GPU 索引的對應表
- **管理 API 整合** - 透過 JWT 認證連接管理系統獲取使用者任務資訊
- **自動化數據收集** - 支援定時任務，每日自動收集 GPU 與 VRAM 使用率數據  
- **詳細統計分析** - 計算平均使用率、生成摘要報告

### 📊 視覺化與分析
- **多種圖表類型** - 節點對比、GPU趨勢、VRAM分析、熱力圖、時間序列分析
- **🔥 堆疊區域圖** - 新增 GPU/VRAM 使用率堆疊圖，清楚展示各節點貢獻
- **中文字體支援** - 自動配置中文字體，完美顯示中文標籤
- **跨平台相容** - 支援 Linux、Windows、macOS

### 🛠️ 工具與腳本
- **🔥 Python 數據收集器** - 功能完整的 Python 版本，提供更好的錯誤處理和擴展性
- **Shell 數據收集腳本** - 原始穩定的 Bash 版本數據收集工具
- **日期區間分析** - 靈活的時間範圍分析功能
- **節點對比分析** - 多節點效能比較工具

##  快速開始

**1. 環境檢查與測試**
```bash
# 檢查環境並測試所有功能
python3 python/test_gpu_collector.py
```

**2. 立即開始收集數據**
```bash
# 收集今天的 GPU 數據（推薦使用 Python 版本）
./python/run_daily_gpu_log.sh
```

**3. 生成視覺化圖表**
```bash
# 自動偵測數據並生成所有圖表
./run_gpu_visualization.sh auto
```

## 📖 詳細使用說明

### 1. 數據收集

#### 🔥 Python 版本 (推薦)
基於 Python 開發，提供更好的錯誤處理、數據驗證和 API 整合。

```bash
# 收集今天的數據
./python/run_daily_gpu_log.sh

# 收集指定日期的數據
./python/run_daily_gpu_log.sh 2025-08-01

# 查看說明
./python/run_daily_gpu_log.sh --help
```

**輸出檔案:**
- CSV 報表 (`average_YYYY-MM-DD.csv`): 包含 GPU/VRAM 使用率及使用者資訊。
- 摘要報告 (`summary_YYYY-MM-DD.txt`): 包含詳細的使用者任務資訊。

#### Shell 版本 (備用)
原始的 Bash 腳本，功能穩定但擴展性較低。

```bash
./scripts/daily_gpu_log.sh [日期]
```

### 2. 視覺化工具

使用 `run_gpu_visualization.sh` 腳本生成各種圖表。

```bash
# 自動模式 - 偵測數據並生成所有圖表
./run_gpu_visualization.sh auto

# 快速模式 - 生成常用圖表
./run_gpu_visualization.sh quick [開始日期] [結束日期]

# 🔥 各節點 GPU 使用率堆疊區域圖（新功能）
./run_gpu_visualization.sh stacked [開始日期] [結束日期]

# 🔥 各節點 VRAM 使用率堆疊區域圖（新功能）
./run_gpu_visualization.sh vram-stacked [開始日期] [結束日期]

# 節點對比圖
./run_gpu_visualization.sh nodes [開始日期] [結束日期]

# 熱力圖
./run_gpu_visualization.sh heatmap [開始日期] [結束日期]

# 執行所有範例
./run_gpu_visualization.sh examples
```

### 3. 分析工具

#### 🔥 Colab-GPU 專用統計工具
專為 colab-gpu 1-4 節點設計的綜合分析工具。

```bash
# 簡潔總平均摘要（自動最新日期）
./colab_gpu_stats.sh

# 詳細分析（包含IP、活躍GPU等）
./colab_gpu_stats.sh detailed [日期]

# 🔥 各使用者平均 GPU 使用率
./colab_gpu_stats.sh user [日期]

# 趨勢分析
./colab_gpu_stats.sh trend [開始日期] [結束日期]
```

#### 通用總平均工具
```bash
# 最近一天的總平均
./gpu_total_avg.sh

# 指定日期的總平均
./gpu_total_avg.sh custom [日期]
```

#### 其他腳本
- `scripts/calculate_gpu_range.sh`: 日期區間 GPU 使用率統計
- `scripts/calculate_node_gpu_usage.sh`: 節點使用率分析

### 🔥 使用者監控腳本 (run_user_monitor.sh)
整合了數據收集、視覺化和使用者查詢功能的綜合工具。

```bash
# 顯示使用說明
./run_user_monitor.sh help

# 常用命令
./run_user_monitor.sh collect [日期]           # 收集數據
./run_user_monitor.sh quick <開始> <結束>       # 快速圖表
./run_user_monitor.sh query-user <使用者> <日期> # 查詢使用者
```


## ⚙️ 配置與安裝

### 系統需求
- **Python**: 3.7+
- **Python 套件**: `requests`, `pandas` (數據收集); `matplotlib`, `seaborn` (視覺化)
- **Shell 工具**: `bash`, `curl`, `jq`, `awk`, `bc`

### 安裝步驟

1. **克隆專案**
   ```bash
   git clone <repository-url>
   cd data_collection
   ```

2. **安裝依賴**
   ```bash
   # 安裝數據收集器依賴
   pip3 install -r python/requirements.txt
   
   # 安裝視覺化工具依賴
   pip3 install -r visualization/requirements.txt
   ```

3. **設定權限**
   ```bash
   chmod +x python/run_daily_gpu_log.sh
   chmod +x run_gpu_visualization.sh
   chmod +x scripts/*.sh
   chmod +x *.sh
   ```

### 節點配置
目前配置監控以下節點：
- **colab-gpu1**: 192.168.10.103
- **colab-gpu2**: 192.168.10.104
- **colab-gpu3**: 192.168.10.105
- **colab-gpu4**: 192.168.10.106

每個節點監控 8 個 GPU ID: `1, 9, 17, 25, 33, 41, 49, 57`

### 🔥 GPU 硬體對應表
系統自動建立以下對應關係：
| GPU Index | Card ID |
|-----------|---------|
| GPU[0] | Card 1 |
| ... | ... |
| GPU[7] | Card 57 |

### ⏰ 定時任務 (Crontab)
建議設定在每天晚上 23:45 自動執行：

```bash
45 23 * * * /bin/bash /path/to/data_collection/python/run_daily_gpu_log.sh
```

## 📁 專案結構

```text
data_collection/
├── README.md                           # 專案說明文件
├── run_gpu_visualization.sh           # 主要視覺化執行腳本
├── colab_gpu_stats.sh                 # 🔥 Colab GPU 綜合統計工具
├── gpu_total_avg.sh                   # 通用總平均工具
├── python/                           # 🔥 Python 版本數據收集器
│   ├── daily_gpu_log.py             # 核心收集腳本
│   ├── run_daily_gpu_log.sh         # 執行腳本
│   └── requirements.txt             # 依賴套件
├── scripts/                          # Shell 版本腳本
│   ├── daily_gpu_log.sh             # 核心收集腳本
│   └── ...
├── visualization/                    # Python 視覺化工具集
│   ├── gpu_trend_visualizer.py      # 核心繪圖邏輯
│   ├── run_viz.sh                   # 執行腳本
│   └── ...
├── data/                              # 數據目錄 (git 忽略)
└── plots/                             # 圖表輸出目錄
```
