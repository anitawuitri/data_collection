# GPU 硬體對應表功能整合報告

## 概述
已成功將 GPU 硬體對應表功能整合到 `daily_gpu_log.sh` 和 `daily_gpu_log.py` 中，基於 `gpu_hardware_mapping.txt` 檔案的對應關係。

## 主要變更

### 1. 建立硬體對應檔案
- **檔案**: `gpu_hardware_mapping.txt`
- **內容**: DRM card ID 到 GPU index 的對應關係
- **格式**: `card{id} -> GPU[{index}]`

### 2. Shell 腳本更新 (`scripts/daily_gpu_log.sh`)

#### 新增功能:
- **GPU 對應陣列**: 建立 `GPU_CARD_TO_INDEX` 和 `GPU_INDEX_TO_CARD` 關聯陣列
- **變數重新定義**: 
  - `GPU_CARD_IDS`: 用於 API 查詢的 card IDs
  - `CARD_ID`, `GPU_INDEX`: 在迴圈中使用的變數
- **檔案命名**: 使用 GPU index 而非 card ID 命名檔案
- **顯示功能**: 在執行時顯示硬體對應表

#### 修改的程式碼區段:
1. **對應表初始化** (第 25-42 行)
2. **數據收集迴圈** (第 60-90 行)
3. **平均值計算** (第 100-130 行)
4. **摘要報告生成** (第 140-160 行)

### 3. Python 腳本更新 (`python/daily_gpu_log.py`)

#### 新增功能:
- **對應字典**: `gpu_card_to_index` 和 `gpu_index_to_card`
- **雙重列表**: 
  - `gpu_card_ids`: 用於 API 查詢
  - `gpu_indices`: 用於檔案命名
- **檔案命名**: 統一使用 GPU index
- **報告增強**: 在摘要中包含硬體對應表

#### 修改的類別方法:
1. **`__init__`**: 初始化對應表
2. **`process_gpu_data`**: 使用新的變數命名
3. **`calculate_averages`**: 更新檔案處理邏輯
4. **`generate_summary_report`**: 加入硬體對應資訊

### 4. 測試與驗證工具

#### 新建檔案:
- **`test_gpu_mapping.py`**: 完整的對應表功能測試
- **`demo_gpu_mapping.sh`**: 功能示範腳本

## 功能變化對比

### 舊系統:
- 檔案命名: `gpu1_date.csv`, `gpu9_date.csv`, `gpu17_date.csv`...
- 報告顯示: `GPU 1`, `GPU 9`, `GPU 17`...
- 無硬體對應資訊

### 新系統:
- 檔案命名: `gpu0_date.csv`, `gpu1_date.csv`, `gpu2_date.csv`...
- 報告顯示: `GPU[0] (Card 1)`, `GPU[1] (Card 9)`, `GPU[2] (Card 17)`...
- 包含完整硬體對應表

## 相容性
- **API 查詢**: 仍使用原始 card ID，確保與 Netdata 相容
- **資料格式**: CSV 檔案內部格式不變
- **功能性**: 所有原有功能保持完整

## 驗證結果
✅ Python 版本對應表測試通過
✅ Shell 版本對應表測試通過  
✅ 雙向對應一致性驗證通過
✅ 檔案命名邏輯正確
✅ 硬體對應表顯示正常

## 使用方式
兩個腳本的使用方式保持不變:

### Shell 版本:
```bash
./scripts/daily_gpu_log.sh [日期]
```

### Python 版本:
```bash
python3 python/daily_gpu_log.py [日期]
```

## 輸出檔案範例
現在的檔案結構將是:
```
data/colab-gpu1/2025-05-25/
├── gpu0_2025-05-25.csv    # 原 gpu1_2025-05-25.csv
├── gpu1_2025-05-25.csv    # 原 gpu9_2025-05-25.csv  
├── gpu2_2025-05-25.csv    # 原 gpu17_2025-05-25.csv
├── ...
├── average_2025-05-25.csv
└── summary_2025-05-25.txt (包含硬體對應表)
```

## 結論
GPU 硬體對應表功能已成功整合到兩個版本的腳本中，提供更清晰的 GPU 識別方式，同時保持與現有系統的完全相容性。
