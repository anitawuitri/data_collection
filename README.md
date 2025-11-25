# AMD GPU 使用率監控與視覺化工具

[![License: WTFPL](https://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-2.png)](http://www.wtfpl.net/)

> 🎉 **重大更新 (2025-11-25)**: Docker 執行環境與自動化功能上線！
>
> ✨ **新功能亮點**:
> - 🐳 **Docker 支援** - 提供一致的執行環境，免去繁瑣的依賴安裝
> - 🤖 **自動化排程** - 內建 Cron Job 設定腳本，自動處理數據收集、繪圖與歸檔
> - 📦 **數據歸檔** - 自動按月歸檔舊數據，保持工作目錄整潔
> - 📈 **週報表** - 自動生成每週 GPU 使用趨勢圖
>
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
- **🐳 Docker 容器化** - 透過 Docker 確保執行環境一致性

### 📊 視覺化與分析
- **多種圖表類型** - 節點對比、GPU趨勢、VRAM分析、熱力圖、時間序列分析
- **🔥 堆疊區域圖** - 新增 GPU/VRAM 使用率堆疊圖，清楚展示各節點貢獻
- **中文字體支援** - 自動配置中文字體，完美顯示中文標籤
- **跨平台相容** - 支援 Linux、Windows、macOS
- **📈 自動週報表** - 每週自動生成趨勢圖表

### 🛠️ 工具與腳本
- **🔥 Python 數據收集器** - 功能完整的 Python 版本，提供更好的錯誤處理和擴展性
- **Shell 數據收集腳本** - 原始穩定的 Bash 版本數據收集工具
- **日期區間分析** - 靈活的時間範圍分析功能
- **節點對比分析** - 多節點效能比較工具
- **📦 自動歸檔工具** - 按月歸檔歷史數據

##  快速開始

**1. 環境準備**
確保系統已安裝 Docker。

**2. 立即開始收集數據**
```bash
# 收集今天的 GPU 數據 (自動構建 Docker 映像檔)
./run_user_monitor.sh collect
```

**3. 設定自動化排程**
```bash
# 安裝 Crontab 排程 (每日收集、每週繪圖、每月歸檔)
./setup_cron.sh
```

## 📖 詳細使用說明

### 1. 數據收集 (Docker 版本)

使用 `run_user_monitor.sh` 腳本，它會自動處理 Docker 容器的構建與執行。

```bash
# 收集今天的數據 (預設)
./run_user_monitor.sh collect

# 收集指定日期的數據
./run_user_monitor.sh collect 2025-11-25

# 查看說明
./run_user_monitor.sh help
```

**輸出檔案:**
數據會保存在主機的 `data/` 目錄中，該目錄會掛載到容器內。

### 2. 視覺化工具

同樣使用 `run_user_monitor.sh` 執行視覺化命令。

```bash
# 快速模式 - 生成常用圖表
./run_user_monitor.sh quick [開始日期] [結束日期]

# 生成上週圖表
./run_user_monitor.sh weekly-plot

# 其他視覺化命令與之前相同，只需將腳本換為 ./run_user_monitor.sh
./run_user_monitor.sh heatmap [開始日期] [結束日期]
```

### 3. 數據歸檔

將舊數據移動到 `data_archive/` 目錄。

```bash
# 歸檔上個月的數據
./run_user_monitor.sh archive

# 歸檔指定月份的數據
./run_user_monitor.sh archive --month 2025-10

# 測試歸檔 (不移動檔案)
./run_user_monitor.sh archive --dry-run
```

### 🔥 使用者監控腳本 (run_user_monitor.sh)
整合了數據收集、視覺化和使用者查詢功能的綜合工具。

```bash
# 顯示使用說明
./run_user_monitor.sh help

# 常用命令
./run_user_monitor.sh collect [日期]           # 收集數據
./run_user_monitor.sh quick <開始> <結束>       # 快速圖表
./run_user_monitor.sh query-user <使用者> <日期> # 查詢使用者
./run_user_monitor.sh archive                  # 歸檔數據
./run_user_monitor.sh weekly-plot              # 週報表
```


## ⚙️ 配置與安裝

### 系統需求
- **Docker**: 建議最新版本
- **Linux**: 支援 Docker 的發行版

### 安裝步驟

1. **克隆專案**
   ```bash
   git clone <repository-url>
   cd data_collection
   ```

2. **執行腳本**
   直接執行 `run_user_monitor.sh` 即可，首次執行會自動構建 Docker 映像檔。

### ⏰ 定時任務 (Crontab)
使用 `setup_cron.sh` 自動設定 Crontab：

```bash
./setup_cron.sh
```

這將設定：
- **每日 23:55**: 收集當日數據
- **每週日 00:30**: 生成過去 7 天的圖表
- **每月 1 日 01:00**: 歸檔上個月的數據

## 📁 專案結構

```text
data_collection/
├── README.md                           # 專案說明文件
├── Dockerfile                         # 🐳 Docker 建置檔
├── run_user_monitor.sh                # 🚀 主要執行腳本 (Docker Wrapper)
├── setup_cron.sh                      # 🤖 自動化排程設定腳本
├── run_gpu_visualization.sh           # (舊版) 視覺化執行腳本
├── colab_gpu_stats.sh                 # 🔥 Colab GPU 綜合統計工具
├── gpu_total_avg.sh                   # 通用總平均工具
├── python/                           # 🔥 Python 版本數據收集器
│   ├── daily_gpu_log.py             # 核心收集腳本
│   ├── run_daily_gpu_log.sh         # 執行腳本
│   └── requirements.txt             # 依賴套件
├── scripts/                          # Shell 版本腳本
│   ├── daily_gpu_log.sh             # 核心收集腳本
│   ├── archive_data.py              # 📦 數據歸檔腳本
│   └── ...
├── visualization/                    # Python 視覺化工具集
│   ├── gpu_trend_visualizer.py      # 核心繪圖邏輯
│   ├── run_viz.sh                   # 執行腳本
│   └── ...
├── data/                              # 數據目錄 (git 忽略)
├── data_archive/                      # 📦 歸檔數據目錄
└── plots/                             # 圖表輸出目錄
```
