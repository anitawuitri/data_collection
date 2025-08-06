# GPU 監控系統使用者資訊功能說明

## 概述

本系統已成功整合使用者資訊功能，可在 GPU 監控報告和視覺化圖表中顯示使用者資訊。

## 功能特色

### 1. CSV 報告中的使用者資訊
- **檔案位置**: `data/{node}/{date}/average_{date}.csv`
- **新增欄位**: `使用者` 欄位顯示每個 GPU 的使用者名稱
- **格式範例**:
  ```csv
  GPU編號,平均GPU使用率(%),平均VRAM使用率(%),使用者
  GPU[0],0.00,0.00,nycubme
  GPU[1],0.00,0.00,nycubme
  GPU[2],0.00,0.00,itrd
  ```

### 2. 視覺化圖表中的使用者資訊
- **圖表標題**: 自動包含使用者資訊摘要
- **圖例增強**: 顯示 GPU 編號和對應使用者
- **控制參數**: `show_users=True/False` 控制是否顯示使用者資訊

### 3. 新增的圖表類型
- **使用者活動摘要**: 專門顯示使用者在各節點的 GPU 使用情況
- **GPU 使用率熱力圖**: 顯示多日期、多節點的 GPU 使用率分佈及使用者資訊
- **增強版節點對比**: 包含使用者資訊的節點使用率對比
- **單節點 GPU 詳情**: 顯示特定節點所有 GPU 及其使用者
- **跨節點 GPU 比較**: 同編號 GPU 在不同節點的使用者分佈

## 使用方法

### 1. 資料收集（包含使用者資訊）
```bash
# 收集今日資料
python3 python/daily_gpu_log.py

# 收集指定日期資料
python3 python/daily_gpu_log.py 2025-08-04
```

### 2. 快速視覺化（包含使用者資訊）
```bash
# 生成包含使用者資訊的所有圖表（包括熱力圖）
python3 visualization/quick_gpu_trend_plots.py 2025-08-04 2025-08-05

# 使用統一管理腳本生成所有圖表
./run_user_monitor.sh quick 2025-08-04 2025-08-05

# 單獨生成熱力圖
./run_user_monitor.sh heatmap 2025-08-04 2025-08-05

# 生成不包含使用者資訊的圖表
python3 visualization/quick_gpu_trend_plots.py 2025-08-04 2025-08-05 --no-users
```

### 3. 程式化使用
```python
from quick_gpu_trend_plots import *

# 節點對比（包含使用者資訊）
quick_nodes_trend('2025-08-04', '2025-08-05', show_users=True)

# 單節點GPU詳情（包含使用者資訊）
quick_single_node_gpus('colab-gpu4', '2025-08-04', '2025-08-05', show_users=True)

# 跨節點GPU比較（包含使用者資訊）
quick_gpu_across_nodes(0, '2025-08-04', '2025-08-05', show_users=True)

# 使用者活動摘要（專門的使用者資訊圖表）
quick_user_activity_summary('2025-08-04', '2025-08-05')

# GPU 使用率熱力圖（包含使用者資訊）
quick_gpu_heatmap('2025-08-04', '2025-08-05', show_users=True)
```

## 核心函數說明

### 1. `load_gpu_data_with_users(csv_file)`
- **功能**: 讀取包含使用者資訊的 CSV 檔案
- **回傳**: DataFrame，包含 gpu, usage, vram, user 欄位

### 2. `get_user_info_for_node(node, date, data_dir)`
- **功能**: 獲取特定節點在特定日期的使用者資訊
- **回傳**: 字典，GPU編號對應使用者名稱

### 3. `quick_user_activity_summary(start_date, end_date)`
- **功能**: 生成使用者活動摘要圖表
- **特色**: 顯示各使用者在不同節點的 GPU 使用分佈

### 4. `quick_gpu_heatmap(start_date, end_date, show_users=True)`
- **功能**: 生成 GPU 使用率熱力圖
- **特色**: 顯示多日期、多節點的使用率分佈及使用者資訊

## 技術細節

### 1. GPU ID 對應關系
- **API 絕對 ID**: 0-31 (連續編號)
- **硬體 Card ID**: 1, 9, 17, 25, 33, 41, 49, 57 (每節點 8 個)
- **對應函數**: `map_absolute_gpu_to_card_id()`

### 2. 使用者資訊來源
- **API 端點**: `http://192.168.10.100/api/v2/consumption/task`
- **認證方式**: JWT Bearer Token
- **資料格式**: JSON，包含使用者名稱和 GPU 資訊

### 3. 字體配置
- **中文字體**: Noto Sans CJK JP
- **配置檔案**: `font_config.py`
- **自動載入**: 所有視覺化函數自動使用中文字體

## 範例輸出

### 1. 終端輸出範例
```
GPU監控報告 - 2025-08-04
==================================================
節點: colab-gpu4
==================================================
GPU[0] (Card 1, nycubme): 平均使用率 = 0.00%
GPU[1] (Card 9, nycubme): 平均使用率 = 0.00%
GPU[2] (Card 17, itrd): 平均使用率 = 0.00%
GPU[3] (Card 25, itrd): 平均使用率 = 0.00%
GPU[4] (Card 33, admin): 平均使用率 = 0.00%
GPU[5] (Card 41, tku_csie): 平均使用率 = 0.00%
GPU[6] (Card 49, easycard): 平均使用率 = 0.08%
GPU[7] (Card 57): 平均使用率 = 0.00%
```

### 2. 圖表標題範例
```
GPU 使用率趨勢 (2025-08-04 to 2025-08-05)
使用者: nycubme(2), itrd(2), admin(1), tku_csie(1), easycard(1)
```

### 3. 使用者分佈統計
```
使用者分佈統計：
  nycubme: 2 個 GPU
  itrd: 2 個 GPU
  admin: 1 個 GPU
  tku_csie: 1 個 GPU
  easycard: 1 個 GPU
  未使用: 1 個 GPU
```

## 測試和驗證

### 1. 功能測試
```bash
# 運行完整功能測試
python3 visualization/test_user_info.py

# 驗證圖表檔案
python3 visualization/chart_verification.py
```

### 2. 驗證檢查項目
- ✓ 資料讀取功能 - 成功讀取 CSV 檔案並解析使用者資訊
- ✓ 使用者資訊提取 - 正確從檔案中提取使用者名稱
- ✓ 圖表標題增強 - 包含使用者資訊的圖表標題
- ✓ 多種圖表類型 - 節點對比、單節點GPU、跨節點、使用者活動摘要
- ✓ 中文字體支援 - 正確顯示中文字元
- ✓ 參數控制 - show_users 參數可控制是否顯示使用者資訊

## 故障排除

### 1. 使用者資訊顯示為 "未使用"
- **原因**: Management API 無法取得該 GPU 的使用者資訊
- **解決**: 檢查 API 連線和 GPU 是否有活動任務

### 2. 圖表中文字顯示異常
- **原因**: 缺少中文字體
- **解決**: 安裝 Noto Sans CJK 字體包

### 3. CSV 檔案格式錯誤
- **原因**: 資料收集過程中出現異常
- **解決**: 重新運行資料收集腳本

## 更新歷史

### v2.0 (2025-08-06)
- ✅ 修復 GPU ID 對應問題
- ✅ 新增使用者資訊顯示功能
- ✅ 增強視覺化系統
- ✅ 新增使用者活動摘要圖表
- ✅ 完整的中文字體支援

### v1.0 (2025-05-xx)
- ✅ 基礎 GPU 監控功能
- ✅ CSV 報告生成
- ✅ 基本視覺化圖表
