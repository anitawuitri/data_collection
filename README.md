# AMD GPU 使用率監控工具
[![License: WTFPL](https://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-2.png)](http://www.wtfpl.net/)

此專案提供一組用於收集、分析和視覺化 AMD GPU 使用率的腳本工具，支援從多個節點收集數據，並進行詳細的使用率統計分析。

## 功能概述

- 從多個節點收集 AMD GPU 使用率數據
- 計算每日及每個節點的 GPU 平均使用率
- 針對多節點環境進行 GPU 使用率統計
- 生成詳細的 GPU 使用率報告與 CSV 數據檔案
- 提供日期區間分析功能

## 節點配置

目前配置監控以下節點：
- **colab-gpu1**: 192.168.10.103
- **colab-gpu2**: 192.168.10.104
- **colab-gpu3**: 192.168.10.105
- **colab-gpu4**: 192.168.10.106

每個節點監控 8 個 GPU ID: 1, 9, 17, 25, 33, 41, 49, 57

## 腳本說明

### 1. 數據收集與平均值計算 (`scripts/daily_gpu_log.sh`)

此腳本會從多個節點收集所有 AMD GPU 的使用率數據，並計算每日平均值。會每天 23:45 自動執行。

用法:
```bash
./scripts/daily_gpu_log.sh [日期]
```

參數:
- `日期`: 可選，指定要收集的日期 (格式: YYYY-MM-DD)，如不指定則使用當天日期

輸出:
- 各節點的 SVG 格式 GPU 使用率圖表
- 各節點的 CSV 格式 GPU 使用率數據
- 各節點的每日 GPU 平均使用率摘要

### 2. 日期區間 GPU 使用率統計 (`scripts/calculate_gpu_range.sh`)

此腳本計算指定日期區間內，各 GPU 的平均使用率。

用法:
```bash
./scripts/calculate_gpu_range.sh 開始日期 結束日期 [特定 GPU ID]
```

參數:
- `開始日期`: 分析的起始日期 (格式: YYYY-MM-DD)
- `結束日期`: 分析的結束日期 (格式: YYYY-MM-DD)
- `特定 GPU ID`: 可選，指定要分析的 GPU ID（例如: 1, 9, 17...等）

輸出:
- 包含每個 GPU 平均使用率的摘要報表
- 詳細的 CSV 格式統計數據

### 3. 節點 GPU 使用率統計 (`scripts/calculate_node_gpu_usage.sh`)

此腳本針對多節點環境，計算指定日期區間內每個節點的 GPU 平均使用率。

用法:
```bash
./scripts/calculate_node_gpu_usage.sh 開始日期 結束日期 [節點名稱]
```

參數:
- `開始日期`: 分析的起始日期 (格式: YYYY-MM-DD)
- `結束日期`: 分析的結束日期 (格式: YYYY-MM-DD)
- `節點名稱`: 可選，指定要分析的節點 (例如: colab-gpu1)

輸出:
- 各節點的平均 GPU 使用率統計
- 各節點中每個 GPU 的平均使用率統計
- 每日使用率統計
- CSV 格式的詳細數據

### 4. 時間轉換工具 (`scripts/test/time_convert.sh`)

輔助工具，用於在日期時間與 Unix 時間戳之間進行轉換，支援多種時區。

用法:
```bash
# 日期轉時間戳記
./scripts/test/time_convert.sh date2ts "2025-05-27 00:00:00" [時區]

# 時間戳記轉日期
./scripts/test/time_convert.sh ts2date 1748217600 [時區]
```

## 數據存放結構

```
data_collection/
├── data/
│   ├── colab-gpu1/          # colab-gpu1 節點的數據
│   │   ├── 2025-05-23/      # 依日期存放
│   │   │   ├── average_2025-05-23.csv # 平均使用率
│   │   │   ├── gpu1_2025-05-23.csv    # GPU 1 數據
│   │   │   ├── gpu1_2025-05-23.svg    # GPU 1 圖表
│   │   │   └── summary_2025-05-23.txt # 摘要報告
│   │   └── ...
│   ├── colab-gpu2/          # colab-gpu2 節點的數據
│   ├── colab-gpu3/          # colab-gpu3 節點的數據
│   ├── colab-gpu4/          # colab-gpu4 節點的數據
│   └── reports/             # 綜合報告
│       ├── node_gpu_usage_*.csv       # 節點分析數據
│       ├── node_gpu_summary_*.txt     # 節點分析摘要
│       ├── gpu_usage_*.csv            # 單 GPU 分析數據
│       └── gpu_summary_*.txt          # 單 GPU 分析摘要
├── scripts/
│   ├── daily_gpu_log.sh              # 主要數據收集腳本
│   ├── calculate_gpu_range.sh        # GPU 日期區間分析
│   ├── calculate_node_gpu_usage.sh   # 節點使用率分析
│   └── test/                         # 輔助工具
│       └── time_convert.sh           # 時間轉換工具
└── README.md                         # 專案說明文件
```

## 定時任務

系統設定在每天晚上 23:45 自動執行 `daily_gpu_log.sh`，收集當天的 GPU 使用率數據：
```
45 23 * * * /bin/bash /home/amditri/data_collection/scripts/daily_gpu_log.sh
```

## 依賴項

- `bash`
- `curl`
- `jq`
- `awk`
- `bc` (基本計算器)

## 範例

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

### 將日期時間轉換為時間戳記
```bash
./scripts/test/time_convert.sh date2ts "2025-05-27 00:00:00" Asia/Taipei
```

## 注意事項

- 這些腳本依賴於 Netdata 監控系統來收集 GPU 使用率數據
- 確保各節點的 Netdata 服務正常運行並可透過網路存取
- 若要調整 GPU 的採樣頻率，可修改 `daily_gpu_log.sh` 中的 `POINTS` 變數

### License information
<a href="http://www.wtfpl.net/"><img
       src="https://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-1.png"
       width="88" height="31" alt="WTFPL" /></a>

This projects uses the WTFPL license (Do What The Fuck You Want To Public License)